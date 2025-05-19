from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_car_list  
# from servis_form import ServisForm  
# from add_car import AddCarForm  
class CarSelectListForm(QWidget):
    def __init__(self, parent_form=None):
        super().__init__()
        self.parent_form = parent_form  # Parent form referansı
        self.setWindowTitle("Araç Listesi")
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
        btn_iptal.clicked.connect(self.close)
        btn_yeni = self.stil_buton("Yeni Ekle", 'fa5s.plus-circle', '#43a047')
        buton_layout.addWidget(btn_aktar)
        buton_layout.addWidget(btn_iptal)
        buton_layout.addWidget(btn_yeni)
        ana_layout.addLayout(buton_layout)

        # Tablo
        self.table = QTableWidget(0, 5)  # Satır sayısını 0 olarak başlat
        self.table.setHorizontalHeaderLabels([
            "Araç Plakası", "Araç Tipi", "Model Yılı", "Marka", "Model"
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
        araclar = load_car_list()  # Veritabanından verileri al
        self.table.setRowCount(len(araclar))  # Satır sayısını ayarla
        for row, (cari_kodu, cari_unvan, plaka, arac_tipi, model_yili, marka, model) in enumerate(araclar):
            self.table.setItem(row, 0, QTableWidgetItem(plaka))
            self.table.setItem(row, 1, QTableWidgetItem(arac_tipi))
            self.table.setItem(row, 2, QTableWidgetItem(str(model_yili)))
            self.table.setItem(row, 3, QTableWidgetItem(marka))
            self.table.setItem(row, 4, QTableWidgetItem(model))

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
            plaka = self.table.item(secili_satir, 0).text()
            arac_tipi = self.table.item(secili_satir, 1).text()
            model_yili = self.table.item(secili_satir, 2).text()
            marka = self.table.item(secili_satir, 3).text()
            model = self.table.item(secili_satir, 4).text()
            # Parent formda bir set_arac_bilgileri metodu varsa çağır
            if hasattr(self.parent_form, 'set_arac_bilgileri'):
                self.parent_form.set_arac_bilgileri(plaka, arac_tipi, model_yili, marka, model)
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CarSelectListForm()
    form.show()
    sys.exit(app.exec_())