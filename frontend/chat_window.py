import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import requests
import customtkinter as ctk


PROJECT_DIR = Path(__file__).resolve().parent.parent
PYTHON_EXE = PROJECT_DIR / "venv" / "Scripts" / "python.exe"
BACKEND_LOG = PROJECT_DIR / "data" / "backend.log"
API_BASE_URL = "http://127.0.0.1:8000/api"
API_URL = f"{API_BASE_URL}/chat"
HEALTH_URL = f"{API_BASE_URL}/health"
BACKEND_ROOT_URL = "http://127.0.0.1:8000/"
HISTORY_URL = f"{API_BASE_URL}/history"
PET_STATE_FILE = PROJECT_DIR / "data" / "pet_state.json"
PET_MOODS = {"happy", "sad", "stressed", "tired", "excited", "angry", "normal"}


def pet_mood_for(mood):
    mood = str(mood).lower().strip()
    if mood == "calm" or mood == "neutral":
        return "normal"
    return mood if mood in PET_MOODS else "happy"


class BilboChat(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bilbo 🐰")
        self.geometry("460x620")
        self.minsize(380, 500)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color="#FFF8FC")

        self.title_label = ctk.CTkLabel(
            self,
            text="Bilbo 🐰",
            font=("Segoe UI", 28, "bold"),
            text_color="#8D5A8C",
        )
        self.title_label.pack(pady=(20, 4))

        self.subtitle = ctk.CTkLabel(
            self,
            text="Your little desktop companion",
            font=("Segoe UI", 13),
            text_color="#9B7A99",
        )
        self.subtitle.pack(pady=(0, 12))

        self.chat_area = ctk.CTkTextbox(
            self,
            wrap="word",
            font=("Segoe UI", 14),
            fg_color="#FFFFFF",
            text_color="#453847",
            corner_radius=14,
        )
        self.chat_area.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=10,
        )
        self.chat_area.configure(state="disabled")

        self.status_label = ctk.CTkLabel(
            self,
            text="Bilbo is waking up... 🐰",
            font=("Segoe UI", 11),
            text_color="#9B7A99",
        )
        self.status_label.pack(pady=(2, 4))

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=18, pady=(4, 18))

        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Talk to Bilbo...",
            height=42,
            font=("Segoe UI", 13),
        )
        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            width=75,
            height=42,
            command=self.send_message,
        )
        self.send_button.pack(side="right")

        self.write_pet_state("happy")

        # Load saved conversations from Bilbo's local database.
        self.load_history()

    def write_pet_state(self, mood):
        pet_mood = pet_mood_for(mood)
        try:
            PET_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            PET_STATE_FILE.write_text(json.dumps({"mood": pet_mood}), encoding="utf-8")
        except OSError:
            pass

    def add_message(self, speaker, message, timestamp=None):
        timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.chat_area.configure(state="normal")
        self.chat_area.insert(
            "end",
            f"{speaker} ({timestamp}):\n{message}\n\n",
        )
        self.chat_area.see("end")
        self.chat_area.configure(state="disabled")

    def load_history(self):
        self.status_label.configure(text="Loading our chats... 🐰")
        threading.Thread(target=self.fetch_history, daemon=True).start()

    def fetch_history(self):
        try:
            self.ensure_backend()
            response = requests.get(HISTORY_URL, timeout=5)
            response.raise_for_status()
            history = response.json()
            messages = history.get("messages", history.get("history", []))
        except (OSError, requests.RequestException, RuntimeError) as error:
            self.after(
                0,
                self.show_error,
                f"I couldn't connect to Bilbo's backend: {error}",
            )
            return

        self.after(0, self.show_history, messages)

    def ensure_backend(self):
        try:
            response = requests.get(HEALTH_URL, timeout=1)
            if response.status_code == 404:
                response = requests.get(BACKEND_ROOT_URL, timeout=1)
            response.raise_for_status()
            return
        except requests.ConnectionError:
            pass

        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        with BACKEND_LOG.open("a", encoding="utf-8") as log_file:
            subprocess.Popen(
                [
                    str(PYTHON_EXE),
                    "-m",
                    "uvicorn",
                    "backend.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ],
                cwd=str(PROJECT_DIR),
                stdout=log_file,
                stderr=log_file,
                creationflags=creation_flags,
            )

        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            try:
                response = requests.get(HEALTH_URL, timeout=1)
                if response.status_code == 404:
                    response = requests.get(BACKEND_ROOT_URL, timeout=1)
                response.raise_for_status()
                return
            except requests.ConnectionError:
                time.sleep(0.25)

        raise RuntimeError(
            f"Backend did not start. Check its log at {BACKEND_LOG}."
        )

    def show_history(self, messages):
        if messages:
            for item in messages:
                self.add_message(
                    item["speaker"],
                    item["message"],
                    item.get("created_at"),
                )
            self.status_label.configure(text="Our memories are here! 🥕")
        else:
            self.add_message(
                "Bilbo",
                "Hiii! I'm Bilbo. What's on your mind? 🐰",
            )
            self.status_label.configure(text="Bilbo is ready 🥕")

    def send_message(self, event=None):
        message = self.message_entry.get().strip()

        if not message:
            return

        self.message_entry.delete(0, "end")
        self.add_message("You", message)

        self.status_label.configure(text="Bilbo is thinking... 🐰")
        self.send_button.configure(state="disabled")

        threading.Thread(
            target=self.get_reply,
            args=(message,),
            daemon=True,
        ).start()

    def get_reply(self, message):
        try:
            response = requests.post(
                API_URL,
                json={"message": message},
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()

            self.after(
                0,
                self.show_reply,
                data["reply"],
                data.get("mood", "neutral"),
            )

        except requests.RequestException:
            self.after(
                0,
                self.show_error,
                "I can't reach my local backend. "
                "Is the first terminal still running?",
            )

    def apply_mood_theme(self, mood):
        themes = {
            "happy": {
                "background": "#FFF4D6",
                "panel": "#FFFFFF",
                "text": "#684B2A",
                "accent": "#E6A23C",
                "subtitle": "#A47735",
            },
            "calm": {
                "background": "#EAF4F4",
                "panel": "#FFFFFF",
                "text": "#34545A",
                "accent": "#6B9FA3",
                "subtitle": "#63858A",
            },
            "neutral": {
                "background": "#FFF8FC",
                "panel": "#FFFFFF",
                "text": "#453847",
                "accent": "#A477A5",
                "subtitle": "#9B7A99",
            },
        }

        colors = themes.get(mood, themes["neutral"])

        self.configure(fg_color=colors["background"])
        self.title_label.configure(text_color=colors["accent"])
        self.subtitle.configure(text_color=colors["subtitle"])

        self.chat_area.configure(
            fg_color=colors["panel"],
            text_color=colors["text"],
        )

        self.status_label.configure(text_color=colors["subtitle"])

        self.message_entry.configure(
            fg_color=colors["panel"],
            text_color=colors["text"],
        )

        self.send_button.configure(
            fg_color=colors["accent"],
            hover_color=colors["subtitle"],
        )

    def show_reply(self, reply, mood):
        self.write_pet_state(mood)
        self.apply_mood_theme(mood)
        self.add_message("Bilbo", reply)

        self.status_label.configure(
            text=f"Bilbo's mood: {mood} 🐰"
        )
        self.send_button.configure(state="normal")
        self.message_entry.focus()

    def show_error(self, error):
        self.add_message("Bilbo", error)
        self.status_label.configure(text="Connection problem")
        self.send_button.configure(state="normal")


if __name__ == "__main__":
    app = BilboChat()
    app.mainloop()