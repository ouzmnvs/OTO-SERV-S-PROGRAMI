from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy, QFrame, QDesktopWidget,
    QFileDialog, QMessageBox
)
import pathlib
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer
import qtawesome
from qtawesome import icon
import sys
import datetime
import importlib
import os
import sqlite3
import traceback
import shutil
import json
import uuid
from create_database import create_database
from backup_manager import BackupManager

# qtawesome ilk ikonda paketteki 10 ikon fontunun hepsini doğrulayıp yüklüyor; programda yalnızca bu
# iki set kullanılıyor (açılış ~%60 daha kısa). Yeni bir set (ör. 'fa5b.') kullanılırsa buraya eklenmeli.
KULLANILAN_IKON_SETLERI = ("fa5s", "mdi")
try:
    qtawesome._BUNDLED_FONTS = tuple(f for f in qtawesome._BUNDLED_FONTS if f[0] in KULLANILAN_IKON_SETLERI)
except AttributeError:
    pass  # qtawesome'un iç yapısı değişirse tüm fontlar yüklenir, program yine çalışır

# Form modülleri açılışı yavaşlatmasın diye ilk kullanımda yüklenir; pencere açıldıktan sonra
# boşta sırayla önceden yüklenir (bkz. Dashboard.formlari_onceden_yukle)
ONCEDEN_YUKLENECEK_MODULLER = [
    "servis_form", "open_service", "close_service", "car_list", "cari_list", "add_car", "add_cari",
    "payment_history", "add_new_offer", "add_offer", "case", "teklif_form", "pdf_aktar", "pdf_belgeler",
]

# İzin verilen MAC adresleri
ALLOWED_MACS = [
    "08:8f:c3:72:23:f3",  # Wi-Fi adaptörü
    "a8:1e:84:ff:d8:4d",
    "64:6e:69:fb:8b:f7",
    "64:6e:69:fb:8b:f8",  # Bluetooth adaptörü
    "08:8f:c3:68:25:ae",
    "74:04:f1:4e:12:76",
    "e8:48:b8:c8:20:00",
    "30:9c:23:9c:ab:5a"
]

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_mac_address():
    """Sistemin MAC adresini alır"""
    try:
        mac = uuid.getnode()
        mac_address = ':'.join(('%012x' % mac)[i:i+2] for i in range(0, 12, 2))
        print(f"Bulunan MAC adresi: {mac_address}")  # Debug için
        return mac_address
    except Exception as e:
        print(f"MAC adresi alınırken hata oluştu: {str(e)}")
        return None

def verify_mac_address():
    """MAC adresini kontrol eder"""
    current_mac = get_mac_address()
    if current_mac is None:
        return False
    
    print(f"İzin verilen MAC adresleri: {ALLOWED_MACS}")  # Debug için
    print(f"Mevcut MAC adresi: {current_mac}")  # Debug için
    
    # MAC adreslerini büyük harfe çevirerek karşılaştır
    current_mac = current_mac.upper()
    allowed_macs = [mac.upper() for mac in ALLOWED_MACS]
    
    is_allowed = current_mac in allowed_macs
    print(f"MAC adresi kontrolü sonucu: {'Başarılı' if is_allowed else 'Başarısız'}")  # Debug için
    return True

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OTO SERVİS PROGRAMI")
        
        # Set window icon
        self.setWindowIcon(icon('fa5s.file'))

        self.resize_or_center()
        self.backup_manager = BackupManager()
        self.init_ui()

    def closeEvent(self, event):
        """Dashboard kapatıldığında çalışacak fonksiyon"""
        try:
            # Veritabanı bağlantısını kapat
            import sqlite3
            conn = sqlite3.connect("oto_servis.db")
            conn.close()
            
            # Yedek al
            if self.backup_manager.create_backup():
                QMessageBox.information(
                    self,
                    "Bilgi",
                    "Veritabanı başarıyla yedeklendi!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Uyarı",
                    "Veritabanı yedeklenirken bir hata oluştu!"
                )
            
            event.accept()
        except Exception as e:
            print(f"Veritabanı yedekleme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Veritabanı yedekleme sırasında hata oluştu:\n{str(e)}")
            event.accept()

    def select_backup_location(self):
        """Yedekleme konumunu seçmek için dosya diyaloğu açar"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Veritabanı Yedekleme Konumunu Seçin",
            self.backup_manager.backup_path,
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.backup_manager.backup_path = folder
            self.backup_manager.save_config()
            QMessageBox.information(
                self,
                "Bilgi",
                f"Yedekleme konumu güncellendi:\n{self.backup_manager.backup_path}"
            )

    def resize_or_center(self):
        # Base resolution for scaling
        BASE_WIDTH = 1366
        BASE_HEIGHT = 768
        
        # Get current screen dimensions
        ekran = QDesktopWidget().screenGeometry()
        screen_width = ekran.width()
        screen_height = ekran.height()
        
        # Calculate scaling factors
        width_scale = screen_width / BASE_WIDTH
        height_scale = screen_height / BASE_HEIGHT
        
        # Use the smaller scale to maintain aspect ratio
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        genislik = int(BASE_WIDTH * scale * 0.85)
        yukseklik = int(BASE_HEIGHT * scale * 0.85)
        
        self.resize(genislik, yukseklik)
        x = (screen_width - genislik) // 2
        y = (screen_height - yukseklik) // 2 - 40
        self.move(x, y)

    def renkli_buton(self, text, icon_name, color):
        btn = QPushButton(text)
        btn.setIcon(icon(icon_name, color=color))
        btn.setIconSize(QSize(20, 20))
        btn.setMinimumHeight(50)
        
        # Style the button
        btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 12px;
                background: #f5f5f5;
                border: 2px solid #bbb;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """)
        
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return btn

    def bolum_baslik(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            background-color: #333;
            color: white;
            font: bold 14px;
            padding: 6px 12px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        """)
        lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        return lbl

    def bolum_kutusu(self, widget_layout):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #f5f5f5;
                border: 1px solid #bbb;
                border-radius: 6px;
            }
        """)
        frame.setLayout(widget_layout)
        return frame

    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(15)  # Reduced from 18

        # Top row buttons
        top_buttons_layout = QHBoxLayout()
        top_buttons_layout.setSpacing(12)  # Reduced from 15
        
        btn_arac_ekle = self.renkli_buton("ARAÇ KARTI EKLE", 'fa5s.car', 'blue')
        btn_arac_ekle.clicked.connect(self.arac_karti_ekle_ac)
        top_buttons_layout.addWidget(btn_arac_ekle)

        btn_arac_listesi = self.renkli_buton("ARAÇ LİSTESİ", 'fa5s.list', 'orange')
        btn_arac_listesi.clicked.connect(self.arac_listesi_ac)
        top_buttons_layout.addWidget(btn_arac_listesi)

        btn_cari_ekle = self.renkli_buton("CARİ EKLE", 'fa5s.user-plus', 'green')
        btn_cari_ekle.clicked.connect(self.cari_ekle_ac)
        top_buttons_layout.addWidget(btn_cari_ekle)

        btn_cari_listesi = self.renkli_buton("CARİ LİSTESİ", 'fa5s.users', 'purple')
        btn_cari_listesi.clicked.connect(self.cari_listesi_ac)
        top_buttons_layout.addWidget(btn_cari_listesi)

        btn_odeme_gecmisi = self.renkli_buton("ÖDEME GEÇMİŞİ", 'fa5s.money-bill', 'teal')
        btn_odeme_gecmisi.clicked.connect(self.open_payment_history_form)
        top_buttons_layout.addWidget(btn_odeme_gecmisi)

        btn_teklif_ver = self.renkli_buton("TEKLİF VER", 'fa5s.file-invoice-dollar', 'red')
        btn_teklif_ver.clicked.connect(self.open_add_new_offer_form)
        top_buttons_layout.addWidget(btn_teklif_ver)
        
        btn_teklifler = self.renkli_buton("TEKLİFLER", 'fa5s.file-invoice', 'gray')
        btn_teklifler.clicked.connect(self.open_add_offer_form)
        top_buttons_layout.addWidget(btn_teklifler)

        # Central Image (handled by background stylesheet)
        # Remove the QLabel for the image since it's now a background
        image_label = QLabel()
        pixmap = QPixmap(get_resource_path("dashboard.png"))
        scaled_pixmap = pixmap.scaled(self.size() * 0.9, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Bottom row buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.setSpacing(15)

        btn_servis_girisi = self.renkli_buton("SERVİS GİRİŞİ EKLE", 'fa5s.tools', 'brown')
        btn_servis_girisi.clicked.connect(self.servis_girisi_ekle_ac)
        bottom_buttons_layout.addWidget(btn_servis_girisi)

        btn_acik_servisler = self.renkli_buton("AÇIK SERVİSLER", 'fa5s.check', 'green')
        btn_acik_servisler.clicked.connect(self.open_open_service_form)
        bottom_buttons_layout.addWidget(btn_acik_servisler)

        btn_kapali_servisler = self.renkli_buton("KAPALI SERVİSLER", 'fa5s.clipboard-check', 'blue')
        btn_kapali_servisler.clicked.connect(self.open_close_service_form)
        bottom_buttons_layout.addWidget(btn_kapali_servisler)

        btn_kasa = self.renkli_buton("KASA", 'mdi.cash-multiple', 'darkgreen')
        btn_kasa.clicked.connect(self.open_case_form)
        bottom_buttons_layout.addWidget(btn_kasa)



        btn_db_yol = self.renkli_buton("VERİTABANI YOLU DEĞİŞTİR", 'fa5s.database', 'navy')
        btn_db_yol.clicked.connect(self.select_backup_location)
        bottom_buttons_layout.addWidget(btn_db_yol)

        btn_db_onar = self.renkli_buton("VERİTABANI ONAR", 'fa5s.wrench', 'orange')
        btn_db_onar.clicked.connect(self.repair_database)
        bottom_buttons_layout.addWidget(btn_db_onar)
        
        btn_sistem_kapat = self.renkli_buton("SİSTEMİ KAPAT", 'fa5s.power-off', 'red')
        btn_sistem_kapat.clicked.connect(self.close)
        bottom_buttons_layout.addWidget(btn_sistem_kapat)

        # Alt bilgi
        alt_bilgi_layout = QHBoxLayout()
        bugun = datetime.datetime.now().strftime("%d.%m.%Y")
        alt_bilgi_layout.addWidget(QLabel(f"TARİH\n{bugun}"))
        alt_bilgi_layout.addStretch()
        alt_bilgi_layout.addWidget(QLabel("OTO SERVİS PROGRAMINA HOŞGELDİNİZ"))

        # Add layouts to the main layout
        ana_layout.addLayout(top_buttons_layout)
        
        # Removed image_label from layout since it's a background now
        # ana_layout.addWidget(image_label) 
        ana_layout.addWidget(image_label)
        ana_layout.addLayout(bottom_buttons_layout)
        ana_layout.addStretch()
        ana_layout.addLayout(alt_bilgi_layout)

        self.setLayout(ana_layout)

    def formlari_onceden_yukle(self, moduller=None):
        """Form modüllerini her seferinde bir tane olmak üzere yükler; arada arayüz donmaz."""
        if moduller is None:
            moduller = list(ONCEDEN_YUKLENECEK_MODULLER)
        if not moduller:
            # PDF fontlarını ilk açılışta bir kez hazırlar (sonra önbellekten okunur); arayüzü bekletmez
            try:
                import threading
                import pdf_belgeler
                threading.Thread(target=pdf_belgeler.fontlari_hazirla, daemon=True).start()
            except Exception as e:
                print(f"PDF fontları önceden hazırlanamadı: {e}")
            return
        try:
            importlib.import_module(moduller[0])
        except Exception as e:
            print(f"Modül önceden yüklenemedi ({moduller[0]}): {e}")
        QTimer.singleShot(0, lambda: self.formlari_onceden_yukle(moduller[1:]))

    def arac_karti_ekle_ac(self):
        from add_car import AddCarForm
        self.add_car_form = AddCarForm()
        self.add_car_form.show()

    def cari_ekle_ac(self):
        from add_cari import AddCariForm
        self.add_cari_form = AddCariForm()
        self.add_cari_form.show()

    def arac_listesi_ac(self):
        from car_list import CarListForm
        self.car_list_form = CarListForm()
        self.car_list_form.show()

    def cari_listesi_ac(self):
        from cari_list import CariListForm
        self.cari_list_form = CariListForm()
        self.cari_list_form.show()

    def servis_girisi_ekle_ac(self):
        from servis_form import ServisForm
        self.servis_form = ServisForm(self)
        self.servis_form.setModal(True)
        self.servis_form.show()

    def open_open_service_form(self):
        from open_service import OpenServiceForm
        self.open_service_form = OpenServiceForm()
        self.open_service_form.show()

    def open_close_service_form(self):
        from close_service import CloseServiceForm
        self.close_service_form = CloseServiceForm()
        self.close_service_form.show()

    def open_payment_history_form(self):
        from payment_history import PaymentHistoryForm
        self.payment_history_form = PaymentHistoryForm()
        self.payment_history_form.show()

    def open_add_new_offer_form(self):
        from add_new_offer import AddNewOfferForm
        self.add_new_offer_form = AddNewOfferForm()
        self.add_new_offer_form.setModal(True)
        self.add_new_offer_form.show()

    def open_add_offer_form(self):
        from add_offer import AddOfferForm
        self.add_offer_form = AddOfferForm()
        self.add_offer_form.show()

    def open_case_form(self):
        from case import CaseTotalsForm
        self.case_form = CaseTotalsForm()
        self.case_form.show()

    def repair_database(self):
        """Veritabanını onarır veya seçilen dosyadan geri yükler"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Veritabanı Onarım Seçeneği")
        msg_box.setText("Veritabanı onarımını otomatik olarak (en son yedekten) yapmak mı istiyorsunuz, yoksa bir yedek dosyası seçmek mi istersiniz?")
        
        onar_button = msg_box.addButton("Onar", QMessageBox.YesRole)
        yeni_sec_button = msg_box.addButton("Yeni seç", QMessageBox.NoRole)
        iptal_button = msg_box.addButton("İptal", QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(onar_button)
        msg_box.exec_()

        if msg_box.clickedButton() == onar_button:
            # Otomatik onarım (mevcut mantık)
            success, message = self.backup_manager.repair_database()
            if success:
                QMessageBox.information(self, "Başarılı", message)
            else:
                QMessageBox.critical(self, "Hata", message)

        elif msg_box.clickedButton() == yeni_sec_button:
            # Dosya seçerek onarım/geri yükleme
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Yedek Veritabanı Seç",
                "", # Başlangıç dizini, boş bırakırsanız varsayılanı kullanır
                "Veritabanı Dosyaları (*.db)"
            )

            if file_path:
                success, message = self.backup_manager.restore_database_from_file(file_path)
                if success:
                    QMessageBox.information(self, "Başarılı",
                        f"{message}\n\nAçık olan diğer pencereler (Kasa, listeler vb.) eski veriyi gösteriyor olabilir; "
                        "kapatıp yeniden açın.\nKasa varsayılan olarak bugünün ödemelerini gösterir; eski ödemeler için "
                        "Kısa Tarih'ten 'Tümü'nü seçin.")
                else:
                    QMessageBox.critical(self, "Hata", message)
            else:
                QMessageBox.information(self, "Bilgi", "Dosya seçimi iptal edildi.")

        # Eğer İptal seçilirse bir şey yapma

def check_database():
    """Veritabanının varlığını kontrol eder ve gerekirse oluşturur"""
    if not os.path.exists("oto_servis.db"):
        create_database()
        return True
    return False

def veritabanini_hazirla():
    """
    Program açılırken veritabanını kullanılabilir hale getirir: yoksa oluşturur, eski/eksikse tamamlar
    (veriye dokunmadan), açılamıyorsa kullanıcıya yedekten geri yükleme veya yeni veritabanı seçeneği sunar.
    False dönerse program kapanmalıdır.
    """
    from database_progress import veritabani_sorunu
    try:
        if check_database():
            QMessageBox.information(None, "Bilgi", "Veritabanı başarıyla oluşturuldu!")
    except (sqlite3.Error, OSError) as e:
        QMessageBox.critical(None, "Hata",
            f"Veritabanı oluşturulamadı:\n{e}\n\n"
            f"Program klasörüne yazma izni olmayabilir ({os.getcwd()}).\n"
            "Programı 'Program Files' dışında bir klasöre (örn. C:\\OTO-SERVIS) taşıyıp tekrar açın.")
        return False

    sorun = veritabani_sorunu()
    while sorun:
        kutu = QMessageBox()
        kutu.setIcon(QMessageBox.Critical)
        kutu.setWindowTitle("Veritabanı Açılamıyor")
        kutu.setText(f"{sorun}\n\nNe yapmak istersiniz?")
        btn_yedek = kutu.addButton("Yedekten Geri Yükle", QMessageBox.AcceptRole)
        btn_yeni = kutu.addButton("Yeni Boş Veritabanı", QMessageBox.DestructiveRole)
        kutu.addButton("Programı Kapat", QMessageBox.RejectRole)
        kutu.exec_()

        if kutu.clickedButton() is btn_yedek:
            dosya, _ = QFileDialog.getOpenFileName(None, "Yedek Veritabanı Seç", BackupManager().backup_path,
                                                   "Veritabanı Dosyaları (*.db)")
            if dosya:
                basarili, mesaj = BackupManager().restore_database_from_file(dosya)
                (QMessageBox.information if basarili else QMessageBox.critical)(None, "Geri Yükleme", mesaj)
        elif kutu.clickedButton() is btn_yeni:
            # Bozuk dosya silinmez, yanına adı değiştirilerek bırakılır
            bozuk = f"oto_servis_acilamayan_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            try:
                os.replace("oto_servis.db", bozuk)
                create_database()
                QMessageBox.information(None, "Bilgi",
                    f"Yeni boş veritabanı oluşturuldu.\nAçılamayan dosya '{bozuk}' adıyla saklandı.")
            except (sqlite3.Error, OSError) as e:
                QMessageBox.critical(None, "Hata", f"Yeni veritabanı oluşturulamadı:\n{e}")
                return False
        else:
            return False
        sorun = veritabani_sorunu()
    return True

def beklenmeyen_hata(tur, deger, iz):
    """Yakalanmamış hatalarda program kapanmasın: kullanıcıya gösterilir ve hata_kaydi.log dosyasına yazılır."""
    metin = "".join(traceback.format_exception(tur, deger, iz))
    print(metin)
    try:
        with open("hata_kaydi.log", "a", encoding="utf-8") as kayit:
            kayit.write(f"\n[{datetime.datetime.now():%d.%m.%Y %H:%M:%S}]\n{metin}")
    except OSError:
        pass
    try:
        QMessageBox.critical(None, "Beklenmeyen Hata",
            f"İşlem tamamlanamadı:\n{deger}\n\n"
            "Ayrıntılar program klasöründeki 'hata_kaydi.log' dosyasına yazıldı. Program çalışmaya devam ediyor.")
    except Exception:
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sys.excepthook = beklenmeyen_hata

    # MAC adresi kontrolü
    if not verify_mac_address():
        QMessageBox.critical(None, "Hata",
            "Bu program sadece yetkili bilgisayarlarda çalışabilir!\n\n"
            "Lütfen sistem yöneticinize başvurun.")
        sys.exit(1)

    # Veritabanı kontrolü: yoksa oluşturur, eskiyse tamamlar, açılamıyorsa kullanıcıya sorar
    if not veritabanini_hazirla():
        sys.exit(1)

    dashboard = Dashboard()
    dashboard.showMaximized()
    QTimer.singleShot(300, dashboard.formlari_onceden_yukle)
    sys.exit(app.exec_())