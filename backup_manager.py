import os
import shutil
import datetime
import json
from PyQt5.QtWidgets import QMessageBox

class BackupManager:
    def __init__(self):
        self.config_file = "db_config.json"
        self.default_backup_path = os.path.join(os.path.expanduser("~"), "Desktop", "OTO-SERVIS-DB")
        self.max_backups = 30  # Maksimum yedek sayısı
        self.load_config()

    def load_config(self):
        """Yedekleme yapılandırmasını yükler"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.backup_path = config.get('backup_path', self.default_backup_path)
            else:
                self.backup_path = self.default_backup_path
        except Exception:
            self.backup_path = self.default_backup_path

    def save_config(self):
        """Yedekleme yapılandırmasını kaydeder"""
        try:
            config = {'backup_path': self.backup_path}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Yapılandırma kaydetme hatası: {str(e)}")

    def create_backup(self):
        """Veritabanının yedeğini alır ve eski yedekleri temizler"""
        try:
            # Yedekleme klasörünü oluştur
            if not os.path.exists(self.backup_path):
                os.makedirs(self.backup_path)

            # Yedek dosya adını oluştur
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_path, f"oto_servis_{timestamp}.db")

            # Veritabanını yedekle
            source_db = "oto_servis.db"
            if os.path.exists(source_db):
                shutil.copy2(source_db, backup_file)
                print(f"Veritabanı yedeği alındı: {backup_file}")
                
                # Ruhsat fotoğraflarını yedekle
                source_photos_dir = os.path.join(os.path.dirname(source_db), "ruhsat_fotograflari")
                if os.path.exists(source_photos_dir):
                    backup_photos_dir = os.path.join(self.backup_path, f"ruhsat_fotograflari_{timestamp}")
                    shutil.copytree(source_photos_dir, backup_photos_dir)
                    print(f"Ruhsat fotoğrafları yedeği alındı: {backup_photos_dir}")
                
                # Eski yedekleri temizle
                self.cleanup_old_backups()
                return True
            else:
                print("Veritabanı dosyası bulunamadı!")
                return False

        except Exception as e:
            print(f"Yedekleme hatası: {str(e)}")
            return False

    def cleanup_old_backups(self):
        """Eski yedekleri temizler"""
        try:
            # Yedek dosyalarını listele
            backup_files = []
            for file in os.listdir(self.backup_path):
                if file.startswith("oto_servis_") and file.endswith(".db"):
                    file_path = os.path.join(self.backup_path, file)
                    backup_files.append((file_path, os.path.getmtime(file_path)))

            # Dosyaları tarihe göre sırala (en yeniden en eskiye)
            backup_files.sort(key=lambda x: x[1], reverse=True)

            # Maksimum yedek sayısından fazla olanları sil
            if len(backup_files) > self.max_backups:
                for file_path, _ in backup_files[self.max_backups:]:
                    try:
                        os.remove(file_path)
                        print(f"Eski yedek silindi: {file_path}")
                        
                        # İlgili ruhsat fotoğrafları klasörünü de sil
                        timestamp = os.path.basename(file_path).replace("oto_servis_", "").replace(".db", "")
                        photos_dir = os.path.join(self.backup_path, f"ruhsat_fotograflari_{timestamp}")
                        if os.path.exists(photos_dir):
                            shutil.rmtree(photos_dir)
                            print(f"Eski ruhsat fotoğrafları silindi: {photos_dir}")
                    except Exception as e:
                        print(f"Yedek silme hatası: {str(e)}")

            # Ruhsat fotoğrafları klasörlerini kontrol et ve temizle
            photo_dirs = []
            for item in os.listdir(self.backup_path):
                if item.startswith("ruhsat_fotograflari_"):
                    dir_path = os.path.join(self.backup_path, item)
                    if os.path.isdir(dir_path):
                        photo_dirs.append((dir_path, os.path.getmtime(dir_path)))

            # Fotoğraf klasörlerini tarihe göre sırala
            photo_dirs.sort(key=lambda x: x[1], reverse=True)

            # Maksimum sayıdan fazla olan fotoğraf klasörlerini sil
            if len(photo_dirs) > self.max_backups:
                for dir_path, _ in photo_dirs[self.max_backups:]:
                    try:
                        shutil.rmtree(dir_path)
                        print(f"Eski ruhsat fotoğrafları klasörü silindi: {dir_path}")
                    except Exception as e:
                        print(f"Fotoğraf klasörü silme hatası: {str(e)}")

        except Exception as e:
            print(f"Yedek temizleme hatası: {str(e)}")

    def get_backup_info(self):
        """Yedekleme bilgilerini döndürür"""
        try:
            backup_files = []
            total_size = 0
            
            for file in os.listdir(self.backup_path):
                if file.startswith("oto_servis_") and file.endswith(".db"):
                    file_path = os.path.join(self.backup_path, file)
                    size = os.path.getsize(file_path)
                    modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    backup_files.append({
                        'filename': file,
                        'size': size,
                        'modified': modified.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    total_size += size

            return {
                'backup_path': self.backup_path,
                'total_backups': len(backup_files),
                'total_size': total_size,
                'backups': sorted(backup_files, key=lambda x: x['modified'], reverse=True)
            }

        except Exception as e:
            print(f"Yedek bilgisi alma hatası: {str(e)}")
            return None

    def restore_database(self, backup_filename=None):
        """
        Veritabanını yedekten geri yükler.
        Eğer backup_filename belirtilmezse, en son yedeği kullanır.
        """
        try:
            # Eğer belirli bir yedek belirtilmemişse, en son yedeği bul
            if backup_filename is None:
                backup_files = []
                for file in os.listdir(self.backup_path):
                    if file.startswith("oto_servis_") and file.endswith(".db"):
                        file_path = os.path.join(self.backup_path, file)
                        backup_files.append((file_path, os.path.getmtime(file_path)))
                
                if not backup_files:
                    return False, "Yedek bulunamadı!"
                
                # En son yedeği al
                backup_files.sort(key=lambda x: x[1], reverse=True)
                backup_path = backup_files[0][0]
            else:
                backup_path = os.path.join(self.backup_path, backup_filename)
                if not os.path.exists(backup_path):
                    return False, "Belirtilen yedek bulunamadı!"

            # Mevcut veritabanını yedekle
            current_db = "oto_servis.db"
            if os.path.exists(current_db):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                emergency_backup = f"emergency_backup_{timestamp}.db"
                shutil.copy2(current_db, emergency_backup)

            # Yedeği geri yükle
            shutil.copy2(backup_path, current_db)
            
            # Ruhsat fotoğraflarını geri yükle
            backup_timestamp = os.path.basename(backup_path).replace("oto_servis_", "").replace(".db", "")
            backup_photos_dir = os.path.join(self.backup_path, f"ruhsat_fotograflari_{backup_timestamp}")
            if os.path.exists(backup_photos_dir):
                current_photos_dir = os.path.join(os.path.dirname(current_db), "ruhsat_fotograflari")
                if os.path.exists(current_photos_dir):
                    shutil.rmtree(current_photos_dir)
                shutil.copytree(backup_photos_dir, current_photos_dir)
            
            return True, f"Veritabanı başarıyla geri yüklendi: {os.path.basename(backup_path)}"

        except Exception as e:
            error_msg = f"Veritabanı geri yükleme hatası: {str(e)}"
            print(error_msg)
            return False, error_msg

    def verify_database(self):
        """
        Veritabanının bütünlüğünü kontrol eder.
        """
        try:
            import sqlite3
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            
            # Temel tabloları kontrol et
            tables = [
                "cariler", "araclar", "servisler", "islemler",
                "kasa", "teklifler", "teklif_islemler"
            ]
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
                except sqlite3.Error as e:
                    return False, f"Tablo kontrol hatası ({table}): {str(e)}"
            
            conn.close()
            return True, "Veritabanı bütünlüğü kontrol edildi, sorun bulunamadı."
            
        except Exception as e:
            return False, f"Veritabanı kontrol hatası: {str(e)}"

    def repair_database(self):
        """
        Veritabanını onarmaya çalışır.
        Önce bütünlük kontrolü yapar, sorun varsa en son yedeği geri yükler.
        """
        # Önce veritabanını kontrol et
        is_valid, message = self.verify_database()
        
        if is_valid:
            return True, "Veritabanı sağlam, onarım gerekmiyor."
        
        # Sorun varsa en son yedeği geri yükle
        success, message = self.restore_database()
        if success:
            return True, "Veritabanı başarıyla onarıldı."
        else:
            return False, f"Veritabanı onarılamadı: {message}"

    def restore_database_from_file(self, file_path):
        """
        Belirtilen dosya yolundaki veritabanını geri yükler.
        """
        try:
            if not os.path.exists(file_path):
                return False, "Belirtilen dosya bulunamadı!"

            # Mevcut veritabanını yedekle (acil durum yedeği)
            current_db = "oto_servis.db"
            if os.path.exists(current_db):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                emergency_backup = f"emergency_backup_{timestamp}.db"
                shutil.copy2(current_db, emergency_backup)
                print(f"Mevcut veritabanı acil durum yedeği alındı: {emergency_backup}")

            # Belirtilen dosyayı ana veritabanı olarak kopyala
            shutil.copy2(file_path, current_db)

            # Yeni kopyalanan veritabanının bütünlüğünü kontrol et
            is_valid, message = self.verify_database() # verify_database method is already in the class
            if not is_valid:
                return False, f"Seçilen dosya geçerli bir veritabanı değil veya bozuk: {message}"

            return True, f"Veritabanı başarıyla geri yüklendi: {os.path.basename(file_path)}"

        except Exception as e:
            error_msg = f"Veritabanı geri yükleme hatası: {str(e)}"
            print(error_msg)
            return False, error_msg 