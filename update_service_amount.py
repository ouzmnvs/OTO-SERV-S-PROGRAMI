import sqlite3

def update_service_amount():
    try:
        # Veritabanına bağlan
        conn = sqlite3.connect('orjinal.db')
        cursor = conn.cursor()
        
        # Güncellenecek servis kaydını bul ve güncelle
        # ID: 7, Plaka: 65 AG 265, cari_kodu: 00002, servis_kapanis_tutar: 30020.0 olan kaydı bul
        cursor.execute("""
            UPDATE servisler 
            SET servis_kapanis_tutar = 36024.0
            WHERE id = 7
            AND plaka = '65 AG 265' 
            AND cari_kodu = '00002' 
            AND servis_tutar = 27024.0
            AND servis_kapanis_tutar = 30020.0
            AND servis_kapanis_tarihi = '2025-06-13'
            AND servis_durumu = 'Kapalı'
            AND servis_tarihi = '2025-05-27'
            AND arac_getiren_kisi = 'ADNAN GÜL'
        """)
        
        # Etkilenen satır sayısını kontrol et
        affected_rows = cursor.rowcount
        
        if affected_rows > 0:
            # Değişiklikleri kaydet
            conn.commit()
            print(f"✅ Başarılı! {affected_rows} adet servis kaydı güncellendi.")
            print("Güncellenen kayıt:")
            print("- ID: 7")
            print("- Plaka: 65 AG 265")
            print("- Cari Kodu: 00002")
            print("- servis_tutar: 27024.0 (değişmedi)")
            print("- Eski servis_kapanis_tutar: 30020.0")
            print("- Yeni servis_kapanis_tutar: 36024.0")
        else:
            print("❌ Güncellenecek kayıt bulunamadı!")
            print("Lütfen verileri kontrol edin.")
            
            # Mevcut kayıtları göster
            cursor.execute("""
                SELECT * FROM servisler 
                WHERE id = 7
            """)
            
            records = cursor.fetchall()
            if records:
                print(f"\nID 7 ile {len(records)} kayıt bulundu:")
                for record in records:
                    print(f"ID: {record[0]}, Plaka: {record[1]}, Cari: {record[2]}, Tutar: {record[3]}, Kapanış: {record[4]}, Tarih: {record[5]}, Durum: {record[7]}, Servis Tarihi: {record[8]}, Kişi: {record[9]}")
            else:
                print("ID 7 ile hiç kayıt bulunamadı.")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Veritabanı hatası: {e}")
    except Exception as e:
        print(f"❌ Genel hata: {e}")

if __name__ == "__main__":
    update_service_amount() 