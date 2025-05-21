from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_cari_list  # Veritabanı fonksiyonunu içe aktar
from add_cari import AddCariForm  # Satırın başına ekleyin

class CariSelectListForm(QDialog):  # QWidget yerine QDialog kullanıyoruz
    def __init__(self, parent_form=None):
        super().__init__(parent_form)
        self.parent_form = parent_form  # AddCarForm veya ServisForm referansı
        self.setWindowTitle("Cari Seçim Listesi")
        self.setModal(True)  # Modal olarak ayarla
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.40)
        yukseklik = int(ekran.height() * 0.60)
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
        btn_yeni.clicked.connect(self.yeni_cari_ekle_ac)  # <-- Bu satırı ekleyin
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
        self.table = QTableWidget(0, 4)  # 4 sütun: Cari Kodu, Cari Ünvanı, Telefon, Cari Tipi
        self.table.setHorizontalHeaderLabels([
            "Cari Kodu", "Cari Adı / Ünvanı", "Telefon", "Cari Tipi"
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
        self.table.setRowCount(len(cariler))  # Satır sayısını ayarla

        for row, cari in enumerate(cariler):
            # Sadece gerekli sütunları al
            cari_kodu = cari[1]
            cari_ad_unvan = cari[2]
            cep_telefonu = cari[7]
            cari_tipi = cari[3]

            # Tabloya ekle
            self.table.setItem(row, 0, QTableWidgetItem(cari_kodu))
            self.table.setItem(row, 1, QTableWidgetItem(cari_ad_unvan))
            self.table.setItem(row, 2, QTableWidgetItem(cep_telefonu))
            self.table.setItem(row, 3, QTableWidgetItem(cari_tipi))

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
            telefon = self.table.item(secili_satir, 2).text()
            cari_tipi = self.table.item(secili_satir, 3).text()

            # Parent formun türüne göre bilgileri aktar
            if hasattr(self.parent_form, 'set_cari_bilgileri'):
                self.parent_form.set_cari_bilgileri(cari_kodu, cari_unvani, telefon, cari_tipi)
            self.close()

    def yeni_cari_ekle_ac(self):
        def tabloyu_guncelle():
            self.load_data_to_table()
        self.add_cari_form = AddCariForm(on_saved=tabloyu_guncelle)
        self.add_cari_form.setWindowModality(Qt.ApplicationModal)
        self.add_cari_form.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CariSelectListForm()
    form.show()
    sys.exit(app.exec_())