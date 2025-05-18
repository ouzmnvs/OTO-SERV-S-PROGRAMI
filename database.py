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
    telefon TEXT,
    cari_tipi TEXT,
    borc REAL DEFAULT 0
)
""")

# ARAÇLAR tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS ARAÇLAR (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cari_kodu INTEGER NOT NULL,
    plaka TEXT NOT NULL UNIQUE,
    arac_tipi TEXT,
    model_yili INTEGER,
    marka TEXT,
    model TEXT,
    FOREIGN KEY (cari_kodu) REFERENCES CARİ (cari_kodu) 
)
""")
# ON DELETE CASCADE FOREING KEY
# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()

print("Veritabanı ve tablolar başarıyla oluşturuldu.")