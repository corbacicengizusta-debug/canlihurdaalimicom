import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import time
import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import winsound  # Sesli alarm için

POST_URLS = [
    "https://itemtr.com/fiyat-alici.php",
    "https://canlihurdafiyatlari.com/fiyat-alici.php",
    "https://kirachurdaci.com/fiyat-alici.php",
    "https://hurdacihadimkoy.com/fiyat-alici.php",
    "https://kocaeligebzehurdaalan.com.tr/fiyat-alici.php"
]
SECRET_KEY = "hurda_merkezi_99"
PRICES_HISTORY_FILE = "fiyat-gecmis.json"

# Gerçek hurda sitelerinin yapılandırması
REAL_HURDA_SITES = [
    {
        "name": "hurdafiyatlari.ist",
        "url": "https://www.hurdafiyatlari.ist/",
        "price_selector": None,  # metin tabanlı
    },
    {
        "name": "hurmetsan.com",
        "url": "https://hurmetsan.com/hurda-fiyatlari/",
        "price_selector": None,
    },
    {
        "name": "hurdacifiyatlari.com.tr",
        "url": "https://hurdacifiyatlari.com.tr/",
        "price_selector": None,
    },
    {
        "name": "hurdabakirfiyati.com.tr",
        "url": "https://hurdabakirfiyati.com.tr/",
        "price_selector": None,
    },
    {
        "name": "ahmetal.com",
        "url": "https://ahmetal.com/tr/fiyat-listesi",
        "price_selector": None,
    },
    {
        "name": "emirhurda.com.tr",
        "url": "https://emirhurda.com.tr/",
        "price_selector": None,
    },
]

# Anahtar kelime → fiyat aralığı (TL/kg)
ITEM_KEYWORDS = {
    "Soyulmuş Bakır Fiyatı":    (["soyulmuş bakır", "soyulmus bakir", "bakır fiyat"], (450, 700)),
    "Lama Bakır İmalat":        (["lama bakır", "imalat bakır"], (430, 680)),
    "Boru Bakır":               (["boru bakır"], (420, 670)),
    "Yanık Bakır":              (["yanık bakır", "yanik bakir"], (400, 650)),
    "Soyma Bakır Fiyatı":       (["soyma bakır"], (440, 680)),
    "Hurda Bakırlı Petek":      (["petek", "bakırlı petek"], (150, 350)),
    "Sarı Hurda":               (["sarı hurda", "sari hurda", "pirinç hurda"], (250, 500)),
    "Musluk":                   (["musluk"], (220, 450)),
    "Pirinç Araiş":             (["pirinç araiş", "prinç araış", "araiş"], (280, 480)),
    "Batarya Vana Su Saati":    (["batarya", "vana", "su saati"], (220, 420)),
    "Sarı Talaşı":              (["sarı talaş", "sari talas"], (280, 480)),
    "Ms 58 Ms 64 Ms 70":        (["ms 58", "ms58", "ms 64", "ms64"], (310, 510)),
    "Dkp":                      (["dkp"], (8, 25)),
    "Ekstra":                   (["ekstra demir"], (7, 22)),
    "Toplama":                  (["toplama demir"], (6, 20)),
    "Mahalle":                  (["mahalle"], (6, 20)),
    "Soyulmamış Kablo":         (["soyulmamış kablo", "soyulmamis kablo"], (280, 500)),
    "Ttr Hurda Kablo Fiyatları": (["ttr kablo", "ttr hurda"], (270, 490)),
    "Nya Kablo Hurda Fiyatı":   (["nya kablo", "nya hurda"], (350, 600)),
    "Tekdamar Kalın":           (["tekdamar"], (400, 650)),
    "Karışık Bakır Kablo":      (["karışık bakır kablo", "karışık kablo"], (270, 490)),
    "Paslanmaz Çelik Hurda":    (["paslanmaz çelik", "paslanmaz"], (30, 80)),
    "316 Krom Çelik":           (["316 krom", "316 paslanmaz"], (55, 130)),
    "304 Paslanmaz Krom Hurda": (["304 krom", "304 paslanmaz"], (30, 80)),
    "Krom Talaşı":              (["krom talaş"], (30, 80)),
    "Hurda Alüminyum":          (["hurda alüminyum", "alüminyum hurda"], (70, 160)),
    "Arayiş Alüminyum":         (["arayiş alüminyum", "araış alüminyum"], (110, 200)),
    "Beyaz Profil Alüminyum":   (["profil alüminyum", "beyaz profil"], (110, 200)),
    "Renkli Alüminyum":         (["renkli alüminyum"], (90, 180)),
    "Sineklik Alüminyum":       (["sineklik alüminyum"], (90, 180)),
    "Jant Alüminyum":           (["jant alüminyum", "alüminyum jant"], (65, 150)),
    "Sert Alüminyum":           (["sert alüminyum"], (85, 170)),
    "Kalıp Alüminyum":          (["kalıp alüminyum"], (90, 175)),
    "Ayakkabı Kalıbı Alüminyum": (["ayakkabı kalıbı", "ayakkabı kalıp"], (90, 175)),
    "Sert Nikkelli":            (["sert nikkelli", "nikelli"], (70, 160)),
    "Sert Talaşı":              (["sert talaş"], (55, 135)),
    "Kuru Akü":                 (["kuru akü", "kuru aku"], (18, 50)),
    "Jel Akü":                  (["jel akü", "jel aku"], (18, 50)),
    "Karışık Akü":              (["karışık akü", "karışık aku"], (18, 50)),
    "Sulu Akü":                 (["sulu akü", "sulu aku"], (18, 50)),
    "Levha Çıkma Çinko":        (["levha çinko", "çıkma çinko"], (65, 140)),
    "Karışık Hurda Çinko":      (["hurda çinko", "karışık çinko"], (50, 120)),
    "Çatı Minare Sökümü":       (["çatı minare", "minare söküm"], (50, 120)),
    "Külçe Çinko":              (["külçe çinko"], (50, 120)),
    "Çatı Sökümü":              (["çatı sökümü", "kurşun çatı"], (65, 150)),
    "Külçe Kurşun":             (["külçe kurşun"], (50, 130)),
    "Karışık Kurşun":           (["karışık kurşun"], (50, 130)),
    "Olta Kurşunu":             (["olta kurşun"], (45, 120)),
    "Zamak Curuf":              (["zamak curuf", "curuf"], (30, 90)),
    "Kaplamalı Boyalı":         (["kaplamalı boyalı", "boyalı zamak"], (25, 80)),
    "Menteşe":                  (["menteşe"], (25, 80)),
    "Zamak Karışık":            (["zamak karışık"], (15, 65)),
    "Hurda Kalay Fiyatları":    (["kalay", "hurda kalay"], (750, 1500)),
    "Lehim Hurda Fiyatı":       (["lehim"], (500, 1100)),
    "Motor":                    (["motor hurda"], (40, 110)),
    "Buzdolabı Motor":          (["buzdolabı motor", "buzdolabi motor"], (25, 80)),
    "Karışık Sökülecek":        (["karışık sökülecek", "sökülecek"], (30, 90)),
    "Hurda Karbür":             (["karbür", "karbur"], (500, 1000)),
    "Hurda Elmas":              (["hurda elmas"], (500, 1000)),
    "Nikel Hurda":              (["nikel hurda", "hurda nikel"], (500, 950)),
    "Anot Hurda Nikel":         (["anot nikel"], (500, 950)),
    "Hurda Klima":              (["klima hurda", "hurda klima"], (20, 60)),
    "Hurda Klima Motoru":       (["klima motoru", "klima motor"], (15, 50)),
}

# Kategoriler ve ürün listesi
PRICE_CATEGORIES = [
    {"t": "BAKIR HURDASI", "items": ["Arayiş Bakır", "Kalıp Bakır", "Beyaz Bakır", "Hurda Bakır", "Kırkambar Bakır", 
        "Soyulmuş Bakır Fiyatı", "Lama Bakır İmalat", "Boru Bakır",
        "Yanık Bakır", "Soyma Bakır Fiyatı", "Hurda Bakırlı Petek",
    ]},
    {"t": "SARI HURDASI", "items": [
        "Sarı Hurda", "Musluk", "Pirinç Araiş",
        "Batarya Vana Su Saati", "Sarı Talaşı", "Ms 58 Ms 64 Ms 70",
    ]},
    {"t": "DEMİR HURDASI", "items": [
        "Dkp", "Ekstra", "Toplama", "Mahalle",
    ]},
    {"t": "KABLO HURDASI", "items": ["4x 25", "Alüminyum Kablo", "Tesisat Kablo", "Kıl Kablo", "Enya", 
        "Soyulmamış Kablo", "Ttr Hurda Kablo Fiyatları",
        "Nya Kablo Hurda Fiyatı", "Tekdamar Kalın", "Karışık Bakır Kablo",
    ]},
    {"t": "KROM HURDASI", "items": ["310 Krom", "201 - 202 Krom", 
        "Paslanmaz Çelik Hurda", "316 Krom Çelik",
        "304 Paslanmaz Krom Hurda", "Krom Talaşı",
    ]},
    {"t": "ALÜMİNYUM HURDASI", "items": [
        "Arayiş Alüminyum", "Beyaz Profil Alüminyum",
        "Renkli Alüminyum", "Sineklik Alüminyum", "Jant Alüminyum",
    ]},
    {"t": "SERT ALÜMİNYUM", "items": [
        "Sert Alüminyum", "Kalıp Alüminyum", "Ayakkabı Kalıbı Alüminyum",
        "Sert Nikkelli", "Sert Talaşı",
    ]},
    {"t": "AKÜ HURDASI", "items": [
        "Kuru Akü", "Jel Akü", "Karışık Akü", "Sulu Akü",
    ]},
    {"t": "ÇİNKO HURDASI", "items": [
        "Levha Çıkma Çinko", "Karışık Hurda Çinko",
        "Çatı Minare Sökümü", "Külçe Çinko",
    ]},
    {"t": "KURŞUN HURDASI", "items": [
        "Çatı Sökümü", "Külçe Kurşun", "Karışık Kurşun", "Olta Kurşunu",
    ]},
    {"t": "ZAMAK HURDASI", "items": [
        "Zamak Curuf", "Kaplamalı Boyalı", "Menteşe", "Zamak Karışık",
    ]},
    {"t": "KALAY HURDASI", "items": [
        "Hurda Kalay Fiyatları", "Lehim Hurda Fiyatı",
    ]},
    {"t": "MOTOR VE SÖKÜLECEK HURDASI", "items": ["Karışık", 
        "Motor", "Buzdolabı Motor", "Karışık Sökülecek",
    ]},
    {"t": "ELMAS HURDASI", "items": [
        "Hurda Karbür", "Hurda Elmas",
    ]},
    {"t": "NİKEL HURDASI", "items": [
        "Nikel Hurda", "Anot Hurda Nikel",
    ]},
    {"t": "KLİMA HURDASI", "items": [
        "Hurda Klima", "Hurda Klima Motoru",
    ]},
]

# Sabit piyasa tabanı (gerçek siteden veri alınamazsa kullanılır)
BASE_PRICES = {
    "Soyulmuş Bakır Fiyatı": 552.15,
    "Arayiş Bakır": 635.40,
    "Kalıp Bakır": 629.57,
    "Beyaz Bakır": 600.00,
    "Hurda Bakır": 617.68,
    "Kırkambar Bakır": 620.00,
    "310 Krom": 90.00,
    "201 - 202 Krom": 25.00,
    "4x 25": 551.65,
    "Alüminyum Kablo": 90.00,
    "Tesisat Kablo": 355.00,
    "Kıl Kablo": 201.00,
    "Enya": 581.65,
    "Karışık": 45.00,

    "Lama Bakır İmalat": 522.34,
    "Boru Bakır": 510.24,
    "Yanık Bakır": 500.84,
    "Soyma Bakır Fiyatı": 532.64,
    "Hurda Bakırlı Petek": 228.24,
    "Sarı Hurda": 342.24,
    "Musluk": 320.34,
    "Pirinç Araiş": 350.04,
    "Batarya Vana Su Saati": 345.00,
    "Sarı Talaşı": 350.17,
    "Ms 58 Ms 64 Ms 70": 390.32,
    "Dkp": 12.20,
    "Ekstra": 11.17,
    "Toplama": 10.54,
    "Mahalle": 10.51,
    "Soyulmamış Kablo": 358.11,
    "Ttr Hurda Kablo Fiyatları": 420.00,
    "Nya Kablo Hurda Fiyatı": 470.10,
    "Tekdamar Kalın": 580.00,
    "Karışık Bakır Kablo": 350.82,
    "Paslanmaz Çelik Hurda": 47.11,
    "316 Krom Çelik": 80.50,
    "304 Paslanmaz Krom Hurda": 110.00,
    "Krom Talaşı": 46.18,
    "Hurda Alüminyum": 95.00,
    "Arayiş Alüminyum": 151.65,
    "Beyaz Profil Alüminyum": 150.00,
    "Renkli Alüminyum": 131.65,
    "Sineklik Alüminyum": 131.65,
    "Jant Alüminyum": 95.19,
    "Sert Alüminyum": 115.00,
    "Kalıp Alüminyum": 120.00,
    "Ayakkabı Kalıbı Alüminyum": 120.00,
    "Sert Nikkelli": 100.00,
    "Sert Talaşı": 85.00,
    "Kuru Akü": 28.11,
    "Jel Akü": 28.47,
    "Karışık Akü": 28.16,
    "Sulu Akü": 28.50,
    "Levha Çıkma Çinko": 90.11,
    "Karışık Hurda Çinko": 70.30,
    "Çatı Minare Sökümü": 70.26,
    "Külçe Çinko": 70.50,
    "Çatı Sökümü": 95.01,
    "Külçe Kurşun": 75.50,
    "Karışık Kurşun": 75.16,
    "Olta Kurşunu": 70.50,
    "Zamak Curuf": 50.01,
    "Kaplamalı Boyalı": 45.01,
    "Menteşe": 45.01,
    "Zamak Karışık": 30.01,
    "Hurda Kalay Fiyatları": 1000.11,
    "Lehim Hurda Fiyatı": 710.50,
    "Motor": 61.50,
    "Buzdolabı Motor": 40.00,
    "Karışık Sökülecek": 50.00,
    "Hurda Karbür": 680.12,
    "Hurda Elmas": 680.50,
    "Nikel Hurda": 650.21,
    "Anot Hurda Nikel": 650.50,
    "Hurda Klima": 30.01,
    "Hurda Klima Motoru": 25.50,
}


class HurdaBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Hurda Bot v3 - Gerçek Zamanlı Fiyatlar + Alarm")
        self.root.geometry("750x850")
        self.root.configure(bg="#0d1117")

        self.running = False
        self.previous_prices = self.load_price_history()
        self.scraped_prices = {}  # Gerçek sitelerden çekilen fiyatlar

        # ── Alarm ayarları ──────────────────────────────────────────────────
        self.alarm_enabled = tk.BooleanVar(value=True)
        self.alarm_threshold = tk.DoubleVar(value=2.0)  # %2 değişimde alarm
        self.alarm_items = set()  # Hangi ürünlerde alarm aktif

        self._build_ui()

    # ─────────────────────────── UI ────────────────────────────────────────

    def _build_ui(self):
        root = self.root
        style = ttk.Style()
        style.theme_use("clam")

        # Üst çerçeve
        top = tk.Frame(root, bg="#161b22", pady=10)
        top.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(top, text="⚙ Margin % :", bg="#161b22", fg="#8b949e",
                 font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, pady=4)
        self.margin = tk.DoubleVar(value=0)
        tk.Entry(top, textvariable=self.margin, width=8,
                 bg="#0d1117", fg="white", insertbackground="white").grid(row=0, column=1, padx=5)

        # Alarm ayarları
        tk.Label(top, text="🔔 Alarm Eşiği % :", bg="#161b22", fg="#8b949e",
                 font=("Segoe UI", 10)).grid(row=0, column=2, padx=5)
        tk.Entry(top, textvariable=self.alarm_threshold, width=6,
                 bg="#0d1117", fg="white", insertbackground="white").grid(row=0, column=3, padx=5)

        tk.Checkbutton(top, text="Alarm Aktif", variable=self.alarm_enabled,
                       bg="#161b22", fg="#58a6ff", selectcolor="#0d1117",
                       activebackground="#161b22").grid(row=0, column=4, padx=10)

        # Butonlar
        btn_frame = tk.Frame(root, bg="#0d1117")
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.start_btn = tk.Button(btn_frame, text="▶ BAŞLAT", bg="#238636", fg="white",
                                   font=("Segoe UI", 10, "bold"), padx=20, command=self.start)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(btn_frame, text="■ DURDUR", bg="#da3633", fg="white",
                                  font=("Segoe UI", 10, "bold"), padx=20, command=self.stop)
        self.stop_btn.pack(side="left", padx=5)

        tk.Button(btn_frame, text="🔍 TEK SEFER TEST", bg="#1f6feb", fg="white",
                  font=("Segoe UI", 10, "bold"), padx=10,
                  command=lambda: threading.Thread(target=self.gonder, daemon=True).start()
                  ).pack(side="left", padx=5)

        tk.Button(btn_frame, text="🌐 SCRAPE TEST", bg="#6e40c9", fg="white",
                  font=("Segoe UI", 10, "bold"), padx=10,
                  command=lambda: threading.Thread(target=self._test_scrape, daemon=True).start()
                  ).pack(side="left", padx=5)

        tk.Button(btn_frame, text="🔔 ALARM TEST", bg="#b08800", fg="white",
                  font=("Segoe UI", 10, "bold"), padx=10,
                  command=self._test_alarm
                  ).pack(side="left", padx=5)

        # Durum çubuğu
        self.status_var = tk.StringVar(value="⏸ Bekleniyor")
        status_lbl = tk.Label(root, textvariable=self.status_var,
                              fg="#58a6ff", bg="#0d1117",
                              font=("Segoe UI", 9, "bold"), anchor="w")
        status_lbl.pack(fill="x", padx=15)

        # Log kutusu
        tk.Label(root, text="▼ LOG", bg="#0d1117", fg="#8b949e",
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x", padx=15)
        self.log_box = scrolledtext.ScrolledText(
            root, height=38, bg="#0d1117", fg="#c9d1d9",
            font=("Consolas", 9), insertbackground="white", wrap="word"
        )
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Renk etiketleri
        self.log_box.tag_config("ok",    foreground="#3fb950")
        self.log_box.tag_config("warn",  foreground="#d29922")
        self.log_box.tag_config("err",   foreground="#f85149")
        self.log_box.tag_config("info",  foreground="#58a6ff")
        self.log_box.tag_config("alarm", foreground="#ff7b72", background="#2d1117",
                                font=("Consolas", 9, "bold"))
        self.log_box.tag_config("price", foreground="#e6edf3")

    # ─────────────────────────── LOG ────────────────────────────────────────

    def log(self, text, tag="price"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{ts}] {text}\n", tag)
        self.log_box.see(tk.END)
        self.root.update_idletasks()

    # ─────────────────────────── GEÇMİŞ ────────────────────────────────────

    def load_price_history(self):
        if os.path.exists(PRICES_HISTORY_FILE):
            try:
                with open(PRICES_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_price_history(self, prices):
        try:
            with open(PRICES_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(prices, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"Geçmiş kaydetme hatası: {e}", "err")

    # ─────────────────────────── GERÇEK SCRAPING ────────────────────────────

    def scrape_real_sites(self):
        """Gerçek hurda sitelerinden fiyat scrape et."""
        self.log("=" * 55, "info")
        self.log("GERÇEK SİTELERDEN FİYAT ÇEKME BAŞLIYOR", "info")
        self.log("=" * 55, "info")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        collected_prices = {}  # item_name → [price_values]

        for site in REAL_HURDA_SITES:
            try:
                self.log(f"\n→ Taraniyor: {site['name']} ({site['url']})", "info")
                resp = requests.get(site["url"], headers=headers, timeout=12,
                                    allow_redirects=True)

                if resp.status_code != 200:
                    self.log(f"  ✗ HTTP {resp.status_code}", "err")
                    continue

                # Türkçe karakter dönüşümü
                resp.encoding = resp.apparent_encoding or "utf-8"
                soup = BeautifulSoup(resp.text, "html.parser")

                # Sayfa metnini al – script/style çıkar
                for tag in soup(["script", "style", "nav", "header", "footer"]):
                    tag.decompose()
                page_text = soup.get_text(separator="\n")

                # Her ürün için anahtar kelime tara
                found_count = 0
                for item_name, (keywords, (pmin, pmax)) in ITEM_KEYWORDS.items():
                    lines = page_text.split("\n")
                    for i, line in enumerate(lines):
                        line_lower = line.lower()
                        if any(kw in line_lower for kw in keywords):
                            # Bu satırın ±3 satır yakınında fiyat ara
                            window = "\n".join(lines[max(0, i-2):i+4])
                            prices = self._extract_prices_from_text(window, pmin, pmax)
                            if prices:
                                if item_name not in collected_prices:
                                    collected_prices[item_name] = []
                                collected_prices[item_name].extend(prices)
                                found_count += 1
                                break  # Bu site için bu ürünü buldum

                self.log(f"  ✓ {found_count} ürün fiyatı bulundu", "ok" if found_count > 0 else "warn")

            except requests.exceptions.ConnectionError:
                self.log(f"  ✗ Bağlantı kurulamadı (site çevrimdışı?)", "err")
            except requests.exceptions.Timeout:
                self.log(f"  ✗ Zaman aşımı", "err")
            except Exception as e:
                self.log(f"  ✗ Hata: {e}", "err")

            time.sleep(0.8)  # Rate limit

        # Özet
        self.log(f"\n--- SCRAPING ÖZET ---", "info")
        self.log(f"Fiyat bulunan ürün sayısı: {len(collected_prices)}", "ok")
        for name, vals in list(collected_prices.items())[:8]:
            avg = sum(vals) / len(vals)
            self.log(f"  {name[:35]:35s} → ort. {avg:.2f} TL ({len(vals)} kaynak)", "ok")

        self.scraped_prices = collected_prices
        return collected_prices

    def _extract_prices_from_text(self, text, pmin=1, pmax=10000):
        """Metinden aralıktaki fiyatları çek."""
        patterns = [
            r'₺\s*(\d{1,6}(?:[.,]\d{1,2})?)',
            r'(\d{1,6}(?:[.,]\d{1,2})?)\s*₺',
            r'(\d{1,6}(?:[.,]\d{1,2})?)\s*TL',
            r'TL\s*(\d{1,6}(?:[.,]\d{1,2})?)',
        ]
        found = []
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                raw = m.group(1).replace(".", "").replace(",", ".")
                try:
                    val = float(raw)
                    if pmin <= val <= pmax:
                        found.append(val)
                except ValueError:
                    pass
        return list(set(found))

    def _test_scrape(self):
        """UI'den çağrılan scraping test fonksiyonu."""
        self.status_var.set("🌐 Scraping testi çalışıyor...")
        result = self.scrape_real_sites()
        self.log(f"\n✅ Test tamamlandı. {len(result)} ürün için fiyat çekildi.", "ok")
        self.status_var.set(f"✅ Scraping tamamlandı: {len(result)} ürün")

    # ─────────────────────────── FİYAT HESAPLAMA ────────────────────────────

    def build_price_list(self, scraped):
        """Scraping + base_prices ile tam fiyat listesi oluştur."""
        k = 1 + (self.margin.get() / 100)
        result = []

        for cat in PRICE_CATEGORIES:
            items_out = []
            for iname in cat["items"]:
                base = BASE_PRICES.get(iname, 50.0)

                if iname in scraped and scraped[iname]:
                    # Ortalama al, ±%15 saptırmaları filtrele
                    raw_vals = scraped[iname]
                    avg = sum(raw_vals) / len(raw_vals)
                    filtered = [v for v in raw_vals if abs(v - avg) / avg < 0.15]
                    actual_price = sum(filtered) / len(filtered) if filtered else avg
                    source = "WEB"
                    self.log(f"  [WEB] {iname[:35]:35s}: {actual_price:.2f} TL", "ok")
                else:
                    actual_price = base
                    source = "BASE"
                    self.log(f"  [BASE] {iname[:35]:35s}: {actual_price:.2f} TL", "warn")

                final = round(actual_price * k, 2)
                items_out.append({"n": iname, "p": final, "src": source})

            result.append({"t": cat["t"], "i": items_out})

        return result

    # ─────────────────────────── ALARM SİSTEMİ ──────────────────────────────

    def check_alarms(self, data, changes):
        """Fiyat değişikliklerine göre alarm üret."""
        if not self.alarm_enabled.get():
            return

        threshold = self.alarm_threshold.get()
        alarm_msgs = []

        for key, ch in changes.items():
            if ch["direction"] in ("up", "down") and ch["previous"] is not None:
                abs_pct = abs(ch["percent"])
                if abs_pct >= threshold:
                    arrow = "▲" if ch["direction"] == "up" else "▼"
                    msg = (f"{arrow} ALARM: {key.split('__')[1]} "
                           f"{ch['previous']:.2f} → {ch['current']:.2f} TL "
                           f"({'+' if ch['direction']=='up' else '-'}{abs_pct:.2f}%)")
                    alarm_msgs.append(msg)

        if alarm_msgs:
            self.log("", "alarm")
            self.log("🚨🚨🚨 FİYAT ALARMITRIGGERED 🚨🚨🚨", "alarm")
            for msg in alarm_msgs:
                self.log(msg, "alarm")
            self.log("", "alarm")

            # Pop-up pencere (non-blocking)
            combined = "\n".join(alarm_msgs[:10])
            threading.Thread(
                target=lambda: messagebox.showwarning(
                    "⚠ FİYAT ALARMI!", combined
                ),
                daemon=True
            ).start()

            # Sesli alarm
            try:
                for _ in range(3):
                    winsound.Beep(1000, 300)
                    time.sleep(0.15)
            except Exception:
                pass  # Bazı sistemlerde çalışmayabilir

    def _test_alarm(self):
        """Alarm sistemini test et."""
        self.log("🔔 Alarm testi...", "alarm")
        try:
            for _ in range(3):
                winsound.Beep(1000, 300)
                time.sleep(0.15)
            self.log("✅ Sesli alarm çalıştı!", "ok")
        except Exception as e:
            self.log(f"⚠ Sesli alarm hatası: {e}", "warn")

        threading.Thread(
            target=lambda: messagebox.showinfo(
                "🔔 Alarm Test",
                "Bu bir test alarmı!\n\nFiyat değişimi %2 eşiğini aşarsa bu pencere açılır."
            ),
            daemon=True
        ).start()

    # ─────────────────────────── FİYAT KARŞILAŞTIRMA ───────────────────────

    def compare_prices(self, current_data):
        changes = {}
        for cat in current_data:
            ct = cat["t"]
            for item in cat["i"]:
                key = f"{ct}__{item['n']}"
                cur = item["p"]
                prev = self.previous_prices.get(key)

                if prev:
                    diff = cur - prev
                    pct = (diff / prev) * 100
                    direction = "up" if diff > 0 else ("down" if diff < 0 else "same")
                else:
                    diff, pct, direction = 0, 0, "new"

                changes[key] = {
                    "current": cur, "previous": prev,
                    "change": diff, "percent": pct, "direction": direction
                }
        return changes

    # ─────────────────────────── ANA DÖNGÜ ──────────────────────────────────

    def gonder(self):
        self.status_var.set("🔄 Fiyatlar çekiliyor...")

        # 1) Gerçek sitelerden scraping
        scraped = self.scrape_real_sites()

        # 2) Fiyat listesi oluştur
        self.log("\n--- FİYAT LİSTESİ OLUŞTURULUYOR ---", "info")
        data = self.build_price_list(scraped)

        # 3) Fiyat değişikliklerini hesapla
        changes = self.compare_prices(data)

        # 4) Alarm kontrolü
        self.check_alarms(data, changes)

        # 5) Değişim özetini logla
        up = sum(1 for c in changes.values() if c["direction"] == "up")
        dn = sum(1 for c in changes.values() if c["direction"] == "down")
        sa = sum(1 for c in changes.values() if c["direction"] == "same")
        nw = sum(1 for c in changes.values() if c["direction"] == "new")
        self.log(f"\nÖzet: ▲{up} yükseldi | ▼{dn} düştü | ={sa} değişmedi | ★{nw} yeni", "info")

        # Değişim detayları
        for key, ch in changes.items():
            if ch["direction"] == "up":
                self.log(f"  ↑ {key}: {ch['previous']:.2f} → {ch['current']:.2f} (+{ch['percent']:.1f}%)", "ok")
            elif ch["direction"] == "down":
                self.log(f"  ↓ {key}: {ch['previous']:.2f} → {ch['current']:.2f} ({ch['percent']:.1f}%)", "err")

        # 6) Data'ya change bilgisi ekle
        for cat in data:
            for item in cat["i"]:
                key = f"{cat['t']}__{item['n']}"
                if key in changes:
                    ch = changes[key]
                    item["change"] = ch["direction"]
                    item["percent"] = round(ch["percent"], 2)

        # 7) 5 siteye gönder
        self.log("\n" + "=" * 55, "info")
        self.log("FİYATLAR 5 SİTEYE GÖNDERİLİYOR", "info")
        self.log("=" * 55, "info")

        # Gönderim verisinden "src" alanını çıkar (PHP beklemiyor)
        send_data = []
        for cat in data:
            send_data.append({
                "t": cat["t"],
                "i": [{"n": i["n"], "p": i["p"],
                        "change": i.get("change", "same"),
                        "percent": i.get("percent", 0)} for i in cat["i"]]
            })

        success_count = 0
        for site_url in POST_URLS:
            site_name = site_url.split("//")[1].split("/")[0]
            try:
                r = requests.post(
                    site_url,
                    data={"key": SECRET_KEY, "data": json.dumps(send_data, ensure_ascii=False)},
                    timeout=10
                )
                if r.status_code == 200:
                    self.log(f"  ✓ {site_name}: {r.text.strip()}", "ok")
                    success_count += 1
                else:
                    self.log(f"  ✗ {site_name}: HTTP {r.status_code}", "err")
            except Exception as e:
                self.log(f"  ✗ {site_name}: {e}", "err")

        self.log(f"\n✅ {success_count}/{len(POST_URLS)} site güncellendi.", "ok")

        # 8) Geçmişi kaydet
        history = {}
        for cat in data:
            for item in cat["i"]:
                history[f"{cat['t']}__{item['n']}"] = item["p"]
        self.save_price_history(history)
        self.previous_prices = history

        now = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"✅ Son güncelleme: {now}  |  WEB: {len(scraped)} ürün  |  Gönderim: {success_count}/{len(POST_URLS)}")

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.loop, daemon=True).start()
            self.log("▶ Bot başlatıldı", "ok")

    def stop(self):
        self.running = False
        self.status_var.set("⏸ Bot durduruldu")
        self.log("■ Bot durduruldu", "warn")

    def loop(self):
        while self.running:
            try:
                self.gonder()
                self.log("⏳ 60 saniye bekleniyor...", "info")
                for _ in range(60):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                self.log(f"DÖNGÜ HATASI: {e}", "err")
                time.sleep(5)


if __name__ == "__main__":
    root = tk.Tk()
    app = HurdaBot(root)
    root.mainloop()