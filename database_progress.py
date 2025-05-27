# Database fonskiyonlarım burada olacak
import sqlite3
import os
import json
import shutil
from datetime import datetime

def get_db_path():
    """Veritabanı yolunu yapılandırma dosyasından alır"""
    config_file = "db_config.json"
    default_db_path = "oto_servis.db"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                backup_path = config.get('backup_path')
                if backup_path and os.path.exists(os.path.join(backup_path, "oto_servis.db")):
                    return os.path.join(backup_path, "oto_servis.db")
    except Exception:
        pass
    
    return default_db_path

def recover_database():
    """Ana veritabanı bozulduğunda yedekten geri yükleme yapar"""
    config_file = "db_config.json"
    default_db_path = "oto_servis.db"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                backup_path = config.get('backup_path')
                if backup_path:
                    backup_db = os.path.join(backup_path, "oto_servis.db")
                    if os.path.exists(backup_db):
                        # Yedek dosyasını ana konuma kopyala
                        shutil.copy2(backup_db, default_db_path)
                        print(f"Veritabanı başarıyla yedekten geri yüklendi: {default_db_path}")
                        return True
    except Exception as e:
        print(f"Veritabanı kurtarma hatası: {str(e)}")
    
    return False

def get_db_connection():
    """Veritabanı bağlantısı oluşturur"""
    db_path = get_db_path()
    
    try:
        # Önce bağlantıyı test et
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # Basit bir sorgu ile veritabanını test et
        cursor.close()
        conn.close()
        
        # Test başarılıysa yeni bağlantı oluştur
        return sqlite3.connect(db_path)
    except sqlite3.Error:
        # Veritabanı bozuksa veya erişilemiyorsa
        print("Veritabanı bağlantısı başarısız, yedekten kurtarma deneniyor...")
        
        # Yedekten kurtarmayı dene
        if recover_database():
            # Kurtarma başarılıysa yeni bağlantı oluştur
            return sqlite3.connect(db_path)
        else:
            # Kurtarma başarısızsa hata fırlat
            raise Exception("Veritabanı bağlantısı kurulamadı ve yedekten kurtarma başarısız oldu.")

def backup_database():
    """Veritabanının yedeğini alır"""
    config_file = "db_config.json"
    default_db_path = "oto_servis.db"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                backup_path = config.get('backup_path')
                if backup_path:
                    # Yedekleme klasörünü oluştur
                    if not os.path.exists(backup_path):
                        os.makedirs(backup_path)
                    
                    # Yedek dosya adını tarih ile oluştur
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = os.path.join(backup_path, f"oto_servis_backup_{timestamp}.db")
                    
                    # Veritabanını yedekle
                    shutil.copy2(default_db_path, backup_file)
                    print(f"Veritabanı yedeği alındı: {backup_file}")
                    return True
    except Exception as e:
        print(f"Veritabanı yedekleme hatası: {str(e)}")
    
    return False

def load_cari_list_for_select():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi FROM cariler")
    result = cursor.fetchall()
    conn.close()
    return result

def load_cari_list_for_table():
    """
    Cari listesini tabloya uygun şekilde döndürür.
    (cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi, toplam_tutar, aciklama)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.cari_kodu,
            c.cari_ad_unvan,
            c.cep_telefonu,
            c.cari_tipi,
            COALESCE(SUM(s.servis_tutar), 0) as toplam_tutar,
            c.aciklama
        FROM cariler c
        LEFT JOIN servisler s ON c.cari_kodu = s.cari_kodu AND s.servis_durumu = 'Açık'
        GROUP BY c.cari_kodu, c.cari_ad_unvan, c.cep_telefonu, c.cari_tipi, c.aciklama
        ORDER BY c.cari_kodu
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def load_car_list():
    conn = get_db_connection()
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
    conn = get_db_connection()
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
    conn = get_db_connection()
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
    conn = get_db_connection()
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
    Ayrıca aracın son bakım tarihini günceller.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Önce servisin plakasını al
    cursor.execute("SELECT plaka FROM servisler WHERE id = ?", (servis_id,))
    plaka = cursor.fetchone()[0]
    
    # Servisi kapat
    cursor.execute("""
        UPDATE servisler
        SET servis_durumu = 'Kapalı',
            servis_kapanis_tutar = ?,
            servis_kapanis_tarihi = date('now')
        WHERE id = ?
    """, (servis_kapanis_tutar, servis_id))
    
    # Aracın son bakım tarihini güncelle
    cursor.execute("""
        UPDATE araclar
        SET son_bakim_tarihi = date('now')
        WHERE plaka = ?
    """, (plaka,))
    
    conn.commit()
    conn.close()

def add_servis(cari_kodu, plaka, servis_tarihi, aciklama, arac_getiren_kisi):
    """
    Yeni bir servis kaydı oluşturur ve servis_id döndürür.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO servisler (cari_kodu, plaka, servis_tarihi, aciklama, servis_durumu, arac_getiren_kisi)
        VALUES (?, ?, ?, ?, 'Açık', ?)
    """, (cari_kodu, plaka, servis_tarihi, aciklama, arac_getiren_kisi))
    servis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return servis_id

def add_islem(servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar=1):
    """Yeni bir işlem ekler."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO islemler (servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar))
    conn.commit()
    conn.close()
    update_servis_tutar(servis_id)  # İşlem eklenince servis tutarını güncelle

def delete_service(servis_id):
    """
    Verilen servis_id'ye sahip servisi ve ilişkili işlemleri siler.
    """
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()

    # Servis bilgisi
    cursor.execute("""
        SELECT id, cari_kodu, plaka, servis_tarihi, servis_tutar, servis_durumu, aciklama, arac_getiren_kisi, servis_kapanis_tutar
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
        "arac_getiren_kisi": servis[7],
        "servis_kapanis_tutar": servis[8]
    }

    # Cari bilgisi
    cursor.execute("""
        SELECT cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi, aciklama, vergi_no
        FROM cariler
        WHERE cari_kodu = ?
    """, (servis_dict["cari_kodu"],))
    cari = cursor.fetchone()
    cari_dict = {
        "cari_kodu": cari[0],
        "cari_ad_unvan": cari[1],
        "cep_telefonu": cari[2],
        "cari_tipi": cari[3],
        "aciklama": cari[4],
        "vergi_no": cari[5]
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
        SELECT id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar
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
            "aciklama": row[5],
            "miktar": row[6]
        }
        for row in islemler
    ]

    conn.close()
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
    conn = get_db_connection()
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

def update_servis(servis_id, cari_kodu, plaka, aciklama, arac_getiren_kisi):
    """
    Servis bilgilerini günceller.
    Args:
        servis_id: Güncellenecek servisin ID'si
        cari_kodu: Cari kodu
        plaka: Araç plakası
        aciklama: Müşteri talepleri ve servis açıklaması
        arac_getiren_kisi: Aracı getiren kişinin adı
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE servisler 
        SET cari_kodu = ?, plaka = ?, aciklama = ?, arac_getiren_kisi = ?
        WHERE id = ?
    """, (cari_kodu, plaka, aciklama, arac_getiren_kisi, servis_id))
    conn.commit()
    conn.close()

def delete_islem_by_id(islem_id):
    conn = get_db_connection()
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
    conn = get_db_connection()
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
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL sorgusunu hazırla
    query = """
        INSERT INTO teklifler (
            teklif_no, cari_kodu, plaka, teklif_tarihi, gecerlilik_tarihi,
            odeme_sekli, odeme_vade_gun, teklif_veren_personel, teklif_alan, aciklama
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Parametreleri hazırla
    params = (
        teklif_no, cari_kodu, plaka, teklif_tarihi, gecerlilik_tarihi,
        odeme_sekli, odeme_vade_gun, teklif_veren_personel, teklif_alan, aciklama
    )
    
    cursor.execute(query, params)
    teklif_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return teklif_id

def update_teklif_durumu():
    """
    Tüm tekliflerin durumunu günceller.
    Geçerlilik tarihi geçmiş teklifleri 'Geçerlilik tarihi doldu' olarak işaretler.
    """
    conn = get_db_connection()
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
    
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()

    # Teklif bilgisi
    cursor.execute("""
        SELECT t.id, t.teklif_no, t.cari_kodu, t.plaka, t.teklif_tarihi, t.gecerlilik_tarihi,
               t.odeme_sekli, t.odeme_vade_gun, t.teklif_veren_personel, t.teklif_alan,
               t.aciklama, t.toplam_tutar,
               c.cari_ad_unvan, c.cep_telefonu, c.cari_tipi,
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
        "cari_ad_unvan": teklif[12],
        "cep_telefonu": teklif[13],
        "cari_tipi": teklif[14]
    }

    # Araç bilgileri
    arac_dict = {
        "arac_tipi": teklif[15],
        "model_yili": teklif[16],
        "marka": teklif[17],
        "model": teklif[18]
    }

    # Teklif işlemleri
    cursor.execute("""
        SELECT id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar
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
            "aciklama": row[5],
            "miktar": row[6]
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

def add_teklif_islem(teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar=1):
    """
    Teklif işlemi ekler ve teklif toplam tutarını günceller.
    Args:
        teklif_id: Teklif ID'si
        islem_aciklama: İşlem açıklaması
        islem_tutari: İşlem tutarı
        kdv_orani: KDV oranı
        kdv_tutari: KDV tutarı
        aciklama: Açıklama
        miktar: İşlem miktarı (varsayılan: 1)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO teklif_islemler (teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar))
    conn.commit()
    conn.close()
    update_teklif_tutar(teklif_id)  # Teklif tutarını güncelle

def update_teklif_tutar(teklif_id):
    """
    Belirtilen teklifin işlemlerinin toplam tutarını hesaplar ve toplam_tutar alanını günceller.
    """
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM teklifler WHERE teklif_no = ?", (teklif_no,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def delete_teklif_islem(teklif_id, row_index):
    """
    Belirtilen teklifin belirtilen sıradaki işlemini siler.
    """
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # Foreign key constraints'i aktif et
    cursor.execute("DELETE FROM teklifler WHERE id = ?", (teklif_id,))
    conn.commit()
    conn.close()

def get_kasa_transactions(start_date=None, end_date=None, odeme_tipi=None, islem_tipi=None):
    """
    Kasa işlemlerini getirir.
    Parametreler:
    - start_date: Başlangıç tarihi (YYYY-MM-DD formatında)
    - end_date: Bitiş tarihi (YYYY-MM-DD formatında)
    - odeme_tipi: Ödeme tipi (Nakit, Kredi Kartı, Havale/EFT, Vadeli)
    - islem_tipi: İşlem tipi (TEKLIF veya SERVIS)
    
    Dönüş: [(tarih, odeme_tipi, aciklama, tutar, odeme_kaynagi), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Temel sorgu
    query = """
        SELECT 
            k.tarih,
            k.odeme_tipi,
            k.aciklama,
            k.tutar,
            k.odeme_kaynagi
        FROM kasa k
        WHERE 1=1
    """
    params = []
    
    # Tarih filtresi
    if start_date:
        query += " AND k.tarih >= ?"
        params.append(start_date)
    if end_date:
        query += " AND k.tarih <= ?"
        params.append(end_date)
    
    # Ödeme tipi filtresi
    if odeme_tipi:
        query += " AND k.odeme_tipi = ?"
        params.append(odeme_tipi)
    
    # İşlem tipi filtresi
    if islem_tipi:
        query += " AND k.odeme_kaynagi = ?"
        params.append(islem_tipi)
    
    # Sıralama
    query += " ORDER BY k.tarih DESC"
    
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

def load_service_details(servis_id):
    """Servis detaylarını veritabanından çeker"""
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                s.id,
                s.plaka,
                s.servis_tarihi,
                s.servis_durumu,
                s.servis_kapanis_tarihi,
                s.aciklama,
                c.cari_kodu,
                c.cari_ad_unvan,
                c.cep_telefonu,
                c.vergi_no,
                a.arac_tipi,
                a.marka,
                a.model,
                a.model_yili,
                a.sasi_no,
                a.motor_no
            FROM servisler s
            LEFT JOIN cariler c ON s.cari_kodu = c.cari_kodu
            LEFT JOIN araclar a ON s.plaka = a.plaka
            WHERE s.id = ?
        """, (servis_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'plaka': row[1],
                'servis_tarihi': row[2],
                'servis_durumu': row[3],
                'servis_kapanis_tarihi': row[4],
                'aciklama': row[5],
                'cari_kodu': row[6],
                'cari_ad_unvan': row[7],
                'cep_telefonu': row[8],
                'vergi_no': row[9],
                'arac_tipi': row[10],
                'marka': row[11],
                'model': row[12],
                'model_yili': row[13],
                'sasi_no': row[14],
                'motor_no': row[15]
            }
        return {}
    except Exception as e:
        print(f"Error loading service details: {e}")
        return {}
    finally:
        conn.close()

def load_cari_details(cari_kodu):
    """Cari detaylarını veritabanından çeker"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                cari_kodu,
                cari_ad_unvan,
                cep_telefonu,
                cari_tipi,
                vergi_no,
                aciklama
            FROM cariler
            WHERE cari_kodu = ?
        """, (cari_kodu,))
        
        row = cursor.fetchone()
        if row:
            return {
                'cari_kodu': row[0],
                'cari_ad_unvan': row[1],
                'cep_telefonu': row[2],
                'cari_tipi': row[3],
                'vergi_no': row[4],
                'aciklama': row[5]
            }
        return {}
    except Exception as e:
        print(f"Error loading cari details: {e}")
        return {}
    finally:
        conn.close()

def load_car_details(plaka):
    """Araç detaylarını veritabanından çeker"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                plaka,
                marka,
                model,
                model_yili,
                arac_tipi,
                motor_no,
                sasi_no,
                yakit_cinsi
            FROM araclar
            WHERE plaka = ?
        """, (plaka,))
        
        row = cursor.fetchone()
        if row:
            return {
                'plaka': row[0],
                'marka': row[1],
                'model': row[2],
                'model_yili': row[3],
                'arac_tipi': row[4],
                'motor_no': row[5],
                'sasi_no': row[6],
                'yakit_cinsi': row[7]
            }
        return {}
    except Exception as e:
        print(f"Error loading car details: {e}")
        return {}
    finally:
        conn.close()

def load_cari_arac_servis_bilgileri(cari_kodu):
    """
    Cariye ait araçların servis bilgilerini getirir.
    Dönüş: [(plaka, arac_tipi, model_yili, marka, model, servis_sayisi, toplam_servis_tutari), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.plaka,
            a.arac_tipi,
            a.model_yili,
            a.marka,
            a.model,
            COUNT(s.id) as servis_sayisi,
            COALESCE(
                SUM(
                    CASE 
                        WHEN s.servis_durumu = 'Kapalı' THEN s.servis_kapanis_tutar
                        WHEN s.servis_durumu = 'Açık' THEN s.servis_tutar
                        ELSE 0
                    END
                ), 0
            ) as toplam_servis_tutari
        FROM araclar a
        LEFT JOIN servisler s ON a.plaka = s.plaka
        WHERE a.cari_kodu = ?
        GROUP BY a.plaka, a.arac_tipi, a.model_yili, a.marka, a.model
        ORDER BY a.plaka
    """, (cari_kodu,))
    result = cursor.fetchall()
    conn.close()
    return result

