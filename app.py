import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime
import winsound
import os
import sys

# --- Constants ---
DB_PATH = "barcode_scans.db"
BACKGROUND_IMAGE = "hero-bg.jpg"
SOUND_FILE = "beep.wav"
ICON_FILE = "og_icon.ico"
FADE_IN_DURATION = 800  # milliseconds

# --- Resource Path Fix (for .exe packaging) ---
def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

# --- Database Setup ---
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        barcode TEXT PRIMARY KEY,
        scanned_at TEXT
    )
""")
conn.commit()

# --- Sound ---
def play_alert():
    sound_path = resource_path(SOUND_FILE)
    if os.path.exists(sound_path):
        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

# --- Scan Logic ---
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
        

# --- Delayed Scan Trigger ---
scan_timeout_id = None
def delayed_handle_scan():
    global scan_timeout_id
    scan_timeout_id = None
    handle_scan()

def on_keypress(event):
    global scan_timeout_id
    if scan_timeout_id is not None:
        root.after_cancel(scan_timeout_id)
    scan_timeout_id = root.after(300, delayed_handle_scan)

# --- Fade-in Animation ---
def fade_in(window, interval=0.03):
    alpha = 0.0
    increment = interval / (FADE_IN_DURATION / 1000)
    def increase_opacity():
        nonlocal alpha
        alpha += increment
        if alpha >= 1.0:
            window.attributes("-alpha", 1.0)
        else:
            window.attributes("-alpha", alpha)
            window.after(int(interval * 1000), increase_opacity)
    increase_opacity()

# --- GUI Setup ---
root = tk.Tk()
root.title("OG Barcode Scanner")
root.geometry("520x320")
root.resizable(False, False)
root.attributes("-alpha", 0.0)

# Icon
icon_path = resource_path(ICON_FILE)
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# Background Image
bg_img = Image.open(resource_path(BACKGROUND_IMAGE)).resize((520, 320))
bg_photo = ImageTk.PhotoImage(bg_img)

canvas = tk.Canvas(root, width=520, height=320, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Fonts and Colors
FONT_HEADER = ("Georgia", 28, "bold")
FONT_INPUT = ("Georgia", 18)
FONT_FOOTER = ("Georgia", 11, "italic")

TITLE_COLOR = "#FAFAD2"   # Light golden white
ENTRY_COLOR = "#FFD700"   # Bright gold
FOOTER_COLOR = "#D4AF37"  # Rich gold
SHADOW_COLOR = "#000000"

# Title with drop shadow
canvas.create_text(262, 62, text="Scan Barcode", fill=SHADOW_COLOR, font=FONT_HEADER)
canvas.create_text(260, 60, text="Scan Barcode", fill=TITLE_COLOR, font=FONT_HEADER)

# Entry Box
entry = tk.Entry(root, font=FONT_INPUT, justify="center", fg=ENTRY_COLOR, bg="#111111",
                 insertbackground=ENTRY_COLOR, highlightthickness=2, width=24,
                 highlightbackground=ENTRY_COLOR, highlightcolor=ENTRY_COLOR, bd=0)
canvas.create_window(260, 140, window=entry)

# Footer
canvas.create_text(260, 290, text="Powered by La Familia", fill=FOOTER_COLOR, font=FONT_FOOTER)

entry.focus()
entry.bind("<Key>", on_keypress)

# Launch Fade-in
fade_in(root)
root.mainloop()
