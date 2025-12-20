import tkinter as tk
from tkinter import ttk
import datetime
import time
import threading
import subprocess
import random
import os

# -----------------------------
# Konfiguration
# -----------------------------
INITIAL_COUNTDOWN = 15 * 60   # 15 Minuten
REDUCED_COUNTDOWN = 10 * 60   # 10 Minuten
MIN_COUNTDOWN = 5 * 60        # 5 Minuten
ONE_MINUTE = 60               # 1 Minute

MESSAGES_FILE = "messages.txt"


# -----------------------------
# Sprüche laden
# -----------------------------
def lade_sprueche():
    if not os.path.exists(MESSAGES_FILE):
        return ["Schlaf ist wichtig.", "Morgen wirst du froh sein.", "Geh schlafen, Zukunftsdu dankt dir."]
    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return lines or ["Schlaf ist wichtig."]


MOTIVATION = lade_sprueche()


# -----------------------------
# Shutdown-Funktion
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
        print("Shutdown fehlgeschlagen:", e)


# -----------------------------
# Countdown-Fenster
# -----------------------------
class CountdownWindow:
    def __init__(self, countdown_seconds):
        self.countdown_seconds = countdown_seconds
        self.closed_by_user = False
        self.user_clicked_later = False
        self.user_clicked_shutdown = False

        self.root = tk.Tk()
        self.root.title("Zeit zum Schlafen!")
        self.root.attributes("-topmost", True)
        self.root.geometry("420x200")

        msg = random.choice(MOTIVATION)
        tk.Label(self.root, text=msg, font=("Arial", 12), wraplength=380).pack(pady=10)

        self.progress = ttk.Progressbar(self.root, maximum=self.countdown_seconds, length=380)
        self.progress.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Jetzt herunterfahren", command=self.shutdown_now).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Später", command=self.later).pack(side="left", padx=10)

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

        # Countdown abgelaufen → herunterfahren
        if not self.closed_by_user and not self.user_clicked_later:
            shutdown_computer()

        self.root.destroy()


# -----------------------------
# Hauptlogik
# -----------------------------
def main_loop():
    next_countdown = INITIAL_COUNTDOWN

    while True:
        now = datetime.datetime.now()
        hour = now.hour

        # Vor 22 Uhr: schlafen
        if hour < 22:
            time.sleep(300)  # 5 Minuten
            continue

        # Zwischen 22 und 23 Uhr
        elif 22 <= hour < 23:
            win = CountdownWindow(next_countdown)

            # Countdown-Stufen reduzieren, wenn Nutzer abbricht
            if win.user_clicked_later or win.closed_by_user:
                if next_countdown == INITIAL_COUNTDOWN:
                    next_countdown = REDUCED_COUNTDOWN
                elif next_countdown == REDUCED_COUNTDOWN:
                    next_countdown = MIN_COUNTDOWN
                else:
                    next_countdown = ONE_MINUTE

            time.sleep(300)  # 5 Minuten warten
            continue

        # Ab 23 Uhr: jede Minute
        elif hour >= 23:
            win = CountdownWindow(ONE_MINUTE)
            time.sleep(60)
            continue


# -----------------------------
# Start
# -----------------------------
if __name__ == "__main__":
    main_loop()
