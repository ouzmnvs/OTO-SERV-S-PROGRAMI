from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QDateEdit,
    QDesktopWidget, QFrame
)
from PyQt5.QtCore import Qt, QSize, QDate
from qtawesome import icon
import sys

class PaymentHistoryForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ödeme Geçmişi")
        self.resize_and_center()
        self.init_ui()

    def resize_and_center(self):
        # Ekran boyutlarına göre pencereyi orantılı ayarla (close_service.py referansı)
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
        
        # Üst butonlar (close_service.py referansına uygun)
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

        # Cari bilgi filtresi
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

        # Başlangıç tarihi (QDateEdit)
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

        # Bitiş tarihi (QDateEdit)
        self.bitis_tarihi = QDateEdit()
        # İlk açılışta bitiş tarihi, başlangıç tarihinin 7 gün sonrası olsun
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

        # Takvim popup stilleri (günlerle orantılı olarak daha geniş ve yüksek)
        for dateedit in [self.baslangic_tarihi, self.bitis_tarihi]:
            takvim = dateedit.calendarWidget()
            takvim.setFixedSize(440, 325)  # Genişlik ve yükseklik artırıldı
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

        # Filtrele ve Temizle butonları
        btn_filtrele = self.stil_buton("Filtrele", "fa5s.search", "#1976d2")
        btn_temizle = self.stil_buton("Temizle", "fa5s.sync", "#fb8c00")
        
        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)
        ana_layout.addWidget(filtre_frame)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Cari Kodu", "Cari Ünvanı", "Ödeme Tipi", "Tarih", 
            "Açıklama", "Borç", "Alacak"
        ])
        
        # Örnek veriler
        veriler = [
            ["CR002", "MUSTAFA CAN", "", "10.03.2025", "Servis Bedeli", "5.750,00", "0,00"],
            ["CR001", "FATİH ÖZ", "", "9.03.2025", "Servis Bedeli", "12.219,21", "0,00"],
            ["CR002", "MUSTAFA CAN", "Nakit", "9.03.2025", "", "0,00", "2.500,00"],
            ["CR002", "MUSTAFA CAN", "Kredi Kartı", "9.03.2025", "", "0,00", "10.500,00"],
            ["CR002", "MUSTAFA CAN", "", "8.03.2025", "Servis Bedeli", "2.000,00", "0,00"],
            ["CR002", "MUSTAFA CAN", "", "8.03.2025", "Servis Bedeli", "13.750,68", "0,00"],
            ["CR001", "FATİH ÖZ", "", "8.03.2025", "Servis Bedeli", "1.750,36", "0,00"],
            ["TD002", "AHMET CANDAN", "Nakit", "7.03.2025", "", "250,00", "0,00"],
            ["CR001", "FATİH ÖZ", "Kredi Kartı", "7.03.2025", "", "0,00", "1.800,00"],
            ["TD002", "AHMET CANDAN", "Kredi Kartı", "7.03.2025", "Ödeme Alındı", "0,00", "3.800,00"],
            ["TD002", "AHMET CANDAN", "Nakit", "7.03.2025", "", "0,00", "111,00"],
            ["TD002", "AHMET CANDAN", "", "7.03.2025", "Servis Bedeli", "6.300,00", "0,00"]
        ]

        self.table.setRowCount(len(veriler))
        for row, veri in enumerate(veriler):
            for col, deger in enumerate(veri):
                item = QTableWidgetItem(deger)
                if col in [5, 6]:  # Borç ve Alacak sütunları
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

        # Tablo stilleri
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
        
        # Sütun genişlikleri
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        ana_layout.addWidget(self.table)

        # Alt bilgi
        alt_bilgi = QLabel("12 adet kayıt listeleniyor | Toplam Borç: 42.020,25 TL | Toplam Alacak: 18.711,00 TL | Bakiye: 23.309,25 TL BORÇLU | 7 Günlük Kayıt")
        alt_bilgi.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 10px 0;
            }
        """)
        ana_layout.addWidget(alt_bilgi)

        self.setLayout(ana_layout)

        # Başlangıç tarihi değişince bitiş tarihini otomatik 7 gün sonrası yap
        self.baslangic_tarihi.dateChanged.connect(self.bitis_tarihini_guncelle)

    def bitis_tarihini_guncelle(self):
        yeni_bitis = self.baslangic_tarihi.date().addDays(7)
        self.bitis_tarihi.setDate(yeni_bitis)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaymentHistoryForm()
    window.show()
    sys.exit(app.exec_())