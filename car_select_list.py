from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
   QDesktopWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_car_list_by_cari  # Cari koduna göre araçları yüklemek için fonksiyonu içe aktarın
from add_car import AddCarForm  # En üste ekle

class CarSelectListForm(QDialog):  # QWidget yerine QDialog kullanıyoruz
    def __init__(self, parent_form=None, cari_kodu=None):
        super().__init__(parent_form)  # Set parent form
        self.parent_form = parent_form
        self.cari_kodu = cari_kodu
        self.setWindowTitle("Araç Seçimi")
        
        # Set window flags for modal dialog
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        
        # Set fixed size for smaller dialog
        self.setFixedSize(800, 600)
        
        # Center the dialog relative to parent
        if parent_form:
            parent_geometry = parent_form.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        
        self.setModal(True)  # Modal olarak ayarla
        self.init_ui()
        self.setWindowIcon(icon('fa5s.file')) # Add a file icon

    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(10)

        # Üst butonlar
        buton_layout = QHBoxLayout()
        buton_layout.setSpacing(10)
        btn_aktar = self.stil_buton("Bilgileri Aktar", 'fa5s.mouse-pointer', '#1976d2')
        btn_aktar.clicked.connect(self.bilgileri_aktar)
        btn_yeni_arac = self.stil_buton("Yeni Araç", 'fa5s.car', '#388e3c')  # Yeni Araç butonu
        btn_yeni_arac.clicked.connect(self.yeni_arac_ekle)
        btn_iptal = self.stil_buton("İptal", 'fa5s.times', '#b71c1c')
        btn_iptal.clicked.connect(self.close)
        buton_layout.addWidget(btn_aktar)
        buton_layout.addWidget(btn_yeni_arac)
        buton_layout.addWidget(btn_iptal)
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

        # Veritabanından verileri yükle
        self.load_data_to_table()

        ana_layout.addWidget(self.table)
        self.setLayout(ana_layout)

    def load_data_to_table(self):
        """Veritabanından gelen verileri tabloya yükler."""
        if not self.cari_kodu:
            QMessageBox.warning(self, "Uyarı", "Cari kodu bulunamadı!")
            return

        araclar = load_car_list_by_cari(self.cari_kodu)  # Cari koduna göre araçları yükle
        self.table.setRowCount(len(araclar))  # Satır sayısını ayarla
        for row, (plaka, arac_tipi, model_yili, marka, model) in enumerate(araclar):
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
                font-size: 13px;
                font-weight: 700;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 4px;
                padding: 6px 12px;
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

    def yeni_arac_ekle(self):
        # Yeni araç ekleme formunu aç
        form = AddCarForm(cari_kodu=self.cari_kodu, parent=self)
        result = form.exec_()
        if result == QDialog.Accepted:
            self.load_data_to_table()  # Başarılıysa tabloyu güncelle

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CarSelectListForm()
    form.show()
    sys.exit(app.exec_())