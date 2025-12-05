# reaction.py
# Helper functions to send reactions. Developed by @oxeign

import asyncio
from pyrogram import Client
from pyrogram.errors import RPCError

async def send_reaction(client: Client, chat_id: int | str, message_id: int, emoji: str):
    """
    Try to send a reaction to a message using a Pyrogram Client.
    Tries a few fallbacks with helpful error messages.
    """
    try:
        # Primary (newer Pyrogram): send_reaction(chat_id, message_id, emoji)
        result = await client.send_reaction(chat_id, message_id, emoji)
        return result
    except AttributeError:
        # send_reaction not available on this pyrogram version
        raise RuntimeError(
            "Your Pyrogram version doesn't support client.send_reaction(). "
            "Upgrade Pyrogram or check README for alternative instructions."
        )
    except RPCError as e:
        # Telegram returned an error (e.g., reaction type not allowed, flood, privacy)
        raise e
