import requests
import csv
import io
import threading
import time
import os
import re
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
import customtkinter as ctk
import ctypes
import platform

# Developed by Alp-1863530 | Alp-1863530 tarafından geliştirildi
# --- API -----
VATSIM_DATA_URL = "https://data.vatsim.net/v3/vatsim-data.json"
METAR_BASE = "https://metar.vatsim.net/"
USER_AGENT = "alp-vatsim-tr-gui/8.0"
MAX_WORKERS = 15

# --- DİL PAKETLERİ ---
LANG_DATA = {
    "TR": {
        "title": "Türkiye Havasahasıiçin Meydan Bazlı Metar",
        "pin": "Sabitle",
        "pinned": "Sabitlendi",
        "filter": "Filtre:",
        "refresh": "Yenileme:",
        "status_wait": "Bekliyor",
        "status_upd": "Güncelleniyor...",
        "status_ok": "Güncel",
        "all_list": "TÜM MEYDANLAR",
        "dep": "KALKIŞLAR",
        "arr": "VARIŞLAR",
        "all": "Hepsi",
        "only_dep": "Sadece DEP",
        "only_arr": "Sadece ARR",
        "no_flight": "Aktif uçuş yok.",
        "no_metar": "METAR YOK",
        "local_time": "TR:",
        "utc_time": "UTC:",
        "err_conn": "Bağlantı Hatası:",
        "no_data": "Veri Yok",
        "es_mode": "ES Modu",
        "exit_key": "Çıkış:",
        "summary": "Özet",
        "font_size": "Yazı Boyutu:",
        "last_upd": "Son:",
        "next_upd": "Gelecek:"
    },
    "EN": {
        "title": "Airport Based METAR for Turkiye Airspace",
        "pin": "Pin",
        "pinned": "Pinned",
        "filter": "Filter:",
        "refresh": "Refresh:",
        "status_wait": "Waiting",
        "status_upd": "Updating...",
        "status_ok": "Updated",
        "all_list": "ALL AIRPORTS",
        "dep": "DEPARTURES",
        "arr": "ARRIVALS",
        "all": "All",
        "only_dep": "Only DEP",
        "only_arr": "Only ARR",
        "no_flight": "No active flights.",
        "no_metar": "NO METAR",
        "local_time": "TR:",
        "utc_time": "UTC:",
        "err_conn": "Connection Error:",
        "no_data": "No Data",
        "es_mode": "ES Mode",
        "exit_key": "Exit:",
        "summary": "Summary",
        "font_size": "Font Size:",
        "last_upd": "Last:",
        "next_upd": "Next:"
    }
}

class VatsimTRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = "TR"
        self.title("ShortMetarForTurkAirspace")
        self.geometry("550x800")
        ctk.set_appearance_mode("dark")
        
        # Değişkenler
        self.is_pinned = False
        self.es_overlay = False
        self.summary_mode = ctk.BooleanVar(value=False)
        self.refresh_minutes = ctk.StringVar(value="1 dk")
        self.exit_key = ctk.StringVar(value="Escape")
        self.font_size_var = ctk.IntVar(value=14)
        self.is_running = True
        
        self._x = 0
        self._y = 0

        self.last_update_str = "--:--:--"
        self.next_update_str = "--:--:--"

        # Mouse Bağlantıları
        self.bind("<Key>", self.handle_keypress)

        self.setup_ui()
        self.start_auto_refresh()

    def setup_ui(self):
        L = LANG_DATA[self.current_lang]
        
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=15, pady=10)

        self.title_label = ctk.CTkLabel(self.top_frame, text=L["title"], font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.pack(side="left", padx=10)

        self.es_btn = ctk.CTkButton(self.top_frame, text=L["es_mode"], width=70, fg_color="#27ae60", command=self.toggle_es_mode)
        self.es_btn.pack(side="right", padx=5)

        self.lang_menu = ctk.CTkOptionMenu(self.top_frame, values=["TR", "EN"], width=60, command=self.change_language)
        self.lang_menu.pack(side="right", padx=5)

        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame.pack(fill="x", padx=15, pady=5)

        self.filter_menu = ctk.CTkOptionMenu(self.settings_frame, values=[L["all"], L["only_dep"], L["only_arr"]], width=100, command=self.refresh_ui_manual)
        self.filter_menu.pack(side="left", padx=2)

        self.ref_label = ctk.CTkLabel(self.settings_frame, text=L["refresh"], font=ctk.CTkFont(size=11))
        self.ref_label.pack(side="left", padx=(10, 2))
        self.ref_menu = ctk.CTkOptionMenu(self.settings_frame, values=["0.5 dk", "1 dk", "2 dk", "5 dk"], variable=self.refresh_minutes, width=80)
        self.ref_menu.pack(side="left", padx=2)

        self.summary_switch = ctk.CTkSwitch(self.settings_frame, text=L["summary"], variable=self.summary_mode, command=self.refresh_ui_manual, font=ctk.CTkFont(size=11))
        self.summary_switch.pack(side="left", padx=10)

        self.pin_btn = ctk.CTkButton(self.settings_frame, text=L["pin"], width=60, command=self.toggle_pin, fg_color="#34495e")
        self.pin_btn.pack(side="right", padx=5)

        self.font_key_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.font_key_frame.pack(fill="x", padx=15, pady=2)

        self.font_lbl = ctk.CTkLabel(self.font_key_frame, text=L["font_size"], font=ctk.CTkFont(size=11))
        self.font_lbl.pack(side="left", padx=2)
        self.font_slider = ctk.CTkSlider(self.font_key_frame, from_=10, to=30, variable=self.font_size_var, width=120, command=self.update_font_size)
        self.font_slider.pack(side="left", padx=5)

        self.key_option = ctk.CTkOptionMenu(self.font_key_frame, values=["Escape", "F1", "F12", "Tab", "x"], variable=self.exit_key, width=90)
        self.key_option.pack(side="right", padx=2)
        self.key_label = ctk.CTkLabel(self.font_key_frame, text=L["exit_key"], font=ctk.CTkFont(size=11))
        self.key_label.pack(side="right", padx=2)

        self.status_bar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_bar_frame.pack(fill="x", padx=15)
        self.status_label = ctk.CTkLabel(self.status_bar_frame, text=L["status_wait"], text_color="#f39c12", font=ctk.CTkFont(size=11))
        self.status_label.pack(side="right")

        # --- TEXTBOX (Şeffaf Sürükleme Alanı) ---
        self.text_area = ctk.CTkTextbox(self, font=("Consolas", self.font_size_var.get()), border_width=1, state="disabled")
        self.text_area._textbox.configure(exportselection=0, selectbackground="black", inactiveselectbackground="black")
        self.text_area.pack(expand=True, fill="both", padx=15, pady=(5, 10))
        
        # Sürükleme Eventleri
        self.text_area.bind("<ButtonPress-1>", self.on_press)
        self.text_area.bind("<B1-Motion>", self.on_drag)

        self.time_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.time_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.time_label_tr = ctk.CTkLabel(self.time_frame, text="TR: --:--", font=ctk.CTkFont(size=11), text_color="#3498db")
        self.time_label_tr.pack(side="left", padx=5)

        self.time_label_utc = ctk.CTkLabel(self.time_frame, text="UTC: --:--", font=ctk.CTkFont(size=11), text_color="#e67e22")
        self.time_label_utc.pack(side="left", padx=5)

        self.last_upd_lbl = ctk.CTkLabel(self.time_frame, text="Son: --:--", font=ctk.CTkFont(size=11), text_color="#2ecc71")
        self.last_upd_lbl.pack(side="right", padx=5)

        self.next_upd_lbl = ctk.CTkLabel(self.time_frame, text="Gelecek: --:--", font=ctk.CTkFont(size=11), text_color="#95a5a6")
        self.next_upd_lbl.pack(side="right", padx=5)

    def on_press(self, event):
        # Tıklanan koordinatları pencereye göre kaydet
        self._x = event.x
        self._y = event.y

    def on_drag(self, event):
        # Pencereyi hareket ettir (Windows API kullanmadan)
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def update_font_size(self, val):
        self.text_area.configure(font=("Consolas", int(val)))

    def handle_keypress(self, event):
        if self.es_overlay:
            target = self.exit_key.get().lower()
            if event.keysym.lower() == target or event.char.lower() == target:
                self.toggle_es_mode()

    def toggle_es_mode(self):
        self.es_overlay = not self.es_overlay
        if self.es_overlay:
            self.overrideredirect(True)
            self.configure(fg_color="black")
            if platform.system() == "Windows":
                self.attributes("-transparentcolor", "black")
            
            self.top_frame.pack_forget()
            self.settings_frame.pack_forget()
            self.font_key_frame.pack_forget()
            self.status_bar_frame.pack_forget()
            self.time_frame.pack_forget()
            
            self.text_area.configure(fg_color="black", text_color="#ffffff", border_width=0)
            self.text_area.pack(expand=True, fill="both", padx=5, pady=5)
            
            self.attributes("-topmost", True)
            self.focus_force()
        else:
            self.overrideredirect(False)
            if platform.system() == "Windows":
                self.attributes("-transparentcolor", "")

            self.top_frame.pack(fill="x", padx=15, pady=10)
            self.settings_frame.pack(fill="x", padx=15, pady=5)
            self.font_key_frame.pack(fill="x", padx=15, pady=2)
            self.status_bar_frame.pack(fill="x", padx=15)
            self.text_area.pack(expand=True, fill="both", padx=15, pady=(5,10))
            self.time_frame.pack(fill="x", padx=15, pady=(0,10))
            self.text_area.configure(fg_color=("gray90", "gray15"), text_color=("black", "white"), border_width=1)

            if not self.is_pinned:
                self.attributes("-topmost", False)

        self.refresh_ui_manual()

    def change_language(self, choice):
        self.current_lang = choice
        L = LANG_DATA[self.current_lang]
        self.title_label.configure(text=L["title"])
        self.es_btn.configure(text=L["es_mode"])
        self.pin_btn.configure(text=L["pinned"] if self.is_pinned else L["pin"])
        self.key_label.configure(text=L["exit_key"])
        self.ref_label.configure(text=L["refresh"])
        self.summary_switch.configure(text=L["summary"])
        self.font_lbl.configure(text=L["font_size"])
        self.filter_menu.configure(values=[L["all"], L["only_dep"], L["only_arr"]])
        self.refresh_ui_manual()

    def toggle_pin(self):
        L = LANG_DATA[self.current_lang]
        self.is_pinned = not self.is_pinned
        self.attributes("-topmost", self.is_pinned)
        self.pin_btn.configure(fg_color="#1f538d" if self.is_pinned else "#34495e", text=L["pinned"] if self.is_pinned else L["pin"])

    def parse_compact_metar(self, metar_text):
        if not metar_text or "METAR" in metar_text: return "NO DATA"
        wind = re.search(r'\b\d{3}\d{2,3}(G\d{2,3})?KT\b', metar_text)
        qnh = re.search(r'\b[QA]\d{4}\b', metar_text)
        return f"{wind.group() if wind else '---'} {qnh.group() if qnh else '----'}"

    def log_update(self, content):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", content)
        self.text_area.configure(state="disabled")

    def fetch_data(self):
        L = LANG_DATA[self.current_lang]
        if not self.es_overlay:
            self.status_label.configure(text=L["status_upd"], text_color="#f1c40f")
            
        try:
            r = requests.get(VATSIM_DATA_URL, timeout=10)
            vatsim = r.json()
            v_dep, v_arr = set(), set()
            for p in vatsim.get("pilots", []):
                fp = p.get("flight_plan") or {}
                d, a = fp.get("departure"), fp.get("arrival")
                if d and d.upper().startswith("LT"): v_dep.add(d.upper())
                if a and a.upper().startswith("LT"): v_arr.add(a.upper())

            mode_val = self.filter_menu.get()
            if mode_val == L["only_dep"]: 
                combined = v_dep
                header = L["dep"]
            elif mode_val == L["only_arr"]: 
                combined = v_arr
                header = L["arr"]
            else: 
                combined = v_dep.union(v_arr)
                header = L["all_list"]
            
            metar_results = {}
            if combined:
                with requests.Session() as s:
                    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
                        futures = {exe.submit(self.get_metar_sync, s, icao): icao for icao in combined}
                        for f in futures:
                            res_icao, res_metar = f.result()
                            metar_results[res_icao] = res_metar

            self.format_output(combined, header, metar_results)
            
            self.last_update_str = datetime.now().strftime('%H:%M:%S')
            try:
                val_str = self.refresh_minutes.get().split(" ")[0]
                wait_min = float(val_str)
                self.next_update_str = (datetime.now() + timedelta(minutes=wait_min)).strftime('%H:%M:%S')
            except:
                self.next_update_str = "--:--:--"

            if not self.es_overlay:
                self.status_label.configure(text=L["status_ok"], text_color="#2ecc71")
        except:
            if not self.es_overlay:
                self.status_label.configure(text="Error", text_color="#e74c3c")
        
        self.after(0, self.update_times)

    def update_times(self):
        L = LANG_DATA[self.current_lang]
        now_tr = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime('%H:%M:%S')
        now_utc = datetime.now(timezone.utc).strftime('%H:%M:%S')
        
        self.time_label_tr.configure(text=f"{L['local_time']} {now_tr}")
        self.time_label_utc.configure(text=f"{L['utc_time']} {now_utc}")
        self.last_upd_lbl.configure(text=f"{L['last_upd']} {self.last_update_str}")
        self.next_upd_lbl.configure(text=f"{L['next_upd']} {self.next_update_str}")

    def get_metar_sync(self, session, icao):
        try:
            r = session.get(f"{METAR_BASE}{icao}", timeout=5)
            return icao, r.text.strip() if r.status_code == 200 else None
        except: return icao, None

    def format_output(self, combined_list, header, metars):
        L = LANG_DATA[self.current_lang]
        output = ""
        
        if not combined_list:
            output += f"{L['no_flight']}\n"
        else:
            for icao in sorted(combined_list, reverse=True):
                m = metars.get(icao)
                if self.es_overlay or self.summary_mode.get():
                    output += f"{icao:4}  {self.parse_compact_metar(m)}\n"
                else:
                    output += f"{icao:4}  {m if m else L['no_metar']}\n"
        
        if not self.es_overlay:
            header_str = f"{header} - {len(combined_list)}\n" + "-"*35 + "\n"
            output = header_str + output

        self.log_update(output)

    def refresh_ui_manual(self, *args):
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def start_auto_refresh(self):
        def loop():
            while self.is_running:
                self.fetch_data()
                try:
                    val_str = self.refresh_minutes.get().split(" ")[0]
                    wait_time = int(float(val_str) * 60)
                except: 
                    wait_time = 60
                
                for _ in range(wait_time):
                    if not self.is_running: break
                    self.after(0, self.update_times)
                    time.sleep(1)
        
        threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app = VatsimTRApp()
    def on_closing():
        app.is_running = False
        app.destroy()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()