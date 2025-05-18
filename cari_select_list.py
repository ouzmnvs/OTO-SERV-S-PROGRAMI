from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_cari_list  # Veritabanı fonksiyonunu içe aktar

class CariSelectListForm(QWidget):
    def __init__(self, parent_form=None):
        super().__init__()
        self.parent_form = parent_form  # AddCarForm referansı
        self.setWindowTitle("Cari Listesi")
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.28)
        yukseklik = int(ekran.height() * 0.55)
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
        btn_aktar = self.stil_buton("Bilgileri Aktar", 'fa5s.mouse-pointer', '#1976d2')
        btn_aktar.clicked.connect(self.bilgileri_aktar)
        btn_iptal = self.stil_buton("İptal", 'fa5s.times', '#b71c1c')
        btn_yeni = self.stil_buton("Yeni Ekle", 'fa5s.plus-circle', '#43a047')
        buton_layout.addWidget(btn_aktar)
        buton_layout.addWidget(btn_iptal)
        buton_layout.addWidget(btn_yeni)
        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(8)
        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Adı / Ünvanı")
        self.filtre_input.setMinimumHeight(32)
        self.filtre_input.setStyleSheet("""
            font-size: 16px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            padding: 6px 12px;
            background: #fffbe8;
        """)
        filtre_layout.addWidget(self.filtre_input)
        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = QTableWidget(0, 2)  # Satır sayısını 0 olarak başlat
        self.table.setHorizontalHeaderLabels([
            "Cari Kodu", "Cari Adı / Ünvanı"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

        # Veritabanından verileri yükle
        self.load_data_to_table()

        ana_layout.addWidget(self.table)
        self.setLayout(ana_layout)

    def load_data_to_table(self):
        """Veritabanından gelen verileri tabloya yükler."""
        cariler = load_cari_list()  # Veritabanından verileri al
        print(cariler)
        self.table.setRowCount(len(cariler))  # Satır sayısını ayarla
        for row, (id,cari_kodu, cari_unvani,telefon,cari_tipi,borc) in enumerate(cariler):
            self.table.setItem(row, 0, QTableWidgetItem(cari_kodu))
            self.table.setItem(row, 1, QTableWidgetItem(cari_unvani))

    def stil_buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(44)
        btn.setMinimumWidth(140)
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

    def bilgileri_aktar(self):
        secili_satir = self.table.currentRow()
        if secili_satir >= 0 and self.parent_form:
            cari_kodu = self.table.item(secili_satir, 0).text()
            cari_unvani = self.table.item(secili_satir, 1).text()
            self.parent_form.set_cari_bilgileri(cari_kodu, cari_unvani)
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CariSelectListForm()
    form.show()
    sys.exit(app.exec_())