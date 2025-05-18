def load_cari_list():
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, cari_ad_unvan FROM CARİ")
        cariler = cursor.fetchall()
        return cariler  # Veriyi döndür
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()