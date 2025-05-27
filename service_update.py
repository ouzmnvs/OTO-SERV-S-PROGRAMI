from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
   QDesktopWidget, QSizePolicy, QFrame, QMessageBox, QFileDialog, QTextEdit
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import add_islem, load_service_operations, delete_service, update_servis
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import datetime
from pdf_oluşturucu import mevcut_pdf_duzenle

class ServiceUpdateForm(QDialog):
    def __init__(self):
        super().__init__()
        self.servis_id = None
        self.pending_operations = []
        self.deleted_operations = []
        self.existing_operations = []
        self.setWindowTitle("Servis Güncelleme")
        
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
        
        # Calculate new dimensions
        genislik = int(BASE_WIDTH * scale * 0.90)
        yukseklik = int(BASE_HEIGHT * scale * 0.90)
        
        self.setFixedSize(genislik, yukseklik)
        x = (screen_width - genislik) // 2
        y = (screen_height - yukseklik) // 2 - 40
        if y < 0:
            y = 0
        self.move(x, y)
        self.setWindowIcon(icon('fa5s.file'))
        self.init_ui()

    def init_ui(self):
        ana_layout = QHBoxLayout()
        ana_layout.setSpacing(12)

        # Sol Panel: Araç ve Cari Bilgileri
        sol_panel = QVBoxLayout()
        sol_panel.setSpacing(10)

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
        """)
        bilgi_layout = QGridLayout()
        bilgi_layout.setVerticalSpacing(12)
        bilgi_layout.setHorizontalSpacing(8)

        label_style = "font-size: 12px; font-weight: 600; color: #222;"
        input_style = """
            QLineEdit, QComboBox {
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1.5px solid #bbb;
                background: #fafbfc;
                min-height: 18px;
                min-width: 150px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #1976d2;
                background: #fff;
            }
        """

        bilgi_layout.addWidget(self._label("Cari Kodu", label_style), 0, 0)
        self.txt_cari_kodu = QLineEdit()
        self.txt_cari_kodu.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_cari_kodu, 0, 1)

        bilgi_layout.addWidget(self._label("Cari Adı / Ünvanı", label_style), 1, 0)
        self.txt_cari_unvan = QLineEdit()
        self.txt_cari_unvan.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_cari_unvan, 1, 1)

        bilgi_layout.addWidget(self._label("Telefon", label_style), 2, 0)
        self.txt_telefon = QLineEdit()
        self.txt_telefon.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_telefon, 2, 1)

        bilgi_layout.addWidget(self._label("Cari Tipi *", label_style), 3, 0)
        self.cmb_cari_tipi = QComboBox()
        self.cmb_cari_tipi.setStyleSheet(input_style)
        self.cmb_cari_tipi.addItems(["", "Bireysel", "Kurumsal"])
        bilgi_layout.addWidget(self.cmb_cari_tipi, 3, 1)

        bilgi_layout.addWidget(self._label("Plaka *", label_style), 4, 0)
        self.txt_plaka = QLineEdit()
        self.txt_plaka.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_plaka, 4, 1)

        bilgi_layout.addWidget(self._label("Araç Tipi *", label_style), 5, 0)
        self.cmb_arac_tipi = QComboBox()
        self.cmb_arac_tipi.setStyleSheet(input_style)
        self.cmb_arac_tipi.addItems(["", "Otomobil", "Kamyonet", "Minibüs", "Diğer"])
        bilgi_layout.addWidget(self.cmb_arac_tipi, 5, 1)

        bilgi_layout.addWidget(self._label("Model Yılı", label_style), 6, 0)
        self.txt_model_yili = QLineEdit()
        self.txt_model_yili.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_model_yili, 6, 1)

        bilgi_layout.addWidget(self._label("Marka", label_style), 7, 0)
        self.txt_marka = QLineEdit()
        self.txt_marka.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_marka, 7, 1)

        bilgi_layout.addWidget(self._label("Model", label_style), 8, 0)
        self.txt_model = QLineEdit()
        self.txt_model.setStyleSheet(input_style)
        self.txt_model.setReadOnly(True)
        bilgi_layout.addWidget(self.txt_model, 8, 1)

        # Aracı Getiren Kişi alanı
        bilgi_layout.addWidget(self._label("Aracı Getiren Kişi", label_style), 9, 0)
        self.txt_arac_getiren = QLineEdit()
        self.txt_arac_getiren.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_arac_getiren, 9, 1, 1, 2)

        # Açıklama alanı
        bilgi_layout.addWidget(self._label("Müşteri Talepleri ve Açıklama", label_style), 10, 0)
        self.txt_aciklama = QTextEdit()
        self.txt_aciklama.setStyleSheet(input_style)
        self.txt_aciklama.setMinimumHeight(100)
        self.txt_aciklama.setPlaceholderText("Müşteri talepleri ve servis açıklamasını buraya yazınız...")
        bilgi_layout.addWidget(self.txt_aciklama, 10, 1, 1, 2)

        bilgi_group.setLayout(bilgi_layout)
        sol_panel.addWidget(bilgi_group)

        sol_panel.addStretch(1)
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
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        sag_panel.addWidget(lbl_sag_baslik)

        # --- İşlem Ekleme Alanı ---
        islem_ekle_layout = QGridLayout()
        islem_ekle_layout.setVerticalSpacing(8)
        islem_ekle_layout.setHorizontalSpacing(6)

        # İşlem Açıklaması
        islem_ekle_layout.addWidget(self._label("İşlem Açıklaması", label_style), 0, 0)
        islem_aciklama_layout = QHBoxLayout()
        self.input_islem_aciklama = QLineEdit()
        self.input_islem_aciklama.setStyleSheet(input_style)
        self.input_islem_aciklama.setMinimumWidth(100)
        islem_aciklama_layout.addWidget(self.input_islem_aciklama)

        # Miktar seçimi için ComboBox
        self.input_miktar = QComboBox()
        self.input_miktar.setStyleSheet(input_style)
        self.input_miktar.setFixedWidth(50)
        self.input_miktar.addItems([str(i) for i in range(1, 11)])  # 1'den 10'a kadar
        islem_aciklama_layout.addWidget(self.input_miktar)
        islem_ekle_layout.addLayout(islem_aciklama_layout, 1, 0)

        # İşlem Tutarı
        islem_ekle_layout.addWidget(self._label("Birim Fiyat", label_style), 0, 1)
        self.input_islem_tutar = QLineEdit()
        self.input_islem_tutar.setStyleSheet(input_style)
        self.input_islem_tutar.setMinimumWidth(60)
        islem_ekle_layout.addWidget(self.input_islem_tutar, 1, 1)

        # KDV Oranı
        islem_ekle_layout.addWidget(self._label("KDV (%)", label_style), 0, 2)
        self.input_islem_kdv = QLineEdit()
        self.input_islem_kdv.setStyleSheet(input_style)
        self.input_islem_kdv.setMinimumWidth(40)
        self.input_islem_kdv.setText("20")
        islem_ekle_layout.addWidget(self.input_islem_kdv, 1, 2)

        # Ek Açıklama
        islem_ekle_layout.addWidget(self._label("Ek Açıklama", label_style), 0, 3)
        self.input_islem_ek_aciklama = QLineEdit()
        self.input_islem_ek_aciklama.setStyleSheet(input_style)
        self.input_islem_ek_aciklama.setMinimumWidth(80)
        islem_ekle_layout.addWidget(self.input_islem_ek_aciklama, 1, 3)

        # Ekle butonu
        btn_islem_ekle = QPushButton(icon('fa5s.plus', color='#43a047'), "İŞLEM EKLE")
        btn_islem_ekle.setMinimumHeight(28)
        btn_islem_ekle.setStyleSheet("font-size:12px; font-weight:700; padding:4px 8px;")
        btn_islem_ekle.clicked.connect(self.islem_ekle)
        islem_ekle_layout.addWidget(btn_islem_ekle, 1, 4)

        sag_panel.addLayout(islem_ekle_layout)
        # --- İşlem Ekleme Alanı Sonu ---

        # İşlem Listesi Tablosu
        self.tbl_islemler = QTableWidget(0, 6)
        self.tbl_islemler.setHorizontalHeaderLabels([
            "Açıklama", "Tutar", "KDV (%)", "KDV Tutarı", "Miktar", "Ek Açıklama"
        ])
        self.tbl_islemler.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_islemler.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_islemler.setAlternatingRowColors(True)
        self.tbl_islemler.setStyleSheet("""
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
        sag_panel.addWidget(self.tbl_islemler)

        # Alt Butonlar
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
                margin-top: 5px;
                padding: 12px;
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
        btn_kaydet = self._buton("KAYDET", 'fa5s.save', '#0288d1')
        btn_kaydet.clicked.connect(self.kaydet_servis)

        btn_islem_sil = self._buton("İŞLEMİ SİL", 'fa5s.trash', '#b71c1c')
        btn_islem_sil.clicked.connect(self.islem_sil)

        btn_pdf = self._buton("PDF AKTAR", 'fa5s.file-pdf', '#388e3c')
        btn_pdf.clicked.connect(self.pdf_aktar)

        btn_kaydi_sil = self._buton("KAYDI SİL", 'fa5s.trash', '#b71c1c')
        btn_kaydi_sil.clicked.connect(self.kaydi_sil)

        btn_kapat = self._buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')
        btn_kapat.clicked.connect(self.reject)

        btn_layout.addWidget(btn_kaydet)
        btn_layout.addWidget(btn_islem_sil)
        btn_layout.addWidget(btn_pdf)
        btn_layout.addWidget(btn_kaydi_sil)
        btn_layout.addWidget(btn_kapat)
        alt_layout.addLayout(btn_layout)

        sag_panel.addLayout(alt_layout)

        ana_layout.addLayout(sag_panel, 4)
        self.setLayout(ana_layout)

        # Input alanlarına size policy ekle
        for widget in [self.txt_cari_kodu, self.txt_cari_unvan, self.txt_telefon, 
                      self.txt_plaka, self.txt_model_yili, self.txt_marka, 
                      self.txt_model, self.txt_arac_getiren]:
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            widget.setMinimumWidth(200)

    def _label(self, text, style):
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        return lbl

    def _buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(44)
        btn.setMinimumWidth(140)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 12px;
                font-weight: 700;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: #e0e0e0;
            }}
        """)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return btn

    def set_service_details(self, details):
        self.servis_id = details["servis"]["id"]
        self.txt_cari_kodu.setText(details["cari"].get("cari_kodu", ""))
        self.txt_cari_kodu.setReadOnly(True)
        self.txt_cari_unvan.setText(details["cari"].get("cari_ad_unvan", ""))
        self.txt_cari_unvan.setReadOnly(True)
        self.txt_telefon.setText(details["cari"].get("cep_telefonu", ""))
        self.txt_telefon.setReadOnly(True)
        self.cmb_cari_tipi.setCurrentText(details["cari"].get("cari_tipi", ""))
        self.cmb_cari_tipi.setEnabled(False)
        self.txt_plaka.setText(details["arac"].get("plaka", ""))
        self.txt_plaka.setReadOnly(True)
        self.cmb_arac_tipi.setCurrentText(details["arac"].get("arac_tipi", ""))
        self.cmb_arac_tipi.setEnabled(False)
        self.txt_model_yili.setText(str(details["arac"].get("model_yili", "")))
        self.txt_model_yili.setReadOnly(True)
        self.txt_marka.setText(details["arac"].get("marka", ""))
        self.txt_marka.setReadOnly(True)
        self.txt_model.setText(details["arac"].get("model", ""))
        self.txt_model.setReadOnly(True)
        self.txt_arac_getiren.setText(details["servis"].get("arac_getiren_kisi", ""))
        self.txt_aciklama.setText(details["servis"].get("aciklama", ""))
        
        # İşlemleri tabloya ekle
        self.tbl_islemler.setRowCount(len(details["islemler"]))
        self.existing_operations = []
        for row, islem in enumerate(details["islemler"]):
            self.tbl_islemler.setItem(row, 0, QTableWidgetItem(islem["islem_aciklama"]))
            self.tbl_islemler.setItem(row, 1, QTableWidgetItem(f"{islem['islem_tutari']:.2f}"))
            self.tbl_islemler.setItem(row, 2, QTableWidgetItem(f"{islem['kdv_orani']:.2f}"))
            self.tbl_islemler.setItem(row, 3, QTableWidgetItem(f"{islem['kdv_tutari']:.2f}"))
            self.tbl_islemler.setItem(row, 4, QTableWidgetItem(str(islem["miktar"])))
            self.tbl_islemler.setItem(row, 5, QTableWidgetItem(islem["aciklama"]))
            self.existing_operations.append((
                islem["id"],
                islem["islem_aciklama"],
                islem["islem_tutari"],
                islem["kdv_orani"],
                islem["aciklama"]
            ))
        
        # İşlem özetini güncelle
        self.guncelle_islem_ozeti()

    def islem_sil(self):
        selected_row = self.tbl_islemler.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir işlem seçin!")
            return
        islem_aciklama = self.tbl_islemler.item(selected_row, 0).text()
        islem_tutar = self.tbl_islemler.item(selected_row, 1).text()
        kdv_orani = self.tbl_islemler.item(selected_row, 2).text()
        aciklama = self.tbl_islemler.item(selected_row, 3).text()
        mesaj = (
            f"İşlem Açıklaması: {islem_aciklama}\n"
            f"Tutar: {islem_tutar}\n"
            f"KDV Oranı: {kdv_orani}\n"
            f"Açıklama: {aciklama}\n\n"
            "Bu işlemi silmek istediğinize emin misiniz?"
        )
        yanit = QMessageBox.question(self, "İşlem Sil", mesaj, QMessageBox.Yes | QMessageBox.No)
        if yanit != QMessageBox.Yes:
            return
        if selected_row < len(self.existing_operations):
            from database_progress import delete_islem_by_id
            silinecek_islem = self.existing_operations[selected_row]
            delete_islem_by_id(silinecek_islem[0])
            del self.existing_operations[selected_row]
        else:
            idx = selected_row - len(self.existing_operations)
            if idx < len(self.pending_operations):
                del self.pending_operations[idx]
        self.tbl_islemler.removeRow(selected_row)

    def kaydi_sil(self):
        yanit = QMessageBox.question(
            self, "Onay", "Bu servisi ve tüm işlemlerini silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if yanit == QMessageBox.Yes:
            delete_service(self.servis_id)
            QMessageBox.information(self, "Başarılı", "Servis ve işlemleri silindi.")
            self.accept()

    def kaydet_servis(self):
        """Servis bilgilerini ve işlemleri kaydeder."""
        if not self.servis_id:
            QMessageBox.warning(self, "Uyarı", "Servis ID bulunamadı!")
            return

        # Servis bilgilerini güncelle
        cari_kodu = self.txt_cari_kodu.text().strip()
        plaka = self.txt_plaka.text().strip()
        aciklama = self.txt_aciklama.toPlainText().strip()
        arac_getiren_kisi = self.txt_arac_getiren.text().strip()

        # Gerekli alanların doldurulup doldurulmadığını kontrol et
        if not cari_kodu or not plaka:
            QMessageBox.warning(self, "Uyarı", "Lütfen cari kodu ve plaka bilgilerini doldurun!")
            return

        try:
            # Önce mevcut işlemleri sil
            from database_progress import delete_islem_by_id
            for islem in self.existing_operations:
                delete_islem_by_id(islem[0])
            self.existing_operations.clear()

            # Servis bilgilerini güncelle
            update_servis(self.servis_id, cari_kodu, plaka, aciklama, arac_getiren_kisi)

            # Yeni işlemleri ekle
            for row in range(self.tbl_islemler.rowCount()):
                islem_aciklama = self.tbl_islemler.item(row, 0).text()
                islem_tutari = float(self.tbl_islemler.item(row, 1).text())
                kdv_orani = float(self.tbl_islemler.item(row, 2).text())
                kdv_tutari = float(self.tbl_islemler.item(row, 3).text())
                miktar = int(self.tbl_islemler.item(row, 4).text())
                aciklama = self.tbl_islemler.item(row, 5).text()
                add_islem(self.servis_id, islem_aciklama, islem_tutari, kdv_orani, kdv_tutari, aciklama, miktar)

            QMessageBox.information(self, "Başarılı", "Servis başarıyla güncellendi.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Servis güncellenirken bir hata oluştu: {str(e)}")

    def pdf_aktar(self):
        if not self.servis_id:
            QMessageBox.warning(self, "Uyarı", "Önce bir servis kaydı yüklemelisiniz!")
            return

        try:
            # Servis detaylarını al
            from database_progress import get_service_full_details
            detaylar = get_service_full_details(self.servis_id)
            if not detaylar:
                QMessageBox.warning(self, "Uyarı", "Servis detayları bulunamadı!")
                return

            # Servis, cari ve araç bilgilerini al
            servis = detaylar["servis"]
            cari = detaylar["cari"]
            arac = detaylar["arac"]
            islemler = detaylar["islemler"]

            # İş emri numarasını 6 haneli formatta hazırla
            is_emri_no = f"{int(servis['id']):06d}"  # 6 haneli, başında sıfır olacak şekilde formatla

            # Toplam tutarları ve KDV'yi işlemlere göre hesapla
            toplam_kdv_haric = sum(islem['islem_tutari'] for islem in islemler)-sum(islem['kdv_tutari'] for islem in islemler)
            kdv_tutari_genel = sum(islem['kdv_tutari'] for islem in islemler) # Tüm işlemlerin KDV toplamı
            genel_toplam = toplam_kdv_haric + kdv_tutari_genel # Genel toplam = KDV hariç toplam + KDV

            # İşlemleri PDF için hazırla
            islem_texts = []
            y_start = 155  # 92.5 * 1.67
            line_height = 6  # 3.5 * 1.67

            # İşlemleri benzersiz olarak işle
            processed_operations = set()  # İşlenmiş işlemleri takip etmek için set
            for i, islem in enumerate(islemler, 1):
                # İşlem açıklaması ve miktarını birleştirerek benzersiz bir anahtar oluştur
                operation_key = f"{islem['islem_aciklama']}_{islem['miktar']}"
                
                # Eğer bu işlem daha önce işlenmediyse ekle
                if operation_key not in processed_operations:
                    processed_operations.add(operation_key)
                    islem_texts.extend([
                        (10, y_start - (i * line_height), str(i)),
                        (30, y_start - (i * line_height), f"{islem['islem_aciklama']} {islem['aciklama']}"),
                        (114.5, y_start - (i * line_height), f"{islem['islem_tutari'] / islem['miktar']:.2f}"),  # Birim fiyat = işlem tutarı / miktar
                        (136, y_start - (i * line_height), str(islem['miktar'])),  # Miktar bilgisini ekle
                        (148, y_start - (i * line_height), f"{islem['islem_tutari']:.2f}"),  # Toplam tutar
                        (170, y_start - (i * line_height), f"{islem['kdv_orani']:.1f}%"),  # KDV oranını yüzde olarak göster
                        (184, y_start - (i * line_height), f"{islem['islem_tutari']:.2f}")  # Toplam tutar
                    ])

            # Vergi numarası kontrolü
            vergi_no = cari.get('vergi_no', '')
            if vergi_no is None:
                vergi_no = ''

            # PDF için eklemeler sözlüğünü oluştur
            eklemeler = {
                'text': [
                    (159, 259.6, is_emri_no),  # İş emri numarası 6 haneli formatta
                    (90, 259.6, f"{servis['plaka']}"),
                ]
            }

            # Cari ad unvanını bölme mantığı
            cari_ad_unvan = cari.get('cari_ad_unvan', '')
            cari_ad_unvan_lines = self.split_cari_ad_unvan(cari_ad_unvan)

            # Her satırı PDF'e ekle (cari adı için font boyutu 8)
            for i, line in enumerate(cari_ad_unvan_lines):
                eklemeler['text'].append((45, 250 - (i * 5), line, 8))

            # Diğer bilgileri ekle (font 9)
            eklemeler['text'].extend([
                (50, 237, f"{cari.get('cep_telefonu', '')}", 9),
                (50, 232, f"{vergi_no}", 9),
                (50, 223, f"{arac.get('arac_tipi', '')}", 9),
                (50, 217.2, f"{arac.get('marka', '')} {arac.get('model', '')}", 9),
                (50, 211, f"{arac.get('model_yili', '')}", 9),
                (120, 223, f"{arac.get('sasi_no', 'XXXXXXXX')}", 9),
                (120, 218, f"{arac.get('motor_no', 'XXXXXX')}", 9),
                (58, 204, f"{servis['servis_tarihi']}", 9),
                (58, 192, f"{servis['servis_tarihi']}", 9),
                (25, 181, f"{servis.get('aciklama', '')}", 9),
                (175, 68, f"{toplam_kdv_haric:,.2f} TL", 9),
                (175, 63, f"{kdv_tutari_genel:,.2f} TL", 9),
                (175, 58, f"{genel_toplam:,.2f} TL", 9)
            ])

            # İşlemleri eklemeler listesine ekle (font 9)
            for item in islem_texts:
                if len(item) == 3:
                    eklemeler['text'].append((*item, 9))
                else:
                    eklemeler['text'].append(item)

            # Dosya kaydetme dialogunu göster
            default_filename = f"servis_{is_emri_no}_{servis['plaka']}_{servis['servis_tarihi']}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "PDF Dosyasını Kaydet",
                default_filename,
                "PDF Dosyaları (*.pdf)"
            )

            if file_path:
                # PDF'i oluştur
                mevcut_pdf_duzenle("classiccar.pdf", file_path, eklemeler, font_size=10)
                QMessageBox.information(self, "Başarılı", f"PDF dosyası oluşturuldu:\n{file_path}")
            else:
                QMessageBox.information(self, "Bilgi", "PDF oluşturma işlemi iptal edildi.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken bir hata oluştu:\n{str(e)}")

    def islem_ekle(self):
        """İşlem bilgilerini tabloya ekler."""
        # Formdaki bilgileri al
        islem_aciklama = self.input_islem_aciklama.text().strip()
        birim_fiyat = self.input_islem_tutar.text().strip()
        kdv_orani = self.input_islem_kdv.text().strip() or "20"  # Varsayılan KDV oranı
        aciklama = self.input_islem_ek_aciklama.text().strip()
        miktar = int(self.input_miktar.currentText())  # Seçilen miktarı al

        # Gerekli alanların doldurulup doldurulmadığını kontrol et
        if not islem_aciklama or not birim_fiyat:
            QMessageBox.warning(self, "Uyarı", "Lütfen gerekli alanları doldurun!")
            return

        try:
            # KDV oranını ve birim fiyatı float'a dönüştür
            kdv_orani = float(kdv_orani)
            birim_fiyat_float = float(birim_fiyat)  # Birim fiyat
            islem_tutari_float = birim_fiyat_float * miktar  # Toplam tutar = birim fiyat * miktar
            kdv_tutari = islem_tutari_float * kdv_orani / 100  # KDV tutarı = toplam tutar * KDV oranı

            # İşlemi tabloya ekle
            row_count = self.tbl_islemler.rowCount()
            self.tbl_islemler.insertRow(row_count)
            self.tbl_islemler.setItem(row_count, 0, QTableWidgetItem(islem_aciklama))
            self.tbl_islemler.setItem(row_count, 1, QTableWidgetItem(f"{islem_tutari_float:.2f}"))
            self.tbl_islemler.setItem(row_count, 2, QTableWidgetItem(f"{kdv_orani:.2f}"))
            self.tbl_islemler.setItem(row_count, 3, QTableWidgetItem(f"{kdv_tutari:.2f}"))
            self.tbl_islemler.setItem(row_count, 4, QTableWidgetItem(str(miktar)))
            self.tbl_islemler.setItem(row_count, 5, QTableWidgetItem(aciklama))

            # İşlem özetini güncelle
            self.guncelle_islem_ozeti()

            # Formu temizle
            self.input_islem_aciklama.clear()
            self.input_islem_tutar.clear()
            self.input_islem_kdv.clear()
            self.input_islem_ek_aciklama.clear()
            self.input_miktar.setCurrentIndex(0)  # Miktarı sıfırla

            print("İşlem başarıyla eklendi")
        except ValueError:
            QMessageBox.warning(self, "Hata", "Birim Fiyat ve KDV Oranı geçerli bir sayı olmalıdır!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {e}")

    def guncelle_islem_ozeti(self):
        """İşlem özetini günceller."""
        toplam_tutar = 0
        toplam_kdv = 0
        toplam_islem = self.tbl_islemler.rowCount()

        for row in range(toplam_islem):
            tutar_item = self.tbl_islemler.item(row, 1)
            kdv_tutari_item = self.tbl_islemler.item(row, 3)
            if tutar_item and tutar_item.text():
                toplam_tutar += float(tutar_item.text())
            if kdv_tutari_item and kdv_tutari_item.text():
                toplam_kdv += float(kdv_tutari_item.text())

        self.lbl_islem_sayisi.setText(f"Toplam İşlem Sayısı\n{toplam_islem}")
        self.lbl_islem_tutar.setText(f"Toplam İşlem Tutarı\n{toplam_tutar:.2f}")
        self.lbl_kdv_tutar.setText(f"Toplam KDV Tutarı\n{toplam_kdv:.2f}")

    # close_service.py dosyasından aktarılan satır bölme fonksiyonu
    def split_cari_ad_unvan(self, text, max_words=7, max_chars=40):
        words = text.split()
        lines = []
        line_words = []
        line_length = 0

        for word in words:
            line_words.append(word)
            line_length += len(word) + 1  # +1 boşluk için
            # Satırı bitirme koşulu: 7 kelime olduysa veya satır uzunluğu 40 karakteri geçtiyse
            if len(line_words) == max_words or line_length > max_chars:
                lines.append(' '.join(line_words))
                line_words = []
                line_length = 0

        if line_words:
            lines.append(' '.join(line_words))
        return lines

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ServiceUpdateForm()
    form.show()
    sys.exit(app.exec_())