from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QGridLayout
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from cari_select_list import CariSelectListForm  # En üste ekleyin

class AddCarForm(QWidget):
    def __init__(self, dashboard_ref=None):
        super().__init__()
        self.dashboard_ref = dashboard_ref
        self.setWindowTitle("Araç Kartı Formu")
        # Dashboard %85 ekran kaplıyor, bu form ise yaklaşık %40 genişlik ve %50 yükseklik olsun
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.40)
        yukseklik = int(ekran.height() * 0.50)
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

        # Cari Seçimi
        cari_group = QGroupBox("Cari Seçimi Yapınız")
        cari_group.setStyleSheet(group_style)
        cari_layout = QGridLayout()
        cari_layout.setVerticalSpacing(16)
        cari_layout.setHorizontalSpacing(10)
        lbl_cari_kodu = QLabel("Cari Kodu *")
        lbl_cari_kodu.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_kodu, 0, 0)
        self.cari_kodu = QLineEdit()
        self.cari_kodu.setStyleSheet(input_style)
        self.cari_kodu.setMinimumWidth(160)
        self.cari_kodu.setMaximumWidth(220)
        self.cari_kodu.setMinimumHeight(36)
        cari_layout.addWidget(self.cari_kodu, 0, 1)
        sec_btn = QPushButton(icon('fa5s.user-check', color='black'), "Seç")
        sec_btn.setMinimumHeight(36)
        sec_btn.setStyleSheet("font-size:16px; font-weight:700; padding:6px 18px;")
        sec_btn.clicked.connect(self.cari_sec_ac)
        cari_layout.addWidget(sec_btn, 0, 2)
        lbl_cari_unvani = QLabel("Cari Ünvanı *")
        lbl_cari_unvani.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_unvani, 1, 0)
        self.cari_unvani = QLineEdit()
        self.cari_unvani.setStyleSheet(input_style)
        self.cari_unvani.setMinimumHeight(36)
        cari_layout.addWidget(self.cari_unvani, 1, 1, 1, 2)
        cari_group.setLayout(cari_layout)

        # Araç Bilgileri
        arac_group = QGroupBox("Araç Bilgilerini Giriniz")
        arac_group.setStyleSheet(group_style)
        arac_layout = QGridLayout()
        arac_layout.setVerticalSpacing(16)
        arac_layout.setHorizontalSpacing(10)

        lbl_plaka = QLabel("Plaka *")
        lbl_plaka.setStyleSheet(label_style)
        arac_layout.addWidget(lbl_plaka, 0, 0)
        self.plaka = QLineEdit()
        self.plaka.setStyleSheet(input_style)
        self.plaka.setMinimumHeight(36)
        arac_layout.addWidget(self.plaka, 0, 1, 1, 2)

        lbl_tip = QLabel("Araç Tipi *")
        lbl_tip.setStyleSheet(label_style)
        arac_layout.addWidget(lbl_tip, 1, 0)
        self.arac_tipi = QComboBox()
        self.arac_tipi.setStyleSheet(input_style)
        self.arac_tipi.setMinimumHeight(36)
        self.arac_tipi.addItems(["", "Otomobil", "Kamyonet", "Minibüs", "Diğer"])
        arac_layout.addWidget(self.arac_tipi, 1, 1, 1, 2)

        lbl_model_yili = QLabel("Model Yılı")
        lbl_model_yili.setStyleSheet(label_style)
        arac_layout.addWidget(lbl_model_yili, 2, 0)
        self.model_yili = QLineEdit()
        self.model_yili.setStyleSheet(input_style)
        self.model_yili.setMinimumHeight(36)
        arac_layout.addWidget(self.model_yili, 2, 1, 1, 2)

        lbl_marka = QLabel("Marka")
        lbl_marka.setStyleSheet(label_style)
        arac_layout.addWidget(lbl_marka, 3, 0)
        self.marka = QLineEdit()
        self.marka.setStyleSheet(input_style)
        self.marka.setMinimumHeight(36)
        arac_layout.addWidget(self.marka, 3, 1, 1, 2)

        lbl_model = QLabel("Model")
        lbl_model.setStyleSheet(label_style)
        arac_layout.addWidget(lbl_model, 4, 0)
        self.model = QLineEdit()
        self.model.setStyleSheet(input_style)
        self.model.setMinimumHeight(36)
        arac_layout.addWidget(self.model, 4, 1, 1, 2)
        arac_group.setLayout(arac_layout)

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
        ana_layout.addWidget(arac_group)
        ana_layout.addStretch()
        ana_layout.addLayout(btn_layout)

        self.setLayout(ana_layout)

    def iptal_tiklandi(self):
        self.close()
        if self.dashboard_ref:
            self.dashboard_ref.show()

    def kaydet_tiklandi(self):
        # Formdaki bilgileri al
        cari_kodu = self.cari_kodu.text().strip()  # Cari ID'si
        plaka = self.plaka.text().strip()
        arac_tipi = self.arac_tipi.currentText().strip()
        model_yili = self.model_yili.text().strip()
        marka = self.marka.text().strip()
        model = self.model.text().strip()

        # Gerekli alanların doldurulup doldurulmadığını kontrol et
        if not cari_kodu or not plaka or not arac_tipi:
            print("Lütfen gerekli alanları doldurun!")
            return

        # Veritabanına ekle
        try:
            import sqlite3
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ARAÇLAR (cari_kodu, plaka, arac_tipi, model_yili, marka, model)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cari_kodu, plaka, arac_tipi, model_yili, marka, model))
            conn.commit()
            print("Araç başarıyla eklendi!")
            self.close()  # Formu kapat
            if self.dashboard_ref:
                self.dashboard_ref.show()
        except sqlite3.IntegrityError as e:
            print(f"Veritabanı hatası: {e}")
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
        finally:
            conn.close()

    def cari_sec_ac(self):
        self.cari_select_form = CariSelectListForm(parent_form=self)
        self.cari_select_form.show()

    def set_cari_bilgileri(self, cari_kodu, cari_unvani, telefon=None, cari_tipi=None):
        self.cari_kodu.setText(cari_kodu)
        self.cari_unvani.setText(cari_unvani)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AddCarForm()
    form.show()
    sys.exit(app.exec_())