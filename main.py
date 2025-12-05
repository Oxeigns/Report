#!/usr/bin/env python3
# main.py
# OxyReport - Termux friendly
# Modified: Ask API keys and Session directly

import asyncio
import re
import os
from pyrogram import Client
# Report function import waisa hi rakha hai
from report import send_report 

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
    print(f"\n--- OxyReport (Direct Mode) ---\n")

    # STEP 1: API ID aur HASH input lo
    try:
        api_id_input = input("Enter API ID: ").strip()
        if not api_id_input:
            print("API ID zaruri hai!")
            return
        user_api_id = int(api_id_input)
        
        user_api_hash = input("Enter API HASH: ").strip()
        if not user_api_hash:
            print("API HASH zaruri hai!")
            return
    except ValueError:
        print("Error: API ID number hona chahiye.")
        return

    # STEP 2: Sessions input lo (Directly)
    sessions = []
    print("\n--- Paste Pyrogram Session Strings ---")
    print("(Ek session paste karke Enter dabayein. Jab done ho jaye to khali Enter dabayein)")
    
    i = 1
    while True:
        try:
            s = input(f"Session String {i}: ").strip()
        except EOFError:
            s = ""
        
        if s == "":
            break
        sessions.append(s)
        i += 1

    if len(sessions) == 0:
        print("Koi session nahi diya gaya. Exiting.")
        return

    # STEP 3: Message URL Input
    msg_url = input("\nEnter message URL (t.me/...): ").strip()
    try:
        chat_id, message_id = parse_message_url(msg_url)
    except Exception as e:
        print("URL error:", e)
        return

    # STEP 4: Number of Reports
    try:
        total_reports = int(input("\nHow many reports to send? ").strip())
        if total_reports <= 0:
            print("Number must be > 0.")
            return
    except:
        print("Invalid number.")
        return

    # STEP 5: Reason Selection
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

    # Create clients using input API KEYS
    clients = []
    print(f"\nLogging in with {len(sessions)} sessions...")
    
    for idx, sess in enumerate(sessions, start=1):
        try:
            # Yahan hum user ka diya hua API ID/Hash use kar rahe hain
            client = Client(
                name=f"sess_{idx}", 
                session_string=sess, 
                api_id=user_api_id, 
                api_hash=user_api_hash,
                in_memory=True # Termux storage save karne ke liye
            )
            clients.append(client)
        except Exception as e:
            print(f"Session #{idx} create error: {e}")

    running = []
    print("\nStarting sessions...")
    for idx, c in enumerate(clients, start=1):
        try:
            await c.start()
            running.append(c)
            print(f"Session #{idx} started successfully.")
        except Exception as e:
            print(f"Session #{idx} failed to start: {e}")

    if not running:
        print("No active sessions. Exiting.")
        return

    sent = 0
    idx = 0
    total_clients = len(running)
    print(f"\nActive sessions: {total_clients}. Sending {total_reports} reports...\n")

    try:
        while sent < total_reports:
            client = running[idx % total_clients]
            try:
                # Call the report function
                await send_report(client, chat_id, message_id, reason_code)
                sent += 1
                print(f"[{sent}/{total_reports}] Report sent via session #{(idx % total_clients) + 1}")
            except Exception as e:
                print(f"Session #{(idx % total_clients) + 1} error: {e}")
            
            idx += 1
            await asyncio.sleep(0.8) 
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        print("\nStopping sessions...")
        for c in running:
            try:
                await c.stop()
            except:
                pass
        print("Done.")

if __name__ == "__main__":
    asyncio.run(run())
