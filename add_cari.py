from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QGridLayout
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys

class AddCariForm(QWidget):
    def __init__(self, dashboard_ref=None):
        super().__init__()
        self.dashboard_ref = dashboard_ref
        self.setWindowTitle("Cari Formu")
        # Dashboard %85 ekran kaplıyor, bu form ise yaklaşık %32 genişlik ve %35 yükseklik olsun
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.32)
        yukseklik = int(ekran.height() * 0.35)
        self.setFixedSize(genislik, yukseklik)
        self.init_ui()

    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(18)

        # Ortak stil
        input_style = """
            QLineEdit, QComboBox {
                font-size: 18px;
                padding: 8px 10px;
                border-radius: 6px;
                border: 1.5px solid #bbb;
                background: #fafbfc;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #1976d2;
                background: #fff;
            }
        """
        label_style = "font-size: 17px; font-weight: 600; color: #222;"
        group_style = """
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 12px;
                top: 2px;
                padding: 0 4px;
            }
        """

        # Cari Bilgileri
        cari_group = QGroupBox("Cari Bilgilerini Giriniz")
        cari_group.setStyleSheet(group_style)
        cari_layout = QGridLayout()
        cari_layout.setVerticalSpacing(16)
        cari_layout.setHorizontalSpacing(10)

        lbl_cari_kodu = QLabel("Cari Kodu")
        lbl_cari_kodu.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_kodu, 0, 0)
        self.cari_kodu = QLineEdit()
        self.cari_kodu.setStyleSheet(input_style)
        self.cari_kodu.setMinimumHeight(36)
        cari_layout.addWidget(self.cari_kodu, 0, 1, 1, 2)

        lbl_cari_unvan = QLabel("Cari Adı / Ünvanı")
        lbl_cari_unvan.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_unvan, 1, 0)
        self.cari_unvan = QLineEdit()
        self.cari_unvan.setStyleSheet(input_style)
        self.cari_unvan.setMinimumHeight(36)
        cari_layout.addWidget(self.cari_unvan, 1, 1, 1, 2)

        lbl_telefon = QLabel("Telefon")
        lbl_telefon.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_telefon, 2, 0)
        self.telefon = QLineEdit()
        self.telefon.setStyleSheet(input_style)
        self.telefon.setMinimumHeight(36)
        cari_layout.addWidget(self.telefon, 2, 1, 1, 2)

        lbl_cari_tipi = QLabel("Cari Tipi *")
        lbl_cari_tipi.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_tipi, 3, 0)
        self.cari_tipi = QComboBox()
        self.cari_tipi.setStyleSheet(input_style)
        self.cari_tipi.setMinimumHeight(36)
        self.cari_tipi.addItems(["Bireysel", "Kurumsal", "Diğer"])
        cari_layout.addWidget(self.cari_tipi, 3, 1, 1, 2)

        cari_group.setLayout(cari_layout)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        kaydet_btn = QPushButton(icon('fa5s.save', color='deeppink'), "Kaydet")
        kaydet_btn.setFixedWidth(140)
        kaydet_btn.setMinimumHeight(44)
        kaydet_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 800;
                background: #fff;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: #ffe4f0;
                border: 2px solid #e91e63;
            }
        """)
        kaydet_btn.clicked.connect(self.kaydet_tiklandi)
        iptal_btn = QPushButton(icon('fa5s.times', color='darkred'), "İptal")
        iptal_btn.setFixedWidth(140)
        iptal_btn.setMinimumHeight(44)
        iptal_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 800;
                background: #fff;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: #ffeaea;
                border: 2px solid #b71c1c;
            }
        """)
        iptal_btn.clicked.connect(self.iptal_tiklandi)
        btn_layout.addWidget(kaydet_btn)
        btn_layout.addWidget(iptal_btn)

        # Ana layouta ekle
        ana_layout.addWidget(cari_group)
        ana_layout.addStretch()
        ana_layout.addLayout(btn_layout)

        self.setLayout(ana_layout)

    def iptal_tiklandi(self):
        self.close()
        if self.dashboard_ref:
            self.dashboard_ref.show()

    def kaydet_tiklandi(self):
        # Formdaki bilgileri al
        cari_kodu = self.cari_kodu.text().strip()
        cari_unvan = self.cari_unvan.text().strip()
        telefon = self.telefon.text().strip()
        cari_tipi = self.cari_tipi.currentText().strip()

        # Gerekli alanların doldurulup doldurulmadığını kontrol et
        if not cari_kodu or not cari_unvan or not cari_tipi:
            print("Lütfen gerekli alanları doldurun!")
            return

        # Veritabanına ekle
        try:
            import sqlite3
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO CARİ (cari_kodu, cari_ad_unvan, telefon, cari_tipi, borc)
                VALUES (?, ?, ?, ?, ?)
            """, (cari_kodu, cari_unvan, telefon,cari_tipi, 0))  # Borç varsayılan olarak 0
            conn.commit()
            print("Cari başarıyla eklendi!")
            self.close()  # Formu kapat
            if self.dashboard_ref:
                self.dashboard_ref.show()
        except sqlite3.IntegrityError as e:
            print(f"Veritabanı hatası: {e}")
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AddCariForm()
    form.show()
    sys.exit(app.exec_())