# Database fonskiyonlarım burada olacak
import sqlite3

def load_cari_list():
    conn = sqlite3.connect("oto_servis.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cari_kodu, cari_ad_unvan, tc_kimlik_no, vergi_no, cep_telefonu, aciklama FROM cariler")
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