from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_cari_list  # Cari bilgilerini yüklemek için fonksiyonu içe aktarın

class CariListForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cari Listesi")
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.85)
        yukseklik = int(ekran.height() * 0.85)
        self.setFixedSize(genislik, yukseklik)
        x = (ekran.width() - genislik) // 2
        y = (ekran.height() - yukseklik) // 2 - 40
        if y < 0:
            y = 0
        self.move(x, y)
        self.init_ui()

    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(10)

        # Üst butonlar
        buton_layout = QHBoxLayout()
        buton_layout.setSpacing(10)
        buton_layout.addWidget(self.stil_buton("YENİ CARİ EKLE", 'fa5s.plus-circle', '#43a047'))
        buton_layout.addWidget(self.stil_buton("KAYDI DÜZENLE", 'fa5s.edit', '#0288d1'))
        buton_layout.addWidget(self.stil_buton("KAYDI SİL", 'fa5s.trash', '#b71c1c'))
        buton_layout.addWidget(self.stil_buton("SERVİS HAREKETLERİ", 'fa5s.exchange-alt', '#455a64'))
        buton_layout.addWidget(self.stil_buton("ÖDEME AL", 'fa5s.money-bill-wave', '#fbc02d'))
        buton_layout.addWidget(self.stil_buton("ÖDEME YAP", 'fa5s.wallet', '#ff9800'))
        buton_layout.addWidget(self.stil_buton("PDF AKTAR", 'fa5s.file-pdf', '#388e3c'))
        buton_layout.addStretch()
        btn_kapat = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')
        btn_kapat.clicked.connect(self.close)
        buton_layout.addWidget(btn_kapat)

        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(8)
        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı")
        self.filtre_input.setMinimumHeight(32)
        self.filtre_input.setStyleSheet("""
            font-size: 16px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            padding: 6px 12px;
            background: #fffbe8;
        """)
        filtre_layout.addWidget(self.filtre_input)

        self.filtre_combo = QComboBox()
        self.filtre_combo.setMinimumHeight(32)
        self.filtre_combo.setStyleSheet("""
            font-size: 16px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            padding: 4px 12px;
            background: #fffbe8;
        """)
        self.filtre_combo.addItems(["Cari Tipi *", "Müşteri", "Tedarikçi"])
        filtre_layout.addWidget(self.filtre_combo)

        btn_filtrele = QPushButton(icon('fa5s.search', color='#1976d2'), "Filtrele")
        btn_filtrele.setMinimumHeight(32)
        btn_filtrele.setStyleSheet("""
            font-size: 15px; font-weight: 700; background: #e3f2fd; border-radius: 6px; padding: 4px 18px;
        """)
        btn_temizle = QPushButton(icon('fa5s.sync', color='#fbc02d'), "Temizle")
        btn_temizle.setMinimumHeight(32)
        btn_temizle.setStyleSheet("""
            font-size: 15px; font-weight: 700; background: #fffde7; border-radius: 6px; padding: 4px 18px;
        """)
        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)
        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Cari Kodu", "Cari Adı / Ünvanı", "Telefon No", "Cari Tipi", "Toplam Tutar"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Cari Adı/Ünvanı geniş
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 15px;
                alternate-background-color: #f5f5f5;
                background: #fff;
            }
            QHeaderView::section {
                background: #ececec;
                font-weight: bold;
                font-size: 15px;
                border: 1px solid #bbb;
                padding: 6px;
            }
        """)

        ana_layout.addWidget(self.table)

        # Alt bilgi
        self.alt_bilgi = QLabel("")
        self.alt_bilgi.setStyleSheet("font-size: 14px; color: #444; padding: 6px 0 0 8px;")
        ana_layout.addWidget(self.alt_bilgi)

        self.setLayout(ana_layout)

        # Verileri yükle
        self.load_cari_list_to_table()

    def load_cari_list_to_table(self):
        """Veritabanından cari bilgilerini tabloya yükler."""
        cari_list = load_cari_list()  # Veritabanından tüm cari bilgilerini al
        self.table.setRowCount(len(cari_list))  # Tablo satır sayısını ayarla

        toplam_tutar = 0  # Toplam tutar hesaplamak için

        for row, (id, cari_kodu, cari_ad_unvan, cari_tipi, borc, tc_kimlik_no, vergi_no, cep_telefonu, toplam_tutar_cari) in enumerate(cari_list):
            # Tabloya gerekli alanları ekle
            self.table.setItem(row, 0, QTableWidgetItem(cari_kodu))
            self.table.setItem(row, 1, QTableWidgetItem(cari_ad_unvan))
            self.table.setItem(row, 2, QTableWidgetItem(cep_telefonu))
            self.table.setItem(row, 3, QTableWidgetItem(cari_tipi))
            self.table.setItem(row, 4, QTableWidgetItem(f"{toplam_tutar_cari:.2f}"))

            toplam_tutar += toplam_tutar_cari  # Toplam tutarı hesapla

        # Alt bilgi kısmını güncelle
        self.alt_bilgi.setText(
            f"{len(cari_list)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:.2f} TL"
        )

    def stil_buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(48)
        btn.setMinimumWidth(170)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                font-weight: 800;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                padding: 8px 18px;
            }}
            QPushButton:hover {{
                background: #e0e0e0;
            }}
        """)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return btn

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CariListForm()
    form.show()
    sys.exit(app.exec_())