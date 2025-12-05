OxyReaction - Termux-friendly Pyrogram reaction automation
Developed by: @oxeign

Files:
- main.py           : main orchestrator (run this)
- reaction.py       : helper sending reaction
- config.py         : set API_ID, API_HASH, DEVELOPER
- create_session.py : helper to export string session (run once)
- run.sh            : Termux launcher
- requirements.txt  : pip dependencies
- sessions.txt      : place session strings (one per line)
- README.txt        : this file

Requirements:
- Python 3.9+
- pyrogram >= 2.x
- tgcrypto (optional but recommended)

Install:
    pip install -r requirements.txt

How to get api_id and api_hash:
- Visit https://my.telegram.org, log in, create an app and copy api_id and api_hash into config.py or set as environment variables.

How to create/export session strings:
Run:
    python3 create_session.py
Follow the login flow (enter phone, code). It will print a long session string — copy that and paste into sessions.txt.

Usage:
1. Edit config.py with your API_ID and API_HASH or set environment variables:
    export API_ID=123456
    export API_HASH="your_api_hash_here"

2. Put session strings (one per line) into sessions.txt, or run the script and paste sessions interactively.

3. Run:
    chmod +x run.sh
    ./run.sh

Notes & cautions:
- Telegram can limit or block accounts that automate reactions aggressively — use small counts and delays.
- If client.send_reaction is not available, upgrade Pyrogram.
- Running many sessions at once may use significant memory on mobile devices. Consider batching for large numbers.

Developed by @oxeign
