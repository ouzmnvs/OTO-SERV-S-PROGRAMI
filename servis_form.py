from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QFrame, QMessageBox, QDialog, QTextEdit
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from cari_select_list import CariSelectListForm  # CariSelectListForm'u içe aktarın
from car_select_list import CarSelectListForm  # CarSelectListForm'u içe aktarın
from database_progress import add_servis, add_islem, add_teklif_islem, delete_teklif_islem, update_teklif_tutar, load_servis_kayitlari_by_plaka, get_service_full_details  # Servis ekleme fonksiyonunu içe aktarın
from datetime import datetime
class ServisForm(QDialog):  # QWidget yerine QDialog kullanıyoruz
    def __init__(self, dashboard_ref=None):
        super().__init__()
        self.dashboard_ref = dashboard_ref
        self.setWindowTitle("İş Emri Formu")
        
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
        genislik = int(BASE_WIDTH * scale * 0.90)
        yukseklik = int(BASE_HEIGHT * scale * 0.90)
        
        self.setFixedSize(genislik, yukseklik)
        x = (screen_width - genislik) // 2
        y = (screen_height - yukseklik) // 2 - 40
        if y < 0:
            y = 0
        self.move(x, y)
        
        self.init_ui()
        self.setWindowIcon(icon('fa5s.file')) # Add a file icon
    def init_ui(self):
        ana_layout = QHBoxLayout()
        ana_layout.setSpacing(8)  # Reduced spacing

        # Sol Panel: Araç ve Cari Bilgileri
        sol_panel = QVBoxLayout()
        sol_panel.setSpacing(8)  # Reduced spacing

        # Başlık
        lbl_sol_baslik = QLabel("Araç - Cari Bilgileri")
        lbl_sol_baslik.setStyleSheet("""
            background-color: #333;
            color: white;
            font: bold 14px;
            padding: 6px 12px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        """)
        sol_panel.addWidget(lbl_sol_baslik)

        # Bilgi Girişi
        bilgi_group = QGroupBox("Cari ve Araç Bilgilerini Giriniz")
        bilgi_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 6px;
                margin-top: 8px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 10px;
                top: 2px;
                padding: 0 4px;
            }
        """)
        bilgi_layout = QGridLayout()
        bilgi_layout.setVerticalSpacing(8)  # Reduced spacing
        bilgi_layout.setHorizontalSpacing(6)  # Reduced spacing

        label_style = "font-size: 13px; font-weight: 600; color: #222;"
        input_style = """
            QLineEdit, QComboBox, QTextEdit {
                font-size: 13px;
                padding: 6px 10px;
                border-radius: 4px;
                border: 1.5px solid #bbb;
                background: #fafbfc;
                min-height: 20px;
                min-width: 20px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 2px solid #1976d2;
                background: #fff;
            }
        """

        # Müşteri Talepleri alanı
        bilgi_layout.addWidget(self._label("Müşteri Talepleri", label_style), 0, 0)
        self.musteri_talepleri = QTextEdit()
        self.musteri_talepleri.setStyleSheet(input_style)
        self.musteri_talepleri.setMinimumHeight(100)  # Yüksekliği artır
        self.musteri_talepleri.setPlaceholderText("Müşterinin servis taleplerini ve açıklamalarını buraya yazınız...")
        bilgi_layout.addWidget(self.musteri_talepleri, 0, 1, 1, 2)  # 2 sütun genişliğinde

        # Cari ve Araç Bilgilerini Giriniz (Sadece cari ile ilgili kısım güncellendi)
        bilgi_layout.addWidget(self._label("Cari Kodu", label_style), 1, 0)
        self.cari_kodu = QLineEdit()
        self.cari_kodu.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.cari_kodu, 1, 1)

        bilgi_layout.addWidget(self._label("Cari Adı / Ünvanı", label_style), 2, 0)
        self.cari_unvan = QLineEdit()
        self.cari_unvan.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.cari_unvan, 2, 1)

        bilgi_layout.addWidget(self._label("Telefon", label_style), 3, 0)
        self.telefon = QLineEdit()
        self.telefon.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.telefon, 3, 1)

        bilgi_layout.addWidget(self._label("Cari Tipi *", label_style), 4, 0)
        self.cari_tipi = QComboBox()
        self.cari_tipi.setStyleSheet(input_style)
        self.cari_tipi.addItems(["", "Bireysel","Kurumsal"])
        bilgi_layout.addWidget(self.cari_tipi, 4, 1)

        sec_btn = QPushButton(icon('fa5s.user-check', color='black'), "Seç")
        sec_btn.setMinimumHeight(28)
        sec_btn.setStyleSheet("font-size:13px; font-weight:700; padding:4px 10px;")
        sec_btn.clicked.connect(self.open_cari_select_list)
        bilgi_layout.addWidget(sec_btn, 4, 2)

        bilgi_layout.addWidget(self._label("Plaka *", label_style), 5, 0)
        self.plaka = QLineEdit()
        self.plaka.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.plaka, 5, 1)

        bilgi_layout.addWidget(self._label("Araç Tipi *", label_style), 6, 0)
        self.arac_tipi = QComboBox()
        self.arac_tipi.setStyleSheet(input_style)
        self.arac_tipi.addItems(["", "Otomobil", "Kamyonet", "Minibüs", "Diğer"])
        bilgi_layout.addWidget(self.arac_tipi, 6, 1)

        bilgi_layout.addWidget(self._label("Model Yılı", label_style), 7, 0)
        self.model_yili = QLineEdit()
        self.model_yili.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.model_yili, 7, 1)

        bilgi_layout.addWidget(self._label("Marka", label_style), 8, 0)
        self.marka = QLineEdit()
        self.marka.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.marka, 8, 1)

        bilgi_layout.addWidget(self._label("Model", label_style), 9, 0)
        self.model = QLineEdit()
        self.model.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.model, 9, 1)

        bilgi_layout.addWidget(self._label("Aracı Getiren Kişi", label_style), 10, 0)
        self.arac_getiren_kisi = QLineEdit()
        self.arac_getiren_kisi.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.arac_getiren_kisi, 10, 1, 1, 2)

        arac_sec_btn = QPushButton(icon('fa5s.car', color='blue'), "Seç")
        arac_sec_btn.setMinimumHeight(28)
        arac_sec_btn.setStyleSheet("font-size:13px; font-weight:700; padding:4px 10px;")
        arac_sec_btn.clicked.connect(self.open_car_select_list)
        bilgi_layout.addWidget(arac_sec_btn, 9, 2)

        bilgi_group.setLayout(bilgi_layout)
        sol_panel.addWidget(bilgi_group)

        # Geçmiş Servis Kayıtları
        gecmis_group = QGroupBox("Geçmiş Servis Kayıtları")
        gecmis_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        gecmis_layout = QVBoxLayout()
        self.gecmis_table = QTableWidget(0, 3)
        self.gecmis_table.setHorizontalHeaderLabels(["Tarih", "Tutar", "Durum"])
        self.gecmis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.gecmis_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gecmis_table.setAlternatingRowColors(True)
        self.gecmis_table.setStyleSheet("""
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
        # Çift tıklama olayını bağla
        self.gecmis_table.cellDoubleClicked.connect(self.handle_service_double_click)
        gecmis_layout.addWidget(self.gecmis_table)
        gecmis_group.setLayout(gecmis_layout)
        sol_panel.addWidget(gecmis_group)

        ana_layout.addLayout(sol_panel, 2)

        # Sağ Panel: İşlem ve Özet Bilgileri
        sag_panel = QVBoxLayout()
        sag_panel.setSpacing(10)

        # Sağ başlık
        lbl_sag_baslik = QLabel("İşlem ve Özet Bilgileri")
        lbl_sag_baslik.setStyleSheet("""
            background-color: #333;
            color: white;
            font: bold 18px;
            padding: 5px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
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
                margin-top: 4px;
                padding: 4px;
            }
        """)
        islem_layout = QGridLayout()
        islem_layout.setVerticalSpacing(8)
        islem_layout.setHorizontalSpacing(6)

        # İşlem Açıklamı
        islem_layout.addWidget(self._label("İşlem Açıklamı", label_style), 0, 0)
        islem_aciklama_layout = QHBoxLayout()
        self.islem_aciklama = QLineEdit()
        self.islem_aciklama.setStyleSheet(input_style)
        self.islem_aciklama.setMinimumWidth(10)
        islem_aciklama_layout.addWidget(self.islem_aciklama)

        # Miktar seçimi için ComboBox
        self.miktar = QComboBox()
        self.miktar.setStyleSheet(input_style)
        self.miktar.setFixedWidth(50)
        self.miktar.addItems([str(i) for i in range(1, 11)])  # 1'den 10'a kadar
        islem_aciklama_layout.addWidget(self.miktar)
        islem_layout.addLayout(islem_aciklama_layout, 1, 0)

        # İşlem Tutarı
        islem_layout.addWidget(self._label("İşlem Tutarı", label_style), 0, 1)
        self.islem_tutar = QLineEdit()
        self.islem_tutar.setStyleSheet(input_style)
        self.islem_tutar.setMinimumWidth(60)
        islem_layout.addWidget(self.islem_tutar, 1, 1)

        # Açıklama
        islem_layout.addWidget(self._label("Açıklama", label_style), 0, 2)
        self.islem_ek_aciklama = QLineEdit()
        self.islem_ek_aciklama.setStyleSheet(input_style)
        self.islem_ek_aciklama.setMinimumWidth(80)
        islem_layout.addWidget(self.islem_ek_aciklama, 1, 2)

        # KDV Oranı
        islem_layout.addWidget(self._label("KDV Oranı (%)", label_style), 0, 3)
        self.kdv_orani = QLineEdit()
        self.kdv_orani.setStyleSheet(input_style)
        self.kdv_orani.setMinimumWidth(40)
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
        self.islem_table = QTableWidget(0, 5)  # Sütun sayısını 5'e çıkarıyoruz
        self.islem_table.setHorizontalHeaderLabels([
            "İşlem Açıklamı", "Tutar", "KDV (%)", "KDV Tutarı", "Açıklama"
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
        btn_emri_olustur = self._buton("İŞ EMRİ OLUŞTUR", 'fa5s.save', 'deepskyblue')
        btn_emri_olustur.clicked.connect(self.emri_olustur)
        btn_islemleri_temizle = self._buton("İŞLEMİ SİL", 'fa5s.sync', '#fbc02d')
        btn_islemleri_temizle.clicked.connect(self.islem_sil)
        btn_pdf_aktar = self._buton("PDF AKTAR", 'fa5s.file-pdf', '#388e3c')
        btn_sayfa_kapat = self._buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')
        btn_sayfa_kapat.clicked.connect(self.sayfayi_kapat)
        btn_layout.addWidget(btn_emri_olustur, 2)
        btn_layout.addWidget(btn_islemleri_temizle, 2)
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
        for widget in [self.cari_kodu, self.cari_unvan, self.telefon, self.plaka, 
                      self.model_yili, self.marka, self.model, self.arac_getiren_kisi]:
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
        self.arac_getiren_kisi.clear()  # Aracı getiren kişi alanını temizle
        self.load_servis_kayitlari()  # Servis kayıtlarını yükle

    def load_servis_kayitlari(self):
        """Araca ait servis kayıtlarını yükler."""
        kayitlar = load_servis_kayitlari_by_plaka(self.plaka.text())
        self.gecmis_table.setRowCount(len(kayitlar))
        toplam_tutar = 0
        for row, (tarih, tutar, durum) in enumerate(kayitlar):
            self.gecmis_table.setItem(row, 0, QTableWidgetItem(tarih))
            self.gecmis_table.setItem(row, 1, QTableWidgetItem(f"{tutar:,.2f}"))
            self.gecmis_table.setItem(row, 2, QTableWidgetItem(durum))
            toplam_tutar += tutar

    def _label(self, text, style):
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        return lbl

    def _buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(140)
        btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                font-weight: 700;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return btn
    def sayfayi_kapat(self):
        """Servis formunu kapatır ve dashboard ekranına geri döner."""
        self.close()  # QDialog'da close() kullanılır
        if self.dashboard_ref:
            self.dashboard_ref.show()  # Dashboard ekranını tekrar göster

    def islem_ekle(self):
        """İşlem bilgilerini tabloya ekler."""
        # Cari ve araç seçimi kontrolü
        if not self.cari_kodu.text().strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir cari seçin!")
            return
        if not self.plaka.text().strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir araç seçin!")
            return

        # Formdaki bilgileri al
        islem_aciklama = self.islem_aciklama.text().strip()
        islem_tutari = self.islem_tutar.text().strip()
        kdv_orani = self.kdv_orani.text().strip() or "20"  # Varsayılan KDV oranı
        aciklama = self.islem_ek_aciklama.text().strip()
        miktar = int(self.miktar.currentText())  # Seçilen miktarı al

        # Gerekli alanların doldurulup doldurulmadığını kontrol et
        if not islem_aciklama or not islem_tutari:
            QMessageBox.warning(self, "Uyarı", "Lütfen gerekli alanları doldurun!")
            return

        try:
            # KDV oranını ve tutarı float'a dönüştür
            kdv_orani = float(kdv_orani)
            birim_tutar = float(islem_tutari)  # Birim tutar
            islem_tutari_float = birim_tutar * miktar  # Toplam tutar = birim tutar * miktar
            kdv_tutari = islem_tutari_float * kdv_orani / 100

            # İşlemi tabloya ekle
            row_count = self.islem_table.rowCount()
            self.islem_table.insertRow(row_count)
            self.islem_table.setItem(row_count, 0, QTableWidgetItem(f"{islem_aciklama} ({miktar})"))
            self.islem_table.setItem(row_count, 1, QTableWidgetItem(f"{islem_tutari_float:.2f}"))
            self.islem_table.setItem(row_count, 2, QTableWidgetItem(f"{kdv_orani:.2f}"))
            self.islem_table.setItem(row_count, 3, QTableWidgetItem(f"{kdv_tutari:.2f}"))
            self.islem_table.setItem(row_count, 4, QTableWidgetItem(aciklama))

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
            QMessageBox.warning(self, "Hata", "KDV Oranı ve Tutar geçerli bir sayı olmalıdır!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {e}")

    def guncelle_islem_ozeti(self):
        toplam_tutar = 0
        toplam_kdv = 0
        toplam_islem = self.islem_table.rowCount()

        for row in range(toplam_islem):
            tutar_item = self.islem_table.item(row, 1)
            kdv_tutari_item = self.islem_table.item(row, 3)
            if tutar_item:
                toplam_tutar += float(tutar_item.text())
            if kdv_tutari_item:
                toplam_kdv += float(kdv_tutari_item.text())

        self.lbl_islem_sayisi.setText(f"Toplam İşlem Sayısı\n{toplam_islem}")
        self.lbl_islem_tutar.setText(f"Toplam İşlem Tutarı\n{toplam_tutar:.2f}")
        # Toplam KDV tutarını da göster
        if hasattr(self, "lbl_kdv_tutar"):
            self.lbl_kdv_tutar.setText(f"Toplam KDV Tutarı\n{toplam_kdv:.2f}")
        else:
            self.lbl_kdv_tutar = QLabel(f"Toplam KDV Tutarı\n{toplam_kdv:.2f}")
            self.lbl_kdv_tutar.setStyleSheet("font-size: 13px; background: #ffe0b2; padding: 4px;")
            # Özet grubuna ekleyin
            self.layout().itemAt(1).itemAt(0).widget().layout().addWidget(self.lbl_kdv_tutar)

    def emri_olustur(self):
        """Cari ve araç bilgileriyle servis oluşturur ve işlemleri bu servise bağlar."""
        cari_kodu = self.cari_kodu.text().strip()
        plaka = self.plaka.text().strip()
        servis_tarihi = datetime.now().strftime("%Y-%m-%d")  # Standart tarih formatı
        aciklama = self.musteri_talepleri.toPlainText().strip()  # Müşteri taleplerini açıklama olarak kullan
        arac_getiren_kisi = self.arac_getiren_kisi.text().strip()

        # Gerekli alanların doldurulup doldurulmadığını kontrol et
        if not cari_kodu or not plaka:
            uyari = UyariPenceresi("Lütfen cari kodu ve plaka bilgilerini doldurun!", self)
            uyari.exec_()
            return

        # İşlem tablosunun boş olup olmadığını kontrol et
        toplam_islem = self.islem_table.rowCount()
        if toplam_islem == 0:
            uyari = UyariPenceresi("Lütfen en az bir işlem ekleyin!", self)
            uyari.exec_()
            return

        # Servis ve işlemleri kaydet
        servis_id = add_servis(cari_kodu, plaka, servis_tarihi, aciklama, arac_getiren_kisi)
        for row in range(toplam_islem):
            islem_aciklama = self.islem_table.item(row, 0).text()
            # Miktar bilgisini parantez içinden çıkar
            miktar = 1
            if '(' in islem_aciklama and ')' in islem_aciklama:
                try:
                    miktar = int(islem_aciklama[islem_aciklama.find('(')+1:islem_aciklama.find(')')])
                    islem_aciklama = islem_aciklama[:islem_aciklama.find('(')].strip()
                except:
                    pass

            islem_tutari = float(self.islem_table.item(row, 1).text())
            kdv_orani = float(self.islem_table.item(row, 2).text())
            kdv_tutari = float(self.islem_table.item(row, 3).text())
            islem_aciklama_ek = self.islem_table.item(row, 4).text()
            add_islem(servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, islem_aciklama_ek, miktar)

        # Formu temizle
        self.islem_table.setRowCount(0)
        self.guncelle_islem_ozeti()
        self.cari_kodu.clear()
        self.plaka.clear()
        self.cari_unvan.clear()
        self.telefon.clear()
        self.cari_tipi.setCurrentIndex(0)
        self.arac_tipi.setCurrentIndex(0)
        self.model_yili.clear()
        self.marka.clear()
        self.model.clear()
        self.musteri_talepleri.clear()  # Müşteri taleplerini temizle
        self.arac_getiren_kisi.clear()

        # Bilgilendirme penceresini göster
        bilgi = BilgilendirmePenceresi(self)
        bilgi.exec_()

        QMessageBox.information(self, "Başarılı", "Servis başarıyla oluşturuldu.")
        self.accept()  # Formu başarılı şekilde kapat

    def islem_sil(self):
        """Seçili işlemi tablodan siler."""
        selected = self.islem_table.currentRow()
        if selected >= 0:
            self.islem_table.removeRow(selected)
            self.guncelle_islem_ozeti()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir işlem seçin!")

    def handle_service_double_click(self, row, column):
        """Servis kaydına çift tıklandığında PDF oluşturur."""
        from PyQt5.QtWidgets import QFileDialog
        servis_tarihi = self.gecmis_table.item(row, 0).text()
        
        # Servis ID'sini al
        import sqlite3
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM servisler WHERE plaka=? AND servis_tarihi=?", 
                      (self.plaka.text(), servis_tarihi))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            QMessageBox.warning(self, "Uyarı", "Servis kaydı bulunamadı!")
            return
            
        servis_id = row[0]
        
        # Servis detaylarını al
        detaylar = get_service_full_details(servis_id)
        if not detaylar:
            QMessageBox.warning(self, "Uyarı", "Servis detayları alınamadı!")
            return

        # Detayları ayrıştır
        servis_bilgi = detaylar["servis"]
        cari_bilgi = detaylar["cari"]
        arac_bilgi = detaylar["arac"]
        islem_listesi = detaylar["islemler"]

        # Vergi numarası kontrolü
        vergi_no = cari_bilgi.get('vergi_no', '')
        if vergi_no is None:
            vergi_no = ''

        # İş emri numarasını 6 haneli formatta hazırla
        is_emri_no = f"{servis_id:06d}"

        # Dosya adını hazırla
        default_filename = f"servis_{is_emri_no}_{self.plaka.text()}_{servis_tarihi}.pdf"
        dosya_yolu, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", default_filename, "PDF Files (*.pdf)")
        if not dosya_yolu:
            return

        # İşlemleri PDF için hazırla
        islem_texts = []
        y_baslangic = 155  # 92.5 * 1.67
        satir_yuksekligi = 6  # 3.5 * 1.67

        # Toplam tutarları hesapla
        kdv_haric_toplam = sum(islem['islem_tutari'] for islem in islem_listesi)
        kdv_tutari = sum(islem['kdv_tutari'] for islem in islem_listesi)
        toplam_tutar = kdv_haric_toplam + kdv_tutari

        # İşlemleri PDF için hazırla
        for i, islem in enumerate(islem_listesi, 1):
            islem_texts.extend([
                (10, y_baslangic - (i * satir_yuksekligi), str(i)),
                (30, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_aciklama']} {islem['aciklama']}"),
                (113, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari']:.2f}"),
                (136, y_baslangic - (i * satir_yuksekligi), "1"),
                (148, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari']:.2f}"),
                (170, y_baslangic - (i * satir_yuksekligi), "0.0%"),  # İskonto her zaman 0
                (184, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari']:.2f}")
            ])

        # Cari ad unvanını 7 kelimede bir veya nokta ile biten kelimeden sonra yeni satıra böl
        cari_ad_unvan = cari_bilgi.get('cari_ad_unvan', '')
        words = cari_ad_unvan.split()
        cari_ad_unvan_lines = []
        line_words = []

        for word in words:
            line_words.append(word)
            # Satırı bitirme koşulu: 7 kelime olduysa
            if len(line_words) == 7:
                cari_ad_unvan_lines.append(' '.join(line_words))
                line_words = []

        # Kalan kelimeler varsa ekle
        if line_words:
            cari_ad_unvan_lines.append(' '.join(line_words))

        # Her satırı PDF'e ekle (cari adı için font boyutu 7)
        for i, line in enumerate(cari_ad_unvan_lines):
            eklemeler['text'].append((45, 250 - (i * 5), line, 7))

        # PDF için eklemeler sözlüğünü oluştur
        eklemeler = {
            'text': [
                # Servis ve Cari Bilgileri
                (159, 260, is_emri_no, 9),  # İş emri numarası
                (90, 260, self.plaka.text(), 9),  # Plaka
                (50, 237, cari_bilgi.get('cep_telefonu', ''), 9),  # Telefon
                (50, 232, vergi_no, 9),  # Vergi no
                (50, 223, arac_bilgi.get('arac_tipi', ''), 9),  # Araç tipi
                (50, 218, f"{arac_bilgi.get('marka', '')} {arac_bilgi.get('model', '')}", 9),  # Marka model
                (50, 211, str(arac_bilgi.get('model_yili', '')), 9),  # Model yılı
                (120, 223, arac_bilgi.get('sasi_no', ''), 9),  # Şasi no
                (120, 218, arac_bilgi.get('motor_no', ''), 9),  # Motor no
                (120, 211, servis_bilgi.get('servis_tarihi', ''), 9),  # Servis tarihi
                (58, 204, servis_bilgi.get('servis_tarihi', ''), 9),  # Tarih
                (58, 191, servis_bilgi.get('servis_tarihi', ''), 9),  # Tarih

                # Tutar Bilgileri
                (175, 68, f"₺ {kdv_haric_toplam:,.2f} TL", 9),
                (175, 63, f"₺ {kdv_tutari:,.2f} TL", 9),
                (175, 58, f"₺ {toplam_tutar:,.2f} TL", 9)
            ]
        }

        # İşlemleri eklemeler listesine ekle
        eklemeler['text'].extend(islem_texts)

        # PDF'i oluştur
        from pdf_oluşturucu import mevcut_pdf_duzenle
        mevcut_pdf_duzenle("classiccar.pdf", dosya_yolu, eklemeler, font_size=10)  # Font boyutunu 6'dan 10'a çıkardım
        QMessageBox.information(self, "Başarılı", "PDF başarıyla oluşturuldu.")

class BilgilendirmePenceresi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bilgilendirme")
        self.setFixedSize(350, 120)
        layout = QVBoxLayout()
        label = QLabel("Emir oluşturuldu, açık servislerde görüntüleyebilirsiniz.")
        label.setStyleSheet("font-size: 15px; padding: 12px;")
        label.setWordWrap(True)
        layout.addWidget(label)

        # Tamam butonunu sağa yasla ve küçült
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_tamam = QPushButton("Tamam")
        btn_tamam.setFixedSize(80, 28)
        btn_tamam.clicked.connect(self.accept)
        btn_layout.addWidget(btn_tamam)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

class UyariPenceresi(QDialog):
    def __init__(self, mesaj, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Uyarı")
        self.setFixedSize(350, 120)
        layout = QVBoxLayout()
        label = QLabel(mesaj)
        label.setStyleSheet("font-size: 15px; padding: 12px;")
        label.setWordWrap(True)
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_tamam = QPushButton("Tamam")
        btn_tamam.setFixedSize(80, 28)
        btn_tamam.clicked.connect(self.accept)
        btn_layout.addWidget(btn_tamam)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ServisForm()
    form.show()
    sys.exit(app.exec_())