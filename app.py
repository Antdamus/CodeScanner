import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import winsound
import os

# --- Constants ---
DB_PATH = "barcode_scans.db"
SOUND_PATH = "beep.wav"  # Must be a .wav file

# --- DB Setup ---
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        barcode TEXT PRIMARY KEY,
        scanned_at TEXT
    )
""")
conn.commit()

# --- Sound Alert ---
def play_alert():
    if os.path.exists(SOUND_PATH):
        winsound.PlaySound(SOUND_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)

# --- Scan Handler ---
def handle_scan(event=None):
    barcode = entry.get().strip()
    entry.delete(0, tk.END)
    if not barcode:
        return

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT scanned_at FROM scans WHERE barcode = ?", (barcode,))
    result = cursor.fetchone()

    if result:
        prev_time = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        formatted_time = prev_time.strftime("%I:%M %p")
        play_alert()
        messagebox.showwarning("Duplicate Scan", f"This code was already scanned at {formatted_time}")
    else:
        cursor.execute("INSERT INTO scans (barcode, scanned_at) VALUES (?, ?)", (barcode, timestamp))
        conn.commit()
        messagebox.showinfo("Scan Recorded", "New code saved successfully.")

# --- GUI Setup ---
root = tk.Tk()
root.title("1D Barcode Scanner")
root.geometry("400x180")
root.resizable(False, False)

title_label = tk.Label(root, text="Scan Barcode", font=("Arial", 16))
title_label.pack(pady=10)

entry = tk.Entry(root, font=("Arial", 20), justify="center")
entry.pack(pady=10, ipadx=10, ipady=5)
entry.focus()
entry.bind("<Return>", handle_scan)

info_label = tk.Label(root, text="Make sure cursor is in the box above.", font=("Arial", 10), fg="gray")
info_label.pack()

root.mainloop()
