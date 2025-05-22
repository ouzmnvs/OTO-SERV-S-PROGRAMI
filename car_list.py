from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QDialog,QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_car_list
from add_car import AddCarForm  # En üste ekleyin
from servis_kayitlari import ServisKayitlariForm

class CarListForm(QDialog):
    def __init__(self, dashboard_ref=None):
        super().__init__()
        self.dashboard_ref = dashboard_ref  # Dashboard referansı
        self.setWindowTitle("Araç Listesi")
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.85)
        yukseklik = int(ekran.height() * 0.85)
        self.setFixedSize(genislik, yukseklik)
        # Ortalamak için:
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
        btn_yeni_arac = self.stil_buton("YENİ ARAÇ EKLE", 'fa5s.plus', '#1976d2')
        btn_yeni_arac.clicked.connect(self.yeni_arac_ekle_ac)  # <-- Bağlantı EKLENDİ
        buton_layout.addWidget(btn_yeni_arac)
        buton_layout.addWidget(self.stil_buton("KAYDI DÜZENLE", 'fa5s.edit', '#0288d1'))
        btn_sil = self.stil_buton("KAYDI SİL", 'fa5s.trash', '#b71c1c')
        btn_sil.clicked.connect(self.kaydi_sil_ac)
        buton_layout.addWidget(btn_sil)
        btn_servis_kayitlari = self.stil_buton("SERVİS KAYITLARI", 'fa5s.book', '#455a64')
        btn_servis_kayitlari.clicked.connect(self.servis_kayitlari_ac)
        buton_layout.addWidget(btn_servis_kayitlari)
        buton_layout.addWidget(self.stil_buton("PDF AKTAR", 'fa5s.file-pdf', '#388e3c'))
        buton_layout.addStretch()
        btn_kapat = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')
        btn_kapat.clicked.connect(self.sayfayi_kapat)
        buton_layout.addWidget(btn_kapat)

        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(8)
        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı veya Plaka")
        self.filtre_input.setMinimumHeight(32)
        self.filtre_input.setStyleSheet("""
            font-size: 16px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            padding: 6px 12px;
            background: #fffbe8;
        """)
        filtre_layout.addWidget(self.filtre_input)
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
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Cari Kodu", "Cari Adı / Ünvanı", "Araç Plakası", "Araç Tipi", "Model Yılı", "Marka", "Model"
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

        # Alt bilgi
        self.alt_bilgi = QLabel("")
        self.alt_bilgi.setStyleSheet("font-size: 14px; color: #444; padding: 6px 0 0 8px;")
        ana_layout.addWidget(self.alt_bilgi)

        self.setLayout(ana_layout)

    def load_data_to_table(self):
        data = load_car_list()
        self.table.setRowCount(len(data))
        for row, record in enumerate(data):
            for col, value in enumerate(record):
                self.table.setItem(row, col, QTableWidgetItem(str(value) if value is not None else ""))
        # self.alt_bilgi.setText(f"{len(data)} adet kayıt listeleniyor")

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

    def sayfayi_kapat(self):
        self.hide()
        if self.dashboard_ref:
            self.dashboard_ref.show()

    def yeni_arac_ekle_ac(self):
        def tabloyu_guncelle():
            self.load_data_to_table()
        self.add_car_form = AddCarForm(dashboard_ref=self, on_saved=tabloyu_guncelle)
        self.add_car_form.setWindowModality(Qt.ApplicationModal)
        self.add_car_form.setWindowFlag(Qt.Window)
        result = self.add_car_form.exec_()  # Modal olarak aç
        if result == QDialog.Accepted:
            self.load_data_to_table()

    def servis_kayitlari_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir araç seçin!")
            return
        cari_ad = self.table.item(selected_row, 1).text()
        plaka = self.table.item(selected_row, 2).text()
        arac_tipi = self.table.item(selected_row, 3).text()
        model_yili = self.table.item(selected_row, 4).text()
        marka = self.table.item(selected_row, 5).text()
        model = self.table.item(selected_row, 6).text()
        form = ServisKayitlariForm(cari_ad, plaka, arac_tipi, model_yili, marka, model, self)
        form.exec_()

    def kaydi_sil_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir araç seçin!")
            return

        plaka = self.table.item(selected_row, 2).text()
        cari_ad = self.table.item(selected_row, 1).text()
        marka = self.table.item(selected_row, 5).text()
        model = self.table.item(selected_row, 6).text()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Kaydı Sil")
        msg.setText(
            f"Araç Plakası: {plaka}\n"
            f"Cari Adı: {cari_ad}\n"
            f"Marka/Model: {marka} {model}\n\n"
            "Bu aracı silmek istediğinize emin misiniz?"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        sonuc = msg.exec_()

        if sonuc == QMessageBox.Yes:
            import sqlite3
            try:
                conn = sqlite3.connect("oto_servis.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM araclar WHERE plaka = ?", (plaka,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Başarılı", "Araç kaydı silindi.")
                self.load_data_to_table()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Silme işlemi sırasında hata oluştu:\n{e}")

# Dashboard'dan açarken:
# self.car_list_form = CarListForm(self)
# self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CarListForm()
    form.show()
    sys.exit(app.exec_())