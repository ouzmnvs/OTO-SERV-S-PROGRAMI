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

def add_islem(servis_id, islem_aciklama, islem_tutari, kdv_orani, aciklama):
    """İŞLEMLER tablosuna yeni bir işlem ekler ve servis toplam tutarını günceller."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        
        # İşlem ekleme sorgusu
        cursor.execute("""
        INSERT INTO İŞLEMLER (servis_id, islem_aciklama, islem_tutari, kdv_orani, aciklama)
        VALUES (?, ?, ?, ?, ?)
        """, (servis_id, islem_aciklama, islem_tutari, kdv_orani, aciklama))
        
        # Servis toplam tutarını güncelle
        cursor.execute("""
        UPDATE SERVİSLER
        SET servis_tutar = servis_tutar + ?
        WHERE id = ?
        """, (islem_tutari, servis_id))
        
        conn.commit()
        print("İşlem başarıyla eklendi ve servis toplam tutarı güncellendi.")
    except sqlite3.Error as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        conn.close()

def add_servis(cari_kodu, plaka, servis_tarihi, aciklama):
    """SERVİSLER tablosuna yeni bir servis ekler ve servis ID'sini döndürür."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        
        # Servis ekleme sorgusu
        cursor.execute("""
        INSERT INTO SERVİSLER (cari_kodu, plaka, servis_tarihi, aciklama, servis_durumu)
        VALUES (?, ?, ?, ?, 'Açık')
        """, (cari_kodu, plaka, servis_tarihi, aciklama))
        
        conn.commit()
        servis_id = cursor.lastrowid  # Eklenen servisin ID'sini al
        print("Servis başarıyla eklendi.")
        return servis_id
    except sqlite3.Error as e:
        print(f"Bir hata oluştu: {e}")
        return None
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

def load_car_list_by_cari(cari_kodu):
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        
        # Cari koduna göre araçları filtrele
        cursor.execute("""
        SELECT 
            a.plaka,
            a.arac_tipi,
            a.model_yili,
            a.marka,
            a.model
        FROM ARAÇLAR a
        WHERE a.cari_kodu = ?
        """, (cari_kodu,))
        
        results = cursor.fetchall()
        return results  # Verileri döndür
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()