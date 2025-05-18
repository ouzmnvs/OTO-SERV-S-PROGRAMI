from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy, QFrame, QDesktopWidget
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from qtawesome import icon
import sys
import datetime
from add_car import AddCarForm  # Satırın başına ekle
from add_cari import AddCariForm  # <-- Bunu da ekle
from car_list import CarListForm  # En üste ekle
from cari_list import CariListForm  # En üste ekleyin

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("İŞLEM SEÇİNİZ ...")
        self.resize_or_center()
        self.init_ui()

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
                /* box-shadow: 2px 2px 8px rgba(0,0,0,0.12); */
            }
            QPushButton:hover {
                background: #e0e0e0;
                /* box-shadow: 4px 4px 16px rgba(0,0,0,0.18); */
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
        tanimlamalar_layout.addWidget(self.renkli_buton("ÖDEME GEÇMİŞİ", 'fa5s.money-bill', 'teal'))
        ana_layout.addWidget(self.bolum_kutusu(tanimlamalar_layout))

        # İŞ TANIM VE SORGULAMA
        ana_layout.addWidget(self.bolum_baslik("SERVİS İŞLEMLERİ"))
        is_tanim_layout = QHBoxLayout()
        is_tanim_layout.setSpacing(15)
        is_tanim_layout.addWidget(self.renkli_buton("SERVİS GİRİŞİ EKLE", 'fa5s.tools', 'brown'))
        is_tanim_layout.addWidget(self.renkli_buton("AÇIK SERVİSLER", 'fa5s.check', 'green'))
        is_tanim_layout.addWidget(self.renkli_buton("KAPALI SERVİSLER", 'fa5s.clipboard-check', 'blue'))
        is_tanim_layout.addWidget(self.renkli_buton("RANDEVU", 'fa5s.calendar', 'red'))
        is_tanim_layout.addWidget(self.renkli_buton("ARAÇ GEÇMİŞİ", 'fa5s.history', 'gray'))
        ana_layout.addWidget(self.bolum_kutusu(is_tanim_layout))

        # FİNANS - DİĞER
        ana_layout.addWidget(self.bolum_baslik("FİNANS - DİĞER"))
        finans_layout = QHBoxLayout()
        finans_layout.setSpacing(15)
        finans_layout.addWidget(self.renkli_buton("KASA", 'mdi.cash-multiple', 'darkgreen'))  # <-- Güncellendi
        finans_layout.addWidget(self.renkli_buton("EXCEL'İ GÖSTER", 'fa5s.file-excel', 'green'))
        finans_layout.addWidget(self.renkli_buton("VERİTABANI YOLU DEĞİŞTİR", 'fa5s.database', 'navy'))
        finans_layout.addWidget(self.renkli_buton("SİSTEMİ KAPAT", 'fa5s.power-off', 'red'))
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())