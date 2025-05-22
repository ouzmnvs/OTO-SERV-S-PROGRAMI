from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
)
from qtawesome import icon

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