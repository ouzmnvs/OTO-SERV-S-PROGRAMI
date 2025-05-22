from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
import sqlite3

class AddCariForm(QDialog):
    def __init__(self, dashboard_ref=None, on_saved=None):
        super().__init__()
        self.dashboard_ref = dashboard_ref
        self.on_saved = on_saved
        self.setWindowTitle("Cari Formu")
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.32)
        yukseklik = int(ekran.height() * 0.50)
        self.setFixedSize(genislik, yukseklik)
        self.init_ui()

    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(18)

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

        cari_group = QGroupBox("Cari Bilgilerini Giriniz")
        cari_group.setStyleSheet(group_style)
        cari_layout = QGridLayout()
        cari_layout.setVerticalSpacing(16)
        cari_layout.setHorizontalSpacing(10)

        # Cari Kodu
        lbl_cari_kodu = QLabel("Cari Kodu *")
        lbl_cari_kodu.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_kodu, 0, 0)
        self.cari_kodu = QLineEdit()
        self.cari_kodu.setStyleSheet(input_style)
        self.cari_kodu.setMinimumHeight(36)
        cari_layout.addWidget(self.cari_kodu, 0, 1, 1, 2)

        # Cari Adı / Ünvanı
        lbl_cari_unvan = QLabel("Cari Adı / Ünvanı *")
        lbl_cari_unvan.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_unvan, 1, 0)
        self.cari_unvan = QLineEdit()
        self.cari_unvan.setStyleSheet(input_style)
        self.cari_unvan.setMinimumHeight(36)
        cari_layout.addWidget(self.cari_unvan, 1, 1, 1, 2)

        # TC Kimlik No
        lbl_tc_kimlik_no = QLabel("TC Kimlik No")
        lbl_tc_kimlik_no.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_tc_kimlik_no, 2, 0)
        self.tc_kimlik_no = QLineEdit()
        self.tc_kimlik_no.setStyleSheet(input_style)
        self.tc_kimlik_no.setMinimumHeight(36)
        self.tc_kimlik_no.setMaxLength(11)
        cari_layout.addWidget(self.tc_kimlik_no, 2, 1, 1, 2)

        # Vergi No
        lbl_vergi_no = QLabel("Vergi No")
        lbl_vergi_no.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_vergi_no, 3, 0)
        self.vergi_no = QLineEdit()
        self.vergi_no.setStyleSheet(input_style)
        self.vergi_no.setMinimumHeight(36)
        cari_layout.addWidget(self.vergi_no, 3, 1, 1, 2)

        # Cep Telefonu
        lbl_cep_telefonu = QLabel("Cep Telefonu")
        lbl_cep_telefonu.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cep_telefonu, 4, 0)
        self.cep_telefonu = QLineEdit()
        self.cep_telefonu.setStyleSheet(input_style)
        self.cep_telefonu.setMinimumHeight(36)
        self.cep_telefonu.setMaxLength(11)
        cari_layout.addWidget(self.cep_telefonu, 4, 1, 1, 2)

        # Cari Tipi
        lbl_cari_tipi = QLabel("Cari Tipi *")
        lbl_cari_tipi.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_tipi, 5, 0)
        self.cari_tipi = QComboBox()
        self.cari_tipi.setStyleSheet(input_style)
        self.cari_tipi.setMinimumHeight(36)
        self.cari_tipi.addItems(["Bireysel", "Kurumsal", "Diğer"])
        cari_layout.addWidget(self.cari_tipi, 5, 1, 1, 2)

        # Açıklama
        lbl_aciklama = QLabel("Açıklama")
        lbl_aciklama.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_aciklama, 6, 0)
        self.aciklama = QLineEdit()
        self.aciklama.setStyleSheet(input_style)
        self.aciklama.setMinimumHeight(36)
        cari_layout.addWidget(self.aciklama, 6, 1, 1, 2)

        cari_group.setLayout(cari_layout)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        kaydet_btn = QPushButton(icon('fa5s.save', color='deeppink'), "Kaydet")
        kaydet_btn.setFixedWidth(140)
        kaydet_btn.setMinimumHeight(44)
        kaydet_btn.clicked.connect(self.kaydet_tiklandi)
        iptal_btn = QPushButton(icon('fa5s.times', color='darkred'), "İptal")
        iptal_btn.setFixedWidth(140)
        iptal_btn.setMinimumHeight(44)
        iptal_btn.clicked.connect(self.iptal_tiklandi)
        btn_layout.addWidget(kaydet_btn)
        btn_layout.addWidget(iptal_btn)

        ana_layout.addWidget(cari_group)
        ana_layout.addStretch()
        ana_layout.addLayout(btn_layout)
        self.setLayout(ana_layout)

    def iptal_tiklandi(self):
        self.close()
        if self.dashboard_ref:
            self.dashboard_ref.show()

    def kaydet_tiklandi(self):
        cari_kodu = self.cari_kodu.text().strip()
        cari_unvan = self.cari_unvan.text().strip()
        tc_kimlik_no = self.tc_kimlik_no.text().strip()
        vergi_no = self.vergi_no.text().strip()
        cep_telefonu = self.cep_telefonu.text().strip()
        cari_tipi = self.cari_tipi.currentText().strip()
        aciklama = self.aciklama.text().strip()

        # Zorunlu alan kontrolü
        if not cari_kodu or not cari_unvan or not cari_tipi:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen * ile işaretli alanları doldurun!")
            return

        # TC ve telefon sadece sayı olmalı
        if tc_kimlik_no and not tc_kimlik_no.isdigit():
            QMessageBox.warning(self, "Hatalı Giriş", "TC Kimlik No sadece rakamlardan oluşmalıdır!")
            return
        if cep_telefonu and not cep_telefonu.isdigit():
            QMessageBox.warning(self, "Hatalı Giriş", "Cep Telefonu sadece rakamlardan oluşmalıdır!")
            return

        # Aynı cari kodu var mı kontrolü
        try:
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM cariler WHERE cari_kodu = ?", (cari_kodu,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Tekrarlı Kayıt", "Bu cari kodu zaten kayıtlı!")
                return

            cursor.execute("""
                INSERT INTO cariler (cari_kodu, cari_ad_unvan, cari_tipi, tc_kimlik_no, vergi_no, cep_telefonu, aciklama)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cari_kodu, cari_unvan, cari_tipi, tc_kimlik_no, vergi_no, cep_telefonu, aciklama))
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Cari başarıyla eklendi!")
            self.accept()  # Modalı kapat ve Accepted olarak dön
            if self.on_saved:
                self.on_saved()
            self.close()
            if self.dashboard_ref:
                self.dashboard_ref.show()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu:\n{e}")
        finally:
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AddCariForm()
    form.show()
    sys.exit(app.exec_())