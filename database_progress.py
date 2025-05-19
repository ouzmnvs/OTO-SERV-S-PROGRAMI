def load_cari_list():
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CARİ")
        cariler = cursor.fetchall()
        return cariler  # Veriyi döndür
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()

def add_arac(cari_kodu, plaka, arac_tipi, model_yili, marka, model):
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        
        # ARAÇ ekleme sorgusu
        cursor.execute("""
        INSERT INTO ARAÇLAR (cari_kodu, plaka, arac_tipi, model_yili, marka, model)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (cari_kodu, plaka, arac_tipi, model_yili, marka, model))
        
        conn.commit()
        print("Araç başarıyla eklendi.")
    except sqlite3.IntegrityError as e:
        print(f"Veritabanı hatası: {e}")
    except sqlite3.Error as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        conn.close()


def load_car_list():
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        
        # Sadece gerekli sütunları seç
        cursor.execute("""
        SELECT   
            c.cari_kodu,
            c.cari_ad_unvan,
            a.plaka,
            a.arac_tipi,
            a.model_yili,
            a.marka,
            a.model
        FROM CARİ c
        LEFT JOIN ARAÇLAR a ON c.cari_kodu = a.cari_kodu
        """)
        
        results = cursor.fetchall()
        return results  # Verileri döndür
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()