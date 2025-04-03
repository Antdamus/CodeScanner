import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime
import winsound
import os

# --- Constants ---
DB_PATH = "barcode_scans.db"
SOUND_PATH = "beep.wav"
ICON_PATH = "og_icon.ico"
BACKGROUND_IMAGE = "hero-bg.jpg"
FADE_IN_DURATION = 800  # ms

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

# --- Fade-in Effect ---
def fade_in(window, interval=0.03):
    alpha = 0.0
    increment = interval / (FADE_IN_DURATION / 1000)
    def increase_opacity():
        nonlocal alpha
        alpha += increment
        if alpha >= 1.0:
            alpha = 1.0
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

if os.path.exists(ICON_PATH):
    root.iconbitmap(ICON_PATH)

# Load and set background image
bg_img = Image.open(BACKGROUND_IMAGE).resize((520, 320))
bg_photo = ImageTk.PhotoImage(bg_img)

canvas = tk.Canvas(root, width=520, height=320, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# --- Fonts & Colors ---
TITLE_FONT = ("Georgia", 28, "bold")
ENTRY_FONT = ("Georgia", 18)
FOOTER_FONT = ("Georgia", 11, "italic")

TITLE_COLOR = "#FAFAD2"   # light golden white
ENTRY_COLOR = "#FFD700"   # bright gold
FOOTER_COLOR = "#D4AF37"  # rich gold
SHADOW_COLOR = "#000000"

# --- Title with shadow layer for contrast ---
canvas.create_text(262, 62, text="Scan Barcode", fill=SHADOW_COLOR, font=TITLE_FONT)
canvas.create_text(260, 60, text="Scan Barcode", fill=TITLE_COLOR, font=TITLE_FONT)

# --- Entry box ---
entry = tk.Entry(root, font=ENTRY_FONT, justify="center", fg=ENTRY_COLOR, bg="#111111",
                 insertbackground=ENTRY_COLOR, highlightthickness=2, width=24,
                 highlightbackground=ENTRY_COLOR, highlightcolor=ENTRY_COLOR, bd=0)
canvas.create_window(260, 140, window=entry)

# --- Footer text ---
canvas.create_text(260, 290, text="Powered by La Familia", fill=FOOTER_COLOR, font=FOOTER_FONT)

entry.focus()
entry.bind("<Return>", handle_scan)

# Launch animation
fade_in(root)
root.mainloop()
