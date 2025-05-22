def load_cari_list():
    """Veritabanından cari bilgilerini ve toplam tutarlarını yükler."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.id,
                c.cari_kodu,
                c.cari_ad_unvan,
                c.cari_tipi,
                c.borc,
                c.tc_kimlik_no,
                c.vergi_no,
                c.cep_telefonu,
                IFNULL(SUM(s.servis_tutar), 0) AS toplam_tutar
            FROM CARİ c
            LEFT JOIN SERVİSLER s ON c.cari_kodu = s.cari_kodu
            GROUP BY c.id, c.cari_kodu, c.cari_ad_unvan, c.cari_tipi, c.borc, c.tc_kimlik_no, c.vergi_no, c.cep_telefonu
        """)
        return cursor.fetchall()
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

def load_car_list_by_cari_with_last_closed_service(cari_kodu):
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                a.plaka, a.arac_tipi, a.model_yili, a.marka, a.model,
                (
                    SELECT s.servis_kapanis_tutari
                    FROM SERVİSLER s
                    WHERE s.plaka = a.plaka AND s.servis_durumu = 'Kapalı'
                    ORDER BY s.servis_tarihi DESC
                    LIMIT 1
                ) as son_kapali_servis_tutar
            FROM ARAÇLAR a
            WHERE a.cari_kodu = ?
        """, (cari_kodu,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()

def load_car_list_by_cari_with_last_closed_service_info(cari_kodu):
    """
    Her araç için son kapalı servisin kapanış tutarını ve tarihini döndürür.
    Dönüş: [(plaka, arac_tipi, model_yili, marka, model, son_kapali_servis_tutar, son_kapali_servis_tarihi), ...]
    """
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                a.plaka, a.arac_tipi, a.model_yili, a.marka, a.model,
                (
                    SELECT s.servis_kapanis_tutari
                    FROM SERVİSLER s
                    WHERE s.plaka = a.plaka AND s.servis_durumu = 'Kapalı'
                    ORDER BY s.servis_tarihi DESC
                    LIMIT 1
                ) as son_kapali_servis_tutar,
                (
                    SELECT s.servis_tarihi
                    FROM SERVİSLER s
                    WHERE s.plaka = a.plaka AND s.servis_durumu = 'Kapalı'
                    ORDER BY s.servis_tarihi DESC
                    LIMIT 1
                ) as son_kapali_servis_tarihi
            FROM ARAÇLAR a
            WHERE a.cari_kodu = ?
        """, (cari_kodu,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()

def load_open_services():
    """Servis durumu 'Açık' olan servisleri yükler."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        
        # Açık servisleri sorgula
        cursor.execute("""
        SELECT 
            s.id,
            s.cari_kodu,
            c.cari_ad_unvan,
            s.plaka,
            s.servis_tarihi,
            s.servis_tutar,
            s.servis_durumu
        FROM SERVİSLER s
        LEFT JOIN CARİ c ON s.cari_kodu = c.cari_kodu
        WHERE s.servis_durumu = 'Açık'
        """)
        
        results = cursor.fetchall()
        return results  # Açık servisleri döndür
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()

def load_closed_services():
    """Kapalı servisleri veritabanından yükler (araç_tipi ve telefon dahil)."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.id,
                a.arac_tipi,
                s.cari_kodu,
                c.cari_ad_unvan,
                c.cep_telefonu,
                s.plaka,
                s.servis_tarihi,
                s.servis_tutar
            FROM SERVİSLER s
            LEFT JOIN CARİ c ON s.cari_kodu = c.cari_kodu
            LEFT JOIN ARAÇLAR a ON s.plaka = a.plaka
            WHERE s.servis_durumu = 'Kapalı'
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()

def load_service_operations(servis_id):
    """Belirtilen servis ID'sine ait işlemleri id ile birlikte döndürür."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, islem_aciklama, islem_tutari, kdv_orani, aciklama
            FROM İŞLEMLER
            WHERE servis_id = ?
        """, (servis_id,))
        results = cursor.fetchall()
        return results  # [(id, açıklama, tutar, kdv, açıklama), ...]
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()

def load_cari_details(cari_kodu):
    import sqlite3
    """Belirtilen cari koduna ait bilgileri döndürür."""
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("SELECT cari_tipi, cep_telefonu FROM CARİ WHERE cari_kodu = ?", (cari_kodu,))
        result = cursor.fetchone()
        if result:
            return {"cari_tipi": result[0], "telefon": result[1]}
        return {}
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return {}
    finally:
        conn.close()

def load_car_details(plaka):
    import sqlite3
    """Belirtilen plakaya ait araç bilgilerini döndürür."""
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("SELECT arac_tipi, model_yili, marka, model FROM ARAÇLAR WHERE plaka = ?", (plaka,))
        result = cursor.fetchone()
        if result:
            return {"arac_tipi": result[0], "model_yili": result[1], "marka": result[2], "model": result[3]}
        return {}
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return {}
    finally:
        conn.close()

def close_service(servis_id):
    """Servisi kapatır ve kapanış tutarını kaydeder."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        # Mevcut tutarı al
        cursor.execute("SELECT servis_tutar FROM SERVİSLER WHERE id = ?", (servis_id,))
        tutar = cursor.fetchone()[0]
        # Servisi kapalı yap ve kapanış tutarını kaydet
        cursor.execute("""
            UPDATE SERVİSLER
            SET servis_durumu = 'Kapalı', servis_kapanis_tutari = ?
            WHERE id = ?
        """, (tutar, servis_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
    finally:
        conn.close()

def delete_islem_by_id(islem_id):
    """İşlemi id ile siler ve servis tutarını günceller."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        # Önce tutarı ve servis_id'yi al
        cursor.execute("SELECT servis_id, islem_tutari FROM İŞLEMLER WHERE id = ?", (islem_id,))
        row = cursor.fetchone()
        if row:
            servis_id, islem_tutari = row
            cursor.execute("DELETE FROM İŞLEMLER WHERE id = ?", (islem_id,))
            cursor.execute("""
                UPDATE SERVİSLER
                SET servis_tutar = servis_tutar - ?
                WHERE id = ?
            """, (islem_tutari, servis_id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        conn.close()

def odeme_al(cari_kodu, servis_id, tutar, odeme_tipi, aciklama, cari_ad_unvan, plaka):
    """KASA tablosuna ödeme kaydeder ve servis_tutarını düşer."""
    import sqlite3
    from datetime import datetime
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # KASA tablosuna ödeme kaydı ekle
        cursor.execute("""
            INSERT INTO KASA (servis_id, cari_kodu, cari_ad_unvan, plaka, tarih, tutar, odeme_tipi, aciklama)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (servis_id, cari_kodu, cari_ad_unvan, plaka, tarih, tutar, odeme_tipi, aciklama))
        # SERVİSLER tablosunda servis_tutarı düş
        cursor.execute("""
            UPDATE SERVİSLER
            SET servis_tutar = servis_tutar - ?
            WHERE id = ?
        """, (tutar, servis_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ödeme kaydedilemedi: {e}")
    finally:
        conn.close()

def load_servis_kayitlari_by_plaka(plaka):
    """Belirtilen plakaya ait KAPALI servis kayıtlarını (tarih, kapanış_tutarı, durum) döndürür."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT servis_tarihi, servis_kapanis_tutari, servis_durumu
            FROM SERVİSLER
            WHERE plaka = ? AND servis_durumu = 'Kapalı'
            ORDER BY servis_tarihi ASC
        """, (plaka,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()