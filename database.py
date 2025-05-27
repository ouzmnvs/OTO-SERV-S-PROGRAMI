import sqlite3
import os

# Veritabanı yolu
DB_PATH = "oto_servis.db"  # Yerel dizinde oluştur

# Veritabanı bağlantısı oluştur
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# CARİ tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS cariler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cari_kodu TEXT NOT NULL UNIQUE,
    cari_ad_unvan TEXT NOT NULL,
    cari_tipi TEXT,
    tc_kimlik_no TEXT,
    vergi_no TEXT,
    cep_telefonu TEXT,
    aciklama TEXT
)
""")

# ARAÇLAR tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS araclar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cari_kodu TEXT NOT NULL,
    plaka TEXT NOT NULL UNIQUE,
    marka TEXT,
    model TEXT,
    model_yili INTEGER,
    motor_no TEXT,
    sasi_no TEXT,
    arac_tipi TEXT,
    motor_hacmi TEXT,
    motor_gucu_kw TEXT,
    yakit_cinsi TEXT,
    son_bakim_tarihi TEXT,
    aciklama TEXT,
    ruhsat_foto TEXT,  -- Ruhsat fotoğrafı dosya yolu
    FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE CASCADE
)
""")

# İŞLEMLER tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS islemler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servis_id INTEGER NOT NULL,
    islem_aciklama TEXT NOT NULL,
    islem_tutari REAL NOT NULL,
    kdv_orani REAL DEFAULT 20,
    kdv_tutari REAL,
    aciklama TEXT,
    miktar INTEGER DEFAULT 1,
    FOREIGN KEY (servis_id) REFERENCES servisler (id) ON DELETE CASCADE
)
""")

# SERVİSLER tablosunu oluştur veya güncelle
cursor.execute("""
CREATE TABLE IF NOT EXISTS servisler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plaka TEXT NOT NULL,
    cari_kodu TEXT NOT NULL,
    servis_tutar REAL DEFAULT 0,
    servis_kapanis_tutar REAL,
    servis_kapanis_tarihi TEXT,
    aciklama TEXT,  -- Müşteri talepleri ve servis açıklaması
    servis_durumu TEXT DEFAULT 'Açık',
    servis_tarihi TEXT NOT NULL,
    arac_getiren_kisi TEXT,
    FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE NO ACTION,
    FOREIGN KEY (plaka) REFERENCES araclar (plaka) ON DELETE NO ACTION
)
""")

# KASA tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS kasa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servis_id INTEGER,
    cari_kodu TEXT,
    cari_ad_unvan TEXT,
    plaka TEXT,
    tarih TEXT NOT NULL,
    tutar REAL NOT NULL,
    odeme_tipi TEXT NOT NULL,
    odeme_kaynagi TEXT,  -- 'TEKLIF' veya 'SERVIS'
    kaynak_id INTEGER,   -- Teklif veya servis ID'si
    aciklama TEXT,
    FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE NO ACTION
)
""")

# TEKLİFLER tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS teklifler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teklif_no TEXT NOT NULL UNIQUE,
    cari_kodu TEXT NOT NULL,
    plaka TEXT NOT NULL,
    teklif_tarihi TEXT NOT NULL,
    gecerlilik_tarihi TEXT NOT NULL,
    odeme_sekli TEXT NOT NULL,
    odeme_vade_gun INTEGER,
    teklif_veren_personel TEXT NOT NULL,
    teklif_alan TEXT,
    aciklama TEXT,
    toplam_tutar REAL DEFAULT 0,
    teklif_durumu TEXT DEFAULT 'Açık',
    FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE NO ACTION,
    FOREIGN KEY (plaka) REFERENCES araclar (plaka) ON DELETE NO ACTION
)
""")

# TEKLİF İŞLEMLER tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS teklif_islemler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teklif_id INTEGER NOT NULL,
    islem_aciklama TEXT NOT NULL,
    islem_tutari REAL NOT NULL,
    kdv_orani REAL DEFAULT 20,
    kdv_tutari REAL,
    aciklama TEXT,
    miktar INTEGER DEFAULT 1,
    FOREIGN KEY (teklif_id) REFERENCES teklifler (id) ON DELETE CASCADE
)
""")

# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()

# Mevcut servisler tablosunu güncelle
try:
    cursor.execute("ALTER TABLE servisler ADD COLUMN servis_kapanis_tutar REAL")
except sqlite3.OperationalError:
    pass  # Kolon zaten varsa hata vermesini engelle

try:
    cursor.execute("ALTER TABLE servisler ADD COLUMN servis_kapanis_tarihi TEXT")
except sqlite3.OperationalError:
    pass  # Kolon zaten varsa hata vermesini engelle

# Mevcut kasa tablosunu güncelle
try:
    cursor.execute("ALTER TABLE kasa ADD COLUMN odeme_kaynagi TEXT")
except sqlite3.OperationalError:
    pass  # Kolon zaten varsa hata vermesini engelle

try:
    cursor.execute("ALTER TABLE kasa ADD COLUMN kaynak_id INTEGER")
except sqlite3.OperationalError:
    pass  # Kolon zaten varsa hata vermesini engelle

# Mevcut işlemler tablosunu güncelle
try:
    cursor.execute("ALTER TABLE islemler ADD COLUMN miktar INTEGER DEFAULT 1")
except sqlite3.OperationalError:
    pass  # Kolon zaten varsa hata vermesini engelle

# Mevcut kayıtların miktar değerlerini 1 olarak güncelle
try:
    cursor.execute("UPDATE islemler SET miktar = 1 WHERE miktar IS NULL")
except sqlite3.OperationalError:
    pass  # Hata durumunda sessizce devam et

# Mevcut teklif_islemler tablosunu güncelle
try:
    cursor.execute("ALTER TABLE teklif_islemler ADD COLUMN miktar INTEGER DEFAULT 1")
except sqlite3.OperationalError:
    pass  # Kolon zaten varsa hata vermesini engelle

# Mevcut kayıtların miktar değerlerini 1 olarak güncelle
try:
    cursor.execute("UPDATE teklif_islemler SET miktar = 1 WHERE miktar IS NULL")
except sqlite3.OperationalError:
    pass  # Hata durumunda sessizce devam et

conn.commit()
conn.close()

print("Veritabanı ve tablolar başarıyla güncellendi.")