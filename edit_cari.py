from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt

import sqlite3

class EditCariForm(QDialog):
    def __init__(self, cari_kodu, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cari Kaydı Düzenle")
        self.cari_kodu = cari_kodu
        self.setMinimumWidth(600)  # Genişlik artırıldı
        self.init_ui()
        self.load_cari()

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

        cari_group = QGroupBox("Cari Bilgilerini Düzenle")
        cari_group.setStyleSheet(group_style)
        cari_layout = QGridLayout()
        cari_layout.setVerticalSpacing(16)
        cari_layout.setHorizontalSpacing(10)

        # Cari Kodu (readonly)
        lbl_cari_kodu = QLabel("Cari Kodu")
        lbl_cari_kodu.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_kodu, 0, 0)
        self.cari_kodu_edit = QLineEdit()
        self.cari_kodu_edit.setReadOnly(True)
        self.cari_kodu_edit.setStyleSheet(input_style)
        self.cari_kodu_edit.setMinimumHeight(36)
        cari_layout.addWidget(self.cari_kodu_edit, 0, 1, 1, 2)

        # Cari Adı / Ünvanı
        lbl_cari_unvan = QLabel("Cari Adı / Ünvanı *")
        lbl_cari_unvan.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_unvan, 1, 0)
        self.cari_ad_unvan_edit = QLineEdit()
        self.cari_ad_unvan_edit.setStyleSheet(input_style)
        self.cari_ad_unvan_edit.setMinimumHeight(36)
        cari_layout.addWidget(self.cari_ad_unvan_edit, 1, 1, 1, 2)

        # Cari Tipi
        lbl_cari_tipi = QLabel("Cari Tipi *")
        lbl_cari_tipi.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_tipi, 2, 0)
        self.cari_tipi_combo = QComboBox()
        self.cari_tipi_combo.setStyleSheet(input_style)
        self.cari_tipi_combo.setMinimumHeight(36)
        self.cari_tipi_combo.addItems(["Bireysel", "Kurumsal", "Diğer"])
        cari_layout.addWidget(self.cari_tipi_combo, 2, 1, 1, 2)

        # TC Kimlik No
        lbl_tc_kimlik_no = QLabel("TC Kimlik No")
        lbl_tc_kimlik_no.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_tc_kimlik_no, 3, 0)
        self.tc_kimlik_no_edit = QLineEdit()
        self.tc_kimlik_no_edit.setStyleSheet(input_style)
        self.tc_kimlik_no_edit.setMinimumHeight(36)
        self.tc_kimlik_no_edit.setMaxLength(11)
        cari_layout.addWidget(self.tc_kimlik_no_edit, 3, 1, 1, 2)

        # Vergi No
        lbl_vergi_no = QLabel("Vergi No")
        lbl_vergi_no.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_vergi_no, 4, 0)
        self.vergi_no_edit = QLineEdit()
        self.vergi_no_edit.setStyleSheet(input_style)
        self.vergi_no_edit.setMinimumHeight(36)
        cari_layout.addWidget(self.vergi_no_edit, 4, 1, 1, 2)

        # Cep Telefonu
        lbl_cep_telefonu = QLabel("Cep Telefonu")
        lbl_cep_telefonu.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cep_telefonu, 5, 0)
        self.cep_telefonu_edit = QLineEdit()
        self.cep_telefonu_edit.setStyleSheet(input_style)
        self.cep_telefonu_edit.setMinimumHeight(36)
        self.cep_telefonu_edit.setMaxLength(11)
        cari_layout.addWidget(self.cep_telefonu_edit, 5, 1, 1, 2)

        # Açıklama
        lbl_aciklama = QLabel("Açıklama")
        lbl_aciklama.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_aciklama, 6, 0)
        self.aciklama_edit = QLineEdit()
        self.aciklama_edit.setStyleSheet(input_style)
        self.aciklama_edit.setMinimumHeight(36)
        cari_layout.addWidget(self.aciklama_edit, 6, 1, 1, 2)

        cari_group.setLayout(cari_layout)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_guncelle = QPushButton("Güncelle")
        btn_guncelle.setFixedWidth(140)
        btn_guncelle.setMinimumHeight(44)
        btn_guncelle.clicked.connect(self.guncelle)
        btn_iptal = QPushButton("İptal")
        btn_iptal.setFixedWidth(140)
        btn_iptal.setMinimumHeight(44)
        btn_iptal.clicked.connect(self.reject)
        btn_layout.addWidget(btn_guncelle)
        btn_layout.addWidget(btn_iptal)

        ana_layout.addWidget(cari_group)
        ana_layout.addStretch()
        ana_layout.addLayout(btn_layout)
        self.setLayout(ana_layout)

    def load_cari(self):
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cari_kodu, cari_ad_unvan, cari_tipi, tc_kimlik_no, vergi_no, cep_telefonu, aciklama
            FROM cariler WHERE cari_kodu = ?
        """, (self.cari_kodu,))
        row = cursor.fetchone()
        conn.close()
        if row:
            self.cari_kodu_edit.setText(row[0])
            self.cari_ad_unvan_edit.setText(row[1])
            idx = self.cari_tipi_combo.findText(row[2]) if row[2] else 0
            self.cari_tipi_combo.setCurrentIndex(idx)
            self.tc_kimlik_no_edit.setText(row[3] or "")
            self.vergi_no_edit.setText(row[4] or "")
            self.cep_telefonu_edit.setText(row[5] or "")
            self.aciklama_edit.setText(row[6] or "")

    def guncelle(self):
        cari_ad_unvan = self.cari_ad_unvan_edit.text().strip()
        cari_tipi = self.cari_tipi_combo.currentText()
        tc_kimlik_no = self.tc_kimlik_no_edit.text().strip()
        vergi_no = self.vergi_no_edit.text().strip()
        cep_telefonu = self.cep_telefonu_edit.text().strip()
        aciklama = self.aciklama_edit.text().strip()

        if not cari_ad_unvan:
            QMessageBox.warning(self, "Uyarı", "Cari adı/ünvanı boş olamaz!")
            return

        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cariler SET
                cari_ad_unvan = ?,
                cari_tipi = ?,
                tc_kimlik_no = ?,
                vergi_no = ?,
                cep_telefonu = ?,
                aciklama = ?
            WHERE cari_kodu = ?
        """, (cari_ad_unvan, cari_tipi, tc_kimlik_no, vergi_no, cep_telefonu, aciklama, self.cari_kodu))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Başarılı", "Cari başarıyla güncellendi.")
        self.accept()