#!/usr/bin/env python3
# create_session.py
# Run this to export a string session. Follow on-screen login steps.
from pyrogram import Client
from config import API_ID, API_HASH

def main():
    name = "temp_session_for_export"
    with Client(name, api_id=API_ID, api_hash=API_HASH) as app:
        me = app.get_me()
        print("Logged in as:", me.username or me.first_name)
        s = app.export_session_string()
        print("\n--- COPY THIS SESSION STRING ---\n")
        print(s)
        print("\n--- End ---\n")
        # Optionally save to sessions.txt
        save = input("Save this session to sessions.txt? (y/N): ").strip().lower()
        if save == "y":
            with open("sessions.txt", "a", encoding="utf-8") as f:
                f.write(s + "\n")
            print("Saved to sessions.txt")

if __name__ == "__main__":
    main()
