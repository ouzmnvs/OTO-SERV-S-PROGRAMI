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

# ARAÇLAR tablosunu oluştur veya güncelle
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
    yakit_cinsi TEXT,  -- Benzin, Dizel, LPG, Benzin-LPG
    ruhsat_fotografi BLOB,  -- Fotoğraf binary olarak saklanacak
    FOREIGN KEY (cari_kodu) REFERENCES CARİ (cari_kodu) ON DELETE CASCADE
)
""")

# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()

print("Veritabanı ve tablolar başarıyla güncellendi.")