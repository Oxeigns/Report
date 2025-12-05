#!/usr/bin/env python3
# main.py
# OxyReport - Fully Streamlined & Concurrent
# Features: Multi-Session Concurrency, FloodWait Handling, Existence Check

import asyncio
import re
import os
import datetime
import sys
from pyrogram import Client
from pyrogram.errors import FloodWait, BadRequest, RPCError
# Assuming send_report is in report.py. 
# If you want FloodWait to work perfectly, send_report must NOT catch exceptions internally,
# or it must re-raise them.
from report import send_report 

# Shared variables for concurrency
TOTAL_SENT = 0
STOP_EVENT = asyncio.Event()

def parse_message_url(url: str):
    url = url.strip()
    m = re.search(r"(?:t\.me|telegram\.me)/(c/)?([^/]+)/?(\d+)?", url)
    if not m:
        raise ValueError("Invalid message URL format.")
    
    c_group = m.group(1) 
    part = m.group(2)    
    msg = m.group(3)     

    if msg:
        message_id = int(msg)
        if c_group == "c/":
            chat_id = int("-100" + part)
        else:
            chat_id = part if not part.isdigit() else int(part)
    else:
        raise ValueError("Message ID missing in URL.")
    
    return chat_id, message_id

async def verify_message(client, chat_id, message_id):
    """Checks if the message exists before starting."""
    try:
        msg = await client.get_messages(chat_id, message_ids=message_id)
        if msg.empty:
            return False
        return True
    except Exception as e:
        print(f"Error verifying message: {e}")
        return False

async def report_worker(client, chat_id, message_id, reason_code, reason_text, total_target, session_name):
    """
    Worker function for each session. 
    Runs concurrently and handles FloodWait.
    """
    global TOTAL_SENT
    
    while not STOP_EVENT.is_set():
        if TOTAL_SENT >= total_target:
            break

        try:
            # We assume send_report performs the API call. 
            # Ideally, send_report should just return the result of client.send_report
            # For this logic to work best, we call the API directly or handle the specific error here.
            
            # Using the imported function (Make sure report.py allows exceptions to propagate or handles them)
            success = await send_report(client, chat_id, message_id, reason_code, reason_text)
            
            if success:
                TOTAL_SENT += 1
                print(f"[{TOTAL_SENT}/{total_target}] Sent via {session_name}")
            else:
                # If success is False without exception, it might be a generic fail
                await asyncio.sleep(1) 

        except FloodWait as e:
            print(f"[{session_name}] FloodWait hit! Sleeping for {e.value} seconds (Real User Mode).")
            await asyncio.sleep(e.value)
        
        except BadRequest as e:
            # If message is deleted or invalid (INPUT_USER_DEACTIVATED, MESSAGE_ID_INVALID, etc.)
            print(f"[{session_name}] Stop Signal: Message invalid or deleted. ({e})")
            STOP_EVENT.set()
            break
            
        except RPCError as e:
            print(f"[{session_name}] RPC Error: {e}")
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"[{session_name}] Error: {e}")
            await asyncio.sleep(1)
            
        # Small delay to prevent CPU overload, but keeps it fast
        await asyncio.sleep(0.1)

async def run():
    print(f"\n--- OxyReport (Concurrent Mode) ---\n")

    # --- STEP 1: INPUT API KEYS ---
    print("--- Login Configuration ---")
    while True:
        try:
            api_id_in = input("Enter API ID: ").strip()
            if api_id_in.isdigit():
                user_api_id = int(api_id_in)
                break
            else:
                print("API ID must be a number.")
        except KeyboardInterrupt:
            return

    while True:
        user_api_hash = input("Enter API HASH: ").strip()
        if len(user_api_hash) > 5:
            break
        print("Invalid API Hash.")

    # --- STEP 2: INPUT SESSIONS ---
    sessions = []
    print("\n--- Session Entry ---")
    while True:
        sess_str = input(f"Enter Session String #{len(sessions)+1}: ").strip()
        if sess_str:
            sessions.append(sess_str)
            print(f"Session #{len(sessions)} added.")
        choice = input("Add another? (y/n): ").strip().lower()
        if choice != 'y':
            break
    
    if not sessions:
        return

    # --- STEP 3: TARGET & DETAILS ---
    while True:
        msg_url = input("\nEnter Group/Message URL: ").strip()
        try:
            chat_id, message_id = parse_message_url(msg_url)
            break
        except Exception as e:
            print(f"Invalid URL: {e}")

    print("\nSelect Report Reason (1-8):")
    reason_code = input("Choice: ").strip()
    if reason_code not in ['1', '2', '3', '4', '5', '6', '7', '8']:
        reason_code = '1'
        
    reason_text = input("Report Description: ").strip()
    if not reason_text:
        reason_text = "Spam"

    try:
        report_input = input("Total Reports to send (Default 5000): ").strip()
        total_reports = int(report_input) if report_input else 5000
    except:
        total_reports = 5000

    # --- INITIALIZE CLIENTS ---
    active_clients = []
    print(f"\nLogging in {len(sessions)} sessions...")

    for idx, sess_str in enumerate(sessions):
        try:
            c = Client(
                name=f"sess_{idx}",
                api_id=user_api_id,
                api_hash=user_api_hash,
                session_string=sess_str,
                in_memory=True,
                no_updates=True
            )
            await c.start()
            active_clients.append(c)
        except Exception as e:
            print(f"Session #{idx+1} Failed: {e}")

    if not active_clients:
        print("No active sessions.")
        return

    # --- CHECK IF MESSAGE EXISTS ---
    print("\nChecking if message exists...")
    exists = await verify_message(active_clients[0], chat_id, message_id)
    if not exists:
        print("❌ Error: Message does not exist or has already been deleted.")
        for c in active_clients: await c.stop()
        return
    print("✅ Message valid. Starting concurrent attack...")

    # --- START CONCURRENT REPORTING ---
    start_time = datetime.datetime.now()
    
    # Create a task for each session
    tasks = []
    for i, client in enumerate(active_clients):
        task = asyncio.create_task(
            report_worker(
                client, 
                chat_id, 
                message_id, 
                reason_code, 
                reason_text, 
                total_reports, 
                f"Sess-{i+1}"
            )
        )
        tasks.append(task)

    # Wait for all tasks to complete or stop signal
    try:
        # We use asyncio.wait to monitor tasks. 
        # We verify checking TOTAL_SENT or STOP_EVENT within the workers.
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\nProcess stopped by user.")
        STOP_EVENT.set()
    finally:
        end_time = datetime.datetime.now()
        
        print(f"\n{'='*40}")
        print("✅ MISSION COMPLETED") 
        print(f"{'='*40}")
        print(f"Total Sent  : {TOTAL_SENT}")
        print(f"Duration    : {end_time - start_time}")
        print(f"{'='*40}")

        print("Stopping sessions...")
        for c in active_clients:
            await c.stop()
        print("Goodbye.")

if __name__ == "__main__":
    asyncio.run(run())
