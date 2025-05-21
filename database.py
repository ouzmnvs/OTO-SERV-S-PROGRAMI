import sqlite3

# Veritabanı bağlantısı oluştur
conn = sqlite3.connect("oto_servis.db")
cursor = conn.cursor()

# CARİ tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS CARİ (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cari_kodu TEXT NOT NULL UNIQUE,
    cari_ad_unvan TEXT NOT NULL,
    cari_tipi TEXT,
    borc REAL DEFAULT 0,
    tc_kimlik_no TEXT,
    vergi_no TEXT,
    cep_telefonu TEXT
)
""")

# ARAÇLAR tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS ARAÇLAR (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cari_kodu TEXT NOT NULL,
    plaka TEXT NOT NULL UNIQUE,
    marka TEXT,
    model TEXT,
    model_yili INTEGER,
    sasi_no TEXT,
    ruhsat_sahibi_adi TEXT,
    arac_tipi TEXT,
    yakit_cinsi TEXT,
    ruhsat_fotografi BLOB,
    FOREIGN KEY (cari_kodu) REFERENCES CARİ (cari_kodu) ON DELETE CASCADE
)
""")

# İŞLEMLER tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS İŞLEMLER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servis_id INTEGER NOT NULL,
    islem_aciklama TEXT NOT NULL,
    islem_tutari REAL NOT NULL,
    kdv_orani REAL NOT NULL,
    aciklama TEXT,
    FOREIGN KEY (servis_id) REFERENCES SERVİSLER (id) ON DELETE CASCADE
)
""")

# SERVİSLER tablosunu oluştur veya güncelle
cursor.execute("""
CREATE TABLE IF NOT EXISTS SERVİSLER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cari_kodu TEXT NOT NULL,
    plaka TEXT NOT NULL,
    servis_tarihi TEXT NOT NULL,
    aciklama TEXT,
    servis_durumu TEXT DEFAULT 'Açık',  -- Varsayılan değer "Açık"
    servis_tutar REAL DEFAULT 0,  -- Toplam servis tutarı için sütun
    FOREIGN KEY (cari_kodu) REFERENCES CARİ (cari_kodu) ON DELETE CASCADE,
    FOREIGN KEY (plaka) REFERENCES ARAÇLAR (plaka) ON DELETE CASCADE
)
""")

# KASA tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS KASA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarih TEXT NOT NULL,  -- Ödeme tarihi
    tutar REAL NOT NULL,  -- Ödeme tutarı
    odeme_tipi TEXT NOT NULL,  -- Ödeme tipi (Nakit, Kredi Kartı, Havale)
    aciklama TEXT  -- Ödeme açıklaması
)
""")

# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()

print("Veritabanı ve tablolar başarıyla güncellendi.")