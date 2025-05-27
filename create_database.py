import sqlite3
import os
from datetime import datetime

def create_database():
    """Veritabanını ve gerekli tabloları oluşturur"""
    # Veritabanı dosyası
    db_file = "oto_servis.db"
    
    # Eğer veritabanı zaten varsa, yedek al
    if os.path.exists(db_file):
        backup_file = f"oto_servis_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            os.rename(db_file, backup_file)
            print(f"Mevcut veritabanı yedeklendi: {backup_file}")
        except OSError as e:
            print(f"Mevcut veritabanı yedeklenirken hata oluştu: {e}")
            # Yedekleme başarısız olursa devam etme veya kullanıcıya sor gibi bir mantık eklenebilir
            # Şu an için hata mesajı verip devam ediyoruz
            
    # Veritabanı bağlantısı
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Foreign key kısıtlamalarını etkinleştir
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Cariler tablosu
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
    
    # Araclar tablosu
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
        ruhsat_foto TEXT,
        FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE CASCADE
    )
    """)
    
    # Servisler tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servisler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plaka TEXT NOT NULL,
        cari_kodu TEXT NOT NULL,
        servis_tutar REAL DEFAULT 0,
        servis_kapanis_tutar REAL,
        servis_kapanis_tarihi TEXT,
        aciklama TEXT,
        servis_durumu TEXT DEFAULT 'Açık',
        servis_tarihi TEXT NOT NULL,
        arac_getiren_kisi TEXT,
        FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE NO ACTION,
        FOREIGN KEY (plaka) REFERENCES araclar (plaka) ON DELETE NO ACTION
    )
    """)
    
    # İşlemler tablosu
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
    
    # Kasa tablosu
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
        odeme_kaynagi TEXT,
        kaynak_id INTEGER,
        aciklama TEXT,
        FOREIGN KEY (cari_kodu) REFERENCES cariler (cari_kodu) ON DELETE NO ACTION
    )
    """)
    
    # Teklifler tablosu
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
    
    # Teklif işlemleri tablosu
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
    
    # Örnek veri ekle (İsteğe bağlı, kaldırılabilir)
    try:
        # Örnek cari
        cursor.execute("""
        INSERT INTO cariler (cari_kodu, cari_ad_unvan, cari_tipi, cep_telefonu)
        VALUES ('C001', 'Örnek Müşteri', 'Bireysel', '5551234567')
        """)
        
        # Örnek araç
        cursor.execute("""
        INSERT INTO araclar (cari_kodu, plaka, marka, model, model_yili)
        VALUES ('C001', '34ABC123', 'Toyota', 'Corolla', 2020)
        """)
        
        print("Örnek veriler eklendi.")
    except sqlite3.IntegrityError:
        print("Örnek veriler zaten mevcut.")
    
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

    # Değişiklikleri kaydet
    conn.commit()
    conn.close()
    
    print("Veritabanı başarıyla oluşturuldu!")
    return True

if __name__ == "__main__":
    create_database()