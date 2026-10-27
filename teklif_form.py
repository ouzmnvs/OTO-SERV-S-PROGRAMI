from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
   QDesktopWidget, QGroupBox, QComboBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QFrame, QMessageBox, QDialog, QFileDialog
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from cari_select_list import CariSelectListForm
from car_select_list import CarSelectListForm
from database_progress import add_teklif_islem, delete_teklif_islem, update_teklif_tutar, get_teklif_details, delete_teklif
from datetime import datetime
import sqlite3
from sayi import sayi_oku

class TeklifForm(QDialog):
    def __init__(self, dashboard_ref=None, teklif_id=None, teklif_no=None):
        super().__init__()
        self.dashboard_ref = dashboard_ref
        self.teklif_id = teklif_id
        self.teklif_no = teklif_no
        self.setWindowTitle("Teklif Formu")
        
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
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions - using 90% of base resolution instead of 100%
        genislik = int(BASE_WIDTH * scale * 0.90)
        yukseklik = int(BASE_HEIGHT * scale * 0.90)
        
        self.setFixedSize(genislik, yukseklik)
        x = (screen_width - genislik) // 2
        y = (screen_height - yukseklik) // 2 - 40
        if y < 0:
            y = 0
        self.move(x, y)
        self.init_ui()
        self.setWindowIcon(icon('fa5s.file'))
        
        # Teklif detaylarını yükle
        if teklif_no:
            self.load_teklif_details()

    def init_ui(self):
        ana_layout = QHBoxLayout()
        ana_layout.setSpacing(12)

        # Sol Panel: Araç, Cari ve Teklif Bilgileri
        sol_panel = QVBoxLayout()
        sol_panel.setSpacing(10)

        # Başlık
        lbl_sol_baslik = QLabel("Araç - Cari - Teklif Bilgileri")
        lbl_sol_baslik.setStyleSheet("""
            background-color: #333;
            color: white;
            font: bold 14px;
            padding: 6px 12px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        """)
        lbl_sol_baslik.setFixedHeight(32)
        sol_panel.addWidget(lbl_sol_baslik)

        # Bilgi Girişi
        bilgi_group = QGroupBox("Cari, Araç ve Teklif Bilgilerini Giriniz")
        bilgi_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 12px;
                top: 2px;
                padding: 0 4px;
            }
        """)
        bilgi_layout = QGridLayout()
        bilgi_layout.setVerticalSpacing(15)
        bilgi_layout.setHorizontalSpacing(15)

        label_style = "font-size: 13px; font-weight: 600; color: #222;"
        input_style = """
            QLineEdit, QComboBox {
                font-size: 13px;
                padding: 6px 10px;
                border-radius: 4px;
                border: 1.5px solid #bbb;
                background: #fafbfc;
                min-height: 20px;
                min-width: 30px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #1976d2;
                background: #fff;
            }
        """

        # Teklif Bilgileri
        bilgi_layout.addWidget(self._label("Teklif No", label_style), 0, 0)
        self.teklif_no_input = QLineEdit()
        self.teklif_no_input.setStyleSheet(input_style)
        self.teklif_no_input.setReadOnly(True)
        bilgi_layout.addWidget(self.teklif_no_input, 0, 1)

        bilgi_layout.addWidget(self._label("Teklif Tarihi", label_style), 1, 0)
        self.teklif_tarihi = QLineEdit()
        self.teklif_tarihi.setStyleSheet(input_style)
        self.teklif_tarihi.setReadOnly(True)
        bilgi_layout.addWidget(self.teklif_tarihi, 1, 1)

        bilgi_layout.addWidget(self._label("Geçerlilik Tarihi", label_style), 2, 0)
        self.gecerlilik_tarihi = QLineEdit()
        self.gecerlilik_tarihi.setStyleSheet(input_style)
        self.gecerlilik_tarihi.setReadOnly(True)
        bilgi_layout.addWidget(self.gecerlilik_tarihi, 2, 1)

        bilgi_layout.addWidget(self._label("Ödeme Şekli", label_style), 3, 0)
        self.odeme_sekli = QComboBox()
        self.odeme_sekli.setStyleSheet(input_style)
        self.odeme_sekli.addItems(["", "Nakit", "Kredi Kartı", "Havale/EFT", "Vadeli"])
        bilgi_layout.addWidget(self.odeme_sekli, 3, 1)

        bilgi_layout.addWidget(self._label("Vade Günü", label_style), 4, 0)
        self.vade_gun = QLineEdit()
        self.vade_gun.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.vade_gun, 4, 1)

        bilgi_layout.addWidget(self._label("Teklif Veren", label_style), 5, 0)
        self.teklif_veren = QLineEdit()
        self.teklif_veren.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.teklif_veren, 5, 1)

        bilgi_layout.addWidget(self._label("Teklif Alan", label_style), 6, 0)
        self.teklif_alan = QLineEdit()
        self.teklif_alan.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.teklif_alan, 6, 1)

        # Cari ve Araç Bilgileri
        bilgi_layout.addWidget(self._label("Cari Kodu", label_style), 7, 0)
        self.cari_kodu = QLineEdit()
        self.cari_kodu.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.cari_kodu, 7, 1)

        bilgi_layout.addWidget(self._label("Cari Adı / Ünvanı", label_style), 8, 0)
        self.cari_unvan = QLineEdit()
        self.cari_unvan.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.cari_unvan, 8, 1)

        bilgi_layout.addWidget(self._label("Telefon", label_style), 9, 0)
        self.telefon = QLineEdit()
        self.telefon.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.telefon, 9, 1)

        bilgi_layout.addWidget(self._label("Cari Tipi *", label_style), 10, 0)
        self.cari_tipi = QComboBox()
        self.cari_tipi.setStyleSheet(input_style)
        self.cari_tipi.addItems(["", "Bireysel","Kurumsal"])
        bilgi_layout.addWidget(self.cari_tipi, 10, 1)

        sec_btn = QPushButton(icon('fa5s.user-check', color='black'), "Seç")
        sec_btn.setMinimumHeight(28)
        sec_btn.setStyleSheet("font-size:13px; font-weight:700; padding:4px 10px;")
        sec_btn.clicked.connect(self.open_cari_select_list)
        bilgi_layout.addWidget(sec_btn, 10, 2)

        bilgi_layout.addWidget(self._label("Plaka *", label_style), 11, 0)
        self.plaka = QLineEdit()
        self.plaka.setStyleSheet(input_style)
        self.plaka.setReadOnly(True)
        bilgi_layout.addWidget(self.plaka, 11, 1)

        bilgi_layout.addWidget(self._label("Araç Tipi *", label_style), 12, 0)
        self.arac_tipi = QComboBox()
        self.arac_tipi.setStyleSheet(input_style)
        self.arac_tipi.addItems(["", "Otomobil", "Kamyonet", "Minibüs", "Diğer"])
        self.arac_tipi.setEnabled(False)
        bilgi_layout.addWidget(self.arac_tipi, 12, 1)

        bilgi_layout.addWidget(self._label("Model Yılı", label_style), 13, 0)
        self.model_yili = QLineEdit()
        self.model_yili.setStyleSheet(input_style)
        self.model_yili.setReadOnly(True)
        bilgi_layout.addWidget(self.model_yili, 13, 1)

        bilgi_layout.addWidget(self._label("Marka", label_style), 14, 0)
        self.marka = QLineEdit()
        self.marka.setStyleSheet(input_style)
        self.marka.setReadOnly(True)
        bilgi_layout.addWidget(self.marka, 14, 1)

        bilgi_layout.addWidget(self._label("Model", label_style), 15, 0)
        self.model = QLineEdit()
        self.model.setStyleSheet(input_style)
        self.model.setReadOnly(True)
        bilgi_layout.addWidget(self.model, 15, 1)

        arac_sec_btn = QPushButton(icon('fa5s.car', color='blue'), "Seç")
        arac_sec_btn.setMinimumHeight(28)
        arac_sec_btn.setStyleSheet("font-size:13px; font-weight:700; padding:4px 10px;")
        arac_sec_btn.clicked.connect(self.open_car_select_list)
        bilgi_layout.addWidget(arac_sec_btn, 15, 2)

        bilgi_group.setLayout(bilgi_layout)
        sol_panel.addWidget(bilgi_group)

        ana_layout.addLayout(sol_panel, 2)

        # Sağ Panel: İşlem ve Özet Bilgileri
        sag_panel = QVBoxLayout()
        sag_panel.setSpacing(10)

        # Sağ başlık
        lbl_sag_baslik = QLabel("İşlem ve Özet Bilgileri")
        lbl_sag_baslik.setStyleSheet("""
            background-color: #333;
            color: white;
            font: bold 14px;
            padding: 6px 12px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        """)
        sag_panel.addWidget(lbl_sag_baslik)

        # İşlem Bilgileri Girişi
        islem_group = QGroupBox("İşlem Bilgilerini Giriniz")
        islem_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 6px;
                margin-top: 8px;
            }
        """)
        islem_layout = QGridLayout()
        islem_layout.setVerticalSpacing(8)
        islem_layout.setHorizontalSpacing(6)

        # İşlem Açıklaması
        islem_layout.addWidget(self._label("İşlem Açıklaması", label_style), 0, 0)
        islem_aciklama_layout = QHBoxLayout()
        self.islem_aciklama = QLineEdit()
        self.islem_aciklama.setStyleSheet(input_style)
        self.islem_aciklama.setMinimumWidth(100)
        islem_aciklama_layout.addWidget(self.islem_aciklama)

        # Miktar seçimi için ComboBox
        self.miktar = QComboBox()
        self.miktar.setStyleSheet(input_style)
        self.miktar.setFixedWidth(50)
        self.miktar.addItems([str(i) for i in range(1, 11)])  # 1'den 10'a kadar
        islem_aciklama_layout.addWidget(self.miktar)
        islem_layout.addLayout(islem_aciklama_layout, 1, 0)

        # İşlem Tutarı
        islem_layout.addWidget(self._label("Birim Fiyat", label_style), 0, 1)
        self.islem_tutar = QLineEdit()
        self.islem_tutar.setStyleSheet(input_style)
        self.islem_tutar.setMinimumWidth(70)
        self.islem_tutar.setPlaceholderText("Birim fiyat giriniz")
        islem_layout.addWidget(self.islem_tutar, 1, 1)

        # Açıklama
        islem_layout.addWidget(self._label("Açıklama", label_style), 0, 2)
        self.islem_ek_aciklama = QLineEdit()
        self.islem_ek_aciklama.setStyleSheet(input_style)
        self.islem_ek_aciklama.setMinimumWidth(100)
        islem_layout.addWidget(self.islem_ek_aciklama, 1, 2)

        # KDV Oranı
        islem_layout.addWidget(self._label("KDV Oranı (%)", label_style), 0, 3)
        self.kdv_orani = QLineEdit()
        self.kdv_orani.setStyleSheet(input_style)
        self.kdv_orani.setMinimumWidth(50)
        self.kdv_orani.setPlaceholderText("20")
        islem_layout.addWidget(self.kdv_orani, 1, 3)

        # Ekle butonu
        btn_islem_ekle = QPushButton(icon('fa5s.plus-circle', color='green'), "Ekle")
        btn_islem_ekle.setMinimumHeight(28)
        btn_islem_ekle.setStyleSheet("font-size:12px; font-weight:700; padding:4px 8px;")
        btn_islem_ekle.clicked.connect(self.islem_ekle)
        islem_layout.addWidget(btn_islem_ekle, 1, 4)

        islem_group.setLayout(islem_layout)
        sag_panel.addWidget(islem_group)

        # İşlem Listesi Tablosu
        self.islem_table = QTableWidget(0, 6)
        self.islem_table.setHorizontalHeaderLabels([
            "İşlem Açıklaması", "Miktar", "İşlem Tutarı", "KDV (%)", "KDV Tutarı", "Açıklama"
        ])
        self.islem_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.islem_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.islem_table.setAlternatingRowColors(True)
        self.islem_table.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                alternate-background-color: #f5f5f5;
                background: #fff;
            }
            QHeaderView::section {
                background: #ececec;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #bbb;
                padding: 4px;
            }
        """)
        sag_panel.addWidget(self.islem_table)

        # İşlem Özeti ve Alt Butonlar
        alt_layout = QVBoxLayout()
        alt_layout.setSpacing(10)

        # İşlem Özeti
        ozet_group = QGroupBox("İşlem Özeti")
        ozet_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        ozet_layout = QHBoxLayout()
        self.lbl_islem_sayisi = QLabel("Toplam İşlem Sayısı\n0")
        self.lbl_islem_sayisi.setStyleSheet("font-size: 13px; background: #fffde7; padding: 4px;")
        self.lbl_islem_tutar = QLabel("Toplam İşlem Tutarı\n0,00")
        self.lbl_islem_tutar.setStyleSheet("font-size: 13px; background: #e0f7fa; padding: 4px;")
        self.lbl_kdv_tutar = QLabel("Toplam KDV Tutarı\n0,00")
        self.lbl_kdv_tutar.setStyleSheet("font-size: 13px; background: #ffe0b2; padding: 4px;")

        ozet_layout.addWidget(self.lbl_islem_sayisi)
        ozet_layout.addWidget(self.lbl_islem_tutar)
        ozet_layout.addWidget(self.lbl_kdv_tutar)

        ozet_group.setLayout(ozet_layout)
        alt_layout.addWidget(ozet_group)

        # Alt Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_kaydet = self._buton("KAYDET", 'fa5s.save', 'deepskyblue')
        btn_kaydet.clicked.connect(self.teklifi_kaydet)
        btn_islemleri_temizle = self._buton("İŞLEMİ SİL", 'fa5s.sync', '#fbc02d')
        btn_islemleri_temizle.clicked.connect(self.islem_sil)
        btn_teklif_sil = self._buton("TEKLİFİ SİL", 'fa5s.trash', '#b71c1c')
        btn_teklif_sil.clicked.connect(self.teklifi_sil)
        btn_pdf_aktar = self._buton("PDF AKTAR", 'fa5s.file-pdf', '#388e3c')
        btn_pdf_aktar.clicked.connect(self.pdf_aktar)
        btn_sayfa_kapat = self._buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')
        btn_sayfa_kapat.clicked.connect(self.sayfayi_kapat)

        btn_layout.addWidget(btn_kaydet, 2)
        btn_layout.addWidget(btn_islemleri_temizle, 2)
        btn_layout.addWidget(btn_teklif_sil, 2)
        btn_layout.addWidget(btn_pdf_aktar, 2)
        btn_layout.addWidget(btn_sayfa_kapat, 2)

        alt_layout.addLayout(btn_layout)
        sag_panel.addLayout(alt_layout)

        # Alt bilgi
        alt_bilgi = QLabel("10.03.2025    |    01:23")
        alt_bilgi.setStyleSheet("font-size: 12px; color: #444; padding: 4px 0 0 6px;")
        sag_panel.addWidget(alt_bilgi)

        ana_layout.addLayout(sag_panel, 4)
        self.setLayout(ana_layout)

        # Input alanlarına size policy ekle
        for widget in [self.teklif_no_input, self.teklif_tarihi, self.gecerlilik_tarihi,
                      self.vade_gun, self.teklif_veren, self.teklif_alan,
                      self.cari_kodu, self.cari_unvan, self.telefon,
                      self.plaka, self.model_yili, self.marka, self.model]:
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            widget.setMinimumWidth(200)

    def open_cari_select_list(self):
        """Cari seçme penceresini açar."""
        self.cari_select_form = CariSelectListForm(parent_form=self)
        self.cari_select_form.show()

    def open_car_select_list(self):
        """Araç seçme penceresini açar."""
        if not self.cari_kodu.text().strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir cari seçin!")
            return

        cari_kodu = self.cari_kodu.text().strip()
        self.car_select_form = CarSelectListForm(parent_form=self, cari_kodu=cari_kodu)
        self.car_select_form.show()

    def set_cari_bilgileri(self, cari_kodu, cari_unvani, telefon, cari_tipi):
        """Cari bilgilerini doldurur."""
        self.cari_kodu.setText(cari_kodu)
        self.cari_unvan.setText(cari_unvani)
        self.telefon.setText(telefon)
        self.cari_tipi.setCurrentText(cari_tipi)

    def set_arac_bilgileri(self, plaka, arac_tipi, model_yili, marka, model):
        """Araç bilgilerini doldurur."""
        self.plaka.setText(plaka)
        self.arac_tipi.setCurrentText(arac_tipi)
        self.model_yili.setText(model_yili)
        self.marka.setText(marka)
        self.model.setText(model)

    def _label(self, text, style):
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        return lbl

    def _buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(36)
        btn.setMinimumWidth(120)
        btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: 700;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return btn

    def sayfayi_kapat(self):
        """Teklif formunu kapatır ve dashboard ekranına geri döner."""
        self.close()
        if self.dashboard_ref:
            self.dashboard_ref.show()

    def islem_ekle(self):
        """İşlem bilgilerini tabloya ekler."""
        # Formdaki bilgileri al
        islem_aciklama = self.islem_aciklama.text().strip()
        birim_fiyat = self.islem_tutar.text().strip()  # Artık bu birim fiyat
        kdv_orani = self.kdv_orani.text().strip() or "20"  # Varsayılan KDV oranı
        aciklama = self.islem_ek_aciklama.text().strip()
        miktar = int(self.miktar.currentText())  # Seçilen miktar

        # Gerekli alanların doldurulup doldurulmadığını kontrol et
        if not islem_aciklama or not birim_fiyat:
            QMessageBox.warning(self, "Uyarı", "Lütfen gerekli alanları doldurun!")
            return

        try:
            # KDV oranını ve birim fiyatı sayıya dönüştür ("1500,50" ve "1.500,50" yazımları da kabul edilir)
            kdv_orani = sayi_oku(kdv_orani)
            birim_fiyat_float = sayi_oku(birim_fiyat)  # Birim fiyat
            islem_tutari_float = birim_fiyat_float * miktar  # Toplam tutar = birim fiyat * miktar
            kdv_tutari = islem_tutari_float * kdv_orani / 100  # KDV tutarı = toplam tutar * KDV oranı

            # İşlemi tabloya ekle
            row_count = self.islem_table.rowCount()
            self.islem_table.insertRow(row_count)
            self.islem_table.setItem(row_count, 0, QTableWidgetItem(islem_aciklama))  # İşlem açıklaması
            self.islem_table.setItem(row_count, 1, QTableWidgetItem(str(miktar)))  # Miktar
            self.islem_table.setItem(row_count, 2, QTableWidgetItem(f"{islem_tutari_float:.2f}"))  # İşlem tutarı (Miktar x Birim Fiyat)
            self.islem_table.setItem(row_count, 3, QTableWidgetItem(f"{kdv_orani:.2f}"))  # KDV oranı
            self.islem_table.setItem(row_count, 4, QTableWidgetItem(f"{kdv_tutari:.2f}"))  # KDV tutarı
            self.islem_table.setItem(row_count, 5, QTableWidgetItem(aciklama))  # Açıklama

            # İşlem özetini güncelle
            self.guncelle_islem_ozeti()

            # Formu temizle
            self.islem_aciklama.clear()
            self.islem_tutar.clear()
            self.kdv_orani.clear()
            self.islem_ek_aciklama.clear()
            self.miktar.setCurrentIndex(0)  # Miktarı sıfırla

            print("İşlem başarıyla eklendi")
        except ValueError:
            QMessageBox.warning(self, "Hata", "Birim Fiyat ve KDV Oranı geçerli bir sayı olmalıdır!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {e}")

    def guncelle_islem_ozeti(self):
        """İşlem özetini günceller."""
        toplam_tutar = 0
        toplam_kdv = 0
        toplam_islem = self.islem_table.rowCount()

        for row in range(toplam_islem):
            tutar_item = self.islem_table.item(row, 2)
            kdv_tutari_item = self.islem_table.item(row, 4)
            if tutar_item:
                toplam_tutar += float(tutar_item.text())
            if kdv_tutari_item:
                toplam_kdv += float(kdv_tutari_item.text())

        self.lbl_islem_sayisi.setText(f"Toplam İşlem Sayısı\n{toplam_islem}")
        self.lbl_islem_tutar.setText(f"Toplam İşlem Tutarı\n{toplam_tutar:.2f}")
        self.lbl_kdv_tutar.setText(f"Toplam KDV Tutarı\n{toplam_kdv:.2f}")

    def teklifi_kaydet(self):
        """Teklif işlemlerini kaydeder."""
        if not self.teklif_id:
            QMessageBox.warning(self, "Uyarı", "Teklif ID bulunamadı!")
            return

        try:
            # Veritabanı bağlantısı
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            
            # Cari kontrolü
            cursor.execute("SELECT COUNT(*) FROM cariler WHERE cari_kodu = ?", (self.cari_kodu.text(),))
            if cursor.fetchone()[0] == 0:
                QMessageBox.warning(self, "Uyarı", "Seçilen cari veritabanında bulunamadı cari kodunu ve diğer alanları kontrol ediniz!")
                conn.close()
                return

            # Araç kontrolü
            cursor.execute("SELECT COUNT(*) FROM araclar WHERE plaka = ?", (self.plaka.text(),))
            if cursor.fetchone()[0] == 0:
                QMessageBox.warning(self, "Uyarı", "Seçilen araç veritabanında bulunamadı!")
                conn.close()
                return
            
            # Teklif tablosunu güncelle
            cursor.execute("""
                UPDATE teklifler 
                SET cari_kodu = ?,
                    plaka = ?,
                    odeme_sekli = ?,
                    odeme_vade_gun = ?,
                    teklif_alan = ?,
                    teklif_veren_personel = ?
                WHERE id = ?
            """, (
                self.cari_kodu.text(),
                self.plaka.text(),
                self.odeme_sekli.currentText(),
                (lambda text: int(text) if text and text.lower() != 'none' else None)(self.vade_gun.text().strip()),
                self.teklif_alan.text(),
                self.teklif_veren.text(),
                self.teklif_id
            ))

            # Mevcut işlemleri sil
            cursor.execute("DELETE FROM teklif_islemler WHERE teklif_id = ?", (self.teklif_id,))
            
            # Yeni işlemleri ekle
            for row in range(self.islem_table.rowCount()):
                islem_aciklama = self.islem_table.item(row, 0).text()
                miktar = int(self.islem_table.item(row, 1).text())
                islem_tutari = float(self.islem_table.item(row, 2).text())
                kdv_orani = float(self.islem_table.item(row, 3).text())
                kdv_tutari = float(self.islem_table.item(row, 4).text())
                aciklama = self.islem_table.item(row, 5).text()

                cursor.execute("""
                    INSERT INTO teklif_islemler 
                    (teklif_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.teklif_id,
                    islem_aciklama,
                    islem_tutari,
                    kdv_orani,
                    kdv_tutari,
                    aciklama,
                    miktar
                ))
            
            conn.commit()
            conn.close()

            # Teklif tutarını güncelle
            update_teklif_tutar(self.teklif_id)
            QMessageBox.information(self, "Başarılı", "Teklif başarıyla kaydedildi.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Teklif kaydedilirken bir hata oluştu: {str(e)}")

    def islem_sil(self):
        """Seçili işlemi tablodan siler."""
        selected = self.islem_table.currentRow()
        if selected >= 0:
            # İşlem detaylarını al
            islem_aciklama = self.islem_table.item(selected, 0).text()
            islem_tutar = self.islem_table.item(selected, 2).text()
            kdv_orani = self.islem_table.item(selected, 3).text()
            kdv_tutari = self.islem_table.item(selected, 4).text()
            aciklama = self.islem_table.item(selected, 5).text()

            # Silme onayı için mesaj oluştur
            mesaj = (
                f"İşlem Açıklaması: {islem_aciklama}\n"
                f"Tutar: {islem_tutar}\n"
                f"KDV Oranı: {kdv_orani}\n"
                f"KDV Tutarı: {kdv_tutari}\n"
                f"Açıklama: {aciklama}\n\n"
                "Bu işlemi silmek istediğinize emin misiniz?"
            )

            # Kullanıcıdan onay al
            reply = QMessageBox.question(
                self,
                "İşlem Silme Onayı",
                mesaj,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                if self.teklif_id:
                    delete_teklif_islem(self.teklif_id, selected)
                    update_teklif_tutar(self.teklif_id)

                self.islem_table.removeRow(selected)
                self.guncelle_islem_ozeti()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir işlem seçin!")

    def teklifi_sil(self):
        """Teklifi ve ilişkili işlemleri siler."""
        if not self.teklif_id:
            QMessageBox.warning(self, "Uyarı", "Teklif ID bulunamadı!")
            return

        # Silme işlemi için onay al
        reply = QMessageBox.question(
            self, 
            "Teklif Silme Onayı",
            "Bu teklifi ve tüm işlemlerini silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Teklifi sil
                delete_teklif(self.teklif_id)
                QMessageBox.information(self, "Başarılı", "Teklif başarıyla silindi.")
                self.close()
                if self.dashboard_ref:
                    self.dashboard_ref.show()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Teklif silinirken bir hata oluştu: {str(e)}")

    def load_teklif_details(self):
        """Teklif detaylarını yükler ve formu doldurur."""
        try:
            # Teklif detaylarını al
            teklif_details = get_teklif_details(self.teklif_no)
            if not teklif_details:
                raise Exception("Teklif detayları bulunamadı!")

            # Teklif bilgilerini doldur
            self.teklif_no_input.setText(teklif_details['teklif']['teklif_no'])
            self.teklif_tarihi.setText(teklif_details['teklif']['teklif_tarihi'])
            self.gecerlilik_tarihi.setText(teklif_details['teklif']['gecerlilik_tarihi'])
            self.odeme_sekli.setCurrentText(teklif_details['teklif']['odeme_sekli'])
            self.vade_gun.setText(str(teklif_details['teklif']['odeme_vade_gun']))
            self.teklif_veren.setText(teklif_details['teklif']['teklif_veren_personel'])
            self.teklif_alan.setText(teklif_details['teklif']['teklif_alan'])

            # Cari bilgilerini doldur
            self.set_cari_bilgileri(
                cari_kodu=teklif_details['teklif']['cari_kodu'],
                cari_unvani=teklif_details['cari']['cari_ad_unvan'],
                telefon=teklif_details['cari']['cep_telefonu'] or "",
                cari_tipi=teklif_details['cari']['cari_tipi'] or ""
            )

            # Araç bilgilerini doldur
            self.set_arac_bilgileri(
                plaka=teklif_details['teklif']['plaka'],
                arac_tipi=teklif_details['arac']['arac_tipi'] or "",
                model_yili=str(teklif_details['arac']['model_yili']) if teklif_details['arac']['model_yili'] else "",
                marka=teklif_details['arac']['marka'] or "",
                model=teklif_details['arac']['model'] or ""
            )

            # Teklif işlemlerini tabloya ekle
            for islem in teklif_details.get('islemler', []):
                row_count = self.islem_table.rowCount()
                self.islem_table.insertRow(row_count)
                
                # İşlem açıklaması
                self.islem_table.setItem(row_count, 0, QTableWidgetItem(islem['islem_aciklama']))
                
                # Miktar
                miktar = islem.get('miktar', 1)
                self.islem_table.setItem(row_count, 1, QTableWidgetItem(str(miktar)))
                
                # İşlem tutarı (eski kayıtlarda boş/NULL alanlar olabilir)
                self.islem_table.setItem(row_count, 2, QTableWidgetItem(f"{islem['islem_tutari'] or 0:.2f}"))

                # KDV oranı
                self.islem_table.setItem(row_count, 3, QTableWidgetItem(f"{islem['kdv_orani'] or 0:.2f}"))

                # KDV tutarı
                self.islem_table.setItem(row_count, 4, QTableWidgetItem(f"{islem['kdv_tutari'] or 0:.2f}"))

                # Açıklama
                self.islem_table.setItem(row_count, 5, QTableWidgetItem(islem['aciklama'] or ""))

            # İşlem özetini güncelle
            self.guncelle_islem_ozeti()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Teklif detayları yüklenirken bir hata oluştu: {str(e)}")

    def pdf_aktar(self):
        try:
            from pdf_aktar import teklif_pdf_aktar
            teklif_pdf_aktar(self, self.teklif_no_input.text())
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = TeklifForm()
    form.show()
    sys.exit(app.exec_()) 