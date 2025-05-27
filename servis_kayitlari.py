from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
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

    def load_servis_kayitlari(self):
        # Veritabanından servis kayıtlarını çek
        from database_progress import load_servis_kayitlari_by_plaka
        kayitlar = load_servis_kayitlari_by_plaka(self.plaka)
        self.table.setRowCount(len(kayitlar))
        toplam_tutar = 0
        for row, (tarih, tutar, durum) in enumerate(kayitlar):
            self.table.setItem(row, 0, QTableWidgetItem(tarih))
            self.table.setItem(row, 1, QTableWidgetItem(f"{tutar:,.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(durum))
            toplam_tutar += tutar
        self.lbl_alt.setText(f"{len(kayitlar)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:,.2f} TL")

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
                (170, y_baslangic - (i * satir_yuksekligi), "0.0%"),
                (184, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari']:.2f}")
            ])

        # PDF için eklemeler sözlüğünü oluştur
        eklemeler = {
            'text': [
                # Servis ve Cari Bilgileri
                (159, 260, is_emri_no),
                (90, 260, self.plaka),
                (43, 248, cari_bilgi.get('cari_ad_unvan', '')),
                (50, 236, cari_bilgi.get('cep_telefonu', '')),
                (50, 232, vergi_no),
                (50, 223, arac_bilgi.get('arac_tipi', '')),
                (50, 218, f"{arac_bilgi.get('marka', '')} {arac_bilgi.get('model', '')}"),
                (50, 211, str(arac_bilgi.get('model_yili', ''))),
                (120, 223, arac_bilgi.get('sasi_no', '')),
                (120, 218, arac_bilgi.get('motor_no', '')),
                (120, 212, servis_bilgi.get('servis_tarihi', '')),
                (58, 204, servis_bilgi.get('servis_tarihi', '')),
                (58, 191, servis_bilgi.get('servis_tarihi', '')),

                # Tutar Bilgileri
                (175, 68, f"{kdv_haric_toplam:,.2f} TL"),
                (175, 63, f"{kdv_tutari:,.2f} TL"),
                (175, 58, f"{toplam_tutar:,.2f} TL")
            ]
        }

        # İşlemleri eklemeler listesine ekle
        eklemeler['text'].extend(islem_texts)

        # PDF'i oluştur
        mevcut_pdf_duzenle("classiccar.pdf", dosya_yolu, eklemeler, font_size=6)
        QMessageBox.information(self, "Başarılı", "PDF başarıyla oluşturuldu.")