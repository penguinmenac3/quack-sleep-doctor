import tkinter as tk
from tkinter import ttk
import datetime
import time
import threading
import subprocess
import random
import os
from languages import get_string

# -----------------------------
# Configuration
# -----------------------------
INITIAL_COUNTDOWN = 15 * 60   # 15 minutes
REDUCED_COUNTDOWN = 10 * 60   # 10 minutes
MIN_COUNTDOWN = 5 * 60        # 5 minutes
ONE_MINUTE = 60               # 1 minute

MESSAGES_FILE = "messages.txt"


# -----------------------------
# Load messages
# -----------------------------
def load_messages():
    if not os.path.exists(MESSAGES_FILE):
        return [
            get_string("sleep_message"),
            get_string("future_thanks"),
            get_string("go_to_sleep"),
        ]
    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return lines or [get_string("sleep_message")]


MOTIVATION = load_messages()


# -----------------------------
# Shutdown function
# -----------------------------
def shutdown_computer():
    try:
        # Windows:
        subprocess.run(["shutdown", "/s", "/t", "0"])

        # macOS:
        # subprocess.run(["sudo", "shutdown", "-h", "now"])

        # Linux:
        # subprocess.run(["shutdown", "-h", "now"])
    except Exception as e:
        print(get_string("shutdown_failed"), e)


# -----------------------------
# Countdown window
# -----------------------------
class CountdownWindow:
    def __init__(self, countdown_seconds):
        self.countdown_seconds = countdown_seconds
        self.closed_by_user = False
        self.user_clicked_later = False
        self.user_clicked_shutdown = False

        self.root = tk.Tk()
        self.root.title(get_string("window_title"))
        self.root.attributes("-topmost", True)
        self.root.geometry("420x200")

        msg = random.choice(MOTIVATION)
        tk.Label(self.root, text=msg, font=("Arial", 12), wraplength=380).pack(pady=10)

        self.progress = ttk.Progressbar(self.root, maximum=self.countdown_seconds, length=380)
        self.progress.pack(pady=10)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text=get_string("shutdown_now"), command=self.shutdown_now).pack(side="left", padx=10)
        tk.Button(button_frame, text=get_string("later"), command=self.later).pack(side="left", padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.later)

        threading.Thread(target=self.run_countdown, daemon=True).start()
        self.root.mainloop()

    def later(self):
        self.user_clicked_later = True
        self.closed_by_user = True
        self.root.destroy()

    def shutdown_now(self):
        self.user_clicked_shutdown = True
        self.root.destroy()
        shutdown_computer()

    def run_countdown(self):
        remaining = self.countdown_seconds
        while remaining > 0:
            if self.closed_by_user or self.user_clicked_later:
                return
            if self.user_clicked_shutdown:
                return

            self.progress["value"] = self.countdown_seconds - remaining
            time.sleep(1)
            remaining -= 1

        # Countdown expired → shutdown
        if not self.closed_by_user and not self.user_clicked_later:
            shutdown_computer()

        self.root.destroy()


# -----------------------------
# Main logic
# -----------------------------
def main_loop():
    next_countdown = INITIAL_COUNTDOWN

    while True:
        now = datetime.datetime.now()
        hour = now.hour

        # Before 10 PM: sleep
        if hour < 22:
            time.sleep(300)  # 5 minutes
            continue

        # Between 10 PM and 11 PM
        elif 22 <= hour < 23:
            window = CountdownWindow(next_countdown)

            # Reduce countdown stages if the user cancels
            if window.user_clicked_later or window.closed_by_user:
                if next_countdown == INITIAL_COUNTDOWN:
                    next_countdown = REDUCED_COUNTDOWN
                elif next_countdown == REDUCED_COUNTDOWN:
                    next_countdown = MIN_COUNTDOWN
                else:
                    next_countdown = ONE_MINUTE

            time.sleep(300)  # Wait 5 minutes
            continue

        # After 11 PM: every minute
        elif hour >= 23:
            window = CountdownWindow(ONE_MINUTE)
            time.sleep(60)
            continue


# -----------------------------
# Start
# -----------------------------
if __name__ == "__main__":
    main_loop()
