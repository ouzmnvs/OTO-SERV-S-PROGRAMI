from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QLineEdit
)
from qtawesome import icon
from PyQt5.QtCore import Qt

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
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Tarih", "Tutar", "Durum", "Açıklama"])
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
        for row, (servis_id, tarih, tutar, durum, aciklama) in enumerate(kayitlar):
            item_tarih = QTableWidgetItem(tarih)
            item_tarih.setData(Qt.UserRole, servis_id)
            self.table.setItem(row, 0, item_tarih)
            self.table.setItem(row, 1, QTableWidgetItem(f"{tutar:,.2f} TL"))
            self.table.setItem(row, 2, QTableWidgetItem(durum))
            self.table.setItem(row, 3, QTableWidgetItem(aciklama))
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
        from PyQt5.QtWidgets import QMessageBox
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        # servis_id'yi doğrudan Qt.UserRole'dan al
        item = self.table.item(selected_row, 0)
        if not item or not item.data(Qt.UserRole):
            QMessageBox.warning(self, "Uyarı", "Servis ID bulunamadı!")
            return

        from pdf_aktar import servis_pdf_aktar
        servis_pdf_aktar(self, item.data(Qt.UserRole), varsayilan="is_emri")