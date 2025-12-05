#!/usr/bin/env python3
# main.py
# OxyReport - Fully Streamlined & Config-Free
# Modified: Notification system removed (Termux Only)

import asyncio
import re
import os
import datetime
from pyrogram import Client
from report import send_report

# --- CONFIGURATION REMOVED ---
# Ab yahan koi log channel set karne ki zarurat nahi hai.

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

async def run():
    print(f"\n--- OxyReport (Silent Mode) ---\n")

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

    # --- STEP 2: INPUT SESSIONS (LOOP) ---
    sessions = []
    print("\n--- Session Entry ---")
    
    while True:
        sess_str = input(f"Enter Session String #{len(sessions)+1}: ").strip()
        if sess_str:
            sessions.append(sess_str)
            print(f"Session #{len(sessions)} added.")
        
        choice = input("Do you want to add another session? (y/n): ").strip().lower()
        if choice != 'y':
            break
    
    if not sessions:
        print("No sessions provided. Exiting.")
        return

    # --- STEP 3: TARGET LINK ---
    while True:
        msg_url = input("\nEnter Group/Message URL (t.me/...): ").strip()
        try:
            chat_id, message_id = parse_message_url(msg_url)
            break
        except Exception as e:
            print(f"Invalid URL: {e}")

    # --- STEP 4: REPORT DETAILS ---
    print("\nSelect Report Reason:")
    print("1. Spam")
    print("2. Violence")
    print("3. Child Abuse")
    print("4. Pornography")
    print("5. Fake Account")
    print("6. Illegal Drugs")
    print("7. Personal Details")
    print("8. Other")
    
    reason_code = input("Enter choice (1-8): ").strip()
    if reason_code not in ['1', '2', '3', '4', '5', '6', '7', '8']:
        print("Invalid choice. Defaulting to Spam (1).")
        reason_code = '1'
        
    # New Input: Report Description text
    reason_text = input("Enter the Report Description (What to write in report box): ").strip()
    if not reason_text:
        reason_text = "Reported via OxyReport"

    # --- STEP 5: NUMBER OF REPORTS ---
    # Yahan aap decide kar sakte hain kitni reports bhejni hain
    try:
        report_input = input("\nHow many total reports to send? (Default 5000): ").strip()
        if report_input:
            total_reports = int(report_input)
        else:
            total_reports = 5000
    except:
        print("Invalid number. Defaulting to 5000.")
        total_reports = 5000

    # --- INITIALIZE CLIENTS ---
    active_clients = []
    print(f"\nLogging in with {len(sessions)} sessions...")

    for idx, sess_str in enumerate(sessions):
        try:
            c = Client(
                name=f"temp_sess_{idx}",
                api_id=user_api_id,
                api_hash=user_api_hash,
                session_string=sess_str,
                in_memory=True,
                no_updates=True
            )
            await c.start()
            active_clients.append(c)
            print(f"Session #{idx+1} Connected.")
        except Exception as e:
            print(f"Session #{idx+1} Failed: {e}")

    if not active_clients:
        print("No sessions could connect. Exiting.")
        return

    # --- START REPORTING ---
    start_time = datetime.datetime.now()
    print(f"\n{'='*40}")
    print(f"Target: {msg_url}")
    print(f"Reports to Send: {total_reports}")
    print(f"Start Time: {start_time.strftime('%H:%M:%S')}")
    print(f"{'='*40}\n")
    
    count = 0
    client_idx = 0
    
    try:
        while count < total_reports:
            current_client = active_clients[client_idx % len(active_clients)]
            
            # Pass reason_text to the report function
            success = await send_report(current_client, chat_id, message_id, reason_code, reason_text)
            
            if success:
                count += 1
                print(f"[{count}/{total_reports}] Report sent from Session #{(client_idx % len(active_clients)) + 1}")
            else:
                print(f"[FAIL] Session #{(client_idx % len(active_clients)) + 1} failed to report.")
            
            client_idx += 1
            await asyncio.sleep(0.5) 
            
    except KeyboardInterrupt:
        print("\nProcess stopped by user.")
    finally:
        end_time = datetime.datetime.now()
        
        # --- STATS SUMMARY ---
        print(f"\n{'='*40}")
        print("✅ MISSION COMPLETED") # Termux Message Only
        print(f"{'='*40}")
        print(f"Target Link : {msg_url}")
        print(f"Total Sent  : {count}")
        print(f"Start Time  : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time    : {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*40}")

        print("\nStopping sessions...")
        for c in active_clients:
            await c.stop()
        print("Goodbye.")

if __name__ == "__main__":
    asyncio.run(run())
