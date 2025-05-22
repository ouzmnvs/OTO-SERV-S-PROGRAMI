from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
   QDialog, QGroupBox, QComboBox, QGridLayout, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sqlite3
import sys
from cari_select_list import CariSelectListForm

class AddCarForm(QDialog):
    def __init__(self, dashboard_ref=None, on_saved=None):
        super().__init__()
        self.dashboard_ref = dashboard_ref
        self.on_saved = on_saved
        self.setWindowTitle("Araç Ekleme Formu")
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.56)   # Daha büyük pencere
        yukseklik = int(ekran.height() * 0.78)
        self.setFixedSize(genislik, yukseklik)
        self.ruhsat_foto_path = ""
        self.init_ui()

    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(32)  # Gruplar arası boşluk

        input_style = """
            QLineEdit, QComboBox {
                font-size: 18px;
                padding: 8px 12px;
                border-radius: 7px;
                border: 1.5px solid #b0bec5;
                background: #f7fafd;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #1976d2;
                background: #fff;
            }
        """
        label_style = "font-size: 16px; font-weight: 600; color: #222;"
        group_style = """
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #90caf9;
                border-radius: 10px;
                margin-top: 12px;
                background: #f5faff;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 14px;
                top: 2px;
                padding: 0 6px;
            }
        """

        # Cari Bilgileri Grubu
        cari_group = QGroupBox("Cari Seçimi Yapınız")
        cari_group.setStyleSheet(group_style)
        cari_layout = QGridLayout()
        cari_layout.setVerticalSpacing(18)   # Alanlar arası dikey boşluk
        cari_layout.setHorizontalSpacing(12) # Alanlar arası yatay boşluk

        lbl_cari_kodu = QLabel("Cari Kodu *")
        lbl_cari_kodu.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_kodu, 0, 0)
        self.cari_kodu = QLineEdit()
        self.cari_kodu.setStyleSheet(input_style)
        self.cari_kodu.setMinimumHeight(32)
        self.cari_kodu.setMaximumWidth(180)
        cari_layout.addWidget(self.cari_kodu, 0, 1)
        sec_btn = QPushButton("Seç")
        sec_btn.setMinimumHeight(32)
        sec_btn.setStyleSheet("font-size:15px; font-weight:700; padding:6px 18px;")
        sec_btn.clicked.connect(self.cari_sec_ac)
        cari_layout.addWidget(sec_btn, 0, 2)
        lbl_cari_unvani = QLabel("Cari Ünvanı *")
        lbl_cari_unvani.setStyleSheet(label_style)
        cari_layout.addWidget(lbl_cari_unvani, 1, 0)
        self.cari_unvani = QLineEdit()
        self.cari_unvani.setStyleSheet(input_style)
        self.cari_unvani.setMinimumHeight(32)
        cari_layout.addWidget(self.cari_unvani, 1, 1, 1, 2)
        cari_group.setLayout(cari_layout)

        # Araç Bilgileri Grubu
        arac_group = QGroupBox("Araç Bilgilerini Giriniz")
        arac_group.setStyleSheet(group_style)
        arac_layout = QGridLayout()
        arac_layout.setVerticalSpacing(28)  # Araç alanları arası boşluk artırıldı
        arac_layout.setHorizontalSpacing(16)

        def add_row(lbl, widget, row):
            lbl.setStyleSheet(label_style)
            widget.setStyleSheet(input_style)
            widget.setMinimumHeight(32)
            arac_layout.addWidget(lbl, row, 0)
            arac_layout.addWidget(widget, row, 1, 1, 2)

        self.plaka = QLineEdit()
        add_row(QLabel("Plaka *"), self.plaka, 0)
        self.arac_tipi = QComboBox()
        self.arac_tipi.addItems(["", "Otomobil", "Kamyonet", "Minibüs", "Diğer"])
        add_row(QLabel("Araç Tipi *"), self.arac_tipi, 1)
        self.model_yili = QLineEdit()
        add_row(QLabel("Model Yılı"), self.model_yili, 2)
        self.marka = QLineEdit()
        add_row(QLabel("Marka"), self.marka, 3)
        self.model = QLineEdit()
        add_row(QLabel("Model"), self.model, 4)
        self.sasi_no = QLineEdit()
        add_row(QLabel("Şasi No"), self.sasi_no, 5)
        self.motor_no = QLineEdit()
        add_row(QLabel("Motor No"), self.motor_no, 6)
        self.motor_hacmi = QLineEdit()
        add_row(QLabel("Motor Hacmi"), self.motor_hacmi, 7)
        self.motor_gucu = QLineEdit()
        add_row(QLabel("Motor Gücü (kW)"), self.motor_gucu, 8)
        self.yakit_cinsi = QComboBox()
        self.yakit_cinsi.addItems(["", "Benzin", "Dizel", "LPG", "Benzin/LPG", "Hybrid", "Elektrik"])
        add_row(QLabel("Yakıt Cinsi"), self.yakit_cinsi, 9)
        self.getiren_kisi = QLineEdit()
        add_row(QLabel("Getiren Kişi"), self.getiren_kisi, 10)
        self.son_bakim_tarihi = QLineEdit()
        add_row(QLabel("Son Bakım Tarihi"), self.son_bakim_tarihi, 11)
        self.aciklama = QLineEdit()
        add_row(QLabel("Açıklama"), self.aciklama, 12)

        # Ruhsat Fotoğrafı
        lbl_ruhsat_foto = QLabel("Ruhsat Fotoğrafı")
        lbl_ruhsat_foto.setStyleSheet(label_style)
        self.ruhsat_foto_btn = QPushButton("Fotoğraf Seç")
        self.ruhsat_foto_btn.setStyleSheet("font-size: 15px; padding: 6px;")
        self.ruhsat_foto_btn.setMinimumHeight(32)
        self.ruhsat_foto_btn.clicked.connect(self.select_photo)
        arac_layout.addWidget(lbl_ruhsat_foto, 13, 0)
        arac_layout.addWidget(self.ruhsat_foto_btn, 13, 1, 1, 2)

        arac_group.setLayout(arac_layout)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        kaydet_btn = QPushButton(icon('fa5s.save', color='deeppink'), "Kaydet")
        kaydet_btn.setFixedWidth(140)
        kaydet_btn.setMinimumHeight(40)
        kaydet_btn.setStyleSheet("font-size: 17px; font-weight: bold; background: #1976d2; color: white; border-radius: 7px;")
        kaydet_btn.clicked.connect(self.kaydet_tiklandi)
        iptal_btn = QPushButton(icon('fa5s.times', color='darkred'), "İptal")
        iptal_btn.setFixedWidth(140)
        iptal_btn.setMinimumHeight(40)
        iptal_btn.setStyleSheet("font-size: 17px; font-weight: bold; background: #b71c1c; color: white; border-radius: 7px;")
        iptal_btn.clicked.connect(self.iptal_tiklandi)
        btn_layout.addWidget(kaydet_btn)
        btn_layout.addWidget(iptal_btn)

        ana_layout.addWidget(cari_group)
        ana_layout.addWidget(arac_group)
        ana_layout.addStretch()
        ana_layout.addLayout(btn_layout)
        self.setLayout(ana_layout)

    def select_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Ruhsat Fotoğrafı Seç", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            self.ruhsat_foto_path = file_name
            self.ruhsat_foto_btn.setText("Seçildi")

    def iptal_tiklandi(self):
        self.close()
        if self.dashboard_ref:
            self.dashboard_ref.show()

    def kaydet_tiklandi(self):
        cari_kodu = self.cari_kodu.text().strip()
        plaka = self.plaka.text().strip().upper()
        arac_tipi = self.arac_tipi.currentText().strip()
        model_yili = self.model_yili.text().strip()
        marka = self.marka.text().strip()
        model = self.model.text().strip()
        sasi_no = self.sasi_no.text().strip()
        motor_no = self.motor_no.text().strip()
        motor_hacmi = self.motor_hacmi.text().strip()
        motor_gucu = self.motor_gucu.text().strip()
        yakit_cinsi = self.yakit_cinsi.currentText().strip()
        getiren_kisi = self.getiren_kisi.text().strip()
        son_bakim_tarihi = self.son_bakim_tarihi.text().strip()
        aciklama = self.aciklama.text().strip()
        ruhsat_foto = self.ruhsat_foto_path

        # Gerekli alan kontrolü
        if not cari_kodu or not plaka or not arac_tipi:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen * ile işaretli alanları doldurun!")
            return

        # Model yılı ve motor gücü sayı mı?
        if model_yili and not model_yili.isdigit():
            QMessageBox.warning(self, "Hatalı Giriş", "Model yılı sadece rakamlardan oluşmalıdır!")
            return
        if motor_gucu and not motor_gucu.isdigit():
            QMessageBox.warning(self, "Hatalı Giriş", "Motor gücü sadece rakamlardan oluşmalıdır!")
            return

        # Aynı plaka var mı kontrolü
        try:
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM araclar WHERE plaka = ?", (plaka,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Tekrarlı Kayıt", "Bu plakaya sahip bir araç zaten kayıtlı!")
                return

            cursor.execute("""
                INSERT INTO araclar (
                    cari_kodu, plaka, marka, model, model_yili, motor_no, sasi_no, arac_tipi,
                    motor_hacmi, motor_gucu_kw, yakit_cinsi, getiren_kisi, son_bakim_tarihi, aciklama, ruhsat_foto
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cari_kodu, plaka, marka, model, model_yili, motor_no, sasi_no, arac_tipi,
                motor_hacmi, motor_gucu, yakit_cinsi, getiren_kisi, son_bakim_tarihi, aciklama, ruhsat_foto
            ))
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Araç başarıyla eklendi!")
            if self.on_saved:
                self.on_saved()
            self.close()
            if self.dashboard_ref:
                self.dashboard_ref.show()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu:\n{e}")
        finally:
            conn.close()

    def cari_sec_ac(self):
        self.cari_select_form = CariSelectListForm(parent_form=self)
        self.cari_select_form.setWindowModality(Qt.ApplicationModal)
        self.cari_select_form.setWindowFlag(Qt.Window)
        self.cari_select_form.exec_()

    def set_cari_bilgileri(self, cari_kodu, cari_unvani, telefon=None, cari_tipi=None):
        self.cari_kodu.setText(cari_kodu)
        self.cari_unvani.setText(cari_unvani)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AddCarForm()
    form.show()
    sys.exit(app.exec_())