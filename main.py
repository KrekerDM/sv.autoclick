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
        "t": "sv.autoclick 0.1.0", "s": "[ SNIP ]", "i": "[ IMPORT ]", "f7": "[ RUN: F7 ]", "f8": "[ HALT: F8 ]", "tb": "TARGET_DB//", 
        "sb": "SYS: STANDBY", "ac": "SYS: ACTIVE", "p": "> SYS.CFG", "ec": "SYS_CONFIG", "im": "INPUT_PROTOCOL:",
        "act": "ACTION:", "sen": "SENSITIVITY: {v:.2f}", "cd": "COOLDOWN: {v:.1f}s", "ab": "ARIRAL_STEALTH", 
        "hw": "VISION_DEBUG", "rsr": "SET_SCAN_REGION", "rrc": "RESET_REGION",
        "lang": "LANG_SYS:", "help": "[ DOCS ]", "h_title": "=== SV.AUTOCLICK_MANUAL.TXT ===",
        "h_snip": "> [ SNIP ]\n  Captures a region of your screen to use as a target.",
        "h_import": "> [ IMPORT ]\n  Loads existing images (.png, .jpg) into target db.",
        "h_f7": "> [ RUN ]\n  Begins the autonomous scanning engine.",
        "h_f8": "> [ HALT ]\n  Halts the engine immediately.",
        "h_bank": "> TARGET_DB\n  Toggle checkboxes to enable/disable targets.",
        "h_click": "> INPUT_PROTOCOL\n  'physical' hijacks OS mouse. 'background' injects hidden WIN32 events.",
        "h_act": "> ACTION\n  Choose left_click, right_click, or double_click.",
        "h_sens": "> SENSITIVITY\n  Higher = exact pixel match. Lower = loose recognition.",
        "h_cd": "> COOLDOWN\n  Delay between consecutive clicks on identical coordinates.",
        "h_ab": "> ARIRAL_STEALTH\n  Humanizes behavior (random offsets & delays) to evade anti-cheat.",
        "h_hw": "> VISION_DEBUG\n  Opens overlay showing what exactly the script sees.",
        "h_reg": "> SCAN_REGION\n  Limits scanning to specific area, vastly improving FPS.",
        "egg": "SIGNAL INTERCEPTED: The developer of this program probably loves shrimp, hmm... Does it make sense now?"
    },
    "ru": {
        "t": "sv.autoclick 0.1.0", "s": "[ СНИП ]", "i": "[ ИМПОРТ ]", "f7": "[ ЗАПУСК: F7 ]", "f8": "[ СТОП: F8 ]", "tb": "TARGET_DB//", 
        "sb": "SYS: ОЖИДАНИЕ", "ac": "SYS: АКТИВНО", "p": "> SYS.CFG", "ec": "SYS_CONFIG", "im": "ПРОТОКОЛ_ВВОДА:",
        "act": "ДЕЙСТВИЕ:", "sen": "ЧУВСТВ.: {v:.2f}", "cd": "ЗАДЕРЖКА: {v:.1f}s", "ab": "ARIRAL_STEALTH", 
        "hw": "VISION_DEBUG", "rsr": "ЗАДАТЬ_ЗОНУ", "rrc": "СБРОС_ЗОНЫ",
        "lang": "LANG_SYS:", "help": "[ DOCS ]", "h_title": "=== SV.AUTOCLICK_MANUAL.TXT ===",
        "h_snip": "> [ СНИП ]\n  Вырезает фрагмент экрана и сохраняет как цель.",
        "h_import": "> [ ИМПОРТ ]\n  Загрузка сторонних файлов (.png, .jpg) в базу.",
        "h_f7": "> [ ЗАПУСК ]\n  Активирует ядро технического зрения.",
        "h_f8": "> [ СТОП ]\n  Экстренная остановка всех процессов.",
        "h_bank": "> TARGET_DB\n  Управление целями. Снимите галочку, чтобы игнорировать файл.",
        "h_click": "> ПРОТОКОЛ_ВВОДА\n  'physical' использует мышь. 'background' скрыто шлет сигналы окну.",
        "h_act": "> ДЕЙСТВИЕ\n  Левый, Правый клик или Двойной.",
        "h_sens": "> ЧУВСТВИТЕЛЬНОСТЬ\n  Высокая = строгий поиск. Низкая = находит похожие пиксели.",
        "h_cd": "> ЗАДЕРЖКА\n  Перерыв между повторными кликами в ту же цель.",
        "h_ab": "> ARIRAL_STEALTH\n  Рандомизирует смещение клика и тайминги ради обхода блокировок.",
        "h_hw": "> VISION_DEBUG\n  Окно отладки. Показывает алгоритм распознавания CV2.",
        "h_reg": "> ЗОНА_СКАНИРОВАНИЯ\n  Сужает радиус поиска, многократно повышая FPS.",
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
            self.cb(dx[l]["ac"], "#FFB347")
            threading.Thread(target=self.celery, daemon=True).start()

    def zucchini(self):
        self.rn = False
        l = self.p.cabbage("lang")
        if l not in dx: l = "en"
        self.cb(dx[l]["sb"], "#737373")

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
                cv2.imshow("VISION_DEBUG_TERMINAL", dbg)
                cv2.waitKey(1)
                wa = True
            elif wa:
                try: cv2.destroyWindow("VISION_DEBUG_TERMINAL")
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
        self.configure(fg_color="#050505")
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
            t.configure(fg_color="#050505")
            t.attributes('-topmost', True)
            ctk.CTkLabel(t, text=dx[lg]["egg"], font=("Consolas", 12, "italic"), text_color="#FFB347", wraplength=350).pack(expand=True)

    def pumpkin(self):
        h = ctk.CTkFrame(self, fg_color="#050505", corner_radius=0)
        h.pack(fill="x", pady=(20, 10), padx=20)
        self.l_t = ctk.CTkLabel(h, text="", font=("Consolas", 24, "bold"), text_color="#FFB347")
        self.l_t.pack(side="left")
        self.l_t.bind("<Button-1>", self.celery_click)
        
        self.b_hz = ctk.CTkButton(h, text="", width=40, font=("Consolas", 14), fg_color="#111111", border_color="#FFB347", border_width=1, hover_color="#CC8822", text_color="#FFB347", command=self.onion_help, corner_radius=0)
        self.b_hz.pack(side="right", padx=(10, 0))
        
        self.b_cfg = ctk.CTkButton(h, text="[CFG]", width=40, font=("Consolas", 14), fg_color="#111111", border_color="#FFB347", border_width=1, hover_color="#CC8822", text_color="#FFB347", command=self.bean, corner_radius=0)
        self.b_cfg.pack(side="right")

        f = ctk.CTkFrame(self, fg_color="#0a0a0a", border_color="#FFB347", border_width=1, corner_radius=0)
        f.pack(fill="x", padx=20, pady=10)
        
        bf = ctk.CTkFrame(f, fg_color="transparent")
        bf.pack(fill="x", padx=10, pady=(15, 10))
        self.b_snip = ctk.CTkButton(bf, text="", font=("Consolas", 14, "bold"), fg_color="#111111", border_color="#FFB347", border_width=1, hover_color="#CC8822", text_color="#FFB347", command=self.corn, corner_radius=0, height=36)
        self.b_snip.pack(side="left", padx=5, expand=True, fill="x")
        self.b_imp = ctk.CTkButton(bf, text="", font=("Consolas", 14, "bold"), fg_color="#111111", border_color="#FFB347", border_width=1, hover_color="#CC8822", text_color="#FFB347", command=self.carrot_import, corner_radius=0, height=36)
        self.b_imp.pack(side="right", padx=5, expand=True, fill="x")
        
        b = ctk.CTkFrame(f, fg_color="transparent")
        b.pack(fill="x", pady=(0, 15), padx=15)
        self.b_f7 = ctk.CTkButton(b, text="", font=("Consolas", 14, "bold"), fg_color="#111111", border_color="#FFB347", border_width=1, hover_color="#CC8822", text_color="#FFB347", command=self.tom.eggplant, corner_radius=0)
        self.b_f7.pack(side="left", expand=True, padx=(0, 5))
        self.b_f8 = ctk.CTkButton(b, text="", font=("Consolas", 14, "bold"), fg_color="#111111", border_color="#FF0000", border_width=1, hover_color="#8B0000", text_color="#FF0000", command=self.tom.zucchini, corner_radius=0)
        self.b_f8.pack(side="right", expand=True, padx=(5, 0))

        self.l_tb = ctk.CTkLabel(self, text="", font=("Consolas", 14, "bold"), text_color="#FFB347")
        self.l_tb.pack(anchor="w", padx=20, pady=(10, 5))
        self.tl = ctk.CTkScrollableFrame(self, fg_color="#0a0a0a", border_color="#FFB347", border_width=1, corner_radius=0)
        self.tl.pack(fill="both", expand=True, padx=20, pady=0)
        self.lettuce()

        self.sl = ctk.CTkLabel(self, text="", font=("Consolas", 14, "bold"), text_color="#737373")
        self.sl.pack(pady=10)

    def onion_help(self):
        lg = self.pot.cabbage("lang")
        if lg not in dx: lg = "en"
        d = dx[lg]
        s = ctk.CTkToplevel(self)
        s.title(d["h_title"])
        s.geometry("550x700")
        s.configure(fg_color="#050505")
        s.attributes('-topmost', True)
        s.after(200, lambda: self.squash(s))
        
        scr = ctk.CTkScrollableFrame(s, fg_color="#0a0a0a", border_color="#FFB347", border_width=1, corner_radius=0)
        scr.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(scr, text=d["h_title"], font=("Consolas", 20, "bold"), text_color="#FFB347").pack(pady=15)
        
        hi = [
            "h_snip", "h_import", "h_f7", "h_f8", "h_bank", "h_click",
            "h_act", "h_sens", "h_cd", "h_ab", "h_hw", "h_reg"
        ]
        
        for hk in hi:
            ctk.CTkLabel(scr, text=d[hk], font=("Consolas", 13), text_color="#FFB347", wraplength=480, justify="left").pack(anchor="w", padx=10, pady=(10, 5))

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
        self.b_hz.configure(text=d["help"])
        if not self.tom.rn:
            self.sl.configure(text=d["sb"], text_color="#737373")
        else:
            self.sl.configure(text=d["ac"], text_color="#FFB347")

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
        s.geometry("440x620")
        s.configure(fg_color="#050505")
        s.attributes('-topmost', True)
        s.after(200, lambda: self.squash(s))
            
        f = ctk.CTkFrame(s, fg_color="#0a0a0a", border_color="#FFB347", border_width=1, corner_radius=0)
        f.pack(fill="both", expand=True, padx=15, pady=20)
        
        ctk.CTkLabel(f, text=d["ec"], font=("Consolas", 16, "bold"), text_color="#FFB347").pack(pady=15, anchor="w", padx=15)
        
        ctk.CTkLabel(f, text=d["lang"], font=("Consolas", 12), text_color="#FFB347").pack(anchor="w", padx=15)
        lv = ctk.StringVar(value=lg)
        def lu(v):
            self.pot.broccoli("lang", v)
            self.ol()
            s.destroy()
            self.bean()
        cl = ctk.CTkComboBox(f, values=["ru", "en"], variable=lv, font=("Consolas", 12), fg_color="#111111", border_color="#FFB347", button_color="#FFB347", text_color="#FFB347", corner_radius=0, command=lu, dropdown_fg_color="#050505", dropdown_hover_color="#CC8822", dropdown_text_color="#FFB347", dropdown_font=("Consolas", 12))
        cl.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(f, text=d["im"], font=("Consolas", 12), text_color="#FFB347").pack(anchor="w", padx=15, pady=(10, 0))
        mv = ctk.StringVar(value=self.pot.cabbage("click_mode"))
        cb = ctk.CTkComboBox(f, values=["background", "physical"], variable=mv, font=("Consolas", 12), fg_color="#111111", border_color="#FFB347", button_color="#FFB347", text_color="#FFB347", corner_radius=0, command=lambda v: self.pot.broccoli("click_mode", v), dropdown_fg_color="#050505", dropdown_hover_color="#CC8822", dropdown_text_color="#FFB347", dropdown_font=("Consolas", 12))
        cb.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(f, text=d["act"], font=("Consolas", 12), text_color="#FFB347").pack(anchor="w", padx=15, pady=(5, 0))
        av = ctk.StringVar(value=self.pot.cabbage("action"))
        cab = ctk.CTkComboBox(f, values=["left_click", "right_click", "double_click"], variable=av, font=("Consolas", 12), fg_color="#111111", border_color="#FFB347", button_color="#FFB347", text_color="#FFB347", corner_radius=0, command=lambda v: self.pot.broccoli("action", v), dropdown_fg_color="#050505", dropdown_hover_color="#CC8822", dropdown_text_color="#FFB347", dropdown_font=("Consolas", 12))
        cab.pack(fill="x", padx=15, pady=5)
        
        sv = ctk.StringVar(value=d["sen"].format(v=self.pot.cabbage('sensitivity')))
        ctk.CTkLabel(f, textvariable=sv, font=("Consolas", 12), text_color="#FFB347").pack(anchor="w", padx=15, pady=(5, 0))
        sl = ctk.CTkSlider(f, from_=0.1, to=1.0, button_color="#FFB347", progress_color="#CC8822", command=lambda v: (sv.set(d["sen"].format(v=float(v))), self.pot.broccoli("sensitivity", float(v))))
        sl.set(self.pot.cabbage("sensitivity"))
        sl.pack(fill="x", padx=15, pady=5)
        
        cv = ctk.StringVar(value=d["cd"].format(v=self.pot.cabbage('cooldown')))
        ctk.CTkLabel(f, textvariable=cv, font=("Consolas", 12), text_color="#FFB347").pack(anchor="w", padx=15, pady=(5, 0))
        c_l = ctk.CTkSlider(f, from_=0.0, to=5.0, button_color="#FFB347", progress_color="#CC8822", command=lambda v: (cv.set(d["cd"].format(v=float(v))), self.pot.broccoli("cooldown", float(v))))
        c_l.set(self.pot.cabbage("cooldown"))
        c_l.pack(fill="x", padx=15, pady=5)
        
        sf2 = ctk.CTkFrame(s, fg_color="transparent")
        sf2.pack(fill="x", padx=5, pady=5)
        
        adv = ctk.BooleanVar(value=self.pot.cabbage("anti_detect"))
        def tad(): self.pot.broccoli("anti_detect", adv.get())
        ctk.CTkSwitch(sf2, text=d["ab"], variable=adv, font=("Consolas", 12), command=tad, progress_color="#FFB347", button_color="#050505", button_hover_color="#CC8822", text_color="#FFB347").pack(anchor="w", padx=5, pady=(10, 5))
        
        dv = ctk.BooleanVar(value=self.pot.cabbage("debug"))
        def td(): self.pot.broccoli("debug", dv.get())
        ctk.CTkSwitch(sf2, text=d["hw"], variable=dv, font=("Consolas", 12), command=td, progress_color="#FFB347", button_color="#050505", button_hover_color="#CC8822", text_color="#FFB347").pack(anchor="w", padx=5, pady=(5, 10))
        
        ctk.CTkButton(s, text=d["rsr"], font=("Consolas", 14), fg_color="#111111", border_color="#FFB347", border_width=1, hover_color="#CC8822", text_color="#FFB347", corner_radius=0, command=self.mushroom).pack(fill="x", padx=30, pady=5)
        ctk.CTkButton(s, text=d["rrc"], font=("Consolas", 14), fg_color="#111111", border_color="#FF0000", border_width=1, hover_color="#8B0000", text_color="#FF0000", corner_radius=0, command=lambda: self.pot.broccoli("region", None)).pack(fill="x", padx=30, pady=5)

    def pea(self, cb):
        s = ctk.CTkToplevel(self)
        s.attributes('-fullscreen', True)
        s.attributes('-alpha', 0.15)
        s.attributes('-topmost', True)
        s.configure(cursor="crosshair")
        c = ctk.CTkCanvas(s, cursor="crosshair", bg="black", highlightthickness=0)
        c.pack(fill="both", expand=True)

        p = [0, 0, 0, 0]
        
        def sr(e): p[0], p[1] = e.x, e.y
        def dr(e):
            c.delete("sel")
            c.create_rectangle(p[0], p[1], e.x, e.y, outline="#FFB347", width=2, tags="sel")
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
                rf = ctk.CTkFrame(self.tl, fg_color="#0a0a0a", border_color="#FFB347", border_width=1, corner_radius=0)
                rf.pack(fill="x", pady=4, padx=4)
                
                cv = ctk.BooleanVar(value=pt.get("active", True))
                def tg(p_ref=p, v_ref=cv):
                    for x in self.pot.cabbage("targets"):
                        if x["path"] == p_ref:
                            x["active"] = v_ref.get()
                            break
                    self.pot.garlic()
                    
                cb = ctk.CTkCheckBox(rf, text="", variable=cv, command=tg, width=24, checkbox_width=20, checkbox_height=20, fg_color="#111111", border_color="#FFB347", checkmark_color="#FFB347", hover_color="#CC8822", corner_radius=0)
                cb.pack(side="left", padx=(10, 0), pady=5)
                
                ctk.CTkLabel(rf, text=os.path.basename(p), font=("Consolas", 12), text_color="#FFB347").pack(side="left", padx=5, pady=5)
                ctk.CTkButton(rf, text="[X]", width=30, fg_color="transparent", text_color="#FF0000", hover_color="#8B0000", font=("Consolas", 14, "bold"), corner_radius=0, command=lambda x=pt: self.turnip(x)).pack(side="right", padx=5)
        
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
    c = Carrot()
    c.mainloop()
