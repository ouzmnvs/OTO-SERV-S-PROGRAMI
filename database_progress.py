# Database fonskiyonlarım burada olacak
import sqlite3
import os
import json
import shutil
from datetime import datetime

def get_db_path():
    """
    Programın kullandığı veritabanı dosyası.
    Eskiden yedek klasöründe 'oto_servis.db' adlı bir dosya varsa o kullanılıyordu; ancak programın diğer
    ekranları her zaman kendi klasöründeki dosyayı kullandığı için veriler iki dosyaya bölünebiliyordu.
    """
    return "oto_servis.db"

def recover_database():
    """Ana veritabanı bozulduğunda yedekten geri yükleme yapar"""
    config_file = "db_config.json"
    default_db_path = "oto_servis.db"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                backup_path = config.get('backup_path')
                if backup_path:
                    backup_db = os.path.join(backup_path, "oto_servis.db")
                    if os.path.exists(backup_db):
                        # Yedek dosyasını ana konuma kopyala
                        shutil.copy2(backup_db, default_db_path)
                        print(f"Veritabanı başarıyla yedekten geri yüklendi: {default_db_path}")
                        return True
    except Exception as e:
        print(f"Veritabanı kurtarma hatası: {str(e)}")
    
    return False

# Sık kullanılan sorgular için indeksler (eski veritabanlarına zarar vermez, sadece hızlandırır)
_INDEKSLER = [
    "CREATE INDEX IF NOT EXISTS idx_islemler_servis_id ON islemler(servis_id)",
    "CREATE INDEX IF NOT EXISTS idx_teklif_islemler_teklif_id ON teklif_islemler(teklif_id)",
    "CREATE INDEX IF NOT EXISTS idx_servisler_plaka ON servisler(plaka)",
    "CREATE INDEX IF NOT EXISTS idx_servisler_cari_kodu ON servisler(cari_kodu)",
    "CREATE INDEX IF NOT EXISTS idx_servisler_durum ON servisler(servis_durumu)",
    "CREATE INDEX IF NOT EXISTS idx_kasa_servis_id ON kasa(servis_id)",
    "CREATE INDEX IF NOT EXISTS idx_araclar_cari_kodu ON araclar(cari_kodu)",
    "CREATE INDEX IF NOT EXISTS idx_teklifler_cari_kodu ON teklifler(cari_kodu)",
]

# Programın beklediği tablolar (create_database.py ile aynı)
_TABLOLAR = {
    "cariler": """CREATE TABLE IF NOT EXISTS cariler (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cari_kodu TEXT NOT NULL UNIQUE, cari_ad_unvan TEXT NOT NULL,
        cari_tipi TEXT, tc_kimlik_no TEXT, vergi_no TEXT, cep_telefonu TEXT, aciklama TEXT)""",
    "araclar": """CREATE TABLE IF NOT EXISTS araclar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cari_kodu TEXT NOT NULL, plaka TEXT NOT NULL UNIQUE, marka TEXT,
        model TEXT, model_yili INTEGER, motor_no TEXT, sasi_no TEXT, arac_tipi TEXT, motor_hacmi TEXT,
        motor_gucu_kw TEXT, yakit_cinsi TEXT, son_bakim_tarihi TEXT, aciklama TEXT, ruhsat_foto TEXT,
        FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE CASCADE)""",
    "servisler": """CREATE TABLE IF NOT EXISTS servisler (
        id INTEGER PRIMARY KEY AUTOINCREMENT, plaka TEXT NOT NULL, cari_kodu TEXT NOT NULL,
        servis_tutar REAL DEFAULT 0, servis_kapanis_tutar REAL, servis_kapanis_tarihi TEXT, aciklama TEXT,
        servis_durumu TEXT DEFAULT 'Açık', servis_tarihi TEXT NOT NULL, arac_getiren_kisi TEXT,
        giris_km INTEGER, cikis_km INTEGER,
        FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE NO ACTION,
        FOREIGN KEY (plaka) REFERENCES araclar (plaka) ON DELETE NO ACTION)""",
    "islemler": """CREATE TABLE IF NOT EXISTS islemler (
        id INTEGER PRIMARY KEY AUTOINCREMENT, servis_id INTEGER NOT NULL, islem_aciklama TEXT NOT NULL,
        islem_tutari REAL NOT NULL, kdv_orani REAL DEFAULT 20, kdv_tutari REAL, aciklama TEXT,
        miktar INTEGER DEFAULT 1,
        FOREIGN KEY (servis_id) REFERENCES servisler (id) ON DELETE CASCADE)""",
    "kasa": """CREATE TABLE IF NOT EXISTS kasa (
        id INTEGER PRIMARY KEY AUTOINCREMENT, servis_id INTEGER, cari_kodu TEXT, cari_ad_unvan TEXT, plaka TEXT,
        tarih TEXT NOT NULL, tutar REAL NOT NULL, odeme_tipi TEXT NOT NULL, odeme_kaynagi TEXT, kaynak_id INTEGER,
        aciklama TEXT,
        FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE NO ACTION)""",
    "teklifler": """CREATE TABLE IF NOT EXISTS teklifler (
        id INTEGER PRIMARY KEY AUTOINCREMENT, teklif_no TEXT NOT NULL UNIQUE, cari_kodu TEXT NOT NULL,
        plaka TEXT NOT NULL, teklif_tarihi TEXT NOT NULL, gecerlilik_tarihi TEXT NOT NULL, odeme_sekli TEXT NOT NULL,
        odeme_vade_gun INTEGER, teklif_veren_personel TEXT NOT NULL, teklif_alan TEXT, aciklama TEXT,
        toplam_tutar REAL DEFAULT 0, teklif_durumu TEXT DEFAULT 'Açık',
        FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE NO ACTION,
        FOREIGN KEY (plaka) REFERENCES araclar (plaka) ON DELETE NO ACTION)""",
    "teklif_islemler": """CREATE TABLE IF NOT EXISTS teklif_islemler (
        id INTEGER PRIMARY KEY AUTOINCREMENT, teklif_id INTEGER NOT NULL, islem_aciklama TEXT NOT NULL,
        islem_tutari REAL NOT NULL, kdv_orani REAL DEFAULT 20, kdv_tutari REAL, aciklama TEXT,
        miktar INTEGER DEFAULT 1,
        FOREIGN KEY (teklif_id) REFERENCES teklifler (id) ON DELETE CASCADE)""",
}

# Programın farklı sürümlerinde sonradan eklenmiş kolonlar; eski bir veritabanında yoksa eklenir
_SONRADAN_EKLENEN_KOLONLAR = {
    "cariler": [("cari_tipi", "TEXT"), ("tc_kimlik_no", "TEXT"), ("vergi_no", "TEXT"), ("cep_telefonu", "TEXT"),
                ("aciklama", "TEXT")],
    "araclar": [("marka", "TEXT"), ("model", "TEXT"), ("model_yili", "INTEGER"), ("motor_no", "TEXT"),
                ("sasi_no", "TEXT"), ("arac_tipi", "TEXT"), ("motor_hacmi", "TEXT"), ("motor_gucu_kw", "TEXT"),
                ("yakit_cinsi", "TEXT"), ("son_bakim_tarihi", "TEXT"), ("aciklama", "TEXT"), ("ruhsat_foto", "TEXT")],
    "servisler": [("servis_tutar", "REAL DEFAULT 0"), ("servis_kapanis_tutar", "REAL"),
                  ("servis_kapanis_tarihi", "TEXT"), ("aciklama", "TEXT"), ("servis_durumu", "TEXT DEFAULT 'Açık'"),
                  ("arac_getiren_kisi", "TEXT"), ("giris_km", "INTEGER"), ("cikis_km", "INTEGER")],
    "islemler": [("kdv_orani", "REAL DEFAULT 20"), ("kdv_tutari", "REAL"), ("aciklama", "TEXT"),
                 ("miktar", "INTEGER DEFAULT 1")],
    "kasa": [("servis_id", "INTEGER"), ("cari_kodu", "TEXT"), ("cari_ad_unvan", "TEXT"), ("plaka", "TEXT"),
             ("odeme_kaynagi", "TEXT"), ("kaynak_id", "INTEGER"), ("aciklama", "TEXT")],
    "teklifler": [("odeme_vade_gun", "INTEGER"), ("teklif_alan", "TEXT"), ("aciklama", "TEXT"),
                  ("toplam_tutar", "REAL DEFAULT 0"), ("teklif_durumu", "TEXT DEFAULT 'Açık'")],
    "teklif_islemler": [("kdv_orani", "REAL DEFAULT 20"), ("kdv_tutari", "REAL"), ("aciklama", "TEXT"),
                        ("miktar", "INTEGER DEFAULT 1")],
}

_SEMA_KONTROL_EDILDI = set()  # (dosya, değişiklik zamanı, boyut): aynı dosyayı her bağlantıda yeniden taramamak için


def ensure_schema(conn):
    """
    Eski, eksik ya da boş veritabanlarını programın beklediği yapıya getirir: olmayan tabloları oluşturur,
    sonradan eklenmiş kolonları ve indeksleri ekler. Mevcut veriye dokunmaz, tekrar çalıştırmak güvenlidir.
    """
    dosya = conn.execute("PRAGMA database_list").fetchone()[2]
    try:
        bilgi = os.stat(dosya)
        anahtar = (os.path.abspath(dosya), bilgi.st_mtime_ns, bilgi.st_size)
    except OSError:
        anahtar = None
    if anahtar in _SEMA_KONTROL_EDILDI:
        return

    mevcut = {}
    for tablo in _TABLOLAR:
        mevcut[tablo] = {row[1] for row in conn.execute(f"PRAGMA table_info({tablo})")}
    eksik_tablo = [t for t, kolonlar in mevcut.items() if not kolonlar]
    eksik_kolon = [(t, ad, tip) for t, liste in _SONRADAN_EKLENEN_KOLONLAR.items() if mevcut[t]
                   for ad, tip in liste if ad not in mevcut[t]]
    indeksler = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
    eksik_indeks = [sql for sql in _INDEKSLER if sql.split(" ON ")[0].split()[-1] not in indeksler]

    if eksik_tablo or eksik_kolon or eksik_indeks:
        try:
            with conn:
                for tablo in eksik_tablo:
                    conn.execute(_TABLOLAR[tablo])
                for tablo, ad, tip in eksik_kolon:
                    conn.execute(f"ALTER TABLE {tablo} ADD COLUMN {ad} {tip}")
                    if (tablo, ad) == ("kasa", "odeme_kaynagi"):
                        # Bu kolondan önceki sürümlerde ödemeler yalnızca servisler için alınıyordu
                        conn.execute("UPDATE kasa SET odeme_kaynagi = 'SERVIS' WHERE servis_id IS NOT NULL")
                    if (tablo, ad) == ("kasa", "kaynak_id"):
                        conn.execute("UPDATE kasa SET kaynak_id = servis_id WHERE kaynak_id IS NULL AND servis_id IS NOT NULL")
                for sql in _INDEKSLER:
                    conn.execute(sql)
        except sqlite3.Error as e:
            print(f"Veritabanı şeması güncellenemedi: {e}")
            return
        try:
            bilgi = os.stat(dosya)
            anahtar = (os.path.abspath(dosya), bilgi.st_mtime_ns, bilgi.st_size)
        except OSError:
            anahtar = None
    if anahtar:
        _SEMA_KONTROL_EDILDI.add(anahtar)


def veritabani_sorunu(yol=None):
    """
    Veritabanı açılıp kullanılabiliyorsa None, değilse sorunu anlatan bir metin döndürür.
    Açılabiliyorsa eksik tablo/kolonları da tamamlar.
    """
    try:
        conn = sqlite3.connect(yol or get_db_path())
        try:
            ensure_schema(conn)
            sonuc = conn.execute("PRAGMA quick_check").fetchone()[0]
            if sonuc != "ok":
                return f"Veritabanı dosyası bozuk ({sonuc})."
            eksik = [t for t in _TABLOLAR if not conn.execute(f"PRAGMA table_info({t})").fetchall()]
            if eksik:
                return f"Veritabanında şu tablolar oluşturulamadı: {', '.join(eksik)}."
            try:
                # Yazılabiliyor mu? Geri alınan bir deneme yazması yapılır, veritabanında hiçbir şey değişmez.
                # (SQLite yazılamayan dosyayı sessizce salt okunur açar; hata ancak gerçek yazmada çıkar.)
                conn.execute("BEGIN IMMEDIATE")
                conn.execute("CREATE TABLE IF NOT EXISTS _yazma_denemesi (x INTEGER)")
                conn.rollback()
            except sqlite3.OperationalError as e:
                try:
                    conn.rollback()
                except sqlite3.Error:
                    pass
                hata = str(e).lower()
                if "readonly" in hata or "read-only" in hata or "unable to open" in hata:
                    return ("Veritabanı dosyası salt okunur ya da klasöre yazılamıyor; kayıt yapılamaz.\n"
                            "Dosyaya sağ tıklayıp Özellikler'den 'Salt okunur' işaretini kaldırın veya programı "
                            "yazılabilir bir klasöre (örn. C:\\OTO-SERVIS) taşıyın.")
            return None
        finally:
            conn.close()
    except sqlite3.Error as e:
        return f"Veritabanı dosyası açılamıyor: {e}"

def get_db_connection():
    """Veritabanı bağlantısı oluşturur"""
    db_path = get_db_path()

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")  # Basit bir sorgu ile veritabanını test et
    except sqlite3.Error:
        # Veritabanı bozuksa veya erişilemiyorsa
        print("Veritabanı bağlantısı başarısız, yedekten kurtarma deneniyor...")

        # Yedekten kurtarmayı dene
        if recover_database():
            # Kurtarma başarılıysa yeni bağlantı oluştur
            conn = sqlite3.connect(db_path)
        else:
            # Kurtarma başarısızsa hata fırlat
            raise Exception("Veritabanı bağlantısı kurulamadı ve yedekten kurtarma başarısız oldu.")

    # Yedekten geri yüklenen eski bir veritabanı da olabilir; şemayı her bağlantıda ucuzca kontrol et
    ensure_schema(conn)
    return conn

def backup_database():
    """Veritabanının yedeğini alır"""
    config_file = "db_config.json"
    default_db_path = "oto_servis.db"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                backup_path = config.get('backup_path')
                if backup_path:
                    # Yedekleme klasörünü oluştur
                    if not os.path.exists(backup_path):
                        os.makedirs(backup_path)
                    
                    # Yedek dosya adını tarih ile oluştur
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = os.path.join(backup_path, f"oto_servis_backup_{timestamp}.db")
                    
                    # Veritabanını yedekle
                    shutil.copy2(default_db_path, backup_file)
                    print(f"Veritabanı yedeği alındı: {backup_file}")
                    return True
    except Exception as e:
        print(f"Veritabanı yedekleme hatası: {str(e)}")
    
    return False

def load_cari_list_for_select():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi FROM cariler")
    result = cursor.fetchall()
    conn.close()
    return result

def load_cari_list_for_table():
    """
    Cari listesini tabloya uygun şekilde döndürür.
    (cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi, toplam_tutar, aciklama)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.cari_kodu,
            c.cari_ad_unvan,
            c.cep_telefonu,
            c.cari_tipi,
            COALESCE(
                SUM(
                    CASE 
                        WHEN s.servis_durumu = 'Kapalı' THEN s.servis_tutar
                        WHEN s.servis_durumu = 'Açık' THEN s.servis_tutar
                        ELSE 0
                    END
                ), 0
            ) as toplam_tutar,
            c.aciklama
        FROM cariler c
        LEFT JOIN araclar a ON c.cari_kodu = a.cari_kodu
        LEFT JOIN servisler s ON a.plaka = s.plaka
        GROUP BY c.cari_kodu, c.cari_ad_unvan, c.cep_telefonu, c.cari_tipi, c.aciklama
        ORDER BY c.cari_kodu
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def load_cari_plakalari():
    """Cari listesinde plakayla arama için {cari_kodu: 'plaka1 plaka2 ...'} döndürür."""
    conn = get_db_connection()
    try:
        return dict(conn.execute("""
            SELECT cari_kodu, GROUP_CONCAT(plaka, ' ') FROM araclar GROUP BY cari_kodu
        """).fetchall())
    finally:
        conn.close()

def load_car_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            a.cari_kodu,
            c.cari_ad_unvan,
            a.plaka,
            a.arac_tipi,
            a.model_yili,
            a.marka,
            a.model
        FROM araclar a
        LEFT JOIN cariler c ON a.cari_kodu = c.cari_kodu
        ORDER BY a.id DESC
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def load_car_list_by_cari(cari_kodu):
    """
    Belirli bir cari_kodu'na ait araçları (plaka, araç_tipi, model_yili, marka, model) döndürür.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            plaka,
            arac_tipi,
            model_yili,
            marka,
            model
        FROM araclar
        WHERE cari_kodu = ?
        ORDER BY id DESC
    """, (cari_kodu,))
    result = cursor.fetchall()
    conn.close()
    return result

def load_open_services():
    """
    servis_durumu 'Açık' olan servisleri döndürür.
    (servis_id, cari_kodu, cari_unvan, plaka, tarih, tutar, durum, arac_getiren_kisi)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.id,
            s.cari_kodu,
            c.cari_ad_unvan,
            s.plaka,
            s.servis_tarihi,
            s.servis_tutar,
            s.servis_durumu,
            s.arac_getiren_kisi
        FROM servisler s
        LEFT JOIN cariler c ON s.cari_kodu = c.cari_kodu
        WHERE s.servis_durumu = 'Açık'
        ORDER BY s.id DESC
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def load_open_services_with_totals():
    """
    load_open_services ile aynı satırları döndürür, ancak tutar sütunu işlemlerden
    (islem_tutari + kdv_tutari) tek sorguda hesaplanır. İşlemi olmayan serviste servis_tutar kullanılır.
    Aramada kullanılmak üzere sonda cari telefonu da gelir.
    (servis_id, cari_kodu, cari_unvan, plaka, tarih, tutar, durum, arac_getiren_kisi, telefon)
    """
    conn = get_db_connection()
    try:
        return conn.execute("""
            SELECT
                s.id,
                s.cari_kodu,
                c.cari_ad_unvan,
                s.plaka,
                s.servis_tarihi,
                COALESCE(t.toplam, s.servis_tutar),
                s.servis_durumu,
                s.arac_getiren_kisi,
                c.cep_telefonu
            FROM servisler s
            LEFT JOIN cariler c ON s.cari_kodu = c.cari_kodu
            LEFT JOIN (
                SELECT servis_id, SUM(islem_tutari) + SUM(kdv_tutari) AS toplam
                FROM islemler
                GROUP BY servis_id
            ) t ON t.servis_id = s.id
            WHERE s.servis_durumu = 'Açık'
            ORDER BY s.id DESC
        """).fetchall()
    finally:
        conn.close()

def load_closed_services():
    """
    servis_durumu 'Kapalı' olan servisleri döndürür.
    (servis_id, cari_kodu, cari_unvan, plaka, tarih, tutar, durum, arac_getiren_kisi)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.id,
            s.cari_kodu,
            c.cari_ad_unvan,
            s.plaka,
            s.servis_tarihi,
            s.servis_tutar,
            s.servis_durumu,
            s.arac_getiren_kisi
        FROM servisler s
        LEFT JOIN cariler c ON s.cari_kodu = c.cari_kodu
        WHERE s.servis_durumu = 'Kapalı'
        ORDER BY s.id DESC
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def close_service(servis_id, servis_kapanis_tutar, cikis_km=None):
    """
    Verilen servis_id'li servisin durumunu 'Kapalı' yapar ve kapanış tutarını kaydeder.
    Ayrıca aracın son bakım tarihini günceller. cikis_km verilirse araç çıkış km'si de kaydedilir.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Önce servisin plakasını al
    cursor.execute("SELECT plaka FROM servisler WHERE id = ?", (servis_id,))
    plaka = cursor.fetchone()[0]

    # Servisi kapat
    cursor.execute("""
        UPDATE servisler
        SET servis_durumu = 'Kapalı',
            servis_kapanis_tutar = ?,
            servis_kapanis_tarihi = date('now'),
            cikis_km = COALESCE(?, cikis_km)
        WHERE id = ?
    """, (servis_kapanis_tutar, cikis_km, servis_id))
    
    # Aracın son bakım tarihini güncelle
    cursor.execute("""
        UPDATE araclar
        SET son_bakim_tarihi = date('now')
        WHERE plaka = ?
    """, (plaka,))
    
    conn.commit()
    conn.close()

def add_servis(cari_kodu, plaka, servis_tarihi, aciklama, arac_getiren_kisi, giris_km=None):
    """
    Yeni bir servis kaydı oluşturur ve servis_id döndürür.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO servisler (cari_kodu, plaka, servis_tarihi, aciklama, servis_durumu, arac_getiren_kisi, giris_km)
        VALUES (?, ?, ?, ?, 'Açık', ?, ?)
    """, (cari_kodu, plaka, servis_tarihi, aciklama, arac_getiren_kisi, giris_km))
    servis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return servis_id

def _islemleri_ekle(conn, servis_id, islemler):
    """islemler: [(islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar), ...]"""
    conn.executemany("""
        INSERT INTO islemler (servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [(servis_id, *islem) for islem in islemler])

def add_servis_ve_islemler(cari_kodu, plaka, servis_tarihi, aciklama, arac_getiren_kisi, islemler, giris_km=None):
    """
    Servisi ve tüm işlemlerini tek seferde (tek transaction) kaydeder, servis_id döndürür.
    Her işlem için ayrı bağlantı açmaktan çok daha hızlıdır; hata olursa hiçbir şey yarım kalmaz.
    islemler: [(islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar), ...]
    """
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.execute("""
                INSERT INTO servisler (cari_kodu, plaka, servis_tarihi, aciklama, servis_durumu, arac_getiren_kisi, giris_km)
                VALUES (?, ?, ?, ?, 'Açık', ?, ?)
            """, (cari_kodu, plaka, servis_tarihi, aciklama, arac_getiren_kisi, giris_km))
            servis_id = cursor.lastrowid
            _islemleri_ekle(conn, servis_id, islemler)
            _servis_tutar_hesapla(conn, servis_id)
        return servis_id
    finally:
        conn.close()

def update_servis_ve_islemler(servis_id, cari_kodu, plaka, aciklama, arac_getiren_kisi,
                              silinecek_islem_idleri, islemler, giris_km=None, cikis_km=None):
    """
    Servis bilgilerini günceller, verilen işlemleri silip yenilerini ekler ve servis tutarını
    yeniden hesaplar; hepsi tek transaction'da.
    islemler: [(islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar), ...]
    """
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
                UPDATE servisler
                SET cari_kodu = ?, plaka = ?, aciklama = ?, arac_getiren_kisi = ?, giris_km = ?, cikis_km = ?
                WHERE id = ?
            """, (cari_kodu, plaka, aciklama, arac_getiren_kisi, giris_km, cikis_km, servis_id))
            conn.executemany("DELETE FROM islemler WHERE id = ?", [(islem_id,) for islem_id in silinecek_islem_idleri])
            _islemleri_ekle(conn, servis_id, islemler)
            if silinecek_islem_idleri or islemler:
                _servis_tutar_hesapla(conn, servis_id)
    finally:
        conn.close()

def add_islem(servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar=1):
    """Yeni bir işlem ekler."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO islemler (servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar))
    conn.commit()
    conn.close()
    update_servis_tutar(servis_id)  # İşlem eklenince servis tutarını güncelle

def delete_service(servis_id):
    """
    Verilen servis_id'ye sahip servisi ve ilişkili işlemleri siler.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # <-- Bunu ekleyin!
    cursor.execute("DELETE FROM servisler WHERE id = ?", (servis_id,))
    conn.commit()
    conn.close()

def get_service_full_details(servis_id):
    """
    Bir servise ait cari bilgileri, araç bilgisi ve işlem listesini döndürür.
    Dönüş: {
        "servis": {...},
        "cari": {...},
        "arac": {...},
        "islemler": [ {...}, ... ]
    }
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Servis bilgisi
    cursor.execute("""
        SELECT id, cari_kodu, plaka, servis_tarihi, servis_tutar, servis_durumu, aciklama, arac_getiren_kisi, servis_kapanis_tutar,
               servis_kapanis_tarihi, giris_km, cikis_km
        FROM servisler
        WHERE id = ?
    """, (servis_id,))
    servis = cursor.fetchone()
    if not servis:
        conn.close()
        return None

    servis_dict = {
        "id": servis[0],
        "cari_kodu": servis[1],
        "plaka": servis[2],
        "servis_tarihi": servis[3],
        "servis_tutar": servis[4],
        "servis_durumu": servis[5],
        "aciklama": servis[6],
        "arac_getiren_kisi": servis[7],
        "servis_kapanis_tutar": servis[8],
        "servis_kapanis_tarihi": servis[9],
        "giris_km": servis[10],
        "cikis_km": servis[11]
    }

    # Cari bilgisi
    cursor.execute("""
        SELECT cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi, aciklama, vergi_no, tc_kimlik_no
        FROM cariler
        WHERE cari_kodu = ?
    """, (servis_dict["cari_kodu"],))
    cari = cursor.fetchone()
    cari_dict = {
        "cari_kodu": cari[0],
        "cari_ad_unvan": cari[1],
        "cep_telefonu": cari[2],
        "cari_tipi": cari[3],
        "aciklama": cari[4],
        "vergi_no": cari[5],
        "tc_kimlik_no": cari[6]
    } if cari else {}

    # Araç bilgisi
    cursor.execute("""
        SELECT plaka, marka, model, model_yili, arac_tipi, motor_no, sasi_no, yakit_cinsi
        FROM araclar
        WHERE plaka = ?
    """, (servis_dict["plaka"],))
    arac = cursor.fetchone()
    arac_dict = {
        "plaka": arac[0],
        "marka": arac[1],
        "model": arac[2],
        "model_yili": arac[3],
        "arac_tipi": arac[4],
        "motor_no": arac[5],
        "sasi_no": arac[6],
        "yakit_cinsi": arac[7]
    } if arac else {}

    # İşlem listesi
    cursor.execute("""
        SELECT id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar
        FROM islemler
        WHERE servis_id = ?
        ORDER BY id
    """, (servis_id,))
    islemler = cursor.fetchall()
    islemler_list = [
        {
            "id": row[0],
            "islem_aciklama": row[1],
            "islem_tutari": row[2],
            "kdv_orani": row[3],
            "kdv_tutari": row[4],
            "aciklama": row[5],
            "miktar": row[6]
        }
        for row in islemler
    ]

    conn.close()
    return {
        "servis": servis_dict,
        "cari": cari_dict,
        "arac": arac_dict,
        "islemler": islemler_list
    }

def get_servis_odenen_tutar(servis_id):
    """Servis için kasaya girilmiş ödemelerin toplamını döndürür."""
    conn = get_db_connection()
    try:
        return conn.execute("""
            SELECT COALESCE(SUM(tutar), 0) FROM kasa
            WHERE servis_id = ? AND odeme_kaynagi = 'SERVIS'
        """, (servis_id,)).fetchone()[0]
    finally:
        conn.close()

def get_son_km(plaka):
    """Aracın önceki servislerde kaydedilmiş en yüksek km değerini döndürür (yoksa None)."""
    conn = get_db_connection()
    try:
        km = conn.execute("""
            SELECT MAX(MAX(COALESCE(giris_km, 0), COALESCE(cikis_km, 0)))
            FROM servisler WHERE plaka = ?
        """, (plaka,)).fetchone()[0]
        return km or None
    finally:
        conn.close()

def load_service_operations(servis_id):
    """
    Belirli bir servise ait işlemleri döndürür.
    Dönüş: [(id, islem_aciklama, islem_tutari, kdv_orani, aciklama), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, islem_aciklama, islem_tutari, kdv_orani, aciklama
        FROM islemler
        WHERE servis_id = ?
        ORDER BY id ASC
    """, (servis_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def update_servis(servis_id, cari_kodu, plaka, aciklama, arac_getiren_kisi):
    """
    Servis bilgilerini günceller.
    Args:
        servis_id: Güncellenecek servisin ID'si
        cari_kodu: Cari kodu
        plaka: Araç plakası
        aciklama: Müşteri talepleri ve servis açıklaması
        arac_getiren_kisi: Aracı getiren kişinin adı
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE servisler 
        SET cari_kodu = ?, plaka = ?, aciklama = ?, arac_getiren_kisi = ?
        WHERE id = ?
    """, (cari_kodu, plaka, aciklama, arac_getiren_kisi, servis_id))
    conn.commit()
    conn.close()

def delete_islem_by_id(islem_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Önce servis_id'yi bul
    cursor.execute("SELECT servis_id FROM islemler WHERE id = ?", (islem_id,))
    row = cursor.fetchone()
    servis_id = row[0] if row else None
    cursor.execute("DELETE FROM islemler WHERE id = ?", (islem_id,))
    conn.commit()
    conn.close()
    if servis_id:
        update_servis_tutar(servis_id)  # Silindikten sonra toplamı güncelle

def _servis_tutar_hesapla(conn, servis_id):
    """update_servis_tutar'ın açık bir bağlantı/transaction içinde çalışan hali."""
    toplam = conn.execute("""
        SELECT SUM(islem_tutari + kdv_tutari) FROM islemler WHERE servis_id = ?
    """, (servis_id,)).fetchone()[0] or 0.0
    conn.execute("""
        UPDATE servisler SET servis_tutar = ? WHERE id = ?
    """, (toplam, servis_id))

def update_servis_tutar(servis_id):
    """
    Belirtilen servisin işlemlerinin toplam tutarını hesaplar ve servis_tutar alanını günceller.
    """
    conn = get_db_connection()
    _servis_tutar_hesapla(conn, servis_id)
    conn.commit()
    conn.close()

def load_servis_kayitlari_by_plaka(plaka, search_text=None):
    """
    Belirtilen plakaya ait TÜM servisleri döndürür:
    (servis_id, servis_tarihi, toplam_servis_tutari_kdv_dahil, servis_durumu, aciklama)
    Args:
        plaka: Araç plakası
        search_text: Arama metni (opsiyonel). Her kelime açıklama, durum veya tarihte geçmelidir;
                     Türkçe harf ve büyük/küçük harf farkı yok sayılır.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            s.id,
            s.servis_tarihi,
            COALESCE(SUM(i.islem_tutari), 0) + COALESCE(SUM(i.kdv_tutari), 0) as toplam_tutar_kdv_dahil,
            s.servis_durumu,
            s.aciklama
        FROM servisler s
        LEFT JOIN islemler i ON s.id = i.servis_id
        WHERE s.plaka = ?
        GROUP BY s.id, s.servis_tarihi, s.servis_durumu, s.aciklama
        ORDER BY s.servis_tarihi DESC
    """, (plaka,))
    result = cursor.fetchall()
    conn.close()
    if search_text:
        # SQLite LIKE Türkçe harflerde büyük/küçük eşleştiremediği için filtre Python'da yapılır
        from arama import eslesir
        result = [r for r in result if eslesir(search_text, r[4], r[3], r[1])]
    return result

def add_teklif(teklif_no, cari_kodu, plaka, teklif_tarihi, gecerlilik_tarihi, 
               odeme_sekli, odeme_vade_gun, teklif_veren_personel, teklif_alan, aciklama):
    """
    Yeni bir teklif kaydı oluşturur ve teklif_id döndürür.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL sorgusunu hazırla
    query = """
        INSERT INTO teklifler (
            teklif_no, cari_kodu, plaka, teklif_tarihi, gecerlilik_tarihi,
            odeme_sekli, odeme_vade_gun, teklif_veren_personel, teklif_alan, aciklama
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Parametreleri hazırla
    params = (
        teklif_no, cari_kodu, plaka, teklif_tarihi, gecerlilik_tarihi,
        odeme_sekli, odeme_vade_gun, teklif_veren_personel, teklif_alan, aciklama
    )
    
    cursor.execute(query, params)
    teklif_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return teklif_id

def update_teklif_durumu():
    """
    Tüm tekliflerin durumunu günceller.
    Geçerlilik tarihi geçmiş teklifleri 'Geçerlilik tarihi doldu' olarak işaretler.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Bugünün tarihini al
    from datetime import datetime
    bugun = datetime.now().strftime("%Y-%m-%d")
    
    # Geçerlilik tarihi geçmiş teklifleri güncelle
    cursor.execute("""
        UPDATE teklifler 
        SET teklif_durumu = 'Geçerlilik tarihi doldu'
        WHERE gecerlilik_tarihi < ? AND teklif_durumu = 'Açık'
    """, (bugun,))
    
    conn.commit()
    conn.close()

def load_teklifler():
    """
    Tüm teklifleri getirir.
    Dönüş: [(teklif_no, cari_kodu, cari_unvan, plaka, teklif_tarihi, gecerlilik_tarihi, teklif_alan, toplam_tutar, teklif_durumu, telefon), ...]
    """
    # Önce teklif durumlarını güncelle
    update_teklif_durumu()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            t.teklif_no,
            t.cari_kodu,
            c.cari_ad_unvan,
            t.plaka,
            t.teklif_tarihi,
            t.gecerlilik_tarihi,
            t.teklif_alan,
            t.toplam_tutar,
            t.teklif_durumu,
            c.cep_telefonu
        FROM teklifler t
        LEFT JOIN cariler c ON t.cari_kodu = c.cari_kodu
        ORDER BY t.teklif_tarihi DESC
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def get_teklif_details(teklif_no):
    """
    Teklif detaylarını ve işlemlerini getirir.
    Dönüş: {
        "teklif": {...},
        "cari": {...},
        "arac": {...},
        "islemler": [ {...}, ... ]
    }
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Teklif bilgisi
    cursor.execute("""
        SELECT t.id, t.teklif_no, t.cari_kodu, t.plaka, t.teklif_tarihi, t.gecerlilik_tarihi,
               t.odeme_sekli, t.odeme_vade_gun, t.teklif_veren_personel, t.teklif_alan,
               t.aciklama, t.toplam_tutar,
               c.cari_ad_unvan, c.cep_telefonu, c.cari_tipi,
               a.arac_tipi, a.model_yili, a.marka, a.model,
               c.vergi_no, c.tc_kimlik_no, a.sasi_no, a.motor_no
        FROM teklifler t
        LEFT JOIN cariler c ON t.cari_kodu = c.cari_kodu
        LEFT JOIN araclar a ON t.plaka = a.plaka
        WHERE t.teklif_no = ?
    """, (teklif_no,))
    teklif = cursor.fetchone()
    if not teklif:
        conn.close()
        return None

    teklif_dict = {
        "id": teklif[0],
        "teklif_no": teklif[1],
        "cari_kodu": teklif[2],
        "plaka": teklif[3],
        "teklif_tarihi": teklif[4],
        "gecerlilik_tarihi": teklif[5],
        "odeme_sekli": teklif[6],
        "odeme_vade_gun": teklif[7],
        "teklif_veren_personel": teklif[8],
        "teklif_alan": teklif[9],
        "aciklama": teklif[10],
        "toplam_tutar": teklif[11]
    }

    # Cari bilgileri
    cari_dict = {
        "cari_ad_unvan": teklif[12],
        "cep_telefonu": teklif[13],
        "cari_tipi": teklif[14],
        "vergi_no": teklif[19],
        "tc_kimlik_no": teklif[20]
    }

    # Araç bilgileri
    arac_dict = {
        "arac_tipi": teklif[15],
        "model_yili": teklif[16],
        "marka": teklif[17],
        "model": teklif[18],
        "sasi_no": teklif[21],
        "motor_no": teklif[22]
    }

    # Teklif işlemleri
    cursor.execute("""
        SELECT id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar
        FROM teklif_islemler
        WHERE teklif_id = ?
    """, (teklif_dict["id"],))
    islemler = cursor.fetchall()
    islemler_list = [
        {
            "id": row[0],
            "islem_aciklama": row[1],
            "islem_tutari": row[2],
            "kdv_orani": row[3],
            "kdv_tutari": row[4],
            "aciklama": row[5],
            "miktar": row[6]
        }
        for row in islemler
    ]

    conn.close()
    return {
        "teklif": teklif_dict,
        "cari": cari_dict,
        "arac": arac_dict,
        "islemler": islemler_list
    }

def add_teklif_islem(teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar=1):
    """
    Teklif işlemi ekler ve teklif toplam tutarını günceller.
    Args:
        teklif_id: Teklif ID'si
        islem_aciklama: İşlem açıklaması
        islem_tutari: İşlem tutarı
        kdv_orani: KDV oranı
        kdv_tutari: KDV tutarı
        aciklama: Açıklama
        miktar: İşlem miktarı (varsayılan: 1)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO teklif_islemler (teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar))
    conn.commit()
    conn.close()
    update_teklif_tutar(teklif_id)  # Teklif tutarını güncelle

def update_teklif_tutar(teklif_id):
    """
    Belirtilen teklifin işlemlerinin toplam tutarını hesaplar ve toplam_tutar alanını günceller.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(islem_tutari + kdv_tutari) FROM teklif_islemler WHERE teklif_id = ?
    """, (teklif_id,))
    toplam = cursor.fetchone()[0] or 0.0
    cursor.execute("""
        UPDATE teklifler SET toplam_tutar = ? WHERE id = ?
    """, (toplam, teklif_id))
    conn.commit()
    conn.close()

def get_teklif_id_by_no(teklif_no):
    """
    Teklif numarasına göre teklif ID'sini döndürür.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM teklifler WHERE teklif_no = ?", (teklif_no,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def delete_teklif_islem(teklif_id, row_index):
    """
    Belirtilen teklifin belirtilen sıradaki işlemini siler.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Önce işlemin ID'sini bul
    cursor.execute("""
        SELECT id FROM teklif_islemler 
        WHERE teklif_id = ? 
        ORDER BY id 
        LIMIT 1 OFFSET ?
    """, (teklif_id, row_index))
    
    islem_id = cursor.fetchone()
    if islem_id:
        # İşlemi sil
        cursor.execute("DELETE FROM teklif_islemler WHERE id = ?", (islem_id[0],))
        conn.commit()
    
    conn.close()

def delete_teklif(teklif_id):
    """
    Belirtilen teklifi ve ilişkili işlemleri siler.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # Foreign key constraints'i aktif et
    cursor.execute("DELETE FROM teklifler WHERE id = ?", (teklif_id,))
    conn.commit()
    conn.close()

def get_kasa_transactions(start_date=None, end_date=None, odeme_tipi=None, islem_tipi=None):
    """
    Kasa işlemlerini getirir.
    Parametreler:
    - start_date: Başlangıç tarihi (YYYY-MM-DD formatında)
    - end_date: Bitiş tarihi (YYYY-MM-DD formatında)
    - odeme_tipi: Ödeme tipi (Nakit, Kredi Kartı, Havale/EFT, Vadeli)
    - islem_tipi: İşlem tipi (TEKLIF veya SERVIS)
    
    Dönüş: [(tarih, odeme_tipi, aciklama, tutar, odeme_kaynagi), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Temel sorgu
    query = """
        SELECT 
            k.tarih,
            k.odeme_tipi,
            k.aciklama,
            k.tutar,
            k.odeme_kaynagi
        FROM kasa k
        WHERE 1=1
    """
    params = []
    
    # Tarih filtresi (tarih saatle kaydedildiği için gün bazında karşılaştırılır; bitiş günü de dahil)
    if start_date:
        query += " AND date(k.tarih) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date(k.tarih) <= ?"
        params.append(end_date)
    
    # Ödeme tipi filtresi
    if odeme_tipi:
        query += " AND k.odeme_tipi = ?"
        params.append(odeme_tipi)
    
    # İşlem tipi filtresi
    if islem_tipi:
        query += " AND k.odeme_kaynagi = ?"
        params.append(islem_tipi)
    
    # Sıralama
    query += " ORDER BY k.tarih DESC"
    
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

def get_kasa_ozeti():
    """Kasadaki tüm ödemelerin (adet, ilk tarih, son tarih) bilgisini döndürür; tarihler 'YYYY-MM-DD'."""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT COUNT(*), MIN(date(tarih)), MAX(date(tarih)) FROM kasa").fetchone()
    finally:
        conn.close()

def load_service_details(servis_id):
    """Servis detaylarını veritabanından çeker"""
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                s.id,
                s.plaka,
                s.servis_tarihi,
                s.servis_durumu,
                s.servis_kapanis_tarihi,
                s.aciklama,
                c.cari_kodu,
                c.cari_ad_unvan,
                c.cep_telefonu,
                c.vergi_no,
                a.arac_tipi,
                a.marka,
                a.model,
                a.model_yili,
                a.sasi_no,
                a.motor_no
            FROM servisler s
            LEFT JOIN cariler c ON s.cari_kodu = c.cari_kodu
            LEFT JOIN araclar a ON s.plaka = a.plaka
            WHERE s.id = ?
        """, (servis_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'plaka': row[1],
                'servis_tarihi': row[2],
                'servis_durumu': row[3],
                'servis_kapanis_tarihi': row[4],
                'aciklama': row[5],
                'cari_kodu': row[6],
                'cari_ad_unvan': row[7],
                'cep_telefonu': row[8],
                'vergi_no': row[9],
                'arac_tipi': row[10],
                'marka': row[11],
                'model': row[12],
                'model_yili': row[13],
                'sasi_no': row[14],
                'motor_no': row[15]
            }
        return {}
    except Exception as e:
        print(f"Error loading service details: {e}")
        return {}
    finally:
        conn.close()

def load_cari_details(cari_kodu):
    """Cari detaylarını veritabanından çeker"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                cari_kodu,
                cari_ad_unvan,
                cep_telefonu,
                cari_tipi,
                vergi_no,
                aciklama
            FROM cariler
            WHERE cari_kodu = ?
        """, (cari_kodu,))
        
        row = cursor.fetchone()
        if row:
            return {
                'cari_kodu': row[0],
                'cari_ad_unvan': row[1],
                'cep_telefonu': row[2],
                'cari_tipi': row[3],
                'vergi_no': row[4],
                'aciklama': row[5]
            }
        return {}
    except Exception as e:
        print(f"Error loading cari details: {e}")
        return {}
    finally:
        conn.close()

def load_car_details(plaka):
    """Araç detaylarını veritabanından çeker"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                plaka,
                marka,
                model,
                model_yili,
                arac_tipi,
                motor_no,
                sasi_no,
                yakit_cinsi
            FROM araclar
            WHERE plaka = ?
        """, (plaka,))
        
        row = cursor.fetchone()
        if row:
            return {
                'plaka': row[0],
                'marka': row[1],
                'model': row[2],
                'model_yili': row[3],
                'arac_tipi': row[4],
                'motor_no': row[5],
                'sasi_no': row[6],
                'yakit_cinsi': row[7]
            }
        return {}
    except Exception as e:
        print(f"Error loading car details: {e}")
        return {}
    finally:
        conn.close()

def load_cari_arac_servis_bilgileri(cari_kodu):
    """
    Cariye ait araçların servis bilgilerini getirir.
    Dönüş: [(plaka, arac_tipi, model_yili, marka, model, servis_sayisi, toplam_servis_tutari), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.plaka,
            a.arac_tipi,
            a.model_yili,
            a.marka,
            a.model,
            COUNT(s.id) as servis_sayisi,
            COALESCE(
                SUM(
                    CASE 
                        WHEN s.servis_durumu = 'Kapalı' THEN s.servis_kapanis_tutar
                        WHEN s.servis_durumu = 'Açık' THEN s.servis_tutar
                        ELSE 0
                    END
                ), 0
            ) as toplam_servis_tutari
        FROM araclar a
        LEFT JOIN servisler s ON a.plaka = s.plaka
        WHERE a.cari_kodu = ?
        GROUP BY a.plaka, a.arac_tipi, a.model_yili, a.marka, a.model
        ORDER BY a.plaka
    """, (cari_kodu,))
    result = cursor.fetchall()
    conn.close()
    return result

