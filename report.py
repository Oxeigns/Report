# report.py
# Logic to send reports to Telegram servers

from pyrogram import Client
from pyrogram.raw import functions, types
from pyrogram.errors import RPCError

async def send_report(client: Client, chat_id: int | str, message_id: int, reason_code: str, reason_text: str):
    """
    Sends a report for a specific message using the raw Telegram API.
    """
    try:
        # Resolve the chat peer (channel/group/user)
        peer = await client.resolve_peer(chat_id)
        
        # Map user input code to Telegram Report Reason
        if reason_code == '1':
            reason = types.InputReportReasonSpam()
        elif reason_code == '2':
            reason = types.InputReportReasonViolence()
        elif reason_code == '3':
            reason = types.InputReportReasonChildAbuse()
        elif reason_code == '4':
            reason = types.InputReportReasonPornography()
        elif reason_code == '5':
            reason = types.InputReportReasonFake()
        elif reason_code == '6':
            reason = types.InputReportReasonIllegalDrugs()
        elif reason_code == '7':
            reason = types.InputReportReasonPersonalDetails()
        else:
            reason = types.InputReportReasonOther()

        # Execute the report function
        await client.invoke(
            functions.messages.Report(
                peer=peer,
                id=[message_id],
                reason=reason,
                message=reason_text
            )
        )
        return True

    except RPCError as e:
        print(f"Telegram Error: {e}")
        return False
    except Exception as e:
        print(f"Unknown Error: {e}")
        return False
