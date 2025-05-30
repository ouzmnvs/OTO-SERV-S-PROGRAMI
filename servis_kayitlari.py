from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QLineEdit
)
from qtawesome import icon
from pdf_oluşturucu import mevcut_pdf_duzenle

class ServisKayitlariForm(QDialog):
    def __init__(self, cari_ad, plaka, arac_tipi, model_yili, marka, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Servis Kayıtları")
        self.setFixedSize(700, 500)
        self.cari_ad = cari_ad
        self.plaka = plaka
        self.arac_tipi = arac_tipi
        self.model_yili = model_yili
        self.marka = marka
        self.model = model
        self.init_ui()

    def init_ui(self):
        ana_layout = QVBoxLayout()

        # Üst butonlar
        buton_layout = QHBoxLayout()
        btn_detay = QPushButton(icon('fa5s.file-alt', color='#1976d2'), "DETAY GÖRÜNTÜLE")
        btn_detay.clicked.connect(self.detay_goruntule)
        btn_kapat = QPushButton(icon('fa5s.times', color='#b71c1c'), "SAYFAYI KAPAT")
        btn_kapat.clicked.connect(self.close)
        buton_layout.addWidget(btn_detay)
        buton_layout.addStretch()
        buton_layout.addWidget(btn_kapat)
        ana_layout.addLayout(buton_layout)

        # Araç Bilgileri
        arac_group = QGroupBox("Araç Bilgileri")
        arac_layout = QHBoxLayout()
        arac_layout.addLayout(self._label_value("Cari Adı", self.cari_ad))
        arac_layout.addLayout(self._label_value("Araç Tipi", self.arac_tipi))
        arac_layout.addLayout(self._label_value("Marka", self.marka))
        arac_layout.addLayout(self._label_value("Plaka", self.plaka))
        arac_layout.addLayout(self._label_value("Model Yılı", str(self.model_yili)))
        arac_layout.addLayout(self._label_value("Model", self.model))
        arac_group.setLayout(arac_layout)
        ana_layout.addWidget(arac_group)

        # Arama alanı
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Servis kayıtlarında ara...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)
        ana_layout.addLayout(search_layout)

        # Servis Kayıtları Tablosu
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Tarih", "Tutar", "Durum"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        ana_layout.addWidget(self.table)

        # Alt bilgi
        self.lbl_alt = QLabel("")
        self.lbl_alt.setStyleSheet("font-size: 14px; color: #444; padding: 6px 0 0 8px;")
        ana_layout.addWidget(self.lbl_alt)

        self.setLayout(ana_layout)
        self.load_servis_kayitlari()

    def _label_value(self, label, value):
        layout = QVBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("font-weight: bold;")
        val = QLabel(str(value))
        val.setStyleSheet("background: #f5f5f5; border: 1px solid #ccc; border-radius: 4px; padding: 4px 8px;")
        layout.addWidget(lbl)
        layout.addWidget(val)
        return layout

    def on_search_text_changed(self, text):
        """Arama metni değiştiğinde servis kayıtlarını filtrele"""
        self.load_servis_kayitlari(text)

    def load_servis_kayitlari(self, search_text=None):
        # Veritabanından servis kayıtlarını çek
        from database_progress import load_servis_kayitlari_by_plaka
        kayitlar = load_servis_kayitlari_by_plaka(self.plaka, search_text)
        self.table.setRowCount(len(kayitlar))
        toplam_tutar = 0
        for row, (tarih, tutar, durum, aciklama) in enumerate(kayitlar):
            self.table.setItem(row, 0, QTableWidgetItem(tarih))
            self.table.setItem(row, 1, QTableWidgetItem(f"{tutar:,.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(durum))
            toplam_tutar += tutar
        self.lbl_alt.setText(f"{len(kayitlar)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:,.2f} TL")

    def split_cari_ad_unvan(self, text, max_words=7, max_chars=40):
        """Split customer name into lines for PDF display."""
        words = text.split()
        lines = []
        line_words = []
        line_length = 0

        for word in words:
            line_words.append(word)
            line_length += len(word) + 1
            if len(line_words) == max_words or line_length > max_chars:
                lines.append(' '.join(line_words))
                line_words = []
                line_length = 0

        if line_words:
            lines.append(' '.join(line_words))
        return lines

    def detay_goruntule(self):
        from PyQt5.QtWidgets import QMessageBox, QFileDialog
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        servis_tarihi = self.table.item(selected_row, 0).text()
        from database_progress import get_service_full_details
        import sqlite3
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM servisler WHERE plaka=? AND servis_tarihi=?", (self.plaka, servis_tarihi))
        row = cursor.fetchone()
        conn.close()
        if not row:
            QMessageBox.warning(self, "Uyarı", "Servis kaydı bulunamadı!")
            return
        servis_id = row[0]

        # Tüm servis detaylarını tek seferde al
        detaylar = get_service_full_details(servis_id)
        if not detaylar:
            QMessageBox.warning(self, "Uyarı", "Servis detayları alınamadı!")
            return

        # Detayları ayrıştır
        servis_bilgi = detaylar["servis"]
        cari_bilgi = detaylar["cari"]
        arac_bilgi = detaylar["arac"]
        islem_listesi = detaylar["islemler"]

        # Vergi numarası kontrolü ekleyelim
        vergi_no = cari_bilgi.get('vergi_no', '')
        if vergi_no is None:
            vergi_no = ''

        # İş emri numarasını 6 haneli formatta hazırla
        is_emri_no = f"{servis_id:06d}"  # 6 haneli, başında sıfır olacak şekilde formatla

        # Dosya adını daha anlamlı hale getir
        default_filename = f"servis_{is_emri_no}_{self.plaka}_{servis_tarihi}.pdf"
        dosya_yolu, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", default_filename, "PDF Files (*.pdf)")
        if not dosya_yolu:
            return

        # İşlemleri PDF için hazırla
        islem_texts = []
        y_baslangic = 152.5
        satir_yuksekligi = 3.7

        # İşlemleri PDF için hazırla
        for i, islem in enumerate(islem_listesi, 1):
            islem_texts.extend([
                (10, y_baslangic - (i * satir_yuksekligi), str(i), 7.5),
                (30, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_aciklama']} {islem['aciklama']}", 7.5),
                (114.5, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari'] / islem['miktar']:.2f}", 7.5),
                (136, y_baslangic - (i * satir_yuksekligi), str(islem['miktar']), 7.5),
                (148, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari']:.2f}", 7.5),
                (170, y_baslangic - (i * satir_yuksekligi), "0.0%", 7.5),
                (184, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari']:.2f}", 7.5)
            ])

        # Cari ad unvanını böl
        cari_ad_unvan = cari_bilgi.get('cari_ad_unvan', '')
        cari_ad_unvan_lines = self.split_cari_ad_unvan(cari_ad_unvan)

        # PDF için eklemeler sözlüğünü oluştur
        eklemeler = {
            'text': [
                # Servis ve Cari Bilgileri
                (159, 260, is_emri_no, 9),
                (90, 259.6, self.plaka, 9),
                (50, 237, cari_bilgi.get('cep_telefonu', ''), 9),
                (50, 232, vergi_no, 9),
                (50, 223, arac_bilgi.get('arac_tipi', ''), 9),
                (50, 218, f"{arac_bilgi.get('marka', '')} {arac_bilgi.get('model', '')}", 9),
                (50, 211, str(arac_bilgi.get('model_yili', '')), 9),
                (120, 223, arac_bilgi.get('sasi_no', ''), 9),
                (120, 218, arac_bilgi.get('motor_no', ''), 9),
                (58, 204.5, servis_bilgi.get('servis_tarihi', ''), 9),
                (58, 191.5, servis_bilgi.get('servis_tarihi', ''), 9),
                (25, 181, servis_bilgi.get('aciklama', ''), 9),

                # Tutar Bilgileri - Updated calculations to match open_service.py
                (175, 68, f"{sum(islem['islem_tutari'] for islem in islem_listesi) - sum(islem['kdv_tutari'] for islem in islem_listesi):,.2f} TL", 9),
                (175, 63, f"{sum(islem['kdv_tutari'] for islem in islem_listesi):,.2f} TL", 9),
                (175, 58, f"{sum(islem['islem_tutari'] for islem in islem_listesi):,.2f} TL", 9)
            ]
        }

        # Her satırı PDF'e ekle (cari adı için font boyutu 7.5)
        for i, line in enumerate(cari_ad_unvan_lines):
            eklemeler['text'].append((45, 250 - (i * 5), line, 7.5))

        # İşlemleri eklemeler listesine ekle
        eklemeler['text'].extend(islem_texts)

        # PDF'i oluştur
        mevcut_pdf_duzenle("classiccar.pdf", dosya_yolu, eklemeler, font_size=9)
        QMessageBox.information(self, "Başarılı", "PDF başarıyla oluşturuldu.")