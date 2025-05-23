# Database fonskiyonlarım burada olacak
import sqlite3

def load_cari_list_for_select():
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi FROM cariler")
    result = cursor.fetchall()
    conn.close()
    return result

def load_cari_list_for_table():
    """
    Cari listesini tabloya uygun şekilde döndürür.
    (cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi, toplam_tutar)
    """
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            cari_kodu,
            cari_ad_unvan,
            cep_telefonu,
            cari_tipi,
            0 as toplam_tutar,
            aciklama
        FROM cariler
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def load_car_list():
    conn = sqlite3.connect("oto_servis.db")
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
    conn = sqlite3.connect("oto_servis.db")
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
    conn = sqlite3.connect("oto_servis.db")
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

def load_closed_services():
    """
    servis_durumu 'Kapalı' olan servisleri döndürür.
    (servis_id, cari_kodu, cari_unvan, plaka, tarih, tutar, durum, arac_getiren_kisi)
    """
    conn = sqlite3.connect("oto_servis.db")
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

def close_service(servis_id, servis_kapanis_tutar):
    """
    Verilen servis_id'li servisin durumunu 'Kapalı' yapar ve kapanış tutarını kaydeder.
    """
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE servisler
        SET servis_durumu = 'Kapalı',
            servis_kapanis_tutar = ?,
            servis_kapanis_tarihi = date('now')
        WHERE id = ?
    """, (servis_kapanis_tutar, servis_id))
    conn.commit()
    conn.close()

def add_servis(cari_kodu, plaka, servis_tarihi, aciklama, arac_getiren_kisi):
    """
    Yeni bir servis kaydı oluşturur ve servis_id döndürür.
    """
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO servisler (cari_kodu, plaka, servis_tarihi, aciklama, servis_durumu, arac_getiren_kisi)
        VALUES (?, ?, ?, ?, 'Açık', ?)
    """, (cari_kodu, plaka, servis_tarihi, aciklama, arac_getiren_kisi))
    servis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return servis_id

def add_islem(servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama):
    import sqlite3
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO islemler (servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama))
    conn.commit()
    conn.close()
    update_servis_tutar(servis_id)  # İşlem eklenince servis tutarını güncelle

def delete_service(servis_id):
    """
    Verilen servis_id'ye sahip servisi ve ilişkili işlemleri siler.
    """
    conn = sqlite3.connect("oto_servis.db")
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
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()

    # Servis bilgisi
    cursor.execute("""
        SELECT id, cari_kodu, plaka, servis_tarihi, servis_tutar, servis_durumu, aciklama, arac_getiren_kisi
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
        "arac_getiren_kisi": servis[7]
    }

    # Cari bilgisi
    cursor.execute("""
        SELECT cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi, aciklama
        FROM cariler
        WHERE cari_kodu = ?
    """, (servis_dict["cari_kodu"],))
    cari = cursor.fetchone()
    cari_dict = {
        "cari_kodu": cari[0],
        "cari_ad_unvan": cari[1],
        "cep_telefonu": cari[2],
        "cari_tipi": cari[3],
        "aciklama": cari[4]
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
        SELECT id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama
        FROM islemler
        WHERE servis_id = ?
    """, (servis_id,))
    islemler = cursor.fetchall()
    islemler_list = [
        {
            "id": row[0],
            "islem_aciklama": row[1],
            "islem_tutari": row[2],
            "kdv_orani": row[3],
            "kdv_tutari": row[4],
            "aciklama": row[5]
        }
        for row in islemler
    ]

    conn.close()
    print({
        "servis": servis_dict,
        "cari": cari_dict,
        "arac": arac_dict,
        "islemler": islemler_list
    })
    return {
        "servis": servis_dict,
        "cari": cari_dict,
        "arac": arac_dict,
        "islemler": islemler_list
    }

def load_service_operations(servis_id):
    """
    Belirli bir servise ait işlemleri döndürür.
    Dönüş: [(id, islem_aciklama, islem_tutari, kdv_orani, aciklama), ...]
    """
    import sqlite3
    conn = sqlite3.connect("oto_servis.db")
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

def update_servis(servis_id, cari_kodu, plaka, aciklama):
    import sqlite3
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE servisler
        SET cari_kodu = ?, plaka = ?, aciklama = ?
        WHERE id = ?
    """, (cari_kodu, plaka, aciklama, servis_id))
    conn.commit()
    conn.close()

def delete_islem_by_id(islem_id):
    import sqlite3
    conn = sqlite3.connect("oto_servis.db")
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

def update_servis_tutar(servis_id):
    """
    Belirtilen servisin işlemlerinin toplam tutarını hesaplar ve servis_tutar alanını günceller.
    """
    import sqlite3
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(islem_tutari) FROM islemler WHERE servis_id = ?
    """, (servis_id,))
    toplam = cursor.fetchone()[0] or 0.0
    cursor.execute("""
        UPDATE servisler SET servis_tutar = ? WHERE id = ?
    """, (toplam, servis_id))
    conn.commit()
    conn.close()

def load_servis_kayitlari_by_plaka(plaka):
    """
    Belirtilen plakaya ait TÜM servisleri döndürür: (servis_tarihi, servis_tutar, servis_durumu)
    """
    import sqlite3
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT servis_tarihi, servis_tutar, servis_durumu
        FROM servisler
        WHERE plaka = ?
        ORDER BY servis_tarihi DESC
    """, (plaka,))
    result = cursor.fetchall()
    conn.close()
    return result

def add_teklif(teklif_no, cari_kodu, plaka, teklif_tarihi, gecerlilik_tarihi, 
               odeme_sekli, odeme_vade_gun, teklif_veren_personel, teklif_alan, aciklama):
    """
    Yeni bir teklif kaydı oluşturur ve teklif_id döndürür.
    """
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO teklifler (
            teklif_no, cari_kodu, plaka, teklif_tarihi, gecerlilik_tarihi,
            odeme_sekli, odeme_vade_gun, teklif_veren_personel, teklif_alan, aciklama
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (teklif_no, cari_kodu, plaka, teklif_tarihi, gecerlilik_tarihi,
          odeme_sekli, odeme_vade_gun, teklif_veren_personel, teklif_alan, aciklama))
    teklif_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return teklif_id

def update_teklif_durumu():
    """
    Tüm tekliflerin durumunu günceller.
    Geçerlilik tarihi geçmiş teklifleri 'Geçerlilik tarihi doldu' olarak işaretler.
    """
    conn = sqlite3.connect("oto_servis.db")
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
    Dönüş: [(teklif_no, cari_kodu, cari_unvan, plaka, teklif_tarihi, gecerlilik_tarihi, teklif_alan, toplam_tutar, teklif_durumu), ...]
    """
    # Önce teklif durumlarını güncelle
    update_teklif_durumu()
    
    conn = sqlite3.connect("oto_servis.db")
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
            t.teklif_durumu
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
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()

    # Teklif bilgisi
    cursor.execute("""
        SELECT t.id, t.teklif_no, t.cari_kodu, t.plaka, t.teklif_tarihi, t.gecerlilik_tarihi,
               t.odeme_sekli, t.odeme_vade_gun, t.teklif_veren_personel, t.teklif_alan,
               t.aciklama, t.toplam_tutar,
               c.cep_telefonu, c.cari_tipi,
               a.arac_tipi, a.model_yili, a.marka, a.model
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
        "cep_telefonu": teklif[12],
        "cari_tipi": teklif[13]
    }

    # Araç bilgileri
    arac_dict = {
        "arac_tipi": teklif[14],
        "model_yili": teklif[15],
        "marka": teklif[16],
        "model": teklif[17]
    }

    # Teklif işlemleri
    cursor.execute("""
        SELECT id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama
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
            "aciklama": row[5]
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

def add_teklif_islem(teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama):
    """
    Teklif işlemi ekler ve teklif toplam tutarını günceller.
    """
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO teklif_islemler (teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama))
    conn.commit()
    conn.close()
    update_teklif_tutar(teklif_id)  # Teklif tutarını güncelle

def update_teklif_tutar(teklif_id):
    """
    Belirtilen teklifin işlemlerinin toplam tutarını hesaplar ve toplam_tutar alanını günceller.
    """
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(islem_tutari) FROM teklif_islemler WHERE teklif_id = ?
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
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM teklifler WHERE teklif_no = ?", (teklif_no,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def delete_teklif_islem(teklif_id, row_index):
    """
    Belirtilen teklifin belirtilen sıradaki işlemini siler.
    """
    conn = sqlite3.connect("oto_servis.db")
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
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # Foreign key constraints'i aktif et
    cursor.execute("DELETE FROM teklifler WHERE id = ?", (teklif_id,))
    conn.commit()
    conn.close()

