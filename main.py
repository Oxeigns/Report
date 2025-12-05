#!/usr/bin/env python3
# main.py
# OxyReport - Termux friendly
# Modified to send Reports instead of Reactions

import asyncio
import re
import os
from pyrogram import Client
from config import API_ID, API_HASH, DEVELOPER
# Import report function instead of reaction
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
    print(f"\n--- OxyReport (Termux) — developed by {DEVELOPER} ---\n")

    # If sessions.txt exists, read sessions from it.
    sessions = []
    sessions_file = "sessions.txt"
    if os.path.isfile(sessions_file):
        with open(sessions_file, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s:
                    sessions.append(s)
        print(f"Loaded {len(sessions)} sessions from {sessions_file}.")
    else:
        print("No sessions.txt found — switch to interactive mode.")
        print("Enter Pyrogram session strings (unlimited). When done press ENTER on empty line.\n")
        i = 1
        while True:
            try:
                s = input(f"Session {i}: ").strip()
            except EOFError:
                s = ""
            if s == "":
                break
            sessions.append(s)
            i += 1

    if len(sessions) == 0:
        print("No sessions provided. Please create sessions.txt.")
        return

    # Message URL input
    msg_url = input("\nEnter message URL (t.me/...): ").strip()
    try:
        chat_id, message_id = parse_message_url(msg_url)
    except Exception as e:
        print("URL error:", e)
        return

    # Number of reports
    try:
        total_reports = int(input("\nHow many reports to send? ").strip())
        if total_reports <= 0:
            print("Number must be > 0.")
            return
    except:
        print("Invalid number.")
        return

    # REASON SELECTION MENU
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

    # Create clients
    clients = []
    for idx, sess in enumerate(sessions, start=1):
        try:
            client = Client(sess, api_id=API_ID, api_hash=API_HASH)
            clients.append(client)
        except Exception as e:
            print(f"Session #{idx} create error: {e}")

    running = []
    print("\nStarting sessions...")
    for idx, c in enumerate(clients, start=1):
        try:
            await c.start()
            running.append(c)
            print(f"Session #{idx} started.")
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
                # Call the new report function
                await send_report(client, chat_id, message_id, reason_code)
                sent += 1
                print(f"[{sent}/{total_reports}] Report sent via session #{(idx % total_clients) + 1}")
            except Exception as e:
                print(f"Session #{(idx % total_clients) + 1} error: {e}")
            
            idx += 1
            await asyncio.sleep(0.8) # Thoda delay safe rehta hai
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        print("\nStopping sessions...")
        for c in running:
            try:
                await c.stop()
            except:
                pass
        print("Done. Modified by oxeign")

if __name__ == "__main__":
    asyncio.run(run())
