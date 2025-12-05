#!/usr/bin/env python3
# main.py
# OxyReport - Fully Streamlined & Config-Free
# Modified by @oxeign request

import asyncio
import re
import os
from pyrogram import Client
from report import send_report

def parse_message_url(url: str):
    url = url.strip()
    # Regex to extract Chat Username/ID and Message ID
    m = re.search(r"(?:t\.me|telegram\.me)/(c/)?([^/]+)/?(\d+)?", url)
    if not m:
        raise ValueError("Invalid message URL format.")
    
    c_group = m.group(1) # 'c/' if it's a private ID based link
    part = m.group(2)    # Username or ID
    msg = m.group(3)     # Message ID

    if msg:
        message_id = int(msg)
        if c_group == "c/":
            # If it's a private link like t.me/c/12345/67
            chat_id = int("-100" + part)
        else:
            # Public username or ID
            chat_id = part if not part.isdigit() else int(part)
    else:
        raise ValueError("Message ID missing in URL.")
    
    return chat_id, message_id

async def run():
    print(f"\n--- OxyReport (Direct Mode) ---\n")

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
        
        # Ask if user wants to add more
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

    # --- STEP 4: REPORT REASON ---
    print("\nSelect Report Reason:")
    print("1. Spam")
    print("2. Violence")
    print("3. Child Abuse")
    print("4. Pornography")
    print("5. Fake Account")
    print("6. Other")
    
    reason_code = input("Enter choice (1-6): ").strip()
    if reason_code not in ['1', '2', '3', '4', '5', '6']:
        print("Invalid choice. Defaulting to Spam (1).")
        reason_code = '1'

    # --- STEP 5: NUMBER OF REPORTS ---
    try:
        total_reports = int(input("\nHow many total reports to send? ").strip())
    except:
        print("Invalid number. Defaulting to 10.")
        total_reports = 10

    # --- INITIALIZE CLIENTS ---
    active_clients = []
    print(f"\nLogging in with {len(sessions)} sessions...")

    for idx, sess_str in enumerate(sessions):
        try:
            # We use the user-provided API Keys here
            c = Client(
                name=f"temp_sess_{idx}",
                api_id=user_api_id,
                api_hash=user_api_hash,
                session_string=sess_str,
                in_memory=True,
                no_updates=True # Faster, we don't need to listen to messages
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
    print(f"\nStarting {total_reports} reports using {len(active_clients)} active sessions...")
    
    count = 0
    client_idx = 0
    
    try:
        while count < total_reports:
            # Round-robin selection of clients
            current_client = active_clients[client_idx % len(active_clients)]
            
            try:
                await send_report(current_client, chat_id, message_id, reason_code)
                count += 1
                print(f"[{count}/{total_reports}] Report sent from Session #{(client_idx % len(active_clients)) + 1}")
            except Exception as e:
                # If a specific client fails, we just print and continue to next
                print(f"Error on Session #{(client_idx % len(active_clients)) + 1}: {e}")
            
            client_idx += 1
            await asyncio.sleep(0.5) # Slight delay to prevent immediate floodwait
            
    except KeyboardInterrupt:
        print("\nProcess stopped by user.")
    finally:
        print("\nStopping sessions...")
        for c in active_clients:
            await c.stop()
        print("Finished.")

if __name__ == "__main__":
    asyncio.run(run())
