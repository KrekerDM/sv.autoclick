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
import random
import sys

BG_COLOR = "#121212"
CARD_COLOR = "#1E1E1E"
PRIMARY = "#8AB4F8"
PRIMARY_HOVER = "#AECBFA"
DANGER = "#F28B82"
DANGER_HOVER = "#F6AEA9"
TEXT_MAIN = "#E8EAED"
TEXT_SUB = "#9AA0A6"
CORNER_RADIUS = 8

FONT_MAIN = ("Roboto", 14)
FONT_TITLE = ("Roboto", 20, "bold")
FONT_SUB = ("Roboto", 12)

def gth(n):
    if getattr(sys, 'frozen', False):
        m = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        b = os.path.join(m, n)
        if os.path.exists(b): return b
        return os.path.join(os.path.dirname(sys.executable), n)
    return n

os.chdir(os.path.dirname(os.path.abspath(__file__)))
fl_cfg = "phantom_config.json"

dx = {
    "en": {
        "t": "sv.autoclick", "s": "SNIP", "i": "IMPORT", "f7": "RUN (F7)", "f8": "HALT (F8)", "tb": "TARGET_DB", 
        "sb": "SYS: STANDBY", "ac": "SYS: ACTIVE", "p": "Settings", "ec": "System Configuration", "im": "Input Protocol:",
        "act": "Action:", "sen": "Sensitivity: {v:.2f}", "cd": "Cooldown: {v:.1f}s", "ab": "Ariral Stealth", 
        "hw": "Vision Debug", "rsr": "Set Scan Region", "rrc": "Reset Region",
        "lang": "Language:", "help": "Docs", "h_title": "sv.autoclick - Manual",
        "h_snip": "• SNIP\n  Captures a region of your screen to use as a target.",
        "h_import": "• IMPORT\n  Loads existing images (.png, .jpg) into target db.",
        "h_f7": "• RUN\n  Begins the autonomous scanning engine.",
        "h_f8": "• HALT\n  Halts the engine immediately.",
        "h_bank": "• TARGET_DB\n  Toggle switches to enable/disable targets.",
        "h_click": "• INPUT PROTOCOL\n  'physical' hijacks OS mouse. 'background' injects hidden WIN32 events.",
        "h_act": "• ACTION\n  Choose left, right, or double click.",
        "h_sens": "• SENSITIVITY\n  Higher = exact pixel match. Lower = loose recognition.",
        "h_cd": "• COOLDOWN\n  Delay between consecutive clicks on identical coordinates.",
        "h_ab": "• ARIRAL STEALTH\n  Humanizes behavior (random offsets & delays) to evade anti-cheat.",
        "h_hw": "• VISION DEBUG\n  Opens overlay showing what exactly the script sees.",
        "h_reg": "• SCAN REGION\n  Limits scanning to specific area, vastly improving FPS.",
        "egg": "SIGNAL INTERCEPTED: The developer of this program probably loves shrimp, hmm... Does it make sense now?"
    },
    "ru": {
        "t": "sv.autoclick", "s": "СНИМОК", "i": "ИМПОРТ", "f7": "ЗАПУСК (F7)", "f8": "СТОП (F8)", "tb": "БАЗА ЦЕЛЕЙ", 
        "sb": "СТАТУС: ОЖИДАНИЕ", "ac": "СТАТУС: АКТИВНО", "p": "Настройки", "ec": "Конфигурация", "im": "Протокол ввода:",
        "act": "Действие:", "sen": "Чувствительность: {v:.2f}", "cd": "Задержка: {v:.1f}s", "ab": "Ariral Stealth (Анти-детект)", 
        "hw": "Отладка зрения (Debug)", "rsr": "Задать зону сканирования", "rrc": "Сбросить зону",
        "lang": "Язык:", "help": "Справка", "h_title": "sv.autoclick - Руководство",
        "h_snip": "• СНИМОК\n  Вырезает фрагмент экрана и сохраняет как цель.",
        "h_import": "• ИМПОРТ\n  Загрузка сторонних файлов (.png, .jpg) в базу.",
        "h_f7": "• ЗАПУСК\n  Активирует ядро технического зрения.",
        "h_f8": "• СТОП\n  Экстренная остановка всех процессов.",
        "h_bank": "• БАЗА ЦЕЛЕЙ\n  Управление целями. Отключите тумблер, чтобы игнорировать файл.",
        "h_click": "• ПРОТОКОЛ ВВОДА\n  'physical' использует мышь. 'background' скрыто шлет сигналы окну.",
        "h_act": "• ДЕЙСТВИЕ\n  Левый, Правый клик или Двойной.",
        "h_sens": "• ЧУВСТВИТЕЛЬНОСТЬ\n  Высокая = строгий поиск. Низкая = находит похожие пиксели.",
        "h_cd": "• ЗАДЕРЖКА\n  Перерыв между повторными кликами в ту же цель.",
        "h_ab": "• ARIRAL STEALTH\n  Рандомизирует смещение клика и тайминги ради обхода блокировок.",
        "h_hw": "• ОТЛАДКА ЗРЕНИЯ\n  Окно отладки. Показывает алгоритм распознавания CV2.",
        "h_reg": "• ЗОНА СКАНИРОВАНИЯ\n  Сужает радиус поиска, многократно повышая FPS.",
        "egg": "ПЕРЕХВАТ СИГНАЛА: Наверное разработчик этой программы любит креветки, хмм, есть ли в этом смысл?"
    }
}

class Potato:
    def __init__(self):
        import locale
        sl = "en"
        try:
            lc = locale.getdefaultlocale()[0]
            if lc and lc.startswith("ru"): sl = "ru"
        except: pass
            
        self.cfg = {
            "targets": [], "sensitivity": 0.8, "cooldown": 1.0, "action": "left_click",
            "debug": False, "anti_detect": False, "click_mode": "background", "region": None, "lang": sl
        }
        self.onion()

    def onion(self):
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

    def garlic(self):
        try:
            with open(fl_cfg, "w") as f: json.dump(self.cfg, f, indent=4)
        except: pass

    def cabbage(self, k): return self.cfg.get(k)
    def broccoli(self, k, v):
        self.cfg[k] = v
        self.garlic()

class Tomato:
    def __init__(self, p, cb):
        self.p = p
        self.rn = False
        self.cb = cb
        self.lt = 0
        
    def eggplant(self):
        if not self.rn:
            self.rn = True
            l = self.p.cabbage("lang")
            if l not in dx: l = "en"
            self.cb(dx[l]["ac"], PRIMARY)
            threading.Thread(target=self.celery, daemon=True).start()

    def zucchini(self):
        self.rn = False
        l = self.p.cabbage("lang")
        if l not in dx: l = "en"
        self.cb(dx[l]["sb"], TEXT_SUB)

    def cucumber(self, x, y, a):
        if a == "left_click": pyautogui.click(int(x), int(y))
        elif a == "right_click": pyautogui.click(int(x), int(y), button="right")
        elif a == "double_click": pyautogui.doubleClick(int(x), int(y))

    def radish(self, x, y, a):
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

    def celery(self):
        wa = False
        while self.rn:
            t = self.p.cabbage("targets")
            if not t:
                time.sleep(0.5)
                continue

            r = self.p.cabbage("region")
            s = self.p.cabbage("sensitivity")
            d = self.p.cabbage("debug")
            ad = self.p.cabbage("anti_detect")
            m = self.p.cabbage("click_mode")
            cd = self.p.cabbage("cooldown")
            ac = self.p.cabbage("action")
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
                    
                    if ad:
                        cx_l += random.randint(-max(1, w//4), max(1, w//4))
                        cy_l += random.randint(-max(1, h//4), max(1, h//4))
                    
                    cx_g = cx_l + (rt[0] if rt else 0)
                    cy_g = cy_l + (rt[1] if rt else 0)
                    
                    if d:
                        cv2.rectangle(dbg, p, (p[0]+w, p[1]+h), (0, 255, 0), 2)
                        cv2.circle(dbg, (cx_l, cy_l), 5, (0, 0, 255), -1)
                        
                    if not fnd and (time.time() - self.lt) >= cd:
                        if ad: time.sleep(random.uniform(0.05, 0.15))
                        if m == "background": self.radish(cx_g, cy_g, ac)
                        else: self.cucumber(cx_g, cy_g, ac)
                        self.lt = time.time()
                        fnd = True

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

class Carrot(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.pot = Potato()
        self.tom = Tomato(self.pot, self.spinach)
        self.eg = 0
        
        self.title("sv.autoclick")
        self.geometry("450x640")
        self.configure(fg_color=BG_COLOR)
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.after(200, lambda: self.squash(self))
        
        self.pumpkin()
        self.pepper()
        self.ol()
        self.protocol("WM_DELETE_WINDOW", self.beet)

    def squash(self, w):
        try:
            ico = gth("logo.ico")
            w.iconbitmap(ico)
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('sv.cli.term')
            hw = ctypes.windll.user32.GetParent(w.winfo_id())
            hi = ctypes.windll.user32.LoadImageW(0, ico, 1, 0, 0, 0x00000010)
            if hi:
                ctypes.windll.user32.SendMessageW(hw, 0x0080, 0, hi)
                ctypes.windll.user32.SendMessageW(hw, 0x0080, 1, hi)
        except Exception as e: pass

    def celery_click(self, ev):
        self.eg += 1
        if self.eg == 5:
            self.eg = 0
            lg = self.pot.cabbage("lang")
            if lg not in dx: lg = "en"
            t = ctk.CTkToplevel(self)
            t.title("???")
            t.geometry("380x120")
            t.configure(fg_color=BG_COLOR)
            t.attributes('-topmost', True)
            ctk.CTkLabel(t, text=dx[lg]["egg"], font=FONT_SUB, text_color=PRIMARY, wraplength=350).pack(expand=True)

    def pumpkin(self):
        h_top = ctk.CTkFrame(self, fg_color="transparent")
        h_top.pack(fill="x", padx=15, pady=(20, 5))
        
        self.l_t = ctk.CTkLabel(h_top, text="", font=FONT_TITLE, text_color=TEXT_MAIN)
        self.l_t.pack(side="left")
        self.l_t.bind("<Button-1>", self.celery_click)
        
        self.b_hz = ctk.CTkButton(h_top, text="?", width=32, height=32, font=FONT_MAIN, 
                                  fg_color=CARD_COLOR, hover_color="#2A2A2A", text_color=TEXT_SUB, 
                                  command=self.onion_help, corner_radius=CORNER_RADIUS)
        self.b_hz.pack(side="right", padx=(5, 0))
        
        self.b_cfg = ctk.CTkButton(h_top, text="⚙", width=32, height=32, font=("Roboto", 16), 
                                   fg_color=CARD_COLOR, hover_color="#2A2A2A", text_color=TEXT_SUB, 
                                   command=self.bean, corner_radius=CORNER_RADIUS)
        self.b_cfg.pack(side="right")
        
        t_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        t_card.pack(fill="both", expand=True, padx=15, pady=(10, 15))
        
        t_head = ctk.CTkFrame(t_card, fg_color="transparent")
        t_head.pack(fill="x", padx=15, pady=(15, 10))
        
        self.l_tb = ctk.CTkLabel(t_head, text="", font=FONT_MAIN, text_color=TEXT_MAIN)
        self.l_tb.pack(side="left")
        
        self.b_imp = ctk.CTkButton(t_head, text="", width=60, font=("Roboto", 11, "bold"), fg_color="#333333", 
                                   hover_color="#444444", text_color=TEXT_MAIN, 
                                   command=self.carrot_import, corner_radius=CORNER_RADIUS, height=28)
        self.b_imp.pack(side="right")
        
        self.b_snip = ctk.CTkButton(t_head, text="", width=60, font=("Roboto", 11, "bold"), fg_color=PRIMARY, 
                                    hover_color=PRIMARY_HOVER, text_color="#121212", 
                                    command=self.corn, corner_radius=CORNER_RADIUS, height=28)
        self.b_snip.pack(side="right", padx=(0, 5))

        self.tl = ctk.CTkScrollableFrame(t_card, fg_color="transparent")
        self.tl.pack(fill="both", expand=True, padx=5, pady=(0, 10))
        self.lettuce()
        
        a_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        a_card.pack(fill="x", padx=15, pady=(0, 20))
        
        self.sl = ctk.CTkLabel(a_card, text="", font=FONT_SUB, text_color=TEXT_SUB)
        self.sl.pack(pady=(15, 5))

        ab = ctk.CTkFrame(a_card, fg_color="transparent")
        ab.pack(fill="x", padx=15, pady=(5, 15))

        self.b_f7 = ctk.CTkButton(ab, text="", font=("Roboto", 15, "bold"), fg_color=PRIMARY, 
                                  hover_color=PRIMARY_HOVER, text_color="#121212", 
                                  command=self.tom.eggplant, corner_radius=CORNER_RADIUS, height=45)
        self.b_f7.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.b_f8 = ctk.CTkButton(ab, text="", font=("Roboto", 15, "bold"), fg_color="transparent", 
                                  border_color=DANGER, border_width=2, hover_color="#331816", text_color=DANGER, 
                                  command=self.tom.zucchini, corner_radius=CORNER_RADIUS, height=45)
        self.b_f8.pack(side="right", expand=True, fill="x", padx=(5, 0))

    def onion_help(self):
        lg = self.pot.cabbage("lang")
        if lg not in dx: lg = "en"
        d = dx[lg]
        s = ctk.CTkToplevel(self)
        s.title(d["h_title"])
        s.geometry("550x650")
        s.configure(fg_color=BG_COLOR)
        s.attributes('-topmost', True)
        s.after(200, lambda: self.squash(s))
        
        scr = ctk.CTkScrollableFrame(s, fg_color=BG_COLOR)
        scr.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(scr, text=d["h_title"], font=FONT_TITLE, text_color=PRIMARY).pack(pady=(10, 20))
        
        hi = [
            "h_snip", "h_import", "h_f7", "h_f8", "h_bank", "h_click",
            "h_act", "h_sens", "h_cd", "h_ab", "h_hw", "h_reg"
        ]
        
        for hk in hi:
            card = ctk.CTkFrame(scr, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(card, text=d[hk], font=FONT_SUB, text_color=TEXT_MAIN, wraplength=480, justify="left").pack(anchor="w", padx=15, pady=10)

    def ol(self):
        lg = self.pot.cabbage("lang")
        if lg not in dx: lg = "en"
        d = dx[lg]
        self.l_t.configure(text=d["t"])
        self.b_snip.configure(text=d["s"])
        self.b_imp.configure(text=d["i"])
        self.b_f7.configure(text=d["f7"])
        self.b_f8.configure(text=d["f8"])
        self.l_tb.configure(text=d["tb"])
        if not self.tom.rn:
            self.sl.configure(text=d["sb"], text_color=TEXT_SUB)
        else:
            self.sl.configure(text=d["ac"], text_color=PRIMARY)

    def carrot_import(self):
        from customtkinter import filedialog
        fs = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if fs:
            t = self.pot.cabbage("targets")
            for f in fs:
                nm = os.path.basename(f)
                dst = f"tgt_imp_{int(time.time())}_{nm}"
                try:
                    shutil.copy(f, dst)
                    t.append({"path": dst, "active": True})
                except: pass
            self.pot.broccoli("targets", t)
            self.lettuce()

    def pepper(self):
        keyboard.add_hotkey('f7', self.tom.eggplant)
        keyboard.add_hotkey('f8', self.tom.zucchini)

    def spinach(self, t, c):
        try: self.sl.configure(text=t, text_color=c)
        except: pass

    def bean(self):
        lg = self.pot.cabbage("lang")
        if lg not in dx: lg = "en"
        d = dx[lg]
        
        s = ctk.CTkToplevel(self)
        s.title(d["p"])
        s.geometry("450x700")
        s.configure(fg_color=BG_COLOR)
        s.attributes('-topmost', True)
        s.after(200, lambda: self.squash(s))
            
        scr = ctk.CTkScrollableFrame(s, fg_color=BG_COLOR)
        scr.pack(fill="both", expand=True)

        ctk.CTkLabel(scr, text=d["ec"], font=FONT_TITLE, text_color=TEXT_MAIN).pack(pady=(20, 15), anchor="w", padx=15)
        
        c1 = ctk.CTkFrame(scr, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        c1.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(c1, text=d["lang"], font=FONT_SUB, text_color=TEXT_SUB).pack(anchor="w", padx=15, pady=(15, 5))
        lv = ctk.StringVar(value=lg)
        def lu(v):
            self.pot.broccoli("lang", v)
            self.ol()
            s.destroy()
            self.bean()
        cl = ctk.CTkComboBox(c1, values=["ru", "en"], variable=lv, font=FONT_MAIN, 
                             fg_color="#2A2A2A", border_width=0, button_color="#2A2A2A", 
                             button_hover_color="#333333", text_color=TEXT_MAIN, corner_radius=CORNER_RADIUS, 
                             command=lu, dropdown_fg_color=CARD_COLOR, dropdown_hover_color="#333333", dropdown_text_color=TEXT_MAIN)
        cl.pack(fill="x", padx=15, pady=(0, 15))
        
        c2 = ctk.CTkFrame(scr, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        c2.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(c2, text=d["im"], font=FONT_SUB, text_color=TEXT_SUB).pack(anchor="w", padx=15, pady=(15, 5))
        mv = ctk.StringVar(value=self.pot.cabbage("click_mode"))
        cb = ctk.CTkComboBox(c2, values=["background", "physical"], variable=mv, font=FONT_MAIN, 
                             fg_color="#2A2A2A", border_width=0, button_color="#2A2A2A", button_hover_color="#333333", text_color=TEXT_MAIN, corner_radius=CORNER_RADIUS, 
                             command=lambda v: self.pot.broccoli("click_mode", v), dropdown_fg_color=CARD_COLOR, dropdown_hover_color="#333333")
        cb.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(c2, text=d["act"], font=FONT_SUB, text_color=TEXT_SUB).pack(anchor="w", padx=15, pady=5)
        av = ctk.StringVar(value=self.pot.cabbage("action"))
        cab = ctk.CTkComboBox(c2, values=["left_click", "right_click", "double_click"], variable=av, font=FONT_MAIN, 
                              fg_color="#2A2A2A", border_width=0, button_color="#2A2A2A", button_hover_color="#333333", text_color=TEXT_MAIN, corner_radius=CORNER_RADIUS, 
                              command=lambda v: self.pot.broccoli("action", v), dropdown_fg_color=CARD_COLOR, dropdown_hover_color="#333333")
        cab.pack(fill="x", padx=15, pady=(0, 10))
        
        sv = ctk.StringVar(value=d["sen"].format(v=self.pot.cabbage('sensitivity')))
        sl_lbl = ctk.CTkLabel(c2, textvariable=sv, font=FONT_SUB, text_color=TEXT_SUB)
        sl_lbl.pack(anchor="w", padx=15, pady=5)
        sl = ctk.CTkSlider(c2, from_=0.1, to=1.0, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER, progress_color=PRIMARY, 
                           command=lambda v: (sv.set(d["sen"].format(v=float(v))), self.pot.broccoli("sensitivity", float(v))))
        sl.set(self.pot.cabbage("sensitivity"))
        sl.pack(fill="x", padx=15, pady=(0, 10))
        
        cv = ctk.StringVar(value=d["cd"].format(v=self.pot.cabbage('cooldown')))
        c_lbl = ctk.CTkLabel(c2, textvariable=cv, font=FONT_SUB, text_color=TEXT_SUB)
        c_lbl.pack(anchor="w", padx=15, pady=5)
        c_l = ctk.CTkSlider(c2, from_=0.0, to=5.0, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER, progress_color=PRIMARY, 
                            command=lambda v: (cv.set(d["cd"].format(v=float(v))), self.pot.broccoli("cooldown", float(v))))
        c_l.set(self.pot.cabbage("cooldown"))
        c_l.pack(fill="x", padx=15, pady=(0, 15))
        
        c3 = ctk.CTkFrame(scr, fg_color=CARD_COLOR, corner_radius=CORNER_RADIUS)
        c3.pack(fill="x", padx=15, pady=5)
        
        adv = ctk.BooleanVar(value=self.pot.cabbage("anti_detect"))
        ctk.CTkSwitch(c3, text=d["ab"], variable=adv, font=FONT_MAIN, 
                      command=lambda: self.pot.broccoli("anti_detect", adv.get()), 
                      progress_color=PRIMARY, button_color=TEXT_MAIN, button_hover_color=TEXT_MAIN, text_color=TEXT_MAIN).pack(anchor="w", padx=15, pady=(15, 10))
        
        dv = ctk.BooleanVar(value=self.pot.cabbage("debug"))
        ctk.CTkSwitch(c3, text=d["hw"], variable=dv, font=FONT_MAIN, 
                      command=lambda: self.pot.broccoli("debug", dv.get()), 
                      progress_color=PRIMARY, button_color=TEXT_MAIN, button_hover_color=TEXT_MAIN, text_color=TEXT_MAIN).pack(anchor="w", padx=15, pady=(5, 15))
        
        c4 = ctk.CTkFrame(scr, fg_color="transparent")
        c4.pack(fill="x", padx=15, pady=15)
        ctk.CTkButton(c4, text=d["rsr"], font=FONT_MAIN, fg_color="#333333", hover_color="#444444", text_color=TEXT_MAIN, 
                      corner_radius=CORNER_RADIUS, height=40, command=self.mushroom).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(c4, text=d["rrc"], font=FONT_MAIN, fg_color="transparent", border_color=DANGER, border_width=1, hover_color="#331816", text_color=DANGER, 
                      corner_radius=CORNER_RADIUS, height=40, command=lambda: self.pot.broccoli("region", None)).pack(fill="x", pady=(0, 10))

    def pea(self, cb):
        s = ctk.CTkToplevel(self)
        s.attributes('-fullscreen', True)
        s.attributes('-alpha', 0.25)
        s.attributes('-topmost', True)
        s.configure(cursor="crosshair")
        c = ctk.CTkCanvas(s, cursor="crosshair", bg="black", highlightthickness=0)
        c.pack(fill="both", expand=True)

        p = [0, 0, 0, 0]
        
        def sr(e): p[0], p[1] = e.x, e.y
        def dr(e):
            c.delete("sel")
            c.create_rectangle(p[0], p[1], e.x, e.y, outline=PRIMARY, width=2, tags="sel")
        def er(e):
            p[2], p[3] = e.x, e.y
            s.destroy()
            x1, y1 = min(p[0], p[2]), min(p[1], p[3])
            x2, y2 = max(p[0], p[2]), max(p[1], p[3])
            if x2 - x1 > 5 and y2 - y1 > 5:
                cb(x1, y1, x2-x1, y2-y1)
                
        c.bind("<ButtonPress-1>", sr)
        c.bind("<B1-Motion>", dr)
        c.bind("<ButtonRelease-1>", er)

    def corn(self):
        def st(x, y, w, h):
            n = f"tgt_{int(time.time())}.png"
            pyautogui.screenshot(region=(x, y, w, h)).save(n)
            t = self.pot.cabbage("targets")
            t.append({"path": n, "active": True})
            self.pot.broccoli("targets", t)
            self.lettuce()
        self.pea(st)

    def mushroom(self):
        def sr(x, y, w, h):
            self.pot.broccoli("region", [x, y, w, h])
        self.pea(sr)

    def lettuce(self):
        for w in self.tl.winfo_children(): w.destroy()
        ts = self.pot.cabbage("targets")
        
        e = set([x["path"] for x in ts])
        for f in os.listdir():
            if f.startswith("tgt_") and f.endswith(".png") and f not in e:
                ts.append({"path": f, "active": True})
                
        vt = []
        for pt in ts:
            p = pt["path"]
            if os.path.exists(p):
                vt.append(pt)
                rf = ctk.CTkFrame(self.tl, fg_color="#2A2A2A", corner_radius=CORNER_RADIUS)
                rf.pack(fill="x", pady=5)
                
                cv = ctk.BooleanVar(value=pt.get("active", True))
                def tg(p_ref=p, v_ref=cv):
                    for x in self.pot.cabbage("targets"):
                        if x["path"] == p_ref:
                            x["active"] = v_ref.get()
                            break
                    self.pot.garlic()
                    
                cb = ctk.CTkSwitch(rf, text="", variable=cv, command=tg, switch_width=36, switch_height=20, 
                                   progress_color=PRIMARY, button_color=TEXT_MAIN, button_hover_color=TEXT_MAIN)
                cb.pack(side="left", padx=(15, 5), pady=10)
                
                fname = os.path.basename(p)
                if len(fname) > 22: fname = fname[:10] + "..." + fname[-8:]
                
                ctk.CTkLabel(rf, text=fname, font=FONT_MAIN, text_color=TEXT_MAIN).pack(side="left", padx=5, pady=10)
                ctk.CTkButton(rf, text="✕", width=30, height=30, fg_color="transparent", hover_color="#331816", text_color=DANGER, 
                              font=("Roboto", 16), corner_radius=CORNER_RADIUS, command=lambda x=pt: self.turnip(x)).pack(side="right", padx=10, pady=10)
        
        if len(vt) != len(ts):
            self.pot.broccoli("targets", vt)

    def turnip(self, pt):
        t = self.pot.cabbage("targets")
        if pt in t: t.remove(pt)
        self.pot.broccoli("targets", t)
        try:
            if os.path.exists(pt["path"]): os.remove(pt["path"])
        except: pass
        self.lettuce()

    def beet(self):
        self.tom.zucchini()
        self.pot.garlic()
        self.destroy()
        os._exit(0)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    c = Carrot()
    c.mainloop()
