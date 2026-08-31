import os
import json
import time
import threading
import cv2
import numpy as np
import pyautogui
import customtkinter as ctk
import win32gui
import win32api
import win32con
import keyboard
import shutil
import sys

BG_COLOR = "#141620"
CARD_COLOR = "#1c1f2b"
PRIMARY = "#5b9dff"
PRIMARY_HOVER = "#74acff"
DANGER = "#ff7a6b"
DANGER_HOVER = "#ff9a8c"
TEXT_MAIN = "#eef1f7"
TEXT_SUB = "#7f889f"
CORNER_RADIUS = 8

FONT_MAIN = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 15, "bold")
FONT_SUB = ("Segoe UI", 9)

def resource_path(n):
    if getattr(sys, 'frozen', False):
        m = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        b = os.path.join(m, n)
        if os.path.exists(b): return b
        return os.path.join(os.path.dirname(sys.executable), n)
    return n

if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
fl_cfg = "phantom_config.json"

STRINGS = {
    "en": {
        "t": "sv.autoclick", "s": "SNIP", "i": "IMPORT", "f7": "RUN ({k})", "f8": "HALT ({k})", "tb": "TARGET_DB", 
        "sb": "SYS: STANDBY", "ac": "SYS: ACTIVE", "p": "Settings", "ec": "System Configuration", "im": "Input Protocol:",
        "act": "Action:", "sen": "Sensitivity: {v:.2f}", "cd": "Cooldown: {v:.1f}s", 
        "hw": "Vision Debug", "rsr": "Set Scan Region", "rrc": "Reset Region",
        "lang": "Language:", "help": "Docs", "h_title": "sv.autoclick - Manual",
        "h_snip": "• SNIP\n  Captures a region of your screen to use as a target.",
        "h_import": "• IMPORT\n  Loads existing images (.png, .jpg) into target db.",
        "h_f7": "• RUN\n  Begins the autonomous scanning engine.",
        "h_f8": "• HALT\n  Halts the engine immediately.",
        "h_bank": "• TARGET_DB\n  Toggle switches to enable/disable targets.",
        "h_click": "• INPUT PROTOCOL\n  'physical' moves the real cursor and clicks. 'background' sends the click straight to the chosen window, so your mouse stays free for other work.",
        "h_act": "• ACTION\n  Choose left, right, or double click.",
        "h_sens": "• SENSITIVITY\n  Higher = exact pixel match. Lower = loose recognition.",
        "h_cd": "• COOLDOWN\n  Delay between consecutive clicks on identical coordinates.",
        "h_hw": "• VISION DEBUG\n  Opens overlay showing what exactly the script sees.",
        "h_reg": "• SCAN REGION\n  Limits scanning to specific area, vastly improving FPS.",
        "stats": "CLICKS: {n} · UPTIME: {t}",
        "limit": "Click limit (0 — unlimited):",
        "hk": "Hotkeys:", "hk_start": "Start", "hk_stop": "Stop",
        "h_limit": "• CLICK LIMIT\n  Stops the engine after the given number of clicks. 0 keeps it running.",
        "h_hk": "• HOTKEYS\n  Keys that start and stop the engine. Combinations like ctrl+shift+r also work.",
        "egg": "SIGNAL INTERCEPTED: The developer of this program probably loves shrimp, hmm... Does it make sense now?"
    },
    "ru": {
        "t": "sv.autoclick", "s": "СНИМОК", "i": "ИМПОРТ", "f7": "ЗАПУСК ({k})", "f8": "СТОП ({k})", "tb": "БАЗА ЦЕЛЕЙ", 
        "sb": "СТАТУС: ОЖИДАНИЕ", "ac": "СТАТУС: АКТИВНО", "p": "Настройки", "ec": "Конфигурация", "im": "Протокол ввода:",
        "act": "Действие:", "sen": "Чувствительность: {v:.2f}", "cd": "Задержка: {v:.1f}s", 
        "hw": "Отладка зрения (Debug)", "rsr": "Задать зону сканирования", "rrc": "Сбросить зону",
        "lang": "Язык:", "help": "Справка", "h_title": "sv.autoclick - Руководство",
        "h_snip": "• СНИМОК\n  Вырезает фрагмент экрана и сохраняет как цель.",
        "h_import": "• ИМПОРТ\n  Загрузка сторонних файлов (.png, .jpg) в базу.",
        "h_f7": "• ЗАПУСК\n  Активирует ядро технического зрения.",
        "h_f8": "• СТОП\n  Экстренная остановка всех процессов.",
        "h_bank": "• БАЗА ЦЕЛЕЙ\n  Управление целями. Отключите тумблер, чтобы игнорировать файл.",
        "h_click": "• ПРОТОКОЛ ВВОДА\n  'physical' двигает настоящий курсор и кликает. 'background' отправляет клик прямо в выбранное окно, поэтому мышь остаётся свободной.",
        "h_act": "• ДЕЙСТВИЕ\n  Левый, Правый клик или Двойной.",
        "h_sens": "• ЧУВСТВИТЕЛЬНОСТЬ\n  Высокая = строгий поиск. Низкая = находит похожие пиксели.",
        "h_cd": "• ЗАДЕРЖКА\n  Перерыв между повторными кликами в ту же цель.",
        "h_hw": "• ОТЛАДКА ЗРЕНИЯ\n  Окно отладки. Показывает алгоритм распознавания CV2.",
        "h_reg": "• ЗОНА СКАНИРОВАНИЯ\n  Сужает радиус поиска, многократно повышая FPS.",
        "stats": "КЛИКОВ: {n} · В РАБОТЕ: {t}",
        "limit": "Лимит кликов (0 — без лимита):",
        "hk": "Горячие клавиши:", "hk_start": "Запуск", "hk_stop": "Стоп",
        "h_limit": "• ЛИМИТ КЛИКОВ\n  Останавливает движок после указанного числа кликов. 0 — работать без предела.",
        "h_hk": "• ГОРЯЧИЕ КЛАВИШИ\n  Клавиши запуска и остановки. Работают и сочетания вида ctrl+shift+r.",
        "egg": "ПЕРЕХВАТ СИГНАЛА: Наверное разработчик этой программы любит креветки, хмм, есть ли в этом смысл?"
    }
}

class Config:
    def __init__(self):
        import locale
        system_lang = "en"
        try:
            lc = locale.getdefaultlocale()[0]
            if lc and lc.startswith("ru"): system_lang = "ru"
        except: pass
            
        self.cfg = {
            "targets": [], "sensitivity": 0.8, "cooldown": 1.0, "action": "left_click",
            "debug": False, "click_mode": "background", "region": None, "lang": system_lang,
            "click_limit": 0, "hotkey_start": "f7", "hotkey_stop": "f8"
        }
        self.load()

    def load(self):
        if os.path.exists(fl_cfg):
            try:
                with open(fl_cfg, "r") as f:
                    self.cfg.update(json.load(f))
                t = self.cfg.get("targets", [])
                for i in range(len(t)):
                    if isinstance(t[i], str):
                        t[i] = {"path": t[i], "active": True}
                self.cfg["targets"] = t
            except: pass

    def save(self):
        try:
            with open(fl_cfg, "w") as f: json.dump(self.cfg, f, indent=4)
        except: pass

    def get(self, k): return self.cfg.get(k)
    def set_value(self, k, v):
        self.cfg[k] = v
        self.save()

class ClickEngine:
    def __init__(self, p, cb):
        self.p = p
        self.running = False
        self.cb = cb
        self.lt = 0
        self.clicks = 0
        self.started_at = 0.0

    def uptime(self):
        return time.time() - self.started_at if self.running else 0.0
        
    def start(self):
        if not self.running:
            self.running = True
            self.clicks = 0
            self.started_at = time.time()
            l = self.p.get("lang")
            if l not in STRINGS: l = "en"
            self.cb(STRINGS[l]["ac"], PRIMARY)
            threading.Thread(target=self._scan_loop, daemon=True).start()

    def stop(self):
        self.running = False
        l = self.p.get("lang")
        if l not in STRINGS: l = "en"
        self.cb(STRINGS[l]["sb"], TEXT_SUB)

    def click_on_screen(self, x, y, a):
        if a == "left_click": pyautogui.click(int(x), int(y))
        elif a == "right_click": pyautogui.click(int(x), int(y), button="right")
        elif a == "double_click": pyautogui.doubleClick(int(x), int(y))

    def click_in_window(self, x, y, a):
        ix, iy = int(x), int(y)
        try:
            h = win32gui.WindowFromPoint((ix, iy))
            if h:
                c = win32gui.ScreenToClient(h, (ix, iy))
                l = win32api.MAKELONG(c[0], c[1])
                if a == "left_click":
                    win32api.PostMessage(h, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l)
                    time.sleep(0.01)
                    win32api.PostMessage(h, win32con.WM_LBUTTONUP, 0, l)
                elif a == "right_click":
                    win32api.PostMessage(h, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, l)
                    time.sleep(0.01)
                    win32api.PostMessage(h, win32con.WM_RBUTTONUP, 0, l)
                elif a == "double_click":
                    win32api.PostMessage(h, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l)
                    time.sleep(0.01)
                    win32api.PostMessage(h, win32con.WM_LBUTTONUP, 0, l)
                    time.sleep(0.05)
                    win32api.PostMessage(h, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l)
                    time.sleep(0.01)
                    win32api.PostMessage(h, win32con.WM_LBUTTONUP, 0, l)
        except: pass

    def _scan_loop(self):
        wa = False
        while self.running:
            t = self.p.get("targets")
            if not t:
                time.sleep(0.5)
                continue

            r = self.p.get("region")
            s = self.p.get("sensitivity")
            d = self.p.get("debug")
            m = self.p.get("click_mode")
            cd = self.p.get("cooldown")
            limit = int(self.p.get("click_limit") or 0)
            ac = self.p.get("action")
            rt = tuple(r) if r else None

            try: scr = pyautogui.screenshot(region=rt)
            except:
                time.sleep(0.5)
                continue
                
            snp = np.array(scr)
            gry = cv2.cvtColor(snp, cv2.COLOR_RGB2GRAY)
            dbg = cv2.cvtColor(snp, cv2.COLOR_RGB2BGR) if d else None  

            for pt in t:
                pth = pt.get("path")
                if not pt.get("active", True) or not os.path.exists(pth): continue
                
                tm = cv2.imread(pth, 0)
                if tm is None: continue
                
                res = cv2.matchTemplate(gry, tm, cv2.TM_CCOEFF_NORMED)
                loc = np.where(res >= s)
                fnd = False
                
                for p in zip(*loc[::-1]):
                    h, w = tm.shape
                    cx_l = p[0] + w // 2
                    cy_l = p[1] + h // 2
                    
                    cx_g = cx_l + (rt[0] if rt else 0)
                    cy_g = cy_l + (rt[1] if rt else 0)
                    
                    if d:
                        cv2.rectangle(dbg, p, (p[0]+w, p[1]+h), (0, 255, 0), 2)
                        cv2.circle(dbg, (cx_l, cy_l), 5, (0, 0, 255), -1)
                        
                    if not fnd and (time.time() - self.lt) >= cd:
                        if m == "background": self.click_in_window(cx_g, cy_g, ac)
                        else: self.click_on_screen(cx_g, cy_g, ac)
                        self.lt = time.time()
                        self.clicks += 1
                        fnd = True
                        if limit and self.clicks >= limit:
                            self.stop()
                            return

            if d and dbg is not None:
                sh = dbg.shape
                sc = 800 / max(sh[0], sh[1])
                if sc < 1: dbg = cv2.resize(dbg, (int(sh[1]*sc), int(sh[0]*sc)))
                cv2.imshow("VISION DEBUG", dbg)
                cv2.waitKey(1)
                wa = True
            elif wa:
                try: cv2.destroyWindow("VISION DEBUG")
                except: pass
                wa = False
            
            time.sleep(0.1)
            
        if wa:
            try: cv2.destroyAllWindows()
            except: pass

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cfg = Config()
        self.engine = ClickEngine(self.cfg, self.set_status)
        self.title_clicks = 0
        
        self.title("sv.autoclick")
        self.geometry("450x640")
        self.configure(fg_color=BG_COLOR)
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.after(200, lambda: self.apply_icon(self))
        
        self.build_header()
        self.bind_hotkeys()
        self.refresh_labels()
        self.tick_stats()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def apply_icon(self, w):
        try:
            ico = resource_path("logo.ico")
            w.iconbitmap(ico)
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('sv.cli.term')
            hw = ctypes.windll.user32.GetParent(w.winfo_id())
            hi = ctypes.windll.user32.LoadImageW(0, ico, 1, 0, 0, 0x00000010)
            if hi:
                ctypes.windll.user32.SendMessageW(hw, 0x0080, 0, hi)
                ctypes.windll.user32.SendMessageW(hw, 0x0080, 1, hi)
        except Exception as e: pass

    def _title_click(self, ev):
        self.title_clicks += 1
        if self.title_clicks == 5:
            self.title_clicks = 0
            lg = self.cfg.get("lang")
            if lg not in STRINGS: lg = "en"
            t = ctk.CTkToplevel(self)
            t.title("???")
            t.geometry("380x120")
            t.configure(fg_color=BG_COLOR)
            t.attributes('-topmost', True)
            ctk.CTkLabel(t, text=STRINGS[lg]["egg"], font=FONT_SUB, text_color=PRIMARY, wraplength=350).pack(expand=True)

    def build_header(self):
        h_top = ctk.CTkFrame(self, fg_color="transparent")
        h_top.pack(fill="x", padx=15, pady=(20, 5))
        
        self.l_t = ctk.CTkLabel(h_top, text="", font=FONT_TITLE, text_color=TEXT_MAIN)
        self.l_t.pack(side="left")
        self.l_t.bind("<Button-1>", self._title_click)
        
        self.b_hz = ctk.CTkButton(h_top, text="?", width=32, height=32, font=FONT_MAIN, 
                                  fg_color=CARD_COLOR, hover_color="#252a38", text_color=TEXT_SUB, 
                                  command=self.open_help, corner_radius=CORNER_RADIUS)
        self.b_hz.pack(side="right", padx=(5, 0))
        
        self.b_cfg = ctk.CTkButton(h_top, text="⚙", width=32, height=32, font=("Segoe UI", 16), 
                                   fg_color=CARD_COLOR, hover_color="#252a38", text_color=TEXT_SUB, 
                                   command=self.open_settings, corner_radius=CORNER_RADIUS)
        self.b_cfg.pack(side="right")
        
        t_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        t_card.pack(fill="both", expand=True, padx=15, pady=(10, 15))
        
        t_head = ctk.CTkFrame(t_card, fg_color="transparent")
        t_head.pack(fill="x", padx=15, pady=(15, 10))
        
        self.l_tb = ctk.CTkLabel(t_head, text="", font=FONT_MAIN, text_color=TEXT_MAIN)
        self.l_tb.pack(side="left")
        
        self.b_imp = ctk.CTkButton(t_head, text="", width=60, font=("Segoe UI", 11, "bold"), fg_color="#282e3d", 
                                   hover_color="#2a2f3f", text_color=TEXT_MAIN, 
                                   command=self.import_targets, corner_radius=CORNER_RADIUS, height=28)
        self.b_imp.pack(side="right")
        
        self.b_snip = ctk.CTkButton(t_head, text="", width=60, font=("Segoe UI", 11, "bold"), fg_color=PRIMARY, 
                                    hover_color=PRIMARY_HOVER, text_color="#141620", 
                                    command=self.snip_target, corner_radius=CORNER_RADIUS, height=28)
        self.b_snip.pack(side="right", padx=(0, 5))

        self.targets_frame = ctk.CTkScrollableFrame(t_card, fg_color="transparent")
        self.targets_frame.pack(fill="both", expand=True, padx=5, pady=(0, 10))
        self.refresh_targets()
        
        a_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        a_card.pack(fill="x", padx=15, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(a_card, text="", font=FONT_SUB, text_color=TEXT_SUB)
        self.status_label.pack(pady=(15, 5))

        ab = ctk.CTkFrame(a_card, fg_color="transparent")
        ab.pack(fill="x", padx=15, pady=(5, 15))

        self.btn_start = ctk.CTkButton(ab, text="", font=("Segoe UI", 15, "bold"), fg_color=PRIMARY, 
                                  hover_color=PRIMARY_HOVER, text_color="#141620", 
                                  command=self.engine.start, corner_radius=CORNER_RADIUS, height=45)
        self.btn_start.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.btn_stop = ctk.CTkButton(ab, text="", font=("Segoe UI", 15, "bold"), fg_color="transparent", 
                                  border_color=DANGER, border_width=2, hover_color="#48242a", text_color=DANGER, 
                                  command=self.engine.stop, corner_radius=CORNER_RADIUS, height=45)
        self.btn_stop.pack(side="right", expand=True, fill="x", padx=(5, 0))

    def open_help(self):
        lg = self.cfg.get("lang")
        if lg not in STRINGS: lg = "en"
        d = STRINGS[lg]
        s = ctk.CTkToplevel(self)
        s.title(d["h_title"])
        s.geometry("550x650")
        s.configure(fg_color=BG_COLOR)
        s.attributes('-topmost', True)
        s.after(200, lambda: self.apply_icon(s))
        
        scr = ctk.CTkScrollableFrame(s, fg_color=BG_COLOR)
        scr.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(scr, text=d["h_title"], font=FONT_TITLE, text_color=PRIMARY).pack(pady=(10, 20))
        
        hi = [
            "h_snip", "h_import", "h_f7", "h_f8", "h_bank", "h_click",
            "h_act", "h_sens", "h_cd", "h_limit", "h_hk", "h_hw", "h_reg"
        ]
        
        for hk in hi:
            card = ctk.CTkFrame(scr, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(card, text=d[hk], font=FONT_SUB, text_color=TEXT_MAIN, wraplength=480, justify="left").pack(anchor="w", padx=15, pady=10)

    def refresh_labels(self):
        lg = self.cfg.get("lang")
        if lg not in STRINGS: lg = "en"
        d = STRINGS[lg]
        self.l_t.configure(text=d["t"])
        self.b_snip.configure(text=d["s"])
        self.b_imp.configure(text=d["i"])
        self.btn_start.configure(text=d["f7"].format(k=(self.cfg.get("hotkey_start") or "f7").upper()))
        self.btn_stop.configure(text=d["f8"].format(k=(self.cfg.get("hotkey_stop") or "f8").upper()))
        self.l_tb.configure(text=d["tb"])
        if not self.engine.running:
            self.status_label.configure(text=d["sb"], text_color=TEXT_SUB)
        else:
            self.status_label.configure(text=d["ac"], text_color=PRIMARY)

    def import_targets(self):
        from customtkinter import filedialog
        fs = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if fs:
            t = self.cfg.get("targets")
            for f in fs:
                nm = os.path.basename(f)
                dst = f"tgt_imp_{int(time.time())}_{nm}"
                try:
                    shutil.copy(f, dst)
                    t.append({"path": dst, "active": True})
                except: pass
            self.cfg.set_value("targets", t)
            self.refresh_targets()

    def strings(self):
        lg = self.cfg.get("lang")
        return STRINGS[lg if lg in STRINGS else "en"]

    def bind_hotkeys(self):
        try:
            keyboard.unhook_all_hotkeys()
        except (AttributeError, KeyError):
            pass
        pairs = ((self.cfg.get("hotkey_start") or "f7", self.engine.start),
                 (self.cfg.get("hotkey_stop") or "f8", self.engine.stop))
        for combo, fn in pairs:
            try:
                keyboard.add_hotkey(combo, fn)
            except ValueError:
                pass

    def tick_stats(self):
        if self.engine.running:
            secs = int(self.engine.uptime())
            self.status_label.configure(
                text=self.strings()["stats"].format(
                    n=self.engine.clicks, t=f"{secs // 60:02d}:{secs % 60:02d}"),
                text_color=PRIMARY)
        self.after(500, self.tick_stats)

    def save_limit(self, widget):
        try:
            value = max(0, int(widget.get().strip() or 0))
        except ValueError:
            value = int(self.cfg.get("click_limit") or 0)
        widget.delete(0, "end")
        widget.insert(0, str(value))
        self.cfg.set_value("click_limit", value)

    def save_hotkey(self, key, widget):
        combo = widget.get().strip().lower()
        if not combo:
            combo = "f7" if key == "hotkey_start" else "f8"
            widget.delete(0, "end")
            widget.insert(0, combo)
        self.cfg.set_value(key, combo)
        self.bind_hotkeys()
        self.refresh_labels()

    def set_status(self, t, c):
        try: self.status_label.configure(text=t, text_color=c)
        except: pass

    def open_settings(self):
        lg = self.cfg.get("lang")
        if lg not in STRINGS: lg = "en"
        d = STRINGS[lg]
        
        s = ctk.CTkToplevel(self)
        s.title(d["p"])
        s.geometry("450x700")
        s.configure(fg_color=BG_COLOR)
        s.attributes('-topmost', True)
        s.after(200, lambda: self.apply_icon(s))
            
        scr = ctk.CTkScrollableFrame(s, fg_color=BG_COLOR)
        scr.pack(fill="both", expand=True)

        ctk.CTkLabel(scr, text=d["ec"], font=FONT_TITLE, text_color=TEXT_MAIN).pack(pady=(20, 15), anchor="w", padx=15)
        
        c1 = ctk.CTkFrame(scr, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        c1.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(c1, text=d["lang"], font=FONT_SUB, text_color=TEXT_SUB).pack(anchor="w", padx=15, pady=(15, 5))
        lv = ctk.StringVar(value=lg)
        def on_language(v):
            self.cfg.set_value("lang", v)
            self.refresh_labels()
            s.destroy()
            self.open_settings()
        cl = ctk.CTkComboBox(c1, values=["ru", "en"], variable=lv, font=FONT_MAIN, 
                             fg_color="#252a38", border_width=0, button_color="#252a38", 
                             button_hover_color="#282e3d", text_color=TEXT_MAIN, corner_radius=CORNER_RADIUS, 
                             command=on_language, dropdown_fg_color=CARD_COLOR, dropdown_hover_color="#282e3d", dropdown_text_color=TEXT_MAIN)
        cl.pack(fill="x", padx=15, pady=(0, 15))
        
        c2 = ctk.CTkFrame(scr, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        c2.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(c2, text=d["im"], font=FONT_SUB, text_color=TEXT_SUB).pack(anchor="w", padx=15, pady=(15, 5))
        mv = ctk.StringVar(value=self.cfg.get("click_mode"))
        cb = ctk.CTkComboBox(c2, values=["background", "physical"], variable=mv, font=FONT_MAIN, 
                             fg_color="#252a38", border_width=0, button_color="#252a38", button_hover_color="#282e3d", text_color=TEXT_MAIN, corner_radius=CORNER_RADIUS, 
                             command=lambda v: self.cfg.set_value("click_mode", v), dropdown_fg_color=CARD_COLOR, dropdown_hover_color="#282e3d")
        cb.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(c2, text=d["act"], font=FONT_SUB, text_color=TEXT_SUB).pack(anchor="w", padx=15, pady=5)
        av = ctk.StringVar(value=self.cfg.get("action"))
        cab = ctk.CTkComboBox(c2, values=["left_click", "right_click", "double_click"], variable=av, font=FONT_MAIN, 
                              fg_color="#252a38", border_width=0, button_color="#252a38", button_hover_color="#282e3d", text_color=TEXT_MAIN, corner_radius=CORNER_RADIUS, 
                              command=lambda v: self.cfg.set_value("action", v), dropdown_fg_color=CARD_COLOR, dropdown_hover_color="#282e3d")
        cab.pack(fill="x", padx=15, pady=(0, 10))
        
        sv = ctk.StringVar(value=d["sen"].format(v=self.cfg.get('sensitivity')))
        sl_lbl = ctk.CTkLabel(c2, textvariable=sv, font=FONT_SUB, text_color=TEXT_SUB)
        sl_lbl.pack(anchor="w", padx=15, pady=5)
        sens_slider = ctk.CTkSlider(c2, from_=0.1, to=1.0, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER, progress_color=PRIMARY, 
                           command=lambda v: (sv.set(d["sen"].format(v=float(v))), self.cfg.set_value("sensitivity", float(v))))
        sens_slider.set(self.cfg.get("sensitivity"))
        sens_slider.pack(fill="x", padx=15, pady=(0, 10))
        
        cv = ctk.StringVar(value=d["cd"].format(v=self.cfg.get('cooldown')))
        c_lbl = ctk.CTkLabel(c2, textvariable=cv, font=FONT_SUB, text_color=TEXT_SUB)
        c_lbl.pack(anchor="w", padx=15, pady=5)
        c_l = ctk.CTkSlider(c2, from_=0.0, to=5.0, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER, progress_color=PRIMARY, 
                            command=lambda v: (cv.set(d["cd"].format(v=float(v))), self.cfg.set_value("cooldown", float(v))))
        c_l.set(self.cfg.get("cooldown"))
        c_l.pack(fill="x", padx=15, pady=(0, 15))
        
        c3 = ctk.CTkFrame(scr, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        c3.pack(fill="x", padx=15, pady=5)
        
        dv = ctk.BooleanVar(value=self.cfg.get("debug"))
        ctk.CTkSwitch(c3, text=d["hw"], variable=dv, font=FONT_MAIN, 
                      command=lambda: self.cfg.set_value("debug", dv.get()), 
                      progress_color=PRIMARY, button_color=TEXT_MAIN, button_hover_color=TEXT_MAIN, text_color=TEXT_MAIN).pack(anchor="w", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(c3, text=d["limit"], font=FONT_MAIN, text_color=TEXT_MAIN
                     ).pack(anchor="w", padx=15, pady=(0, 2))
        lim = ctk.CTkEntry(c3, font=FONT_MAIN, fg_color=BG_COLOR, border_color="#2a2f3f",
                           text_color=TEXT_MAIN, height=32)
        lim.insert(0, str(self.cfg.get("click_limit") or 0))
        lim.pack(fill="x", padx=15, pady=(0, 10))
        lim.bind("<FocusOut>", lambda _e, w=lim: self.save_limit(w))
        lim.bind("<Return>", lambda _e, w=lim: self.save_limit(w))

        ctk.CTkLabel(c3, text=d["hk"], font=FONT_MAIN, text_color=TEXT_MAIN
                     ).pack(anchor="w", padx=15, pady=(0, 2))
        hk_row = ctk.CTkFrame(c3, fg_color="transparent")
        hk_row.pack(fill="x", padx=15, pady=(0, 15))
        for key, caption in (("hotkey_start", d["hk_start"]), ("hotkey_stop", d["hk_stop"])):
            box = ctk.CTkFrame(hk_row, fg_color="transparent")
            box.pack(side="left", expand=True, fill="x", padx=(0, 8))
            ctk.CTkLabel(box, text=caption, font=FONT_SUB, text_color=TEXT_SUB).pack(anchor="w")
            field = ctk.CTkEntry(box, font=FONT_MAIN, fg_color=BG_COLOR, border_color="#2a2f3f",
                                 text_color=TEXT_MAIN, height=32)
            field.insert(0, self.cfg.get(key) or "")
            field.pack(fill="x")
            field.bind("<FocusOut>", lambda _e, k=key, w=field: self.save_hotkey(k, w))
            field.bind("<Return>", lambda _e, k=key, w=field: self.save_hotkey(k, w))

        c4 = ctk.CTkFrame(scr, fg_color="transparent")
        c4.pack(fill="x", padx=15, pady=15)
        ctk.CTkButton(c4, text=d["rsr"], font=FONT_MAIN, fg_color="#282e3d", hover_color="#2a2f3f", text_color=TEXT_MAIN, 
                      corner_radius=CORNER_RADIUS, height=40, command=self.set_scan_region).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(c4, text=d["rrc"], font=FONT_MAIN, fg_color="transparent", border_color=DANGER, border_width=1, hover_color="#48242a", text_color=DANGER, 
                      corner_radius=CORNER_RADIUS, height=40, command=lambda: self.cfg.set_value("region", None)).pack(fill="x", pady=(0, 10))

    def region_overlay(self, cb):
        s = ctk.CTkToplevel(self)
        s.attributes('-fullscreen', True)
        s.attributes('-alpha', 0.25)
        s.attributes('-topmost', True)
        s.configure(cursor="crosshair")
        c = ctk.CTkCanvas(s, cursor="crosshair", bg="black", highlightthickness=0)
        c.pack(fill="both", expand=True)

        p = [0, 0, 0, 0]
        
        def on_press(e): p[0], p[1] = e.x, e.y
        def on_drag(e):
            c.delete("sel")
            c.create_rectangle(p[0], p[1], e.x, e.y, outline=PRIMARY, width=2, tags="sel")
        def on_release(e):
            p[2], p[3] = e.x, e.y
            s.destroy()
            x1, y1 = min(p[0], p[2]), min(p[1], p[3])
            x2, y2 = max(p[0], p[2]), max(p[1], p[3])
            if x2 - x1 > 5 and y2 - y1 > 5:
                cb(x1, y1, x2-x1, y2-y1)
                
        c.bind("<ButtonPress-1>", on_press)
        c.bind("<B1-Motion>", on_drag)
        c.bind("<ButtonRelease-1>", on_release)

    def snip_target(self):
        def on_snip(x, y, w, h):
            n = f"tgt_{int(time.time())}.png"
            pyautogui.screenshot(region=(x, y, w, h)).save(n)
            t = self.cfg.get("targets")
            t.append({"path": n, "active": True})
            self.cfg.set_value("targets", t)
            self.refresh_targets()
        self.region_overlay(on_snip)

    def set_scan_region(self):
        def on_region(x, y, w, h):
            self.cfg.set_value("region", [x, y, w, h])
        self.region_overlay(on_region)

    def refresh_targets(self):
        for w in self.targets_frame.winfo_children(): w.destroy()
        ts = self.cfg.get("targets")
        
        e = set([x["path"] for x in ts])
        for f in os.listdir():
            if f.startswith("tgt_") and f.endswith(".png") and f not in e:
                ts.append({"path": f, "active": True})
                
        vt = []
        for pt in ts:
            p = pt["path"]
            if os.path.exists(p):
                vt.append(pt)
                rf = ctk.CTkFrame(self.targets_frame, fg_color="#252a38", corner_radius=CORNER_RADIUS)
                rf.pack(fill="x", pady=5)
                
                cv = ctk.BooleanVar(value=pt.get("active", True))
                def toggle_target(p_ref=p, v_ref=cv):
                    for x in self.cfg.get("targets"):
                        if x["path"] == p_ref:
                            x["active"] = v_ref.get()
                            break
                    self.cfg.save()
                    
                cb = ctk.CTkSwitch(rf, text="", variable=cv, command=toggle_target, switch_width=36, switch_height=20, 
                                   progress_color=PRIMARY, button_color=TEXT_MAIN, button_hover_color=TEXT_MAIN)
                cb.pack(side="left", padx=(15, 5), pady=10)
                
                fname = os.path.basename(p)
                if len(fname) > 22: fname = fname[:10] + "..." + fname[-8:]
                
                ctk.CTkLabel(rf, text=fname, font=FONT_MAIN, text_color=TEXT_MAIN).pack(side="left", padx=5, pady=10)
                ctk.CTkButton(rf, text="✕", width=30, height=30, fg_color="transparent", hover_color="#48242a", text_color=DANGER, 
                              font=("Segoe UI", 16), corner_radius=CORNER_RADIUS, command=lambda x=pt: self.remove_target(x)).pack(side="right", padx=10, pady=10)
        
        if len(vt) != len(ts):
            self.cfg.set_value("targets", vt)

    def remove_target(self, pt):
        t = self.cfg.get("targets")
        if pt in t: t.remove(pt)
        self.cfg.set_value("targets", t)
        try:
            if os.path.exists(pt["path"]): os.remove(pt["path"])
        except: pass
        self.refresh_targets()

    def on_close(self):
        self.engine.stop()
        self.cfg.save()
        self.destroy()
        os._exit(0)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    c = App()
    c.mainloop()
