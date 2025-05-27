from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
   QDialog, QGroupBox, QComboBox, QGridLayout, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sqlite3
import sys
import os
import shutil
from cari_select_list import CariSelectListForm
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtGui import QImage, QPixmap
import datetime
import hashlib
import uuid
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Veritabanı bağlantısı için context manager"""
    conn = None
    try:
        conn = sqlite3.connect("oto_servis.db")
        yield conn
    finally:
        if conn:
            conn.close()

class AddCarForm(QDialog):
    def __init__(self, cari_kodu=None, cari_unvani=None, parent=None, dashboard_ref=None, on_saved=None, edit_mode=False, car_data=None):
        super().__init__(parent)
        self.dashboard_ref = dashboard_ref
        self.on_saved = on_saved
        self.edit_mode = edit_mode
        self.car_data = car_data
        self.setWindowTitle("Araç Ekleme Formu")
        self.ruhsat_foto_path = ""
        self.cari_kodu_param = cari_kodu
        self.cari_unvani_param = cari_unvani
        
        # Veritabanı yolunu al
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA database_list")
        db_path = cursor.fetchone()[2]  # Veritabanının tam yolunu al
        conn.close()
        
        # Ruhsat fotoğrafları klasörünü oluştur
        self.photo_dir = os.path.join(os.path.dirname(db_path), "ruhsat_fotograflari")
        if not os.path.exists(self.photo_dir):
            os.makedirs(self.photo_dir)
            
        # Base resolution for scaling
        BASE_WIDTH = 1366
        BASE_HEIGHT = 768
        
        # Get current screen dimensions
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        screen_width = ekran.width()
        screen_height = ekran.height()
        
        # Calculate scaling factors
        width_scale = screen_width / BASE_WIDTH
        height_scale = screen_height / BASE_HEIGHT
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        genislik = int(BASE_WIDTH * scale * 0.50)
        yukseklik = int(BASE_HEIGHT * scale * 0.85)
        
        self.setFixedSize(genislik, yukseklik)
        x = (screen_width - genislik) // 2
        y = (screen_height - yukseklik) // 2 - 40
        if y < 0:
            y = 0
        self.move(x, y)
        
        self.init_ui()
        if self.edit_mode and self.car_data:
            self.fill_form_with_car_data()
        self.setWindowIcon(icon('fa5s.file')) # Add a file icon
    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(int(self.height() * 0.03))  # Gruplar arası boşluk

        input_style = f"""
            QLineEdit, QComboBox {{
                font-size: {int(self.height() * 0.018)}px;
                padding: {int(self.height() * 0.006)}px {int(self.height() * 0.008)}px;
                border-radius: {int(self.height() * 0.006)}px;
                border: 1.5px solid #b0bec5;
                background: #f7fafd;
                min-height: {int(self.height() * 0.022)}px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 2px solid #1976d2;
                background: #fff;
            }}
        """
        label_style = f"font-size: {int(self.height() * 0.018)}px; font-weight: 600; color: #222; text-align: left; padding-right: 5px;"
        group_style = f"""
            QGroupBox {{
                font-size: {int(self.height() * 0.018)}px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #90caf9;
                border-radius: {int(self.height() * 0.01)}px;
                margin-top: {int(self.height() * 0.012)}px;
                background: #f5faff;
                padding: {int(self.height() * 0.01)}px;
            }}
            QGroupBox:title {{
                subcontrol-origin: margin;
                left: {int(self.height() * 0.015)}px;
                top: 2px;
                padding: 0 {int(self.height() * 0.006)}px;
            }}
        """

        # Cari Bilgileri Grubu
        cari_group = QGroupBox("Cari Seçimi Yapınız")
        cari_group.setStyleSheet(group_style)
        cari_layout = QGridLayout()
        cari_layout.setVerticalSpacing(int(self.height() * 0.018))   # Alanlar arası dikey boşluk
        cari_layout.setHorizontalSpacing(int(self.width() * 0.008))  # Alanlar arası yatay boşluk

        lbl_cari_kodu = QLabel("Cari Kodu *")
        lbl_cari_kodu.setStyleSheet(label_style)
        lbl_cari_kodu.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cari_layout.addWidget(lbl_cari_kodu, 0, 0)
        self.cari_kodu = QLineEdit()
        self.cari_kodu.setStyleSheet(input_style)
        self.cari_kodu.setMinimumHeight(int(self.height() * 0.035))
        self.cari_kodu.setMaximumWidth(int(self.width() * 0.15))
        cari_layout.addWidget(self.cari_kodu, 0, 1)
        sec_btn = QPushButton("Seç")
        sec_btn.setMinimumHeight(int(self.height() * 0.035))
        sec_btn.setStyleSheet(f"font-size:{int(self.height() * 0.018)}px; font-weight:700; padding:4px 10px;")
        sec_btn.clicked.connect(self.cari_sec_ac)
        cari_layout.addWidget(sec_btn, 0, 2)
        lbl_cari_unvani = QLabel("Cari Ünvanı *")
        lbl_cari_unvani.setStyleSheet(label_style)
        lbl_cari_unvani.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cari_layout.addWidget(lbl_cari_unvani, 1, 0)
        self.cari_unvani = QLineEdit()
        self.cari_unvani.setStyleSheet(input_style)
        self.cari_unvani.setMinimumHeight(int(self.height() * 0.035))
        cari_layout.addWidget(self.cari_unvani, 1, 1, 1, 2)
        cari_group.setLayout(cari_layout)

        # Cari kodu parametresi varsa otomatik doldur
        if self.cari_kodu_param:
            self.cari_kodu.setText(self.cari_kodu_param)
            self.cari_kodu.setReadOnly(True)
        if self.cari_unvani_param:
            self.cari_unvani.setText(self.cari_unvani_param)

        # Araç Bilgileri Grubu
        arac_group = QGroupBox("Araç Bilgilerini Giriniz")
        arac_group.setStyleSheet(group_style)
        arac_layout = QGridLayout()
        arac_layout.setVerticalSpacing(int(self.height() * 0.018))  # Araç alanları arası boşluk
        arac_layout.setHorizontalSpacing(int(self.width() * 0.008))  # Yatay boşluk

        def add_row(lbl, widget, row):
            lbl.setStyleSheet(label_style)
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            widget.setStyleSheet(input_style)
            widget.setMinimumHeight(int(self.height() * 0.035))
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
        self.aciklama = QLineEdit()
        add_row(QLabel("Açıklama"), self.aciklama, 11)

        # Ruhsat Fotoğrafı
        lbl_ruhsat_foto = QLabel("Ruhsat Fotoğrafı")
        lbl_ruhsat_foto.setStyleSheet(label_style)
        lbl_ruhsat_foto.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Fotoğraf butonları için yatay layout
        foto_btn_layout = QHBoxLayout()
        
        self.ruhsat_foto_btn = QPushButton("Fotoğraf Seç")
        self.ruhsat_foto_btn.setStyleSheet(f"font-size: {int(self.height() * 0.02)}px; padding: 4px;")
        self.ruhsat_foto_btn.setMinimumHeight(int(self.height() * 0.035))
        self.ruhsat_foto_btn.clicked.connect(self.select_photo)
        
        self.kamera_btn = QPushButton("Kamera ile Çek")
        self.kamera_btn.setStyleSheet(f"font-size: {int(self.height() * 0.02)}px; padding: 4px;")
        self.kamera_btn.setMinimumHeight(int(self.height() * 0.035))
        self.kamera_btn.clicked.connect(self.open_camera)
        
        foto_btn_layout.addWidget(self.ruhsat_foto_btn)
        foto_btn_layout.addWidget(self.kamera_btn)
        
        arac_layout.addWidget(lbl_ruhsat_foto, 12, 0)
        arac_layout.addLayout(foto_btn_layout, 12, 1, 1, 2)

        arac_group.setLayout(arac_layout)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        kaydet_btn = QPushButton(icon('fa5s.save', color='deeppink'), "Kaydet")
        kaydet_btn.setFixedWidth(int(self.width() * 0.12))
        kaydet_btn.setMinimumHeight(int(self.height() * 0.035))
        kaydet_btn.setStyleSheet(f"font-size: {int(self.height() * 0.018)}px; font-weight: bold; background: #1976d2; color: white; border-radius: {int(self.height() * 0.006)}px;")
        kaydet_btn.clicked.connect(self.kaydet_tiklandi)
        iptal_btn = QPushButton(icon('fa5s.times', color='darkred'), "İptal")
        iptal_btn.setFixedWidth(int(self.width() * 0.12))
        iptal_btn.setMinimumHeight(int(self.height() * 0.035))
        iptal_btn.setStyleSheet(f"font-size: {int(self.height() * 0.018)}px; font-weight: bold; background: #b71c1c; color: white; border-radius: {int(self.height() * 0.006)}px;")
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
            try:
                # Dosyanın hash'ini oluştur
                with open(file_name, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                # Dosya uzantısını al
                _, ext = os.path.splitext(file_name)
                
                # Yeni dosya adını oluştur (hash + timestamp + uzantı)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{file_hash}_{timestamp}{ext}"
                new_path = os.path.join(self.photo_dir, new_filename)
                
                # Eğer aynı hash'li dosya varsa kopyalama
                if not os.path.exists(new_path):
                    shutil.copy2(file_name, new_path)
                
                self.ruhsat_foto_path = new_path
                self.ruhsat_foto_btn.setText("Seçildi")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Fotoğraf kopyalanırken hata oluştu: {str(e)}")

    def open_camera(self):
        # Kamera penceresi oluştur
        self.camera_dialog = QDialog(self)
        self.camera_dialog.setWindowTitle("Kamera")
        self.camera_dialog.setModal(True)
        
        # Kamera görüntüleyici
        self.viewfinder = QCameraViewfinder()
        self.camera = QCamera(QCameraInfo.defaultCamera())
        self.camera.setViewfinder(self.viewfinder)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        capture_btn = QPushButton("Fotoğraf Çek")
        capture_btn.clicked.connect(self.capture_photo)
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.camera_dialog.close)
        
        btn_layout.addWidget(capture_btn)
        btn_layout.addWidget(close_btn)
        
        # Ana layout
        layout = QVBoxLayout()
        layout.addWidget(self.viewfinder)
        layout.addLayout(btn_layout)
        
        self.camera_dialog.setLayout(layout)
        self.camera.start()
        self.camera_dialog.exec_()

    def capture_photo(self):
        try:
            # Fotoğrafı kaydet
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]  # Benzersiz ID oluştur
            new_filename = f"ruhsat_{unique_id}_{timestamp}.jpg"
            new_path = os.path.join(self.photo_dir, new_filename)
            
            # Görüntüyü doğrudan kaydet
            image = self.viewfinder.grab()
            image.save(new_path)
            
            self.ruhsat_foto_path = new_path
            self.ruhsat_foto_btn.setText("Çekildi")
            self.camera_dialog.close()
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Fotoğraf kaydedilirken hata oluştu: {str(e)}")

    def iptal_tiklandi(self):
        self.close()
        if self.dashboard_ref:
            self.dashboard_ref.show()

    def kaydet_tiklandi(self):
        """Araç bilgilerini kaydeder."""
        try:
            # Form verilerini al
            plaka = self.plaka.text().strip()
            cari_kodu = self.cari_kodu.text().strip()
            arac_tipi = self.arac_tipi.currentText()
            model_yili = self.model_yili.text().strip()
            marka = self.marka.text().strip()
            model = self.model.text().strip()
            sasi_no = self.sasi_no.text().strip()
            motor_no = self.motor_no.text().strip()
            motor_hacmi = self.motor_hacmi.text().strip()
            motor_gucu = self.motor_gucu.text().strip()
            yakit_cinsi = self.yakit_cinsi.currentText()
            aciklama = self.aciklama.text().strip()

            # Zorunlu alanları kontrol et
            if not all([plaka, cari_kodu, arac_tipi]):
                QMessageBox.warning(self, "Uyarı", "Lütfen zorunlu alanları doldurun!")
                return

            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Son kapatılan servis tarihini al
                cursor.execute("""
                    SELECT servis_tarihi 
                    FROM servisler 
                    WHERE plaka = ? AND servis_durumu = 'Kapalı' 
                    ORDER BY servis_tarihi DESC 
                    LIMIT 1
                """, (plaka,))
                son_servis = cursor.fetchone()
                son_bakim_tarihi = son_servis[0] if son_servis else None

                if self.edit_mode:
                    # Düzenleme modu - UPDATE işlemi
                    cursor.execute("""
                        UPDATE araclar SET
                            cari_kodu = ?,
                            arac_tipi = ?,
                            model_yili = ?,
                            marka = ?,
                            model = ?,
                            sasi_no = ?,
                            motor_no = ?,
                            motor_hacmi = ?,
                            motor_gucu_kw = ?,
                            yakit_cinsi = ?,
                            son_bakim_tarihi = ?,
                            aciklama = ?,
                            ruhsat_foto = ?
                        WHERE plaka = ?
                    """, (
                        cari_kodu, arac_tipi, model_yili, marka, model,
                        sasi_no, motor_no, motor_hacmi, motor_gucu, yakit_cinsi,
                        son_bakim_tarihi, aciklama, self.ruhsat_foto_path,
                        plaka  # WHERE koşulu için plaka
                    ))
                else:
                    # Yeni kayıt modu - INSERT işlemi
                    cursor.execute("""
                        INSERT INTO araclar (
                            plaka, cari_kodu, arac_tipi, model_yili, marka, model, 
                            sasi_no, motor_no, motor_hacmi, motor_gucu_kw, yakit_cinsi,
                            son_bakim_tarihi, aciklama, ruhsat_foto
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        plaka, cari_kodu, arac_tipi, model_yili, marka, model,
                        sasi_no, motor_no, motor_hacmi, motor_gucu, yakit_cinsi,
                        son_bakim_tarihi, aciklama, self.ruhsat_foto_path
                    ))
                conn.commit()

            QMessageBox.information(self, "Başarılı", "Araç başarıyla kaydedildi!")
            self.accept()

        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Hata", "Bu plaka zaten kayıtlı!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")

    def cari_sec_ac(self):
        self.cari_select_form = CariSelectListForm(parent_form=self)
        self.cari_select_form.setWindowModality(Qt.ApplicationModal)
        self.cari_select_form.setWindowFlag(Qt.Window)
        self.cari_select_form.exec_()

    def set_cari_bilgileri(self, cari_kodu, cari_unvani, telefon=None, cari_tipi=None):
        self.cari_kodu.setText(cari_kodu)
        self.cari_unvani.setText(cari_unvani)

    def fill_form_with_car_data(self):
        # Form alanlarını car_data ile doldur
        self.cari_kodu.setText(self.car_data.get("cari_kodu", ""))
        self.plaka.setText(self.car_data.get("plaka", ""))
        self.arac_tipi.setCurrentText(self.car_data.get("arac_tipi", ""))
        self.model_yili.setText(str(self.car_data.get("model_yili", "")))
        self.marka.setText(self.car_data.get("marka", ""))
        self.model.setText(self.car_data.get("model", ""))
        self.sasi_no.setText(self.car_data.get("sasi_no", ""))
        self.motor_no.setText(self.car_data.get("motor_no", ""))
        
        # Motor hacmi ve gücü için doğru alan isimlerini kullan
        motor_hacmi = self.car_data.get("motor_hacmi", "")
        motor_gucu = self.car_data.get("motor_gucu_kw", "")
        
        # Eğer değerler None ise boş string kullan
        self.motor_hacmi.setText(str(motor_hacmi) if motor_hacmi is not None else "")
        self.motor_gucu.setText(str(motor_gucu) if motor_gucu is not None else "")
        
        self.yakit_cinsi.setCurrentText(self.car_data.get("yakit_cinsi", ""))
        self.aciklama.setText(self.car_data.get("aciklama", ""))
        
        # Cari ünvanını da doldur
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cari_ad_unvan FROM cariler WHERE cari_kodu = ?", (self.car_data.get("cari_kodu", ""),))
            result = cursor.fetchone()
            if result:
                self.cari_unvani.setText(result[0])

        # Düzenleme modunda cari kodu alanını salt okunur yap
        if self.edit_mode:
            self.cari_kodu.setReadOnly(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AddCarForm()
    form.show()
    sys.exit(app.exec_())