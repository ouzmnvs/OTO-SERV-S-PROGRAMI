from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
   QDesktopWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_cari_list_for_select  # Veritabanı fonksiyonunu içe aktar
from hizli_tablo import HizliTablo
from add_cari import AddCariForm  # Satırın başına ekleyin

class CariSelectListForm(QDialog):  # QWidget yerine QDialog kullanıyoruz
    def __init__(self, parent_form=None):
        super().__init__(parent_form)  # Set parent form
        self.parent_form = parent_form
        self.setWindowTitle("Cari Seçimi")
        
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
        btn_iptal = self.stil_buton("İptal", 'fa5s.times', '#b71c1c')
        btn_iptal.clicked.connect(self.reject)  # Modalı kapatır
        btn_yeni = self.stil_buton("Yeni Ekle", 'fa5s.plus-circle', '#43a047')
        btn_yeni.clicked.connect(self.yeni_cari_ekle_ac)
        buton_layout.addWidget(btn_aktar)
        buton_layout.addWidget(btn_iptal)
        buton_layout.addWidget(btn_yeni)
        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(8)
        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı / Ünvanı veya Telefon ile ara...")
        self.filtre_input.textChanged.connect(self.filtrele)
        self.filtre_input.setMinimumHeight(32)
        self.filtre_input.setStyleSheet("""
            font-size: 13px;
            border: 1.5px solid #bbb;
            border-radius: 4px;
            padding: 4px 8px;
            background: #fffbe8;
        """)
        filtre_layout.addWidget(self.filtre_input)
        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = HizliTablo()  # 4 sütun: Cari Kodu, Cari Ünvanı, Telefon, Cari Tipi
        self.table.setHorizontalHeaderLabels([
            "Cari Kodu", "Cari Adı / Ünvanı", "Telefon", "Cari Tipi"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableView {
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
        # (cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi)
        self.table.kayitlari_yukle(load_cari_list_for_select(), hucreler=lambda cari: cari[:4])
        self.filtrele()  # Yeni cari eklendikten sonra yenilemede arama korunur

    def filtrele(self):
        """Arama kutusuna yazılana göre listeyi süzer (Türkçe harf duyarsız)."""
        self.table.filtrele(self.filtre_input.text())

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
            cari_kodu = self.table.item(secili_satir, 0).text()
            cari_unvani = self.table.item(secili_satir, 1).text()
            telefon = self.table.item(secili_satir, 2).text()
            cari_tipi = self.table.item(secili_satir, 3).text()

            # Parent formun türüne göre bilgileri aktar
            if hasattr(self.parent_form, 'set_cari_bilgileri'):
                self.parent_form.set_cari_bilgileri(cari_kodu, cari_unvani, telefon, cari_tipi)
            self.close()

    def yeni_cari_ekle_ac(self):
        dialog = AddCariForm()
        dialog.setWindowModality(Qt.ApplicationModal)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data_to_table()  # Başarıyla eklenirse tabloyu güncelle

if __name__ == "__main__": 
    app = QApplication(sys.argv)
    form = CariSelectListForm()
    form.show()
    sys.exit(app.exec_())