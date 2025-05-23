from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy, QFrame, QDesktopWidget,
    QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from qtawesome import icon
import sys
import datetime
import os
import shutil
import json
from add_car import AddCarForm
from add_cari import AddCariForm
from car_list import CarListForm
from cari_list import CariListForm
from servis_form import ServisForm
from open_service import OpenServiceForm
from close_service import CloseServiceForm
from payment_history import PaymentHistoryForm
from add_new_offer import AddNewOfferForm
from add_offer import AddOfferForm
from case import CaseTotalsForm
from create_database import create_database

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OTO SERVİS PROGRAMI")
        self.resize_or_center()
        self.load_backup_path()
        self.init_ui()

    def load_backup_path(self):
        """Yedekleme yolunu yapılandırma dosyasından yükler"""
        self.config_file = "db_config.json"
        self.default_backup_path = os.path.join(os.path.expanduser("~"), "Desktop", "OTO-SERVIS-DB")
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.backup_path = config.get('backup_path', self.default_backup_path)
            else:
                self.backup_path = self.default_backup_path
        except Exception:
            self.backup_path = self.default_backup_path

    def save_backup_path(self):
        """Yedekleme yolunu yapılandırma dosyasına kaydeder"""
        try:
            config = {'backup_path': self.backup_path}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Yapılandırma kaydetme hatası: {str(e)}")

    def select_backup_location(self):
        """Yedekleme konumunu seçmek için dosya diyaloğu açar"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Veritabanı Yedekleme Konumunu Seçin",
            self.backup_path,
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.backup_path = folder
            self.save_backup_path()
            QMessageBox.information(
                self,
                "Bilgi",
                f"Yedekleme konumu güncellendi:\n{self.backup_path}"
            )

    def closeEvent(self, event):
        """Dashboard kapatıldığında çalışacak fonksiyon"""
        try:
            # Klasör yoksa oluştur
            if not os.path.exists(self.backup_path):
                os.makedirs(self.backup_path)
            
            # Veritabanı dosyasının kaynak ve hedef yolları
            source_db = "oto_servis.db"
            target_db = os.path.join(self.backup_path, "oto_servis.db")
            
            # Veritabanı dosyasını kopyala
            if os.path.exists(source_db):
                shutil.copy2(source_db, target_db)
                print(f"Veritabanı başarıyla yedeklendi: {target_db}")
            
            event.accept()
        except Exception as e:
            print(f"Veritabanı yedekleme hatası: {str(e)}")
            event.accept()

    def resize_or_center(self):
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.85)
        yukseklik = int(ekran.height() * 0.85)
        self.resize(genislik, yukseklik)
        x = (ekran.width() - genislik) // 2
        y = (ekran.height() - yukseklik) // 2 - 40
        self.move(x, y)

    def renkli_buton(self, text, icon_name, color):
        btn = QPushButton(text)
        btn.setIcon(icon(icon_name, color=color))
        btn.setIconSize(QSize(32, 32))
        btn.setMinimumHeight(60)
        btn.setStyleSheet("""
            QPushButton {
                font-weight: 900;
                font-size: 17px;
                background: #f5f5f5;
                border: 1px solid #bbb;
                border-radius: 8px;
                padding: 8px;
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
            font: bold 16px;
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        return lbl

    def bolum_kutusu(self, widget_layout):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #f5f5f5;
                border: 1px solid #bbb;
                border-radius: 8px;
            }
        """)
        frame.setLayout(widget_layout)
        return frame

    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(18)

        # TANIMLAMALAR
        ana_layout.addWidget(self.bolum_baslik("CARİ VE ARAÇ İŞLEMLERİ"))
        tanimlamalar_layout = QHBoxLayout()
        tanimlamalar_layout.setSpacing(15)

        # Araç Kartı Ekle butonunu ayrı tanımla ve sinyal bağla
        btn_arac_ekle = self.renkli_buton("ARAÇ KARTI EKLE", 'fa5s.car', 'blue')
        btn_arac_ekle.clicked.connect(self.arac_karti_ekle_ac)
        tanimlamalar_layout.addWidget(btn_arac_ekle)

        # Araç Listesi butonunu ayrı tanımla ve sinyal bağla
        btn_arac_listesi = self.renkli_buton("ARAÇ LİSTESİ", 'fa5s.list', 'orange')
        btn_arac_listesi.clicked.connect(self.arac_listesi_ac)
        tanimlamalar_layout.addWidget(btn_arac_listesi)

        # Cari Ekle butonunu ayrı tanımla ve sinyal bağla
        btn_cari_ekle = self.renkli_buton("CARİ EKLE", 'fa5s.user-plus', 'green')
        btn_cari_ekle.clicked.connect(self.cari_ekle_ac)
        tanimlamalar_layout.addWidget(btn_cari_ekle)

        btn_cari_listesi = self.renkli_buton("CARİ LİSTESİ", 'fa5s.users', 'purple')
        btn_cari_listesi.clicked.connect(self.cari_listesi_ac)
        tanimlamalar_layout.addWidget(btn_cari_listesi)

        # Ödeme Geçmişi Butonu
        btn_odeme_gecmisi = self.renkli_buton("ÖDEME GEÇMİŞİ", 'fa5s.money-bill', 'teal')
        btn_odeme_gecmisi.clicked.connect(self.open_payment_history_form)
        tanimlamalar_layout.addWidget(btn_odeme_gecmisi)

        ana_layout.addWidget(self.bolum_kutusu(tanimlamalar_layout))

        # İŞ TANIM VE SORGULAMA
        ana_layout.addWidget(self.bolum_baslik("SERVİS İŞLEMLERİ"))
        is_tanim_layout = QHBoxLayout()
        is_tanim_layout.setSpacing(15)
        btn_servis_girisi = self.renkli_buton("SERVİS GİRİŞİ EKLE", 'fa5s.tools', 'brown')
        btn_servis_girisi.clicked.connect(self.servis_girisi_ekle_ac)
        is_tanim_layout.addWidget(btn_servis_girisi)
        btn_acik_servisler = self.renkli_buton("AÇIK SERVİSLER", 'fa5s.check', 'green')
        btn_acik_servisler.clicked.connect(self.open_open_service_form)
        is_tanim_layout.addWidget(btn_acik_servisler)

        # Kapalı Servisler Butonu
        btn_kapali_servisler = self.renkli_buton("KAPALI SERVİSLER", 'fa5s.clipboard-check', 'blue')
        btn_kapali_servisler.clicked.connect(self.open_close_service_form)
        is_tanim_layout.addWidget(btn_kapali_servisler)

        # Teklif Ver butonunu ayrı tanımla ve sinyal bağla
        btn_teklif_ver = self.renkli_buton("TEKLİF VER", 'fa5s.file-invoice-dollar', 'red')
        btn_teklif_ver.clicked.connect(self.open_add_new_offer_form)
        is_tanim_layout.addWidget(btn_teklif_ver)
        
        # Teklifler butonunu ayrı tanımla ve sinyal bağla
        btn_teklifler = self.renkli_buton("TEKLİFLER", 'fa5s.file-invoice', 'gray')
        btn_teklifler.clicked.connect(self.open_add_offer_form)
        is_tanim_layout.addWidget(btn_teklifler)
        
        ana_layout.addWidget(self.bolum_kutusu(is_tanim_layout))

        # FİNANS - DİĞER
        ana_layout.addWidget(self.bolum_baslik("FİNANS - DİĞER"))
        finans_layout = QHBoxLayout()
        finans_layout.setSpacing(15)
        
        # KASA butonunu ayrı tanımla ve sinyal bağla
        btn_kasa = self.renkli_buton("KASA", 'mdi.cash-multiple', 'darkgreen')
        btn_kasa.clicked.connect(self.open_case_form)
        finans_layout.addWidget(btn_kasa)
        
        finans_layout.addWidget(self.renkli_buton("EXCEL'İ GÖSTER", 'fa5s.file-excel', 'green'))
        
        # Veritabanı Yolu Değiştir butonunu ayrı tanımla ve sinyal bağla
        btn_db_yol = self.renkli_buton("VERİTABANI YOLU DEĞİŞTİR", 'fa5s.database', 'navy')
        btn_db_yol.clicked.connect(self.select_backup_location)
        finans_layout.addWidget(btn_db_yol)
        
        # Sistem Kapat butonunu ayrı tanımla ve sinyal bağla
        btn_sistem_kapat = self.renkli_buton("SİSTEMİ KAPAT", 'fa5s.power-off', 'red')
        btn_sistem_kapat.clicked.connect(self.close)
        finans_layout.addWidget(btn_sistem_kapat)
        
        ana_layout.addWidget(self.bolum_kutusu(finans_layout))

        # Alt bilgi
        alt_bilgi_layout = QHBoxLayout()
        bugun = datetime.datetime.now().strftime("%d.%m.%Y")
        alt_bilgi_layout.addWidget(QLabel(f"TARİH\n{bugun}"))
        alt_bilgi_layout.addStretch()
        alt_bilgi_layout.addWidget(QLabel("OTO SERVİS PROGRAMINA HOŞGELDİNİZ"))

        ana_layout.addStretch()
        ana_layout.addLayout(alt_bilgi_layout)

        self.setLayout(ana_layout)

    def arac_karti_ekle_ac(self):
        self.add_car_form = AddCarForm()
        self.add_car_form.show()

    def cari_ekle_ac(self):
        self.add_cari_form = AddCariForm()
        self.add_cari_form.show()

    def arac_listesi_ac(self):
        self.car_list_form = CarListForm()
        self.car_list_form.show()

    def cari_listesi_ac(self):
        self.cari_list_form = CariListForm()
        self.cari_list_form.show()

    def servis_girisi_ekle_ac(self):
        self.servis_form = ServisForm(self)
        self.servis_form.setModal(True)
        self.servis_form.show()

    def open_open_service_form(self):
        self.open_service_form = OpenServiceForm()
        self.open_service_form.show()

    def open_close_service_form(self):
        self.close_service_form = CloseServiceForm()
        self.close_service_form.show()

    def open_payment_history_form(self):
        self.payment_history_form = PaymentHistoryForm()
        self.payment_history_form.show()

    def open_add_new_offer_form(self):
        self.add_new_offer_form = AddNewOfferForm()
        self.add_new_offer_form.setModal(True)
        self.add_new_offer_form.show()

    def open_add_offer_form(self):
        self.add_offer_form = AddOfferForm()
        self.add_offer_form.show()

    def open_case_form(self):
        self.case_form = CaseTotalsForm()
        self.case_form.show()

def check_database():
    """Veritabanının varlığını kontrol eder ve gerekirse oluşturur"""
    if not os.path.exists("oto_servis.db"):
        create_database()
        return True
    return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Veritabanı kontrolü
    if check_database():
        QMessageBox.information(None, "Bilgi", "Veritabanı başarıyla oluşturuldu!")
    
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())