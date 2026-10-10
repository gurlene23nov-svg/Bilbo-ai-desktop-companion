from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database import (
    add_message,
    get_history
)

from backend.system_monitor import (
    get_system_status
)

from backend.mood import (
    detect_mood,
    get_mood_info
)

from backend.file_manager import (
    scan_storage,
    get_storage_summary,
    find_large_files,
    find_temp_files,
    get_security_report,
)


router = APIRouter()


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# LAPTOP REPORT
# ============================================================

def laptop_report():

    status = get_system_status()

    cpu = status["cpu"]
    memory = status["memory"]
    disk = status["disk"]
    battery = status["battery"]
    uptime = status["uptime"]

    battery_text = "Battery information unavailable."

    if battery.get("available"):

        if battery["plugged"]:
            battery_text = (
                f"Battery is at {battery['percent']}% "
                f"and the charger is connected."
            )
        else:
            battery_text = (
                f"Battery is at {battery['percent']}% "
                f"and the laptop is running on battery."
            )

    return (
        "🐰 Bilbo's laptop report:\n\n"
        f"🧠 CPU: {cpu}%\n"
        f"💾 RAM: {memory['percent']}% used "
        f"({memory['used_gb']} / {memory['total_gb']} GB)\n"
        f"💿 C: drive: {disk['percent']}% used "
        f"({disk['free_gb']} GB free)\n"
        f"🔋 {battery_text}\n"
        f"⏱️ Uptime: {uptime['hours']}h "
        f"{uptime['minutes']}m"
    )


# ============================================================
# LAPTOP COMMAND DETECTOR
# ============================================================

def detect_laptop_command(message):

    text = message.lower().strip()

    if (
        "security" in text
        or "protect my laptop" in text
        or "protect laptop" in text
        or "laptop protection" in text
    ):
        return "security"

    if (
        "large files" in text
        or "big files" in text
        or "what is taking space" in text
    ):
        return "large_files"

    if (
        "temporary files" in text
        or "temp files" in text
        or "junk files" in text
        or "unnecessary files" in text
    ):
        return "temp_files"

    if (
        "free up storage" in text
        or "free up space" in text
        or "help me free" in text
        or "scan storage" in text
        or "analyze storage" in text
        or "analyse storage" in text
        or "storage scan" in text
    ):
        return "storage_scan"

    if "cpu" in text:
        return "cpu"

    if "ram" in text or "memory usage" in text:
        return "ram"

    if "battery" in text or "charging" in text:
        return "battery"

    if "uptime" in text:
        return "uptime"

    if "storage" in text or "disk space" in text or "free space" in text:
        return "storage"

    if any(
        phrase in text
        for phrase in [
            "how is my laptop",
            "laptop status",
            "system status",
            "check my laptop",
            "laptop health",
            "how's my laptop",
            "laptop usage",
        ]
    ):
        return "overall"

    return None


def is_history_request(message):
    text = " ".join(message.casefold().split())
    return any(
        phrase in text
        for phrase in (
            "conversation history",
            "chat history",
            "previous conversations",
            "past conversations",
            "previous chats",
            "past chats",
            "recent chats",
            "show my history",
            "show history",
        )
    )


# ============================================================
# LAPTOP COMMAND RESPONSE
# ============================================================

def generate_laptop_response(command):

    if command == "overall":

        return laptop_report()

    if command == "security":

        security = get_security_report()

        return (
            "🔒 Bilbo laptop protection report:\n\n"
            f"🛡️ Windows Defender:\n"
            f"{security['windows_defender']}\n\n"
            f"🔥 Firewall:\n"
            f"{security['firewall']}\n\n"
            "I only report the security state here. "
            "I won't disable protection or change "
            "security settings without your approval."
        )

    if command == "large_files":

        files = find_large_files()

        if not files:

            return (
                "🐰 I couldn't find large files "
                "in your Downloads folder."
            )

        lines = [
            "🐰 Large files in Downloads:\n"
        ]

        for item in files[:10]:

            lines.append(
                f"• {item['name']} — {item['size']}"
            )

        lines.append(
            "\nI haven't deleted anything."
        )

        return "\n".join(lines)

    if command == "temp_files":

        files = find_temp_files()

        if not files:

            return (
                "🐰 I couldn't find accessible "
                "temporary files."
            )

        lines = [
            "🐰 Temporary files I found:\n"
        ]

        for item in files[:10]:

            lines.append(
                f"• {item['name']} — {item['size']}"
            )

        lines.append(
            "\nI won't delete them automatically."
        )

        return "\n".join(lines)

    if command == "storage_scan":

        result = scan_storage()

        storage = result["storage"]

        return (
            "🐰 Storage scan complete!\n\n"
            f"💿 C: drive: "
            f"{storage.get('used_percent', '?')}% used\n"
            f"🟢 Free: {storage.get('free', '?')}\n\n"
            f"📦 Large Downloads: "
            f"{result['large_downloads_total']}\n"
            f"🧹 Temporary files: "
            f"{result['temporary_files_total']}\n\n"
            "Nothing has been deleted."
        )

    status = get_system_status()

    if command == "cpu":

        return (
            f"🐰 CPU usage is currently "
            f"{status['cpu']}%."
        )


    if command == "ram":

        memory = status["memory"]

        return (
            f"🐰 RAM usage is {memory['percent']}%.\n"
            f"Using {memory['used_gb']} GB "
            f"out of {memory['total_gb']} GB."
        )


    if command == "storage":

        disk = status["disk"]

        return (
            f"🐰 Your C: drive is "
            f"{disk['percent']}% full.\n\n"
            f"💿 Used: {disk['used_gb']} GB\n"
            f"🟢 Free: {disk['free_gb']} GB\n"
            f"📦 Total: {disk['total_gb']} GB"
        )


    if command == "battery":

        battery = status["battery"]

        if not battery["available"]:

            return (
                "🐰 I can't read your battery information."
            )

        state = (
            "charging"
            if battery["plugged"]
            else "running on battery"
        )

        return (
            f"🐰 Battery: {battery['percent']}%\n"
            f"🔌 Status: {state}"
        )


    if command == "uptime":

        uptime = status["uptime"]

        return (
            f"🐰 Your laptop has been running for "
            f"{uptime['hours']} hours "
            f"and {uptime['minutes']} minutes."
        )


    return None


# ============================================================
# CHAT
# ============================================================

@router.post("/chat")
@router.post("/api/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:

        return {
            "reply": "🐰 Tell me something!",
            "type": "chat",
        }

    if is_history_request(message):
        messages = get_history(limit=10)

        if messages:
            history_lines = []
            for item in messages:
                speaker = "You" if item["speaker"] == "user" else "Bilbo"
                timestamp = item.get("created_at", "")
                prefix = f"{timestamp} " if timestamp else ""
                history_lines.append(
                    f"{prefix}{speaker}: {item['message']}"
                )
            reply = "Here are your 10 most recent saved messages:\n\n"
            reply += "\n".join(history_lines)
        else:
            reply = "You don't have any saved conversation history yet."

        add_message("user", message)
        add_message("assistant", reply)

        return {
            "reply": reply,
            "type": "history",
        }


    # --------------------------------------------------------
    # LAPTOP COMMANDS FIRST
    # --------------------------------------------------------

    command = detect_laptop_command(message)

    if command:

        reply = generate_laptop_response(
            command
        )

        add_message(
            "user",
            message
        )

        add_message(
            "assistant",
            reply
        )

        return {
            "reply": reply,
            "type": "laptop",
            "command": command,
        }


    # --------------------------------------------------------
    # MOOD
    # --------------------------------------------------------

    mood = detect_mood(message)

    if mood:

        mood_info = get_mood_info(mood)

        reply = mood_info["message"]

        add_message(
            "user",
            message
        )

        add_message(
            "assistant",
            reply
        )

        return {
            "reply": reply,
            "type": "mood",
            "mood": mood,
            "mood_name": mood_info["name"],
            "mood_emoji": mood_info["emoji"],
        }


    # --------------------------------------------------------
    # NORMAL CHAT
    # --------------------------------------------------------

    reply = (
        "Hiii! 🐰 I'm Bilbo. "
        "Tell me what you need!"
    )

    add_message(
        "user",
        message
    )

    add_message(
        "assistant",
        reply
    )

    return {
        "reply": reply,
        "type": "chat",
    }


# ============================================================
# HISTORY
# ============================================================

@router.get("/history")
def history():
    return get_history()


@router.get("/api/history")
def history_api():
    return {"messages": get_history()}


# ============================================================
# SYSTEM STATUS
# ============================================================

@router.get("/system/status")
def system_status():

    return get_system_status()


# ============================================================
# MOOD
# ============================================================

@router.get("/mood")
def mood_status():

    return {
        "message": "Mood system is active."
    }


# ============================================================
# STORAGE
# ============================================================

@router.get("/storage")
def storage_status():

    return get_storage_summary()


@router.get("/storage/scan")
def storage_scan():

    return scan_storage()


# ============================================================
# SECURITY
# ============================================================

@router.get("/security")
def security_status():

    return get_security_report()


# ============================================================
# DISCARD FILE
# ============================================================

class DiscardRequest(BaseModel):
    path: str


@router.post("/files/discard")
def discard(_request: DiscardRequest):

    raise HTTPException(
        status_code=501,
        detail=(
            "File cleanup is disabled until Bilbo can show a preview "
            "and request explicit confirmation. No files were changed."
        ),
    )