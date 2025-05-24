from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QMessageBox
)
from qtawesome import icon
from database_progress import load_cari_arac_servis_bilgileri

class CariServisHareketleriForm(QDialog):
    def __init__(self, cari_kodu, cari_ad, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Servis Hareketleri - {cari_ad}")
        self.setFixedSize(900, 600)
        self.cari_kodu = cari_kodu
        self.cari_ad = cari_ad
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Üst bilgi
        info_layout = QHBoxLayout()
        lbl_cari = QLabel(f"Cari: {self.cari_ad}")
        lbl_cari.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(lbl_cari)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Plaka", "Araç Tipi", "Model Yılı", "Marka", "Model", 
            "Servis Sayısı", "Toplam Servis Tutarı"
        ])
        
        # Sütun genişliklerini ayarla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setDefaultSectionSize(120)
        header.resizeSection(0, 100)  # Plaka
        header.resizeSection(1, 100)  # Araç Tipi
        header.resizeSection(2, 80)   # Model Yılı
        header.resizeSection(3, 120)  # Marka
        header.resizeSection(4, 120)  # Model
        header.resizeSection(5, 100)  # Servis Sayısı
        header.resizeSection(6, 150)  # Toplam Tutar

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                alternate-background-color: #f5f5f5;
                background: #fff;
            }
            QHeaderView::section {
                background: #ececec;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #bbb;
                padding: 8px;
            }
        """)
        layout.addWidget(self.table)

        # Alt bilgi
        self.lbl_alt = QLabel()
        self.lbl_alt.setStyleSheet("font-size: 14px; color: #444; padding: 8px;")
        layout.addWidget(self.lbl_alt)

        # Butonlar
        btn_layout = QHBoxLayout()
        
        # Servisleri Görüntüle butonu
        btn_servisler = QPushButton(icon('fa5s.file-alt', color='#1976d2'), "SERVİSLERİ GÖRÜNTÜLE")
        btn_servisler.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """)
        btn_servisler.clicked.connect(self.servisleri_goruntule)
        btn_layout.addWidget(btn_servisler)
        
        btn_layout.addStretch()
        
        # Kapat butonu
        btn_kapat = QPushButton(icon('fa5s.times', color='#b71c1c'), "KAPAT")
        btn_kapat.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """)
        btn_kapat.clicked.connect(self.close)
        btn_layout.addWidget(btn_kapat)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        # Verileri yükle
        data = load_cari_arac_servis_bilgileri(self.cari_kodu)
        self.table.setRowCount(len(data))

        toplam_servis_sayisi = 0
        toplam_servis_tutari = 0

        for row, (plaka, arac_tipi, model_yili, marka, model, servis_sayisi, toplam_tutar) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(plaka))
            self.table.setItem(row, 1, QTableWidgetItem(arac_tipi))
            self.table.setItem(row, 2, QTableWidgetItem(str(model_yili)))
            self.table.setItem(row, 3, QTableWidgetItem(marka))
            self.table.setItem(row, 4, QTableWidgetItem(model))
            self.table.setItem(row, 5, QTableWidgetItem(str(servis_sayisi)))
            self.table.setItem(row, 6, QTableWidgetItem(f"{toplam_tutar:,.2f} TL"))

            toplam_servis_sayisi += servis_sayisi
            toplam_servis_tutari += toplam_tutar

        # Alt bilgiyi güncelle
        self.lbl_alt.setText(
            f"Toplam {len(data)} araç | "
            f"Toplam {toplam_servis_sayisi} servis | "
            f"Toplam Tutar: {toplam_servis_tutari:,.2f} TL"
        )

    def servisleri_goruntule(self):
        """Seçili araca ait servis kayıtlarını gösterir"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir araç seçin!")
            return

        # Seçili araç bilgilerini al
        plaka = self.table.item(selected_row, 0).text()
        arac_tipi = self.table.item(selected_row, 1).text()
        
        # Model yılı kontrolü
        model_yili_text = self.table.item(selected_row, 2).text()
        try:
            model_yili = int(model_yili_text) if model_yili_text else 0
        except ValueError:
            model_yili = 0
        
        marka = self.table.item(selected_row, 3).text()
        model = self.table.item(selected_row, 4).text()

        # Servis kayıtları formunu aç
        from servis_kayitlari import ServisKayitlariForm
        servis_form = ServisKayitlariForm(
            self.cari_ad,
            plaka,
            arac_tipi,
            model_yili,
            marka,
            model,
            self
        )
        servis_form.exec_()