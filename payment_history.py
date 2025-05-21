from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QDateEdit,
    QDesktopWidget, QFrame
)
from PyQt5.QtCore import Qt, QSize, QDate
from qtawesome import icon
import sys
import sqlite3

class PaymentHistoryForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ödeme Geçmişi")
        self.resize_and_center()
        self.init_ui()

    def resize_and_center(self):
        screen = QDesktopWidget().screenGeometry()
        width = int(screen.width() * 0.86)
        height = int(screen.height() * 0.86)
        self.setFixedSize(width, height)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2 - 40
        self.move(x, y)

    def stil_buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(80)
        btn.setMinimumWidth(80)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                font-weight: bold;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 6px;
                padding: 8px 18px;
            }}
            QPushButton:hover {{
                background: #e0e0e0;
            }}
        """)
        return btn

    def init_ui(self):
        ana_layout = QVBoxLayout()
        
        # Üst butonlar
        ust_butonlar = QHBoxLayout()
        ust_butonlar.setSpacing(10)

        btn_kaydi_duzenle = self.stil_buton("KAYDI DÜZENLE", "fa5s.edit", "#0288d1")
        btn_kaydi_sil = self.stil_buton("KAYDI SİL", "fa5s.trash", "#f44336")
        btn_detay = self.stil_buton("DETAY GÖRÜNTÜLE", "fa5s.info-circle", "#455a64")
        btn_pdf = self.stil_buton("PDF AKTAR", "fa5s.file-pdf", "#43a047")
        btn_kapat = self.stil_buton("SAYFAYI KAPAT", "fa5s.times", "#b71c1c")

        ust_butonlar.addWidget(btn_kaydi_duzenle)
        ust_butonlar.addWidget(btn_kaydi_sil)
        ust_butonlar.addWidget(btn_detay)
        ust_butonlar.addWidget(btn_pdf)
        ust_butonlar.addWidget(btn_kapat)

        ana_layout.addLayout(ust_butonlar)

        # Filtre alanı
        filtre_frame = QFrame()
        filtre_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bbb;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        filtre_layout = QHBoxLayout(filtre_frame)

        self.cari_filtre = QLineEdit()
        self.cari_filtre.setPlaceholderText("Cari Kodu, Cari Adı, Plaka veya Telefon")
        self.cari_filtre.setStyleSheet("""
            font-size: 16px;
            padding: 8px 12px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            background: #fffbe8;
        """)
        filtre_layout.addWidget(self.cari_filtre)

        self.baslangic_tarihi = QDateEdit()
        self.baslangic_tarihi.setDate(QDate.currentDate())
        self.baslangic_tarihi.setCalendarPopup(True)
        self.baslangic_tarihi.setDisplayFormat("dd.MM.yyyy")
        self.baslangic_tarihi.setFixedSize(150, 40)
        self.baslangic_tarihi.setStyleSheet("""
            QDateEdit {
                font-size: 16px;
                padding: 6px 10px;
                border: 1.5px solid #bbb;
                border-radius: 6px;
                background: #fff;
            }
            QDateEdit::drop-down {
                width: 30px;
            }
        """)
        filtre_layout.addWidget(self.baslangic_tarihi)

        self.bitis_tarihi = QDateEdit()
        self.bitis_tarihi.setDate(self.baslangic_tarihi.date().addDays(7))
        self.bitis_tarihi.setCalendarPopup(True)
        self.bitis_tarihi.setDisplayFormat("dd.MM.yyyy")
        self.bitis_tarihi.setFixedSize(150, 40)
        self.bitis_tarihi.setStyleSheet("""
            QDateEdit {
                font-size: 16px;
                padding: 6px 10px;
                border: 1.5px solid #bbb;
                border-radius: 6px;
                background: #fff;
            }
            QDateEdit::drop-down {
                width: 30px;
            }
        """)
        filtre_layout.addWidget(self.bitis_tarihi)

        for dateedit in [self.baslangic_tarihi, self.bitis_tarihi]:
            takvim = dateedit.calendarWidget()
            takvim.setFixedSize(440, 325)
            takvim.setStyleSheet("""
                QCalendarWidget QWidget {
                    alternate-background-color: #f6f6f6;
                }
                QCalendarWidget QToolButton {
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    background: #1976d2;
                    border: none;
                    margin: 2px;
                    padding: 6px 0;
                    border-radius: 4px;
                }
                QCalendarWidget QToolButton:hover {
                    background-color: #1565c0;
                }
                QCalendarWidget QToolButton#qt_calendar_prevmonth,
                QCalendarWidget QToolButton#qt_calendar_nextmonth {
                    font-size: 18px;
                    color: #1976d2;
                    background: transparent;
                }
                QCalendarWidget QToolButton::menu-indicator {
                    image: none;
                }
                QCalendarWidget QTableView {
                    font-size: 20px;
                    font-weight: bold;
                    color: #222;
                    background-color: #fff;
                    selection-background-color: #1976d2;
                    selection-color: white;
                    gridline-color: #e0e0e0;
                }
                QCalendarWidget QTableView::item {
                    padding: 28px 0px;
                    min-width: 70px;
                    min-height: 60px;
                }
                QCalendarWidget QHeaderView::section {
                    background-color: #f0f0f0;
                    color: #1976d2;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 16px 0;
                }
                QCalendarWidget QWidget#qt_calendar_navigationbar { 
                    background-color: #1976d2; 
                }
                QCalendarWidget QAbstractItemView:enabled {
                    font-size: 20px;
                    color: #222;
                    background: #fff;
                    selection-background-color: #1976d2;
                    selection-color: #fff;
                }
                QCalendarWidget QAbstractItemView:disabled {
                    color: #ccc;
                }
            """)

        btn_filtrele = self.stil_buton("Filtrele", "fa5s.search", "#1976d2")
        btn_temizle = self.stil_buton("Temizle", "fa5s.sync", "#fb8c00")
        
        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)
        ana_layout.addWidget(filtre_frame)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Plaka", "Cari Kodu", "Cari Ünvanı", "Tarih", "Ödeme Tipi", "Alınan Tutar"
        ])
        
        self.load_payments()

        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #bbb;
            }
        """)
        
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        ana_layout.addWidget(self.table)

        # Alt bilgi
        alt_bilgi = QLabel("5 adet kayıt listeleniyor | Toplam Alınan: 18.711,00 TL | 7 Günlük Kayıt")
        alt_bilgi.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 10px 0;
            }
        """)
        ana_layout.addWidget(alt_bilgi)

        self.setLayout(ana_layout)

        self.baslangic_tarihi.dateChanged.connect(self.bitis_tarihini_guncelle)

    def bitis_tarihini_guncelle(self):
        yeni_bitis = self.baslangic_tarihi.date().addDays(7)
        self.bitis_tarihi.setDate(yeni_bitis)

    def load_payments(self):
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT plaka, cari_kodu, cari_ad_unvan, tarih, odeme_tipi, tutar
            FROM KASA
            ORDER BY datetime(tarih) DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                if col_idx == 5:  # tutar
                    item = QTableWidgetItem(f"{value:,.2f} TL")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaymentHistoryForm()
    window.show()
    sys.exit(app.exec_())