import customtkinter as ctk
import threading
import os
import sys
import json
import re
import time
import subprocess
import urllib.request
from tkinter import filedialog, colorchooser
import tkinter as tk
import yt_dlp

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except Exception:
    HAS_PYGAME = False


def resource_path(filename: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


PALETTES = {
    "dark": {
        "bg":           "#08080F",
        "card":         "#0F0F1C",
        "card_border":  "#1E1E38",
        "card_hover":   "#141428",
        "input_bg":     "#0B0B18",
        "input_border": "#232342",
        "accent":       "#6366F1",
        "accent_hover": "#818CF8",
        "text":         "#E8E8FF",
        "text_dim":     "#5A5A8A",
        "placeholder":  "#3A3A60",
        "log_bg":       "#07070F",
    },
    "light": {
        "bg":           "#F0F0F6",
        "card":         "#FFFFFF",
        "card_border":  "#E2E2EA",
        "card_hover":   "#F5F5FF",
        "input_bg":     "#F7F7FB",
        "input_border": "#D0D0DA",
        "accent":       "#007AFF",
        "accent_hover": "#3395FF",
        "text":         "#1C1C1E",
        "text_dim":     "#8E8E93",
        "placeholder":  "#AEAEB2",
        "log_bg":       "#F5F5FA",
    },
}

QUALITY_OPTIONS = {
    "Лучшее качество": "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio",
    "1080p":           "bestvideo[ext=mp4][vcodec^=avc][height<=1080]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio",
    "720p":            "bestvideo[ext=mp4][vcodec^=avc][height<=720]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio",
    "480p":            "bestvideo[ext=mp4][vcodec^=avc][height<=480]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio",
    "Только аудио MP3": "bestaudio",
}

LANGUAGES = {
    "Авто": None, "Русский": "ru", "English": "en",
    "Español": "es", "Deutsch": "de", "Français": "fr",
    "日本語": "ja", "中文": "zh",
}

WHISPER_MODELS = {
    "Large (3 GB)": "large",
}

BG_STYLES = ["Обводка", "Тёмный фон", "Без фона", "Неон"]
BG_STYLES_ASS = {
    "Обводка":    dict(borderstyle=1, outw=2, shadow=1, back="&H80000000"),
    "Тёмный фон": dict(borderstyle=3, outw=0, shadow=0, back="&H99000000"),
    "Без фона":   dict(borderstyle=1, outw=1, shadow=0, back="&H00000000"),
    "Неон":       dict(borderstyle=1, outw=2, shadow=5, back="&H00000000"),
}

STYLE_PRESETS = {
    # name: outline, spacing, shadow, bg, text-color, highlight-color, animation, dual_font
    "Классика": {"outline": 3,  "spacing": 0,  "shadow": "none",   "bg": "Обводка",   "text": "#FFFFFF", "hl": "#FFFF44", "anim": "Нет",        "dual_font": False},
    "Кинотитр": {"outline": 8,  "spacing": 8,  "shadow": "hard",   "bg": "Тёмный фон","text": "#FFE070", "hl": "#FF6A00", "anim": "Появление",   "dual_font": False},
    "Неон":     {"outline": 4,  "spacing": 3,  "shadow": "none",   "bg": "Неон",      "text": "#FFFFFF", "hl": "#00FFFF", "anim": "Нет",        "dual_font": False},
    "3D Тень":  {"outline": 3,  "spacing": 1,  "shadow": "3d",     "bg": "Без фона",  "text": "#FFFFFF", "hl": "#FF8800", "anim": "Слайд вверх", "dual_font": False},
    "Глитч":    {"outline": 0,  "spacing": 6,  "shadow": "glitch", "bg": "Без фона",  "text": "#FF88CC", "hl": "#00FFFF", "anim": "Нет",        "dual_font": False},
    "Кино ★":   {"outline": 3,  "spacing": 0,  "shadow": "hard",   "bg": "Без фона",  "text": "#FFFFFF", "hl": "#F5C518", "anim": "Появление",   "dual_font": True},
}

ANIM_MODES = ["Нет", "Появление", "Слайд вверх", "Масштаб"]

DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
WHISPER_CACHE_DIR  = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
REALESRGAN_DIR     = os.path.join(os.path.expanduser("~"), ".cache", "realesrgan")
REALESRGAN_EXE     = os.path.join(REALESRGAN_DIR, "realesrgan-ncnn-vulkan.exe")
REALESRGAN_URL     = ("https://github.com/xinntao/Real-ESRGAN/releases/download/"
                      "v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip")

SCRIPT_FONT_DIR  = os.path.join(os.path.expanduser("~"), ".cache", "ytdownloader", "fonts")
SCRIPT_FONT_URL  = ("https://github.com/google/fonts/raw/main/"
                    "ofl/marckscript/MarckScript-Regular.ttf")
SCRIPT_FONT_PATH = os.path.join(SCRIPT_FONT_DIR, "MarckScript-Regular.ttf")

# Downloadable Google Fonts  (url, cached_filename)
DOWNLOADABLE_FONTS = {
    "Bebas Neue":  ("https://github.com/google/fonts/raw/main/ofl/bebasneuenew/BebasNeue-Regular.ttf",          "BebasNeue-Regular.ttf"),
    "Oswald":      ("https://github.com/google/fonts/raw/main/ofl/oswald/static/Oswald-Regular.ttf",            "Oswald-Regular.ttf"),
    "Roboto":      ("https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Regular.ttf",         "Roboto-Regular.ttf"),
    "Montserrat":  ("https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Regular.ttf",    "Montserrat-Regular.ttf"),
    "Raleway":     ("https://github.com/google/fonts/raw/main/ofl/raleway/static/Raleway-Regular.ttf",          "Raleway-Regular.ttf"),
    "Playfair":    ("https://github.com/google/fonts/raw/main/ofl/playfairdisplay/static/PlayfairDisplay-Regular.ttf", "PlayfairDisplay-Regular.ttf"),
}

def _fw(*paths):
    """Return list of font path candidates (Windows, macOS fallbacks)."""
    return list(paths)

FONT_FAMILIES = {
    "Arial":           _fw("C:/Windows/Fonts/Arial.ttf",
                           "/Library/Fonts/Arial.ttf",
                           "/System/Library/Fonts/Supplemental/Arial.ttf"),
    "Arial Bold":      _fw("C:/Windows/Fonts/Arialbd.ttf",
                           "/Library/Fonts/Arial Bold.ttf",
                           "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    "Impact":          _fw("C:/Windows/Fonts/Impact.ttf",
                           "/Library/Fonts/Impact.ttf",
                           "/System/Library/Fonts/Supplemental/Impact.ttf"),
    "Times New Roman": _fw("C:/Windows/Fonts/Times.ttf",
                           "/Library/Fonts/Times New Roman.ttf",
                           "/System/Library/Fonts/Supplemental/Times New Roman.ttf"),
    "Verdana":         _fw("C:/Windows/Fonts/Verdana.ttf",
                           "/Library/Fonts/Verdana.ttf",
                           "/System/Library/Fonts/Supplemental/Verdana.ttf"),
    "Georgia":         _fw("C:/Windows/Fonts/Georgia.ttf",
                           "/Library/Fonts/Georgia.ttf",
                           "/System/Library/Fonts/Supplemental/Georgia.ttf"),
    "Tahoma":          _fw("C:/Windows/Fonts/Tahoma.ttf",
                           "/Library/Fonts/Tahoma.ttf",
                           "/System/Library/Fonts/Supplemental/Tahoma.ttf"),
    "Trebuchet MS":    _fw("C:/Windows/Fonts/Trebuc.ttf",
                           "/Library/Fonts/Trebuchet MS.ttf",
                           "/System/Library/Fonts/Supplemental/Trebuchet MS.ttf"),
    "Courier New":     _fw("C:/Windows/Fonts/Cour.ttf",
                           "/Library/Fonts/Courier New.ttf",
                           "/System/Library/Fonts/Supplemental/Courier New.ttf"),
    "Comic Sans MS":   _fw("C:/Windows/Fonts/Comic.ttf",
                           "/Library/Fonts/Comic Sans MS.ttf",
                           "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf"),
    "Marck Script":    [SCRIPT_FONT_PATH],
    # Google Fonts (auto-downloaded on first use)
    **{name: [os.path.join(SCRIPT_FONT_DIR, fname)]
       for name, (_, fname) in DOWNLOADABLE_FONTS.items()},
}

# Паттерны галлюцинаций Whisper — текстовый фильтр
_HALLUCINATION_RE = re.compile(
    r"аплодисмент|динамичн|музык[аеи]|смех|тишин|"
    r"applause|laughter|cheering|music|silence|♪|♫|"
    r"субтитры.*перевел|translated.{0,10}by|subbed.{0,10}by",
    re.IGNORECASE)
_BRACKETS_RE = re.compile(r"^\s*[\[\(].*[\]\)]\s*$")

TAB_DL   = "⬇  Скачать"
TAB_PREP = "◎  Подготовка"
TAB_EDIT = "✂  Редактор"


# ─────────────────────── Widget helpers ───────────────────────────

class Card(ctk.CTkFrame):
    def __init__(self, parent, p, **kw):
        super().__init__(parent, fg_color=p["card"], border_color=p["card_border"],
                         border_width=1, corner_radius=14, **kw)

class Lbl(ctk.CTkLabel):
    def __init__(self, parent, text, p, size=12, weight="normal", dim=False, **kw):
        super().__init__(parent, text=text,
                         font=ctk.CTkFont("Segoe UI", size, weight),
                         text_color=p["text_dim"] if dim else p["text"], **kw)

def optmenu(parent, values, var, p, **kw):
    return ctk.CTkOptionMenu(
        parent, values=values, variable=var, height=32, corner_radius=9,
        fg_color=p["input_bg"], button_color=p["accent"],
        button_hover_color=p["accent_hover"],
        dropdown_fg_color=p["card"], dropdown_hover_color=p["card_hover"],
        dropdown_text_color=p["text"], text_color=p["text"],
        font=ctk.CTkFont("Segoe UI", 12), **kw)

def btn(parent, text, p, cmd, accent=False, h=32, w=None, cr=9, **kw):
    if accent:
        kw.setdefault("font", ctk.CTkFont("Segoe UI", 13, "bold"))
        return ctk.CTkButton(parent, text=text, command=cmd, height=h,
                             fg_color=p["accent"], hover_color=p["accent_hover"],
                             text_color="#FFF", corner_radius=cr, width=w or 0, **kw)
    kw.setdefault("font", ctk.CTkFont("Segoe UI", 11, "bold"))
    return ctk.CTkButton(parent, text=text, command=cmd, height=h,
                         fg_color=p["input_bg"], hover_color=p["card_hover"],
                         border_color=p["card_border"], border_width=1,
                         text_color=p["accent"], corner_radius=cr, width=w or 0, **kw)


# ─────────────────────────── App ──────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._theme = "dark"
        self._p = PALETTES["dark"]

        # download
        self._dl_dir      = DEFAULT_DIR
        self._downloading = False
        self._last_pct    = -1

        # subtitle / video state
        self._sub_video   = ""
        self._sub_dur     = 0.0
        self._sub_out_dir = DEFAULT_DIR
        self._words: list = []
        self._segments: list = []
        self._seg_vars: list = []
        self._playing     = False
        self._play_time   = 0.0
        self._play_wall   = 0.0

        # trim
        self._trim_start  = 0.0
        self._trim_end    = 0.0   # 0 = "full video"

        # video capture
        self._cap             = None
        self._vid_fps         = 25.0
        self._photo_ref       = None
        self._canvas_image_id = None   # persistent canvas item for fast updates

        # style
        self._font_size      = 24
        self._font_family    = "Arial"
        self._text_color     = "#FFFFFF"
        self._hl_color       = "#F59E0B"
        self._karaoke_on     = True
        self._sub_pos_y      = 85      # % from top
        self._sub_pos_x      = 50     # % from left (center)
        self._sub_block_w    = 80     # block width as % of video width
        self._outline_width  = 2
        self._letter_spacing = 0
        self._shadow_mode    = "none"
        self._anim_mode      = "Нет"
        self._dual_font      = False
        # subtitle canvas drag
        self._sub_drag_active = False
        self._drag_last_x     = 0
        self._drag_last_y     = 0

        # audio
        self._audio_ready  = False
        self._audio_tmp    = None

        self._whisper_cache: dict = {}
        self._transcribing = False
        self._transcribe_cancel = False

        ctk.set_appearance_mode("dark")
        self.title("YT Downloader")
        self.geometry("720x840")
        self.minsize(580, 660)
        self.resizable(True, True)

        ico = resource_path("icon.ico")
        if os.path.exists(ico):
            self.iconbitmap(ico)

        self._build()

    # ── Build ─────────────────────────────────────────────────────

    def _build(self):
        p = self._p
        self.configure(fg_color=p["bg"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        if self._theme == "dark":
            self._orb = tk.Canvas(self, height=260, highlightthickness=0, bg=p["bg"], bd=0)
            self._orb.place(x=0, y=0, relwidth=1.0)
            self._redraw_orb(self.winfo_width() or 720)
            self._orb_bind = self.bind("<Configure>", self._on_resize, add="+")

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=24, pady=(22, 4), sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)
        hdr.lift()
        ctk.CTkLabel(hdr, text="YT Downloader",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color=p["text"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(hdr, text="скачать · субтитры",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=p["text_dim"]).grid(row=1, column=0, sticky="w")
        ctk.CTkButton(hdr, text="☀" if self._theme == "dark" else "☾",
                      width=42, height=42, corner_radius=21,
                      fg_color=p["card"], hover_color=p["card_hover"],
                      border_color=p["card_border"], border_width=1,
                      text_color=p["text"], font=ctk.CTkFont(size=17),
                      command=self._toggle_theme,
                      ).grid(row=0, column=2, rowspan=2, sticky="e")

        self._tabs = ctk.CTkTabview(
            self, fg_color=p["bg"], border_width=0, corner_radius=14,
            segmented_button_fg_color=p["input_bg"],
            segmented_button_selected_color=p["accent"],
            segmented_button_selected_hover_color=p["accent_hover"],
            segmented_button_unselected_color=p["input_bg"],
            segmented_button_unselected_hover_color=p["card_hover"],
            text_color=p["text"])
        self._tabs.grid(row=2, column=0, padx=14, pady=(0, 10), sticky="nsew")
        self._tabs.lift()
        self._tabs.add(TAB_DL)
        self._tabs.add(TAB_PREP)
        self._tabs.add(TAB_EDIT)
        self._build_download_tab(self._tabs.tab(TAB_DL))
        self._build_prepare_tab(self._tabs.tab(TAB_PREP))
        self._build_editor_tab(self._tabs.tab(TAB_EDIT))

    # ── Tab 1: Download ───────────────────────────────────────────

    def _build_download_tab(self, parent):
        p = self._p
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(4, weight=1)

        uc = Card(parent, p)
        uc.grid(row=0, column=0, padx=6, pady=(6, 5), sticky="ew")
        uc.grid_columnconfigure(0, weight=1)
        Lbl(uc, "  Ссылка на видео", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, padx=14, pady=(12, 4), sticky="w")
        self._url_entry = ctk.CTkEntry(
            uc, placeholder_text="https://youtube.com/watch?v=...",
            height=40, fg_color=p["input_bg"], border_color=p["input_border"],
            text_color=p["text"], placeholder_text_color=p["placeholder"],
            corner_radius=10, font=ctk.CTkFont("Segoe UI", 13))
        self._url_entry.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")

        r2 = ctk.CTkFrame(parent, fg_color="transparent")
        r2.grid(row=1, column=0, padx=6, pady=(0, 5), sticky="ew")
        r2.grid_columnconfigure(0, weight=1)
        r2.grid_columnconfigure(1, weight=1)

        qc = Card(r2, p)
        qc.grid(row=0, column=0, padx=(0, 4), sticky="nsew")
        qc.grid_columnconfigure(0, weight=1)
        Lbl(qc, "  Качество", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w")
        self._quality = ctk.StringVar(value=list(QUALITY_OPTIONS)[0])
        optmenu(qc, list(QUALITY_OPTIONS), self._quality, p
                ).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        fc = Card(r2, p)
        fc.grid(row=0, column=1, padx=(4, 0), sticky="nsew")
        fc.grid_columnconfigure(0, weight=1)
        Lbl(fc, "  Папка", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w")
        self._dl_folder_lbl = Lbl(fc, self._short(self._dl_dir), p, 11, anchor="w")
        self._dl_folder_lbl.grid(row=1, column=0, padx=12, sticky="ew")
        btn(fc, "Выбрать", p, self._pick_dl_folder, h=28
            ).grid(row=2, column=0, padx=10, pady=(6, 10), sticky="w")

        self._dl_btn = btn(parent, "▶   СКАЧАТЬ", p, self._start_download,
                           accent=True, h=48, cr=14)
        self._dl_btn.grid(row=2, column=0, padx=6, pady=(0, 5), sticky="ew")

        pc = Card(parent, p)
        pc.grid(row=3, column=0, padx=6, pady=(0, 5), sticky="ew")
        pc.grid_columnconfigure(0, weight=1)
        ph = ctk.CTkFrame(pc, fg_color="transparent")
        ph.grid(row=0, column=0, padx=14, pady=(10, 4), sticky="ew")
        ph.grid_columnconfigure(0, weight=1)
        Lbl(ph, "  Прогресс", p, 11, "bold", dim=True).grid(row=0, column=0, sticky="w")
        self._dl_pct = ctk.CTkLabel(ph, text="0%",
                                    font=ctk.CTkFont("Segoe UI", 11, "bold"),
                                    text_color=p["accent"])
        self._dl_pct.grid(row=0, column=1, sticky="e")
        self._dl_prog = ctk.CTkProgressBar(pc, height=6, corner_radius=3,
                                           fg_color=p["input_bg"], progress_color=p["accent"])
        self._dl_prog.set(0)
        self._dl_prog.grid(row=1, column=0, padx=14, pady=(0, 10), sticky="ew")

        lc = Card(parent, p)
        lc.grid(row=4, column=0, padx=6, pady=(0, 6), sticky="nsew")
        lc.grid_columnconfigure(0, weight=1)
        lc.grid_rowconfigure(1, weight=1)
        Lbl(lc, "  Статус", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, padx=14, pady=(10, 4), sticky="w")
        self._dl_log = ctk.CTkTextbox(lc, height=80, state="disabled",
                                      font=ctk.CTkFont("Consolas", 11),
                                      fg_color=p["log_bg"], text_color=p["text"],
                                      border_width=0, corner_radius=10)
        self._dl_log.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # ── Tab 2: Подготовка ─────────────────────────────────────────

    def _build_prepare_tab(self, parent):
        p = self._p
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        # File picker
        fcard = Card(parent, p)
        fcard.grid(row=0, column=0, padx=6, pady=(6, 5), sticky="ew")
        fcard.grid_columnconfigure(0, weight=1)
        Lbl(fcard, "  Видеофайл", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, padx=14, pady=(12, 4), sticky="w")
        frow = ctk.CTkFrame(fcard, fg_color="transparent")
        frow.grid(row=1, column=0, padx=12, pady=(0, 6), sticky="ew")
        frow.grid_columnconfigure(0, weight=1)
        self._vid_entry = ctk.CTkEntry(
            frow, placeholder_text="путь к видеофайлу…",
            height=38, fg_color=p["input_bg"], border_color=p["input_border"],
            text_color=p["text"], placeholder_text_color=p["placeholder"],
            corner_radius=10, font=ctk.CTkFont("Segoe UI", 12))
        self._vid_entry.grid(row=0, column=0, sticky="ew")
        btn(frow, "📁", p, self._pick_video, h=38, w=42,
            font=ctk.CTkFont(size=15)).grid(row=0, column=1, padx=(8, 0))
        self._vid_info = Lbl(fcard, "", p, 11, dim=True, anchor="w")
        self._vid_info.grid(row=2, column=0, padx=16, pady=(0, 10), sticky="w")

        # Transcription settings
        tcard = Card(parent, p)
        tcard.grid(row=1, column=0, padx=6, pady=(0, 5), sticky="ew")
        tcard.grid_columnconfigure(0, weight=1)

        th = ctk.CTkFrame(tcard, fg_color="transparent")
        th.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")
        th.grid_columnconfigure(0, weight=1)
        Lbl(th, "  Распознавание речи", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, sticky="w")
        self._model_status_lbl = Lbl(th, "", p, 10, dim=True, anchor="e")
        self._model_status_lbl.grid(row=0, column=1, sticky="e")

        trow = ctk.CTkFrame(tcard, fg_color="transparent")
        trow.grid(row=1, column=0, padx=12, pady=(0, 14), sticky="ew")
        trow.grid_columnconfigure(0, weight=1)
        trow.grid_columnconfigure(1, weight=1)

        self._lang_var = ctk.StringVar(value="Авто")
        optmenu(trow, list(LANGUAGES), self._lang_var, p
                ).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self._model_var = ctk.StringVar(value=list(WHISPER_MODELS)[-1])
        optmenu(trow, list(WHISPER_MODELS), self._model_var, p,
                command=lambda _: self._refresh_model_status()
                ).grid(row=0, column=1, padx=(0, 8), sticky="ew")
        self._trans_btn = btn(trow, "◎  Транскрибировать", p,
                              self._start_transcribe, accent=True, h=36)
        self._trans_btn.grid(row=0, column=2)
        self._trans_cancel_btn = btn(trow, "✕", p, self._cancel_transcribe, h=36, w=36)
        self._trans_cancel_btn.grid(row=0, column=3, padx=(4, 0))
        self._trans_cancel_btn.grid_remove()

        threading.Thread(target=self._refresh_model_status, daemon=True).start()

        # Big log card
        lcard = Card(parent, p)
        lcard.grid(row=2, column=0, padx=6, pady=(0, 6), sticky="nsew")
        lcard.grid_columnconfigure(0, weight=1)
        lcard.grid_rowconfigure(1, weight=1)

        lh = ctk.CTkFrame(lcard, fg_color="transparent")
        lh.grid(row=0, column=0, padx=14, pady=(10, 4), sticky="ew")
        lh.grid_columnconfigure(0, weight=1)
        Lbl(lh, "  Статус / Лог", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, sticky="w")
        self._open_editor_btn = btn(lh, "Открыть редактор  →", p,
                                    self._open_editor, accent=True, h=30)
        self._open_editor_btn.grid(row=0, column=1)
        self._open_editor_btn.grid_remove()   # hidden until transcription done

        self._sub_log = ctk.CTkTextbox(
            lcard, state="disabled",
            font=ctk.CTkFont("Consolas", 11),
            fg_color=p["log_bg"], text_color=p["text"],
            border_width=0, corner_radius=10)
        self._sub_log.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # ── Tab 3: Редактор ───────────────────────────────────────────

    def _build_editor_tab(self, parent):
        p = self._p
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # ── Resizable split: video (top) / controls+style+log (bottom) ──
        vpan = tk.PanedWindow(parent, orient="vertical",
                              sashwidth=8, sashpad=0, sashrelief="flat",
                              bg=p["card_border"], bd=0, relief="flat")
        vpan.grid(row=0, column=0, sticky="nsew")

        top = tk.Frame(vpan, bg=p["bg"])
        vpan.add(top, minsize=140, stretch="always")
        top.grid_columnconfigure(0, weight=1)
        top.grid_rowconfigure(0, weight=1)

        # Inner vertical split: cards area (top) / retrans+export+log (bottom)
        bot_pan = tk.PanedWindow(vpan, orient="vertical",
                                 sashwidth=8, sashpad=0, sashrelief="flat",
                                 bg=p["card_border"], bd=0, relief="flat")
        vpan.add(bot_pan, minsize=200, stretch="never")

        upper_bot = tk.Frame(bot_pan, bg=p["bg"])
        bot_pan.add(upper_bot, minsize=150, stretch="always")
        upper_bot.grid_columnconfigure(0, weight=1)
        upper_bot.grid_rowconfigure(0, weight=1)

        lower_bot = tk.Frame(bot_pan, bg=p["bg"])
        bot_pan.add(lower_bot, minsize=80, stretch="never")
        lower_bot.grid_columnconfigure(0, weight=1)

        # Video canvas — in top pane
        self._video_canvas = tk.Canvas(
            top, bg="#000000", highlightthickness=0, cursor="fleur")
        self._video_canvas.grid(row=0, column=0, padx=10, pady=(6, 4), sticky="nsew")
        self._video_canvas.bind("<Configure>",     self._on_canvas_resize)
        self._video_canvas.bind("<ButtonPress-1>", self._on_sub_press)
        self._video_canvas.bind("<B1-Motion>",     self._on_sub_drag)
        self._video_canvas.bind("<ButtonRelease-1>", self._on_sub_release)
        self._draw_canvas_placeholder("Транскрибируйте видео в разделе «Подготовка»")

        # Playback controls — in top pane
        ctrl = ctk.CTkFrame(top, fg_color="transparent")
        ctrl.grid(row=1, column=0, padx=14, pady=(0, 6), sticky="ew")
        ctrl.grid_columnconfigure(1, weight=1)
        self._play_btn = btn(ctrl, "▶  Играть", p, self._toggle_play, h=30)
        self._play_btn.grid(row=0, column=0, padx=(0, 10))
        self._scrubber = ctk.CTkSlider(
            ctrl, from_=0, to=100, number_of_steps=1000,
            fg_color=p["input_bg"], progress_color=p["accent"],
            button_color=p["accent"], button_hover_color=p["accent_hover"],
            command=self._on_scrubber)
        self._scrubber.set(0)
        self._scrubber.grid(row=0, column=1, sticky="ew")
        self._time_lbl = Lbl(ctrl, "0:00 / 0:00", p, 11, dim=True)
        self._time_lbl.grid(row=0, column=2, padx=(10, 0))

        # Style + Trim — horizontally resizable PanedWindow
        hpan = tk.PanedWindow(upper_bot, orient="horizontal",
                              sashwidth=8, sashpad=0, sashrelief="flat",
                              bg=p["card_border"], bd=0, relief="flat")
        hpan.grid(row=0, column=0, padx=6, pady=(4, 4), sticky="nsew")

        # ─ Style card ─
        scard = Card(hpan, p)
        hpan.add(scard, minsize=260, stretch="always")
        scard.grid_columnconfigure(0, weight=1)
        scard.grid_rowconfigure(1, weight=1)
        Lbl(scard, "  Субтитры", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, padx=14, pady=(10, 6), sticky="w")

        sg = ctk.CTkScrollableFrame(scard, fg_color="transparent",
                                    scrollbar_button_color=p["accent"],
                                    scrollbar_button_hover_color=p["accent_hover"])
        sg.grid(row=1, column=0, padx=6, pady=(0, 4), sticky="nsew")
        sg.grid_columnconfigure(1, weight=1)

        Lbl(sg, "Размер", p, 10, dim=True).grid(row=0, column=0, pady=(0, 6), sticky="w")
        self._size_lbl = Lbl(sg, "24", p, 10)
        self._size_lbl.grid(row=0, column=2, padx=(6, 0))
        fs = ctk.CTkSlider(sg, from_=12, to=56, number_of_steps=44,
                           fg_color=p["input_bg"], progress_color=p["accent"],
                           button_color=p["accent"], button_hover_color=p["accent_hover"],
                           command=self._on_fontsize)
        fs.set(24)
        fs.grid(row=0, column=1, padx=8, pady=(0, 6), sticky="ew")

        Lbl(sg, "Текст", p, 10, dim=True).grid(row=1, column=0, pady=(0, 6), sticky="w")
        tc_row = ctk.CTkFrame(sg, fg_color="transparent")
        tc_row.grid(row=1, column=1, columnspan=2, padx=8, pady=(0, 6), sticky="w")
        self._tc_swatch = ctk.CTkButton(tc_row, text="", width=22, height=18,
                                         corner_radius=5, fg_color=self._text_color,
                                         hover_color=self._text_color,
                                         command=self._pick_text_color)
        self._tc_swatch.grid(row=0, column=0)
        self._tc_hex = Lbl(tc_row, self._text_color.upper(), p, 10)
        self._tc_hex.grid(row=0, column=1, padx=(6, 0))

        Lbl(sg, "Подсветка", p, 10, dim=True).grid(row=2, column=0, pady=(0, 6), sticky="w")
        hl_row = ctk.CTkFrame(sg, fg_color="transparent")
        hl_row.grid(row=2, column=1, columnspan=2, padx=8, pady=(0, 6), sticky="w")
        self._hl_swatch = ctk.CTkButton(hl_row, text="", width=22, height=18,
                                         corner_radius=5, fg_color=self._hl_color,
                                         hover_color=self._hl_color,
                                         command=self._pick_hl_color)
        self._hl_swatch.grid(row=0, column=0)
        self._hl_hex = Lbl(hl_row, self._hl_color.upper(), p, 10)
        self._hl_hex.grid(row=0, column=1, padx=(6, 0))

        Lbl(sg, "Шрифт", p, 10, dim=True).grid(row=3, column=0, pady=(0, 6), sticky="w")
        self._font_var = ctk.StringVar(value=self._font_family)
        optmenu(sg, list(FONT_FAMILIES), self._font_var, p,
                command=self._on_font_change
                ).grid(row=3, column=1, columnspan=2, padx=8, pady=(0, 6), sticky="ew")

        Lbl(sg, "Стиль", p, 10, dim=True).grid(row=4, column=0, sticky="w")
        self._bg_style = ctk.StringVar(value=BG_STYLES[0])
        optmenu(sg, BG_STYLES, self._bg_style, p
                ).grid(row=4, column=1, columnspan=2, padx=8, sticky="ew")

        kar = ctk.CTkFrame(sg, fg_color="transparent")
        kar.grid(row=5, column=0, columnspan=3, pady=(8, 0), sticky="w")
        Lbl(kar, "Karaoke", p, 10, dim=True).grid(row=0, column=0, padx=(0, 8))
        self._karaoke_switch = ctk.CTkSwitch(
            kar, text="", width=40, height=20,
            progress_color=p["accent"], button_color=p["accent_hover"],
            command=self._toggle_karaoke)
        self._karaoke_switch.select()
        self._karaoke_switch.grid(row=0, column=1)

        Lbl(sg, "Позиция Y", p, 10, dim=True).grid(row=6, column=0, pady=(8, 0), sticky="w")
        self._pos_y_lbl = Lbl(sg, "85%", p, 10)
        self._pos_y_lbl.grid(row=6, column=2, padx=(6, 0), pady=(8, 0))
        self._pos_y_slider = ctk.CTkSlider(
            sg, from_=5, to=95, number_of_steps=90,
            fg_color=p["input_bg"], progress_color=p["accent"],
            button_color=p["accent"], button_hover_color=p["accent_hover"],
            command=self._on_pos_y)
        self._pos_y_slider.set(85)
        self._pos_y_slider.grid(row=6, column=1, padx=8, pady=(8, 0), sticky="ew")

        Lbl(sg, "Обводка", p, 10, dim=True).grid(row=7, column=0, pady=(6, 0), sticky="w")
        self._outline_lbl = Lbl(sg, "2", p, 10)
        self._outline_lbl.grid(row=7, column=2, padx=(6, 0), pady=(6, 0))
        self._outline_slider = ctk.CTkSlider(
            sg, from_=0, to=12, number_of_steps=12,
            fg_color=p["input_bg"], progress_color=p["accent"],
            button_color=p["accent"], button_hover_color=p["accent_hover"],
            command=self._on_outline)
        self._outline_slider.set(2)
        self._outline_slider.grid(row=7, column=1, padx=8, pady=(6, 0), sticky="ew")

        Lbl(sg, "Межбукв", p, 10, dim=True).grid(row=8, column=0, pady=(6, 2), sticky="w")
        self._spacing_lbl = Lbl(sg, "0", p, 10)
        self._spacing_lbl.grid(row=8, column=2, padx=(6, 0), pady=(6, 2))
        self._spacing_slider = ctk.CTkSlider(
            sg, from_=0, to=20, number_of_steps=20,
            fg_color=p["input_bg"], progress_color=p["accent"],
            button_color=p["accent"], button_hover_color=p["accent_hover"],
            command=self._on_spacing)
        self._spacing_slider.set(0)
        self._spacing_slider.grid(row=8, column=1, padx=8, pady=(6, 2), sticky="ew")

        Lbl(sg, "Анимация", p, 10, dim=True).grid(row=9, column=0, pady=(4, 4), sticky="w")
        self._anim_var = ctk.StringVar(value="Нет")
        optmenu(sg, ANIM_MODES, self._anim_var, p,
                command=self._on_anim_change
                ).grid(row=9, column=1, columnspan=2, padx=8, pady=(4, 4), sticky="ew")

        Lbl(sg, "Ширина", p, 10, dim=True).grid(row=10, column=0, pady=(4, 0), sticky="w")
        self._block_w_lbl = Lbl(sg, "80%", p, 10)
        self._block_w_lbl.grid(row=10, column=2, padx=(6, 0), pady=(4, 0))
        self._block_w_slider = ctk.CTkSlider(
            sg, from_=10, to=100, number_of_steps=90,
            fg_color=p["input_bg"], progress_color=p["accent"],
            button_color=p["accent"], button_hover_color=p["accent_hover"],
            command=self._on_block_width)
        self._block_w_slider.set(80)
        self._block_w_slider.grid(row=10, column=1, padx=8, pady=(4, 0), sticky="ew")

        kino_row = ctk.CTkFrame(sg, fg_color="transparent")
        kino_row.grid(row=11, column=0, columnspan=3, pady=(8, 2), sticky="w")
        Lbl(kino_row, "Кино-шрифт", p, 10, dim=True).grid(row=0, column=0, padx=(0, 8))
        self._dual_font_switch = ctk.CTkSwitch(
            kino_row, text="", width=40, height=20,
            progress_color=p["accent"], button_color=p["accent_hover"],
            command=self._toggle_dual_font)
        self._dual_font_switch.grid(row=0, column=1)
        Lbl(kino_row, "  (разделяй строки через \\n в тексте)", p, 10, dim=True
            ).grid(row=0, column=2, padx=(6, 0))

        # Preset buttons row
        pr = ctk.CTkFrame(scard, fg_color="transparent")
        pr.grid(row=2, column=0, padx=14, pady=(0, 10), sticky="ew")
        Lbl(pr, "Пресет:", p, 10, dim=True).grid(row=0, column=0, padx=(0, 6))
        for _i, _pname in enumerate(STYLE_PRESETS):
            btn(pr, _pname, p, lambda n=_pname: self._apply_preset(n), h=26, cr=6
                ).grid(row=0, column=_i + 1, padx=(0, 4))

        # ─ Trim card ─
        trcard = Card(hpan, p)
        hpan.add(trcard, minsize=180, stretch="always")
        trcard.grid_columnconfigure(0, weight=1)
        trcard.grid_rowconfigure(1, weight=1)
        Lbl(trcard, "  Обрезка видео", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, padx=14, pady=(10, 6), sticky="w")

        tg = ctk.CTkScrollableFrame(trcard, fg_color="transparent",
                                    scrollbar_button_color=p["accent"],
                                    scrollbar_button_hover_color=p["accent_hover"])
        tg.grid(row=1, column=0, padx=6, pady=(0, 4), sticky="nsew")
        tg.grid_columnconfigure(1, weight=1)

        Lbl(tg, "Начало", p, 10, dim=True).grid(row=0, column=0, pady=(0, 8), sticky="w")
        self._trim_s_lbl = Lbl(tg, "0:00", p, 10)
        self._trim_s_lbl.grid(row=0, column=2, padx=(8, 0))
        self._trim_s_slider = ctk.CTkSlider(
            tg, from_=0, to=100, number_of_steps=1000,
            fg_color=p["input_bg"], progress_color=p["accent"],
            button_color=p["accent"], button_hover_color=p["accent_hover"],
            command=self._on_trim_start)
        self._trim_s_slider.set(0)
        self._trim_s_slider.grid(row=0, column=1, padx=8, pady=(0, 8), sticky="ew")

        Lbl(tg, "Конец", p, 10, dim=True).grid(row=1, column=0, pady=(0, 8), sticky="w")
        self._trim_e_lbl = Lbl(tg, "0:00", p, 10)
        self._trim_e_lbl.grid(row=1, column=2, padx=(8, 0))
        self._trim_e_slider = ctk.CTkSlider(
            tg, from_=0, to=100, number_of_steps=1000,
            fg_color=p["input_bg"], progress_color=p["accent"],
            button_color=p["accent"], button_hover_color=p["accent_hover"],
            command=self._on_trim_end)
        self._trim_e_slider.set(100)
        self._trim_e_slider.grid(row=1, column=1, padx=8, pady=(0, 8), sticky="ew")

        self._trim_dur_lbl = Lbl(tg, "Длина: —", p, 10, dim=True)
        self._trim_dur_lbl.grid(row=2, column=0, columnspan=3, sticky="w")

        # ─ Subtitle text editor card ─
        segedit = self._build_sub_editor_card(upper_bot)
        segedit.grid(row=1, column=0, padx=6, pady=(0, 4), sticky="ew")

        # ─ Re-transcribe row ─
        rtcard = Card(lower_bot, p)
        rtcard.grid(row=0, column=0, padx=6, pady=(4, 4), sticky="ew")
        rtcard.grid_columnconfigure(1, weight=1)
        rtcard.grid_columnconfigure(2, weight=2)
        Lbl(rtcard, "  Модель:", p, 10, dim=True).grid(
            row=0, column=0, padx=(14, 8), pady=7, sticky="w")
        optmenu(rtcard, list(LANGUAGES), self._lang_var, p).grid(
            row=0, column=1, padx=(0, 6), pady=5, sticky="ew")
        optmenu(rtcard, list(WHISPER_MODELS), self._model_var, p,
                command=lambda _: self._refresh_model_status()
                ).grid(row=0, column=2, padx=(0, 6), pady=5, sticky="ew")
        self._retrans_btn = btn(rtcard, "◎ Транскрибировать", p,
                                self._start_transcribe, accent=True, h=32)
        self._retrans_btn.grid(row=0, column=3, padx=(0, 14), pady=5)

        # Upscale + Export row
        act_row = ctk.CTkFrame(lower_bot, fg_color="transparent")
        act_row.grid(row=1, column=0, padx=14, pady=(0, 4), sticky="ew")
        act_row.grid_columnconfigure(1, weight=1)

        Lbl(act_row, "Папка:", p, 11, dim=True).grid(row=0, column=0, sticky="w")
        self._out_lbl = Lbl(act_row, self._short(self._sub_out_dir), p, 11, anchor="w")
        self._out_lbl.grid(row=0, column=1, padx=8, sticky="ew")
        btn(act_row, "Выбрать", p, self._pick_out_folder, h=28, w=80
            ).grid(row=0, column=2, padx=(0, 8))

        # AI upscale button
        self._upscale_btn = btn(act_row, "✨ AI Апскейл", p, self._start_upscale, h=36)
        self._upscale_btn.grid(row=0, column=3, padx=(0, 8))

        self._export_btn = btn(act_row, "💾  Export", p, self._start_export,
                               accent=True, h=36)
        self._export_btn.grid(row=0, column=4)

        # Log header with collapse toggle
        log_hdr = ctk.CTkFrame(lower_bot, fg_color="transparent")
        log_hdr.grid(row=2, column=0, padx=10, pady=(4, 0), sticky="ew")
        log_hdr.grid_columnconfigure(1, weight=1)
        Lbl(log_hdr, "Лог", p, 10, dim=True).grid(row=0, column=0, sticky="w")
        self._log_toggle_btn = ctk.CTkButton(
            log_hdr, text="−", width=24, height=18, corner_radius=5,
            fg_color=p["input_bg"], hover_color=p["card_hover"],
            text_color=p["text"], font=ctk.CTkFont("Segoe UI", 11),
            command=self._toggle_export_log)
        self._log_toggle_btn.grid(row=0, column=2, sticky="e")

        # Log textbox
        self._export_log = ctk.CTkTextbox(
            lower_bot, height=70, state="disabled",
            font=ctk.CTkFont("Consolas", 11),
            fg_color=p["log_bg"], text_color=p["text"],
            border_width=0, corner_radius=10)
        self._export_log.grid(row=3, column=0, padx=10, pady=(2, 6), sticky="ew")

    # ── Orb ──────────────────────────────────────────────────────

    def _redraw_orb(self, w: int):
        p, c = self._p, self._orb
        c.delete("all")
        bg, acc = p["bg"], p["accent"]
        br, bg_, bb = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
        ar, ag, ab  = int(acc[1:3], 16), int(acc[3:5], 16), int(acc[5:7], 16)
        cx, cy, mx, my = w * .5, 0, w * .52, 286
        for i in range(50):
            t = (i / 50) ** 1.8; r2 = 1 - i / 50
            c.create_oval(cx - mx * r2, cy - my * r2, cx + mx * r2, cy + my * r2,
                          fill=f"#{int(br+(ar-br)*t):02x}{int(bg_+(ag-bg_)*t):02x}"
                               f"{int(bb+(ab-bb)*t):02x}", outline="")

    def _on_resize(self, ev):
        if ev.widget is self and hasattr(self, "_orb"):
            self._redraw_orb(ev.width)

    def _on_canvas_resize(self, *_):
        if not self._playing and self._cap:
            self._show_frame_at(self._play_time)

    # ── Theme ─────────────────────────────────────────────────────

    def _toggle_theme(self):
        saved_url = self._url_entry.get()
        saved_vid = self._vid_entry.get()
        if hasattr(self, "_orb_bind"):
            self.unbind("<Configure>", self._orb_bind)
            del self._orb_bind
        if hasattr(self, "_orb"):
            del self._orb
        self._playing = False
        self._theme = "light" if self._theme == "dark" else "dark"
        self._p = PALETTES[self._theme]
        ctk.set_appearance_mode(self._theme)
        for w in self.winfo_children():
            w.destroy()
        self._build()
        self._url_entry.insert(0, saved_url)
        if saved_vid:
            self._vid_entry.insert(0, saved_vid)

    # ── Helpers ───────────────────────────────────────────────────

    def _short(self, path: str) -> str:
        h = os.path.expanduser("~")
        if path.startswith(h):
            path = "~" + path[len(h):]
        return path if len(path) <= 42 else "..." + path[-40:]

    def _fmt(self, s: float) -> str:
        h, r = divmod(int(max(0, s)), 3600)
        m, sec = divmod(r, 60)
        return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"

    def _ts_ass(self, s: float) -> str:
        s = max(0.0, s)
        h, r = divmod(int(s), 3600)
        m, sec = divmod(r, 60)
        return f"{h}:{m:02d}:{sec:02d}.{int((s % 1) * 100):02d}"

    @staticmethod
    def _hex_to_ass(c: str, alpha: int = 0) -> str:
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"

    @staticmethod
    def _dimmed(c: str, f: float = 0.35) -> str:
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        return f"#{int(r*f):02x}{int(g*f):02x}{int(b*f):02x}"

    @staticmethod
    def _hex_to_rgb(c: str) -> tuple:
        return (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16))

    def _get_pil_font(self, size: int):
        if not HAS_PIL:
            return None
        paths = []
        selected = FONT_FAMILIES.get(self._font_family, [])
        if isinstance(selected, list):
            paths.extend(p for p in selected if p)
        elif selected:
            paths.append(selected)
        paths += [
            "C:/Windows/Fonts/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for path in paths:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    # ── Log helpers ───────────────────────────────────────────────

    def _log_dl(self, msg):
        self._dl_log.configure(state="normal")
        self._dl_log.insert("end", msg + "\n")
        self._dl_log.see("end")
        self._dl_log.configure(state="disabled")

    def _log_sub(self, msg):
        self._sub_log.configure(state="normal")
        self._sub_log.insert("end", msg + "\n")
        self._sub_log.see("end")
        self._sub_log.configure(state="disabled")

    def _log_export(self, msg):
        self._export_log.configure(state="normal")
        self._export_log.insert("end", msg + "\n")
        self._export_log.see("end")
        self._export_log.configure(state="disabled")

    # ── Download ──────────────────────────────────────────────────

    def _set_dl_prog(self, v):
        self._dl_prog.set(v)
        self._dl_pct.configure(text=f"{int(v * 100)}%")

    def _pick_dl_folder(self):
        d = filedialog.askdirectory(initialdir=self._dl_dir)
        if d:
            self._dl_dir = d
            self._dl_folder_lbl.configure(text=self._short(d))

    def _start_download(self):
        if self._downloading:
            return
        url = self._url_entry.get().strip()
        if not url:
            self._log_dl("⚠  Введите ссылку.")
            return
        self._downloading = True
        self._last_pct = -1
        self._dl_btn.configure(state="disabled", text="⏳  Скачивание…")
        self._set_dl_prog(0)
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    def _download(self, url):
        q = self._quality.get()
        is_mp3 = "MP3" in q
        opts = {
            "format": QUALITY_OPTIONS[q],
            "outtmpl": os.path.join(self._dl_dir, "%(title)s.%(ext)s"),
            "merge_output_format": "mp4" if not is_mp3 else None,
            "progress_hooks": [self._dl_hook],
            "quiet": True, "no_warnings": True,
        }
        if is_mp3:
            opts["postprocessors"] = [{"key": "FFmpegExtractAudio",
                                        "preferredcodec": "mp3", "preferredquality": "192"}]
        try:
            self.after(0, self._log_dl, "▶  Начинаю загрузку…")
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            self.after(0, self._log_dl, f"✓  Готово: {info.get('title', '')}")
            self.after(0, self._set_dl_prog, 1.0)
        except Exception as e:
            self.after(0, self._log_dl, f"✗  {e}")
        finally:
            self._downloading = False
            self.after(0, self._dl_btn.configure,
                       {"state": "normal", "text": "▶   СКАЧАТЬ"})

    def _dl_hook(self, d):
        if d["status"] == "downloading":
            tot = d.get("total_bytes") or d.get("total_bytes_estimate")
            dl  = d.get("downloaded_bytes", 0)
            if tot:
                pct = int(dl / tot * 100)
                self.after(0, self._set_dl_prog, dl / tot)
                if pct // 10 != self._last_pct // 10:
                    self._last_pct = pct
                    self.after(0, self._log_dl,
                               f"  {pct}%  {d.get('_speed_str', '').strip()}  "
                               f"ETA {d.get('_eta_str', '').strip()}")
        elif d["status"] == "finished":
            self.after(0, self._log_dl, "  ◎  Обработка…")

    # ── Video file & ffprobe ──────────────────────────────────────

    def _pick_video(self):
        f = filedialog.askopenfilename(
            filetypes=[("Видео", "*.mp4 *.mkv *.avi *.mov *.webm *.mp3 *.wav *.m4a"),
                       ("Все файлы", "*.*")])
        if not f:
            return
        self._sub_video = f
        self._vid_entry.delete(0, "end")
        self._vid_entry.insert(0, f)
        self._load_video_info(f)
        self._open_video_capture(f)

    def _load_video_info(self, path: str):
        try:
            res = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", path],
                capture_output=True, text=True, timeout=10)
            info = json.loads(res.stdout)
            dur  = float(info["format"].get("duration", 0))
            self._sub_dur = dur
            vs   = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
            w, h = vs.get("width", "?"), vs.get("height", "?")
            try:
                a, b = vs.get("r_frame_rate", "0/1").split("/")
                fps = str(int(a) // int(b))
            except Exception:
                fps = "?"
            self._vid_info.configure(text=f"  {self._fmt(dur)}  ·  {w}×{h}  ·  {fps} fps")
            self._scrubber.configure(to=max(dur, 1))
            self._scrubber.set(0)
            self._time_lbl.configure(text=f"0:00 / {self._fmt(dur)}")
        except Exception:
            self._vid_info.configure(text="  (ffprobe недоступен)")

    def _open_video_capture(self, path: str):
        if not HAS_CV2:
            self._draw_canvas_placeholder("opencv не установлен")
            return
        if self._cap:
            self._cap.release()
        self._canvas_image_id = None
        self._cap = cv2.VideoCapture(path)
        if not self._cap.isOpened():
            self._draw_canvas_placeholder("Не удалось открыть видео")
            self._cap = None
            return
        self._vid_fps = self._cap.get(cv2.CAP_PROP_FPS) or 25.0
        self._audio_ready = False
        threading.Thread(target=self._extract_audio, args=(path,), daemon=True).start()
        self._show_frame_at(0.0)

    def _pick_out_folder(self):
        d = filedialog.askdirectory(initialdir=self._sub_out_dir)
        if d:
            self._sub_out_dir = d
            self._out_lbl.configure(text=self._short(d))

    def _extract_audio(self, path: str):
        """Extract audio from video to temp MP3 for pygame playback."""
        if not HAS_PYGAME:
            return
        import tempfile
        tmp = os.path.join(tempfile.gettempdir(), "ytdl_preview_audio.mp3")
        r = subprocess.run(
            ["ffmpeg", "-y", "-i", path, "-vn", "-acodec", "mp3", "-q:a", "6", tmp],
            capture_output=True, timeout=120)
        if r.returncode == 0 and os.path.exists(tmp):
            try:
                pygame.mixer.music.load(tmp)
                self._audio_tmp = tmp
                self._audio_ready = True
            except Exception:
                pass

    # ── Trim controls ─────────────────────────────────────────────

    def _on_trim_start(self, val):
        val = float(val)
        if self._trim_end > 0 and val >= self._trim_end:
            val = max(0.0, self._trim_end - 0.5)
            self._trim_s_slider.set(val)
        self._trim_start = val
        self._trim_s_lbl.configure(text=self._fmt(val))
        self._update_trim_dur()
        self._show_frame_at(val)

    def _on_trim_end(self, val):
        val = float(val)
        if val <= self._trim_start:
            val = min(self._sub_dur, self._trim_start + 0.5)
            self._trim_e_slider.set(val)
        self._trim_end = val
        self._trim_e_lbl.configure(text=self._fmt(val))
        self._update_trim_dur()

    def _update_trim_dur(self):
        t_end = self._trim_end if self._trim_end > 0 else self._sub_dur
        dur = max(0.0, t_end - self._trim_start)
        self._trim_dur_lbl.configure(text=f"Длина: {self._fmt(dur)}")

    # ── Model cache status ────────────────────────────────────────

    def _is_model_cached(self, model_name: str) -> bool:
        """Check if a Whisper model .pt file exists in the cache directory."""
        if not os.path.isdir(WHISPER_CACHE_DIR):
            return False
        for fname in os.listdir(WHISPER_CACHE_DIR):
            # large → large-v2.pt / large-v3.pt; tiny → tiny.pt etc.
            if fname.endswith(".pt") and model_name in fname:
                return True
        return False

    def _refresh_model_status(self):
        selected = WHISPER_MODELS.get(self._model_var.get(), "")
        if not selected:
            return
        cached = self._is_model_cached(selected)
        text = "✓ скачана" if cached else "↓ нужно скачать"
        self.after(0, self._model_status_lbl.configure, {"text": text})

    def _cancel_transcribe(self):
        self._transcribe_cancel = True
        self._trans_cancel_btn.configure(state="disabled")
        self._log_sub("⚠  Отменяю… (завершится после текущей операции)")

    # ── Style controls ────────────────────────────────────────────

    def _on_fontsize(self, val):
        self._font_size = int(val)
        self._size_lbl.configure(text=str(self._font_size))

    def _pick_text_color(self):
        _, c = colorchooser.askcolor(color=self._text_color, title="Цвет текста")
        if not c:
            return
        self._text_color = c
        self._tc_swatch.configure(fg_color=c, hover_color=c)
        self._tc_hex.configure(text=c.upper())

    def _pick_hl_color(self):
        _, c = colorchooser.askcolor(color=self._hl_color, title="Цвет подсветки")
        if not c:
            return
        self._hl_color = c
        self._hl_swatch.configure(fg_color=c, hover_color=c)
        self._hl_hex.configure(text=c.upper())

    def _on_font_change(self, val):
        self._font_family = val
        if val in DOWNLOADABLE_FONTS:
            _, fname = DOWNLOADABLE_FONTS[val]
            if not os.path.exists(os.path.join(SCRIPT_FONT_DIR, fname)):
                threading.Thread(target=self._download_google_font,
                                 args=(val,), daemon=True).start()
        if self._cap:
            self._show_frame_at(self._play_time)

    def _toggle_karaoke(self):
        self._karaoke_on = self._karaoke_switch.get() == 1

    def _on_pos_y(self, val):
        self._sub_pos_y = float(val)
        self._pos_y_lbl.configure(text=f"{int(val)}%")

    def _on_outline(self, val):
        self._outline_width = int(val)
        self._outline_lbl.configure(text=str(int(val)))

    def _on_spacing(self, val):
        self._letter_spacing = int(val)
        self._spacing_lbl.configure(text=str(int(val)))

    def _on_anim_change(self, val):
        self._anim_mode = val

    def _toggle_export_log(self):
        if self._export_log.winfo_viewable():
            self._export_log.grid_remove()
            self._log_toggle_btn.configure(text="+")
        else:
            self._export_log.grid()
            self._log_toggle_btn.configure(text="−")

    # ── Canvas subtitle drag ──────────────────────────────────────

    def _on_sub_press(self, ev):
        if self._segments:
            self._sub_drag_active = True
            self._drag_last_x = ev.x
            self._drag_last_y = ev.y

    def _on_sub_drag(self, ev):
        if not self._sub_drag_active:
            return
        c = self._video_canvas
        cw = max(1, c.winfo_width())
        ch = max(1, c.winfo_height())
        # Absolute position from cursor
        self._sub_pos_x = max(5, min(95, ev.x / cw * 100))
        self._sub_pos_y = max(5, min(95, ev.y / ch * 100))
        # Sync Y slider
        if hasattr(self, "_pos_y_slider"):
            self._pos_y_slider.set(self._sub_pos_y)
            self._pos_y_lbl.configure(text=f"{int(self._sub_pos_y)}%")
        self._drag_last_x = ev.x
        self._drag_last_y = ev.y
        self._show_frame_at(self._play_time)

    def _on_sub_release(self, _ev):
        self._sub_drag_active = False

    def _draw_subtitle_anchor(self, cw: int, ch: int):
        """Draw a crosshair anchor on the canvas (preview only, not in export)."""
        c = self._video_canvas
        c.delete("sub_anchor")
        if not self._segments:
            return
        ax = int(cw * self._sub_pos_x / 100)
        ay = int(ch * self._sub_pos_y / 100)
        r = 9
        c.create_oval(ax - r, ay - r, ax + r, ay + r,
                      outline="#7777ff", width=2, tags="sub_anchor")
        c.create_line(ax - r - 5, ay, ax + r + 5, ay,
                      fill="#7777ff", width=1, tags="sub_anchor")
        c.create_line(ax, ay - r - 5, ax, ay + r + 5,
                      fill="#7777ff", width=1, tags="sub_anchor")

    def _apply_preset(self, name: str):
        pr = STYLE_PRESETS.get(name)
        if not pr:
            return
        self._outline_width   = pr["outline"]
        self._letter_spacing  = pr["spacing"]
        self._shadow_mode     = pr["shadow"]
        self._anim_mode       = pr.get("anim", "Нет")
        self._bg_style.set(pr["bg"])
        self._text_color = pr["text"]
        self._hl_color   = pr["hl"]
        self._outline_slider.set(pr["outline"])
        self._spacing_slider.set(pr["spacing"])
        self._outline_lbl.configure(text=str(pr["outline"]))
        self._spacing_lbl.configure(text=str(pr["spacing"]))
        self._tc_swatch.configure(fg_color=pr["text"], hover_color=pr["text"])
        self._tc_hex.configure(text=pr["text"].upper())
        self._hl_swatch.configure(fg_color=pr["hl"], hover_color=pr["hl"])
        self._hl_hex.configure(text=pr["hl"].upper())
        if hasattr(self, "_anim_var"):
            self._anim_var.set(self._anim_mode)
        self._dual_font = pr.get("dual_font", False)
        if hasattr(self, "_dual_font_switch"):
            if self._dual_font:
                self._dual_font_switch.select()
                threading.Thread(target=self._ensure_script_font, daemon=True).start()
            else:
                self._dual_font_switch.deselect()
        # Immediately refresh the canvas preview
        if self._cap:
            self.after(80, lambda: self._show_frame_at(self._play_time))

    # ── Canvas / video player ─────────────────────────────────────

    def _draw_canvas_placeholder(self, msg="Загрузите видео"):
        self._canvas_image_id = None
        c = self._video_canvas
        c.delete("all")
        cw = c.winfo_width() or 680
        ch = c.winfo_height() or 300
        c.create_text(cw // 2, ch // 2, text=msg,
                      fill="#444466", font=("Segoe UI", 13), anchor="center")

    def _show_frame_at(self, t: float):
        if not self._cap or not HAS_CV2 or not HAS_PIL:
            return
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * self._vid_fps))
        ret, frame = self._cap.read()
        if ret:
            self._display_frame_fast(frame, t)

    def _display_frame(self, frame, current_time: float):
        if not HAS_PIL:
            return
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        c = self._video_canvas
        cw = c.winfo_width() or 680
        ch = c.winfo_height() or 300
        if cw < 10 or ch < 10:
            return
        iw, ih = img.size
        scale = min(cw / iw, ch / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        img = img.resize((nw, nh), Image.LANCZOS)
        if self._segments:
            img = self._render_subtitle_pil(img, current_time)
        canvas_img = Image.new("RGB", (cw, ch), (0, 0, 0))
        canvas_img.paste(img, ((cw - nw) // 2, (ch - nh) // 2))
        photo = ImageTk.PhotoImage(canvas_img)
        self._photo_ref = photo
        c.delete("all")
        c.create_image(0, 0, image=photo, anchor="nw")

    def _display_frame_fast(self, frame, current_time: float):
        """Fast path for playback: cv2 resize + persistent canvas item."""
        if not HAS_PIL:
            return
        c = self._video_canvas
        cw = c.winfo_width() or 680
        ch = c.winfo_height() or 300
        if cw < 10 or ch < 10:
            return
        h, w = frame.shape[:2]
        scale = min(cw / w, ch / h)
        nw, nh = int(w * scale), int(h * scale)
        # cv2 resize is ~5x faster than PIL LANCZOS
        rgb = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                         (nw, nh), interpolation=cv2.INTER_LINEAR)
        img = Image.fromarray(rgb)
        if self._segments:
            img = self._render_subtitle_pil(img, current_time)
        photo = ImageTk.PhotoImage(img)
        self._photo_ref = photo
        if self._canvas_image_id is None:
            c.delete("all")
            self._canvas_image_id = c.create_image(cw // 2, ch // 2,
                                                    image=photo, anchor="center")
        else:
            c.itemconfig(self._canvas_image_id, image=photo)
            c.coords(self._canvas_image_id, cw // 2, ch // 2)
        self._draw_subtitle_anchor(cw, ch)

    def _render_subtitle_pil(self, img, current_time: float):
        seg = None
        for s in self._segments:
            if s["start"] - 0.1 <= current_time <= s["end"] + 0.3:
                seg = s
                break
        if seg is None:
            return img

        if self._dual_font and "\n" in seg.get("text", ""):
            return self._render_dual_font_pil(img, seg, current_time)

        iw, ih = img.size
        scale  = iw / 640

        # ── Animation ────────────────────────────────────────────────
        anim    = getattr(self, "_anim_mode", "Нет")
        seg_dur = max(0.001, seg["end"] - seg["start"])
        t_rel   = max(0.0, current_time - seg["start"])
        t_left  = max(0.0, seg["end"] - current_time)

        fade_mul = 1.0; y_offset = 0; fsize_scale = 1.0
        if anim == "Появление":
            fade_mul = min(min(1.0, t_rel / min(0.35, seg_dur * 0.3)),
                           min(1.0, t_left / min(0.25, seg_dur * 0.25)))
        elif anim == "Слайд вверх":
            slide = min(1.0, t_rel / min(0.4, seg_dur * 0.35))
            y_offset = int(55 * scale * (1.0 - slide))
        elif anim == "Масштаб":
            fsize_scale = 0.3 + 0.7 * min(1.0, t_rel / min(0.35, seg_dur * 0.3))

        fsize = max(10, int(self._font_size * scale * fsize_scale))
        font  = self._get_pil_font(fsize)
        draw  = ImageDraw.Draw(img)

        def _fade(rgb):
            if fade_mul >= 1.0:
                return rgb
            return tuple(max(0, int(c * fade_mul)) for c in rgb)

        t_rgb  = _fade(self._hex_to_rgb(self._text_color))
        h_rgb  = _fade(self._hex_to_rgb(self._hl_color))
        bg     = self._bg_style.get()
        smode  = self._shadow_mode
        outpx  = max(0, int(self._outline_width * scale))
        sppx   = max(0, int(self._letter_spacing * scale))
        margin = max(12, int(20 * scale))

        def _tw(t):
            bb = draw.textbbox((0, 0), t, font=font)
            return max(1, bb[2] - bb[0])

        def _lh():
            bb = draw.textbbox((0, 0), "Ag|", font=font)
            return max(1, bb[3] - bb[1])

        def _sw(t):
            if sppx == 0 or len(t) <= 1:
                return _tw(t)
            return sum(_tw(c) for c in t) + sppx * (len(t) - 1)

        def _put(px, py, t, fill, stroke=0, sfill=(0, 0, 0)):
            try:
                kw = {"stroke_width": stroke, "stroke_fill": sfill} if stroke > 0 else {}
                draw.text((px, py), t, font=font, fill=fill, **kw)
            except Exception:
                draw.text((px, py), t, font=font, fill=fill)

        def _puts(px, py, t, fill, stroke=0, sfill=(0, 0, 0)):
            if sppx == 0:
                _put(px, py, t, fill, stroke, sfill)
                return
            cx = px
            for ch in t:
                _put(cx, py, ch, fill, stroke, sfill)
                cx += _tw(ch) + sppx

        # ── Block layout ─────────────────────────────────────────────
        pos_x   = getattr(self, "_sub_pos_x",  50)
        blk_pct = getattr(self, "_sub_block_w", 80)
        blk_px  = max(80, int(iw * blk_pct / 100))
        blk_cx  = int(iw * pos_x / 100)
        blk_l   = max(margin, blk_cx - blk_px // 2)
        blk_r   = min(iw - margin, blk_l + blk_px)
        blk_w   = max(80, blk_r - blk_l)

        # Word-wrap text to block width
        raw_words = seg["text"].split()
        lines_txt: list[str] = []
        cur: list[str] = []
        for w in raw_words:
            test = " ".join(cur + [w])
            if cur and _sw(test) > blk_w:
                lines_txt.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines_txt.append(" ".join(cur))
        if not lines_txt:
            return img

        line_h  = _lh()
        gap     = max(3, int(fsize * 0.15))
        total_h = len(lines_txt) * line_h + (len(lines_txt) - 1) * gap

        y_base = max(margin, min(ih - total_h - margin,
                                 int(ih * self._sub_pos_y / 100) - total_h))
        y_base += y_offset

        sfill_base = h_rgb if bg == "Неон" else (0, 0, 0)
        sfill      = _fade(sfill_base)

        # Background box
        if bg == "Тёмный фон":
            max_lw = max(_sw(l) for l in lines_txt)
            draw.rectangle([blk_l - 10, y_base - 8,
                            blk_l + max_lw + 10, y_base + total_h + 8],
                           fill=(0, 0, 0))

        # Map words → lines for karaoke
        seg_words = seg.get("words", [])
        word_cur  = 0
        lines_wds: list[list[tuple]] = []
        for lt in lines_txt:
            lws = lt.split()
            ld: list[tuple] = []
            for lw in lws:
                if word_cur < len(seg_words):
                    wd = seg_words[word_cur]
                    ld.append((lw, wd["start"], wd["end"]))
                    word_cur += 1
                else:
                    ld.append((lw, 0.0, 0.0))
            lines_wds.append(ld)

        # ── Render each line ─────────────────────────────────────────
        for i, (lt, ld) in enumerate(zip(lines_txt, lines_wds)):
            ly = y_base + i * (line_h + gap)
            lw = _sw(lt)
            # center within block
            lx = blk_l + max(0, (blk_w - lw) // 2)

            if smode == "hard":
                sd = max(3, int(outpx * 1.5) + 3)
                _puts(lx + sd, ly + sd, lt, _fade((0, 0, 0)))
            elif smode == "3d":
                depth = max(3, fsize // 9)
                for d in range(depth, 0, -1):
                    g = min(255, int((25 + d * 14) * fade_mul))
                    _puts(lx + d, ly + d, lt, (g, g, g))
            elif smode == "glitch":
                _puts(lx - 5, ly + 2, lt, _fade((255, 20, 60)))
                _puts(lx + 5, ly - 2, lt, _fade((0, 210, 255)))

            if bg == "Неон" and outpx > 0:
                for r in range(outpx + 6, 0, -1):
                    f = max(0, 160 - r * 18)
                    gl = _fade(tuple(min(255, int(c * f // 160))
                                     for c in self._hex_to_rgb(self._hl_color)))
                    if any(gl):
                        _puts(lx, ly, lt, gl, stroke=r, sfill=gl)
            elif outpx > 0:
                _puts(lx, ly, lt, sfill, stroke=outpx, sfill=sfill)

            if self._karaoke_on and seg_words:
                x_cur = lx
                for (word, ws, we) in ld:
                    ww = _sw(word)
                    if current_time > we:
                        col = _fade(tuple(max(0, int(v * 0.4)) for v in
                                         self._hex_to_rgb(self._text_color)))
                    elif ws <= current_time <= we:
                        col = h_rgb
                    else:
                        col = t_rgb
                    _puts(x_cur, ly, word, col)
                    x_cur += ww + _tw(" ") + sppx
            else:
                _puts(lx, ly, lt, t_rgb)

        return img

    # ── Transcription ─────────────────────────────────────────────

    def _start_transcribe(self):
        if self._transcribing:
            if hasattr(self, "_export_log"):
                self._log_export("⚠  Транскрипция уже выполняется, подождите…")
            return
        # Accept path from prepare-tab entry OR from already-loaded video
        path = self._vid_entry.get().strip() or self._sub_video
        if not path or not os.path.exists(path):
            self._log_sub("⚠  Выберите видеофайл в разделе «Подготовка».")
            if hasattr(self, "_export_log"):
                self._log_export("⚠  Сначала загрузите видео в разделе «Подготовка».")
            return
        self._sub_video = path
        if self._sub_dur == 0:
            self._load_video_info(path)
        if not self._cap and HAS_CV2:
            self._open_video_capture(path)
        self._transcribing = True
        self._transcribe_cancel = False
        self._words = []
        self._segments = []
        self._trans_btn.configure(state="disabled", text="⏳ …")
        self._trans_cancel_btn.configure(state="normal")
        self._trans_cancel_btn.grid()
        if hasattr(self, "_retrans_btn"):
            self._retrans_btn.configure(state="disabled", text="⏳ …")
        threading.Thread(target=self._transcribe_worker, daemon=True).start()

    def _download_model_with_progress(self, model_name: str):
        if self._is_model_cached(model_name):
            return  # Already on disk — whisper.load_model will find it
        try:
            import whisper as _w
            urls = _w._MODELS if hasattr(_w, "_MODELS") else {}
        except Exception:
            return
        url = urls.get(model_name)
        if not url:
            return
        os.makedirs(WHISPER_CACHE_DIR, exist_ok=True)
        dest = os.path.join(WHISPER_CACHE_DIR, url.split("/")[-1])
        if os.path.exists(dest):
            return
        self.after(0, self._log_sub, f"⬇  Скачиваю модель {model_name}…")
        last_pct = [-1]

        def reporthook(block_num, block_size, total_size):
            if self._transcribe_cancel:
                raise InterruptedError("cancelled")
            if total_size <= 0:
                return
            done = block_num * block_size
            pct  = min(100, int(done / total_size * 100))
            if pct // 10 != last_pct[0] // 10:
                last_pct[0] = pct
                self.after(0, self._log_sub,
                           f"   {pct}%  {done/1_048_576:.0f} / {total_size/1_048_576:.0f} MB")

        try:
            urllib.request.urlretrieve(url, dest, reporthook)
            self.after(0, self._log_sub, f"✓  Модель {model_name} скачана")
            self.after(0, self._refresh_model_status)
        except InterruptedError:
            self.after(0, self._log_sub, "⚠  Скачивание отменено.")
            if os.path.exists(dest):
                os.remove(dest)
        except Exception as e:
            self.after(0, self._log_sub, f"✗  Ошибка скачивания: {e}")
            if os.path.exists(dest):
                os.remove(dest)

    def _transcribe_worker(self):
        try:
            import sys as _sys, io, whisper

            # PyInstaller windowed: stdout/stderr are None
            if _sys.stdout is None:
                _sys.stdout = io.TextIOWrapper(open(os.devnull, "wb"))
            if _sys.stderr is None:
                _sys.stderr = io.TextIOWrapper(open(os.devnull, "wb"))

            # Patch whisper assets path when running from PyInstaller bundle
            if getattr(_sys, "frozen", False) and hasattr(_sys, "_MEIPASS"):
                assets_dir = os.path.join(_sys._MEIPASS, "whisper", "assets")
                if os.path.isdir(assets_dir):
                    whisper.audio.__file__ = os.path.join(
                        _sys._MEIPASS, "whisper", "audio.py")

            model_name = WHISPER_MODELS[self._model_var.get()]
            lang       = LANGUAGES[self._lang_var.get()]

            if model_name not in self._whisper_cache:
                if not self._is_model_cached(model_name):
                    # First-ever launch — need to download from internet
                    self._download_model_with_progress(model_name)
                    if self._transcribe_cancel:
                        return
                # Load from disk into RAM (once per session, ~15-30 sec)
                self.after(0, self._log_sub,
                           "◎  Загружаю модель в RAM… (один раз за сессию, ~15–30 сек)")
                self._whisper_cache[model_name] = whisper.load_model(model_name)
                self.after(0, self._log_sub, "✓  Модель готова")
                self.after(0, self._refresh_model_status)

            if self._transcribe_cancel:
                return
            model = self._whisper_cache[model_name]
            self.after(0, self._log_sub, "◎  Распознаю речь…")
            result = model.transcribe(
                self._sub_video, language=lang,
                word_timestamps=True, verbose=False,
                condition_on_previous_text=False,  # снижает галлюцинации
                no_speech_threshold=0.7,           # фильтр тишины
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
            )

            words = []
            for seg in result["segments"]:
                if seg.get("no_speech_prob", 0) > 0.7:
                    continue
                text = seg["text"].strip()
                if _BRACKETS_RE.match(text) or _HALLUCINATION_RE.search(text):
                    continue
                if seg.get("words"):
                    for w in seg["words"]:
                        wt = w["word"].strip()
                        if wt and not _HALLUCINATION_RE.search(wt):
                            words.append((w["word"], float(w["start"]), float(w["end"])))
                else:
                    words.append((text, seg["start"], seg["end"]))

            self._words = words
            self._segments = self._words_to_segments()
            self.after(0, self._log_sub, f"✓  Готово: {len(words)} слов распознано")
            self.after(0, self._on_transcription_done)

            # Free model from RAM immediately — Vulkan / export need the memory
            try:
                import gc, torch
                self._whisper_cache.pop(model_name, None)
                gc.collect()
                torch.cuda.empty_cache()
            except Exception:
                self._whisper_cache.pop(model_name, None)
            self.after(0, self._log_sub, "◎  Модель выгружена из RAM")
            self.after(0, self._refresh_model_status)

        except Exception as e:
            self.after(0, self._log_sub, f"✗  {e}")
        finally:
            self._transcribing = False
            self.after(0, self._trans_btn.configure,
                       {"state": "normal", "text": "◎  Транскрибировать"})
            self.after(0, self._trans_cancel_btn.grid_remove)
            if hasattr(self, "_retrans_btn"):
                self.after(0, self._retrans_btn.configure,
                           {"state": "normal", "text": "◎ Транскрибировать"})

    def _on_transcription_done(self):
        dur = self._sub_dur
        # Init trim sliders
        self._trim_start = 0.0
        self._trim_end   = dur
        self._trim_s_slider.configure(to=max(dur, 1))
        self._trim_e_slider.configure(to=max(dur, 1))
        self._trim_s_slider.set(0)
        self._trim_e_slider.set(dur)
        self._trim_s_lbl.configure(text="0:00")
        self._trim_e_lbl.configure(text=self._fmt(dur))
        self._trim_dur_lbl.configure(text=f"Длина: {self._fmt(dur)}")
        # Show "open editor" button and auto-switch
        self._open_editor_btn.grid()
        self._tabs.set(TAB_EDIT)
        self._show_frame_at(0.0)
        self._refresh_subtitle_list()

    def _open_editor(self):
        self._tabs.set(TAB_EDIT)

    # ── Playback ──────────────────────────────────────────────────

    def _toggle_play(self):
        if not self._cap:
            return
        self._playing = not self._playing
        if self._playing:
            self._play_wall = time.perf_counter() - self._play_time
            self._play_btn.configure(text="⏸  Пауза")
            if HAS_PYGAME and self._audio_ready:
                try:
                    pygame.mixer.music.play(start=self._play_time)
                except Exception:
                    pass
            self._play_tick()
        else:
            self._play_btn.configure(text="▶  Играть")
            if HAS_PYGAME and self._audio_ready:
                try:
                    pygame.mixer.music.pause()
                except Exception:
                    pass

    def _play_tick(self):
        if not self._playing:
            return
        elapsed = time.perf_counter() - self._play_wall
        max_t = self._sub_dur or 9999
        if elapsed >= max_t:
            self._playing = False
            self._play_btn.configure(text="▶  Играть")
            return
        self._play_time = elapsed
        self._scrubber.set(elapsed)
        self._time_lbl.configure(
            text=f"{self._fmt(elapsed)} / {self._fmt(max_t)}")
        if self._cap and HAS_CV2 and HAS_PIL:
            target = int(elapsed * self._vid_fps)
            current = int(self._cap.get(cv2.CAP_PROP_POS_FRAMES))
            # Sequential read is ~10x faster than random seek.
            # Only seek if we're more than 3 frames out of sync.
            if abs(target - current) > 3:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, target)
            ret, frame = self._cap.read()
            if ret:
                self._display_frame_fast(frame, elapsed)
        interval = max(16, int(1000 / self._vid_fps))
        self.after(interval, self._play_tick)

    def _on_scrubber(self, val):
        self._play_time = float(val)
        self._play_wall = time.perf_counter() - self._play_time
        self._time_lbl.configure(
            text=f"{self._fmt(float(val))} / {self._fmt(self._sub_dur or 1)}")
        self._show_frame_at(float(val))
        if HAS_PYGAME and self._audio_ready and self._playing:
            try:
                pygame.mixer.music.play(start=float(val))
            except Exception:
                pass

    # ── Export ────────────────────────────────────────────────────

    # ── AI Upscale ────────────────────────────────────────────────

    def _start_upscale(self):
        if not self._sub_video or not os.path.exists(self._sub_video):
            self._log_export("⚠  Загрузите видео в разделе «Подготовка».")
            return
        self._upscale_btn.configure(state="disabled", text="⏳ …")
        self._export_btn.configure(state="disabled")
        threading.Thread(target=self._upscale_worker, daemon=True).start()

    def _ensure_realesrgan(self) -> bool:
        if os.path.exists(REALESRGAN_EXE):
            return True
        os.makedirs(REALESRGAN_DIR, exist_ok=True)
        self.after(0, self._log_export,
                   "⬇  Скачиваю Real-ESRGAN (~16 MB)… (один раз)")
        zip_path = os.path.join(REALESRGAN_DIR, "realesrgan.zip")
        last_pct = [-1]

        def hook(b, bs, tot):
            if tot > 0:
                pct = min(100, int(b * bs / tot * 100))
                if pct // 10 != last_pct[0] // 10:
                    last_pct[0] = pct
                    self.after(0, self._log_export,
                               f"   {pct}%  {b*bs/1_048_576:.1f} / "
                               f"{tot/1_048_576:.1f} MB")

        try:
            urllib.request.urlretrieve(REALESRGAN_URL, zip_path, hook)
        except Exception as e:
            self.after(0, self._log_export, f"✗  Ошибка скачивания: {e}")
            return False

        import zipfile
        self.after(0, self._log_export, "◎  Распаковываю…")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(REALESRGAN_DIR)
        os.remove(zip_path)
        return os.path.exists(REALESRGAN_EXE)

    def _upscale_worker(self):
        import tempfile, shutil
        tmp = None
        try:
            if not self._ensure_realesrgan():
                self.after(0, self._log_export, "✗  Real-ESRGAN не найден.")
                return

            tmp        = tempfile.mkdtemp(prefix="realesrgan_")
            frames_in  = os.path.join(tmp, "in")
            frames_out = os.path.join(tmp, "out")
            os.makedirs(frames_in)
            os.makedirs(frames_out)

            # ── Фаза 1: Извлечение кадров ────────────────────────────
            self.after(0, self._log_export, "◎  Фаза 1/3: извлечение кадров…")
            self.after(0, self._upscale_btn.configure, {"text": "✨ 1/3 Кадры…"})
            total_frames = max(1, int(self._sub_dur * self._vid_fps))

            proc = subprocess.Popen(
                ["ffmpeg", "-y", "-i", self._sub_video,
                 os.path.join(frames_in, "%08d.png")],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace")
            last_ex_pct = [-1]
            for line in proc.stdout:
                if "frame=" in line:
                    try:
                        fn = int(line.split("frame=")[1].split()[0])
                        pct = min(100, int(fn / total_frames * 100))
                        if pct // 5 != last_ex_pct[0] // 5:
                            last_ex_pct[0] = pct
                            self.after(0, self._log_export,
                                       f"   Извлечение: {pct}%  ({fn} / ~{total_frames})")
                            self.after(0, self._upscale_btn.configure,
                                       {"text": f"✨ 1/3 {pct}%"})
                    except (ValueError, IndexError):
                        pass
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError("FFmpeg: ошибка извлечения кадров")

            n = len(os.listdir(frames_in))
            self.after(0, self._log_export,
                       f"✨  Фаза 2/3: апскейл {n} кадров через Real-ESRGAN… "
                       f"(GPU, ~{max(1,n//30)}–{max(1,n//15)} мин)")
            self.after(0, self._upscale_btn.configure, {"text": "✨ 2/3 Старт…"})

            # ── Фаза 2: AI Апскейл ───────────────────────────────────
            # NOTE: ESRGAN outputs 0→100% PER FRAME, so parsing its stdout
            # gives cycling percentages. Instead, count output files for
            # true overall progress (monotonic, accurate).
            self.after(0, self._upscale_btn.configure, {"text": "✨ 2/3 GPU init…"})

            proc = subprocess.Popen(
                [REALESRGAN_EXE,
                 "-i", frames_in,
                 "-o", frames_out,
                 "-n", "realesrgan-x4plus",
                 "-s", "2",
                 "-f", "png"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace")

            # Drain stdout in background to prevent pipe deadlock; keep for errors
            all_output = []
            def _drain():
                for raw in proc.stdout:
                    for part in raw.replace('\r', '\n').split('\n'):
                        s = part.strip()
                        if s:
                            all_output.append(s)
            drain_t = threading.Thread(target=_drain, daemon=True)
            drain_t.start()

            # Poll output directory every 2 s — gives monotonic frame progress
            zero_ticks = 0
            last_pct   = -1
            while proc.poll() is None:
                try:
                    done = len([f for f in os.listdir(frames_out)
                                if f.endswith('.png')])
                    if done == 0:
                        zero_ticks += 1
                        if zero_ticks == 3:   # ~6 s without output → GPU init
                            self.after(0, self._log_export,
                                       "   ◎ Инициализация GPU / компиляция шейдеров…")
                    else:
                        pct = min(99, int(done / max(1, n) * 100))
                        if pct != last_pct:
                            last_pct = pct
                            self.after(0, self._log_export,
                                       f"   Кадр {done} / {n}  ({pct}%)")
                            self.after(0, self._upscale_btn.configure,
                                       {"text": f"✨ 2/3 {pct}%"})
                except Exception:
                    pass
                time.sleep(2)

            drain_t.join(timeout=5)
            proc.wait()

            if proc.returncode != 0:
                for ln in all_output[-5:]:
                    self.after(0, self._log_export, f"   ↳ {ln[:100]}")
                self.after(0, self._log_export,
                           f"✗  Real-ESRGAN завершился с ошибкой (код {proc.returncode}).")
                return
            self.after(0, self._log_export,
                       f"✓  Апскейл завершён: все {n} кадров обработаны")

            # ── Фаза 3: Сборка видео ─────────────────────────────────
            base  = self._sanitize(
                os.path.splitext(os.path.basename(self._sub_video))[0])
            out   = os.path.join(self._sub_out_dir, base + "_upscaled.mp4")
            n_out = len(os.listdir(frames_out))
            self.after(0, self._log_export, f"◎  Фаза 3/3: сборка {n_out} кадров в видео…")
            self.after(0, self._upscale_btn.configure, {"text": "✨ 3/3 Сборка…"})

            proc = subprocess.Popen(
                ["ffmpeg", "-y",
                 "-framerate", str(self._vid_fps),
                 "-i", os.path.join(frames_out, "%08d.png"),
                 "-i", self._sub_video,
                 "-map", "0:v", "-map", "1:a?",
                 "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                 "-c:a", "copy", out],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace")

            last_asm_pct = [-1]
            for line in proc.stdout:
                if "frame=" in line:
                    try:
                        fn = int(line.split("frame=")[1].split()[0])
                        pct = min(100, int(fn / max(1, n_out) * 100))
                        if pct // 10 != last_asm_pct[0] // 10:
                            last_asm_pct[0] = pct
                            self.after(0, self._log_export, f"   Сборка: {pct}%")
                            self.after(0, self._upscale_btn.configure,
                                       {"text": f"✨ 3/3 {pct}%"})
                    except (ValueError, IndexError):
                        pass
            proc.wait()

            if proc.returncode == 0:
                self.after(0, self._log_export, f"✓  Готово: {out}")
                self.after(0, self._on_upscale_done, out)
            else:
                self.after(0, self._log_export, "✗  FFmpeg: ошибка сборки видео")

        except Exception as e:
            self.after(0, self._log_export, f"✗  {e}")
        finally:
            if tmp:
                shutil.rmtree(tmp, ignore_errors=True)
            self.after(0, self._upscale_btn.configure,
                       {"state": "normal", "text": "✨ AI Апскейл"})
            self.after(0, self._export_btn.configure, {"state": "normal"})

    def _on_upscale_done(self, path: str):
        """Switch to the upscaled video as source."""
        self._sub_video = path
        self._load_video_info(path)
        self._open_video_capture(path)
        self._log_export("◎  Видео в редакторе обновлено — это уже апскейл версия.")

    def _start_export(self):
        if not self._sub_video or not os.path.exists(self._sub_video):
            self._log_export("⚠  Видеофайл не найден.")
            return
        if not self._words:
            self._log_export("⚠  Сначала транскрибируйте видео.")
            return
        self._export_btn.configure(state="disabled", text="⏳ …")
        threading.Thread(target=self._export_worker, daemon=True).start()

    def _export_worker(self):
        try:
            t_start = self._trim_start
            t_end   = self._trim_end if self._trim_end > t_start else self._sub_dur
            use_trim = t_start > 0.01 or (t_end < self._sub_dur - 0.01 and t_end > 0)

            # Build ASS with timestamps shifted to trim start
            segs = [s for s in self._segments
                    if s["end"] > t_start and s["start"] < t_end]
            base     = self._sanitize(os.path.splitext(os.path.basename(self._sub_video))[0])
            ass_path = os.path.join(self._sub_out_dir, base + ".ass")
            with open(ass_path, "w", encoding="utf-8") as f:
                f.write(self._make_ass(segs, time_offset=t_start if use_trim else 0.0))

            out = os.path.join(self._sub_out_dir, base + "_subtitled.mp4")
            safe = ass_path.replace("\\", "/").replace(":", "\\:")
            if self._dual_font and os.path.isdir(SCRIPT_FONT_DIR):
                safe_fd = SCRIPT_FONT_DIR.replace("\\", "/").replace(":", "\\:")
                vf_ass  = f"ass='{safe}'\\:fontsdir='{safe_fd}'"
            else:
                vf_ass = f"ass='{safe}'"

            self.after(0, self._log_export, "◎  Вжигаю субтитры…")

            if use_trim:
                cmd = ["ffmpeg", "-y",
                       "-ss", str(t_start), "-to", str(t_end),
                       "-i", self._sub_video,
                       "-vf", vf_ass, "-c:a", "copy", out]
            else:
                cmd = ["ffmpeg", "-y", "-i", self._sub_video,
                       "-vf", vf_ass, "-c:a", "copy", out]

            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                self.after(0, self._log_export, f"✓  Готово: {out}")
            else:
                self.after(0, self._log_export, f"✗  FFmpeg: {r.stderr[-300:]}")
        except Exception as e:
            self.after(0, self._log_export, f"✗  {e}")
        finally:
            self.after(0, self._export_btn.configure,
                       {"state": "normal", "text": "💾  Export"})

    def _words_to_segments(self):
        segs, buf, s0 = [], [], None
        for word, ts, te in self._words:
            if s0 is None:
                s0 = ts
            buf.append({"word": word, "start": ts, "end": te})
            if te - s0 > 4 or word.rstrip().endswith((".", "?", "!", "…")):
                segs.append({"start": s0, "end": te,
                             "text": "".join(w["word"] for w in buf).strip(),
                             "words": list(buf)})
                buf, s0 = [], None
        if buf:
            segs.append({"start": s0, "end": buf[-1]["end"],
                         "text": "".join(w["word"] for w in buf).strip(),
                         "words": list(buf)})
        return segs

    def _make_ass(self, segments, time_offset: float = 0.0) -> str:
        bg        = BG_STYLES_ASS[self._bg_style.get()]
        primary   = self._hex_to_ass(self._hl_color)
        secondary = self._hex_to_ass(self._text_color)
        outline_w = max(bg["outw"], self._outline_width)
        # MarginV for \an2 (bottom-center): distance from bottom edge
        margin_v  = max(10, int(1080 * (1.0 - self._sub_pos_y / 100.0)))
        sl = (f"Style: Default,{self._font_family},{self._font_size},"
              f"{primary},{secondary},&H00000000,{bg['back']},"
              f"-1,0,0,0,100,100,{self._letter_spacing},0,{bg['borderstyle']},"
              f"{outline_w},{bg['shadow']},2,10,10,{margin_v},1")
        hdr = ("[Script Info]\nScriptType: v4.00+\nTimer: 100.0000\n"
               "PlayResX: 1920\nPlayResY: 1080\n\n"
               "[V4+ Styles]\n"
               "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
               "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
               "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
               f"Alignment, MarginL, MarginR, MarginV, Encoding\n{sl}\n\n"
               "[Events]\nFormat: Layer, Start, End, Style, Name, "
               "MarginL, MarginR, MarginV, Effect, Text\n")

        # Per-dialogue override tags
        ov = ""
        if self._shadow_mode == "hard":
            ov += "\\shad5"
        elif self._shadow_mode == "3d":
            ov += "\\shad8"
        elif self._shadow_mode in ("none", "glitch"):
            ov += "\\shad0"
        if self._shadow_mode == "glitch":
            ov += "\\1c&H3C14FF&\\3c&H00000000&"
        ov_tag = "{" + ov + "}" if ov else ""

        # Position anchor mapped to 1920×1080 ASS space
        x_ass  = max(50, int(1920 * getattr(self, "_sub_pos_x", 50) / 100))
        y_ass  = max(50, int(1080 * self._sub_pos_y / 100))
        anim   = getattr(self, "_anim_mode", "Нет")

        def _pos_tag():
            parts = ["\\an2"]
            if anim == "Слайд вверх":
                parts.append(f"\\move({x_ass},{y_ass+120},{x_ass},{y_ass},0,400)")
            elif anim == "Масштаб":
                parts.append(f"\\pos({x_ass},{y_ass})\\fscx30\\fscy30")
                parts.append("\\t(0,400,\\fscx100\\fscy100)")
            elif anim == "Появление":
                parts.append(f"\\pos({x_ass},{y_ass})\\fad(350,250)")
            else:
                parts.append(f"\\pos({x_ass},{y_ass})")
            return "{" + "".join(parts) + "}"

        evts = []
        for seg in segments:
            s = max(0.0, seg["start"] - time_offset)
            e = max(0.0, seg["end"]   - time_offset)
            if e <= 0:
                continue
            if self._dual_font and "\n" in seg.get("text", ""):
                parts = seg["text"].split("\n", 1)
                l1 = parts[0].strip().upper()
                l2 = parts[1].strip() if len(parts) > 1 else ""
                fs1 = max(8, int(self._font_size * 0.62))
                c1  = self._hex_to_ass(self._text_color)
                c2  = self._hex_to_ass(self._hl_color)
                body = (f"{{\\fn{self._font_family}\\fs{fs1}\\c{c1}\\b1}}{l1}"
                        f"\\N{{\\fnMarck Script\\fs{self._font_size}\\c{c2}\\b0}}{l2}")
            elif self._karaoke_on and seg.get("words"):
                body = "".join(
                    f"{{\\k{int((w['end']-w['start'])*100)}}}{w['word']}"
                    for w in seg["words"])
            else:
                body = seg["text"]
            evts.append(
                f"Dialogue: 0,{self._ts_ass(s)},{self._ts_ass(e)},"
                f"Default,,0,0,0,,{_pos_tag()}{ov_tag}{body}")
        return hdr + "\n".join(evts)

    # ── Block width / dual-font ──────────────────────────────────

    def _on_block_width(self, val):
        self._sub_block_w = int(val)
        self._block_w_lbl.configure(text=f"{self._sub_block_w}%")
        if self._cap:
            self._show_frame_at(self._play_time)

    def _toggle_dual_font(self):
        self._dual_font = self._dual_font_switch.get() == 1
        if self._dual_font:
            threading.Thread(target=self._ensure_script_font, daemon=True).start()
        if self._cap:
            self._show_frame_at(self._play_time)

    def _download_google_font(self, name: str):
        url, fname = DOWNLOADABLE_FONTS[name]
        cache_path = os.path.join(SCRIPT_FONT_DIR, fname)
        if os.path.exists(cache_path):
            if self._cap:
                self.after(0, lambda: self._show_frame_at(self._play_time))
            return
        try:
            import urllib.request
            os.makedirs(SCRIPT_FONT_DIR, exist_ok=True)
            self.after(0, self._log_sub, f"◎  Скачиваю шрифт {name}…")
            urllib.request.urlretrieve(url, cache_path)
            self.after(0, self._log_sub, f"✓  Шрифт {name} готов")
            if self._cap:
                self.after(0, lambda: self._show_frame_at(self._play_time))
        except Exception as e:
            self.after(0, self._log_sub, f"⚠  Не удалось скачать {name}: {e}")

    def _ensure_script_font(self) -> str | None:
        if os.path.exists(SCRIPT_FONT_PATH):
            return SCRIPT_FONT_PATH
        try:
            import urllib.request
            os.makedirs(SCRIPT_FONT_DIR, exist_ok=True)
            self.after(0, self._log_sub, "◎  Скачиваю шрифт Marck Script (~120 КБ)…")
            urllib.request.urlretrieve(SCRIPT_FONT_URL, SCRIPT_FONT_PATH)
            self.after(0, self._log_sub, "✓  Шрифт Marck Script сохранён")
            return SCRIPT_FONT_PATH
        except Exception as e:
            self.after(0, self._log_sub, f"⚠  Не удалось скачать шрифт: {e}")
            return None

    def _get_script_pil_font(self, size: int):
        if not HAS_PIL:
            return None
        try:
            if os.path.exists(SCRIPT_FONT_PATH):
                return ImageFont.truetype(SCRIPT_FONT_PATH, size)
        except Exception:
            pass
        return self._get_pil_font(size)

    def _render_dual_font_pil(self, img, seg: dict, current_time: float):
        """Cinematic two-line rendering: small uppercase header + large script body."""
        parts = seg["text"].split("\n", 1)
        line1 = parts[0].strip().upper()
        line2 = parts[1].strip() if len(parts) > 1 else ""

        iw, ih = img.size
        scale   = iw / 640

        # Animation fade/slide
        seg_dur = max(0.001, seg["end"] - seg["start"])
        t_rel   = max(0.0, current_time - seg["start"])
        t_left  = max(0.0, seg["end"] - current_time)
        anim    = getattr(self, "_anim_mode", "Нет")
        fade_mul = 1.0
        y_offset = 0
        if anim == "Появление":
            fade_mul = min(min(1.0, t_rel / min(0.35, seg_dur * 0.3)),
                           min(1.0, t_left / min(0.25, seg_dur * 0.25)))
        elif anim == "Слайд вверх":
            slide    = min(1.0, t_rel / min(0.4, seg_dur * 0.35))
            y_offset = int(55 * scale * (1.0 - slide))

        def _fade(rgb):
            return rgb if fade_mul >= 1.0 else tuple(max(0, int(c * fade_mul)) for c in rgb)

        draw   = ImageDraw.Draw(img)
        margin = max(12, int(20 * scale))
        outpx  = max(0, int(self._outline_width * scale))

        # Fonts
        fsize1 = max(8,  int(self._font_size * scale * 0.62))
        fsize2 = max(10, int(self._font_size * scale * 1.35))
        font1  = self._get_pil_font(fsize1)
        font2  = self._get_script_pil_font(fsize2) or font1

        c1 = _fade(self._hex_to_rgb(self._text_color))
        c2 = _fade(self._hex_to_rgb(self._hl_color))

        def _meas(f, t):
            bb = draw.textbbox((0, 0), t, font=f)
            return max(1, bb[2] - bb[0]), max(1, bb[3] - bb[1])

        w1, h1 = (_meas(font1, line1) if line1 else (0, 0))
        w2, h2 = (_meas(font2, line2) if line2 else (0, 0))
        gap    = max(2, int(6 * scale))

        total_h = (h1 if line1 else 0) + (gap if line1 and line2 else 0) + (h2 if line2 else 0)

        blk_pct = getattr(self, "_sub_block_w", 80)
        blk_px  = max(80, int(iw * blk_pct / 100))
        blk_cx  = int(iw * getattr(self, "_sub_pos_x", 50) / 100)
        blk_l   = max(margin, blk_cx - blk_px // 2)
        blk_r   = min(iw - margin, blk_l + blk_px)
        blk_w   = max(80, blk_r - blk_l)

        y_base = max(margin, min(ih - total_h - margin,
                                 int(ih * self._sub_pos_y / 100) - total_h))
        y_base += y_offset

        def _draw(f, x, y, text, color):
            if outpx > 0:
                try:
                    draw.text((x, y), text, font=f, fill=(0, 0, 0),
                              stroke_width=outpx, stroke_fill=(0, 0, 0))
                except Exception:
                    pass
            draw.text((x, y), text, font=f, fill=color)

        if line1:
            x1 = blk_l + max(0, (blk_w - w1) // 2)
            _draw(font1, x1, y_base, line1, c1)

        if line2:
            y2 = y_base + (h1 + gap if line1 else 0)
            x2 = blk_l + max(0, (blk_w - w2) // 2)
            _draw(font2, x2, y2, line2, c2)

        return img

    # ── Subtitle text editor ──────────────────────────────────────

    def _build_sub_editor_card(self, parent):
        p = self._p
        card = Card(parent, p)
        card.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=14, pady=(8, 4), sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)
        Lbl(hdr, "  Текст субтитров", p, 11, "bold", dim=True, anchor="w").grid(
            row=0, column=0, sticky="w")
        Lbl(hdr, "Кликните на время чтобы перейти к нужному моменту",
            p, 10, dim=True, anchor="e").grid(row=0, column=1, padx=(8, 0), sticky="e")

        self._seg_scroll = ctk.CTkScrollableFrame(
            card, height=140,
            fg_color=p["input_bg"],
            scrollbar_button_color=p["accent"],
            scrollbar_button_hover_color=p["accent_hover"],
            corner_radius=8)
        self._seg_scroll.grid(row=1, column=0, padx=14, pady=(0, 6), sticky="ew")
        self._seg_scroll.grid_columnconfigure(1, weight=1)

        add_row = ctk.CTkFrame(card, fg_color="transparent")
        add_row.grid(row=2, column=0, padx=14, pady=(0, 10), sticky="ew")
        add_row.grid_columnconfigure(6, weight=1)

        btn(add_row, "+ Добавить", p, self._add_segment, h=28, cr=6
            ).grid(row=0, column=0, padx=(0, 10))
        Lbl(add_row, "с", p, 10, dim=True).grid(row=0, column=1, padx=(0, 4))
        self._new_seg_start_var = ctk.StringVar(value="0:00")
        ctk.CTkEntry(add_row, textvariable=self._new_seg_start_var,
                     width=55, height=28,
                     fg_color=p["input_bg"], border_color=p["card_border"],
                     border_width=1, text_color=p["text"],
                     font=ctk.CTkFont("Consolas", 11)
                     ).grid(row=0, column=2, padx=(0, 8))
        Lbl(add_row, "до", p, 10, dim=True).grid(row=0, column=3, padx=(0, 4))
        self._new_seg_end_var = ctk.StringVar(value="0:05")
        ctk.CTkEntry(add_row, textvariable=self._new_seg_end_var,
                     width=55, height=28,
                     fg_color=p["input_bg"], border_color=p["card_border"],
                     border_width=1, text_color=p["text"],
                     font=ctk.CTkFont("Consolas", 11)
                     ).grid(row=0, column=4, padx=(0, 10))
        self._new_seg_text_var = ctk.StringVar(value="")
        ctk.CTkEntry(add_row, textvariable=self._new_seg_text_var,
                     height=28, placeholder_text="Текст нового субтитра…",
                     fg_color=p["input_bg"], border_color=p["card_border"],
                     border_width=1, text_color=p["text"],
                     font=ctk.CTkFont("Segoe UI", 11)
                     ).grid(row=0, column=6, sticky="ew")
        return card

    def _refresh_subtitle_list(self):
        if not hasattr(self, "_seg_scroll"):
            return
        p = self._p
        for w in self._seg_scroll.winfo_children():
            w.destroy()
        self._seg_vars = []

        if not self._segments:
            Lbl(self._seg_scroll,
                "  Нет субтитров. Транскрибируйте видео или добавьте вручную.",
                p, 10, dim=True, anchor="w"
                ).grid(row=0, column=0, columnspan=3, padx=8, pady=8, sticky="w")
            return

        for i, seg in enumerate(self._segments):
            time_str = f"{self._fmt(seg['start'])}–{self._fmt(seg['end'])}"
            ctk.CTkButton(
                self._seg_scroll, text=time_str,
                width=100, height=26,
                fg_color="transparent", hover_color=p["card_hover"],
                text_color=p["text_dim"],
                font=ctk.CTkFont("Consolas", 10),
                anchor="w", corner_radius=4,
                command=lambda t=seg["start"]: self._seek_to(t)
            ).grid(row=i, column=0, padx=(2, 4), pady=1)

            var = ctk.StringVar(value=seg["text"])
            ctk.CTkEntry(
                self._seg_scroll, textvariable=var,
                height=26,
                fg_color=p["card"], border_color=p["card_border"],
                border_width=1, text_color=p["text"],
                font=ctk.CTkFont("Segoe UI", 11)
            ).grid(row=i, column=1, padx=(0, 4), pady=1, sticky="ew")
            var.trace_add("write",
                          lambda *_, idx=i, v=var: self._on_seg_text_changed(idx, v))
            self._seg_vars.append(var)

            ctk.CTkButton(
                self._seg_scroll, text="✕",
                width=26, height=26,
                fg_color="transparent", hover_color="#7f1d1d",
                text_color=p["text_dim"],
                corner_radius=4,
                command=lambda idx=i: self._delete_segment(idx)
            ).grid(row=i, column=2, padx=(0, 2), pady=1)

    def _on_seg_text_changed(self, i, var):
        if i < len(self._segments):
            self._segments[i]["text"] = var.get()
            self._segments[i]["words"] = []

    def _delete_segment(self, i):
        if i < len(self._segments):
            self._segments.pop(i)
            self._refresh_subtitle_list()
            if self._cap:
                self._show_frame_at(self._play_time)

    def _add_segment(self):
        start = self._parse_time(self._new_seg_start_var.get())
        end   = self._parse_time(self._new_seg_end_var.get())
        text  = self._new_seg_text_var.get().strip()
        if end <= start or not text:
            return
        new_seg = {"start": start, "end": end, "text": text, "words": []}
        ins = len(self._segments)
        for i, seg in enumerate(self._segments):
            if seg["start"] > start:
                ins = i
                break
        self._segments.insert(ins, new_seg)
        self._refresh_subtitle_list()
        self._new_seg_start_var.set(self._fmt(end))
        self._new_seg_end_var.set(self._fmt(end + 5))
        self._new_seg_text_var.set("")
        if self._cap:
            self._show_frame_at(self._play_time)

    def _seek_to(self, t: float):
        if not self._cap:
            return
        t = max(0.0, min(t, self._sub_dur))
        self._play_time = t
        self._play_wall = time.perf_counter() - t
        self._scrubber.set(t)
        self._time_lbl.configure(
            text=f"{self._fmt(t)} / {self._fmt(self._sub_dur or 1)}")
        self._show_frame_at(t)

    def _parse_time(self, s: str) -> float:
        try:
            parts = s.strip().split(":")
            if len(parts) == 1:
                return float(parts[0])
            if len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        except Exception:
            return 0.0

    @staticmethod
    def _sanitize(name: str) -> str:
        return "".join(c if c.isalnum() or c in " ._-" else "_" for c in name)[:60]


if __name__ == "__main__":
    app = App()
    app.mainloop()
