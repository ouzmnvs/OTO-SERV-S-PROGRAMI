from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QDateEdit, QApplication, QSizePolicy, QDesktopWidget, QGridLayout, QSpacerItem, QHeaderView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
from database_progress import get_kasa_transactions
from datetime import datetime

class CaseTotalsForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kasa Toplamları")
        self.set_window_size()
        self.init_ui()
        self.load_transactions()  # Başlangıçta verileri yükle

    def set_window_size(self):
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.85)
        yukseklik = int(ekran.height() * 0.85)
        self.setFixedSize(genislik, yukseklik)
        x = (ekran.width() - genislik) // 2
        y = (ekran.height() - yukseklik) // 2 - 40
        self.move(x, y)

    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(12)
        ana_layout.setContentsMargins(18, 12, 18, 12)

        # Üst filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(12)

        font_label = QFont("Arial", 13, QFont.Bold)
        font_combo = QFont("Arial", 13)
        font_btn = QFont("Arial", 11, QFont.Bold)

        lbl_baslangic = QLabel("Başlangıç")
        lbl_baslangic.setFont(font_label)
        self.date_baslangic = QDateEdit(QDate.currentDate())
        self.date_baslangic.setFont(font_combo)
        self.date_baslangic.setCalendarPopup(True)
        self.date_baslangic.setDisplayFormat("dd.MM.yyyy")
        self.date_baslangic.setFixedWidth(190)

        lbl_bitis = QLabel("Bitiş")
        lbl_bitis.setFont(font_label)
        # Bitiş tarihini yarına ayarla
        tomorrow = QDate.currentDate().addDays(1)
        self.date_bitis = QDateEdit(tomorrow)
        self.date_bitis.setFont(font_combo)
        self.date_bitis.setCalendarPopup(True)
        self.date_bitis.setDisplayFormat("dd.MM.yyyy")
        self.date_bitis.setFixedWidth(190)

        self.cmb_odeme_tipi = QComboBox()
        self.cmb_odeme_tipi.setFont(font_combo)
        self.cmb_odeme_tipi.addItems(["", "Nakit", "Kredi Kartı", "Havale"])
        self.cmb_odeme_tipi.setFixedWidth(200)

        self.cmb_islem_tipi = QComboBox()
        self.cmb_islem_tipi.setFont(font_combo)
        self.cmb_islem_tipi.addItems(["", "Servis İşlemi", "Normal İşlemi"])
        self.cmb_islem_tipi.setFixedWidth(200)

        self.cmb_kisa_tarih = QComboBox()
        self.cmb_kisa_tarih.setFont(font_combo)
        self.cmb_kisa_tarih.addItems([
             "" ,"Bugün", "Bu Hafta", "Bu Ay", "Bu Yıl"
        ])
        self.cmb_kisa_tarih.setFixedWidth(170)

        btn_temizle = QPushButton("🧹 Temizle")
        btn_temizle.setFont(font_btn)
        btn_temizle.setFixedWidth(110)
        btn_temizle.setFixedHeight(60)
        btn_temizle.setStyleSheet("background: #ffe082; color: #333; border-radius: 8px; font-weight: bold;")

        btn_filtrele = QPushButton("🔍 Filtrele")
        btn_filtrele.setFont(font_btn)
        btn_filtrele.setFixedWidth(110)
        btn_filtrele.setFixedHeight(60)
        btn_filtrele.setStyleSheet("background: #1976d2; color: #fff; border-radius: 8px; font-weight: bold;")

        # --- FİLTRE ALANI YENİ DÜZEN ---

        # GridLayout ile label ve inputları hizala
        filtre_grid_layout = QGridLayout()
        filtre_grid_layout.setHorizontalSpacing(12)
        filtre_grid_layout.setVerticalSpacing(6)

        # 1. Satır: Label'lar
        lbl_odeme_tipi = QLabel("Ödeme Tipi")
        lbl_odeme_tipi.setFont(QFont("Arial", 13, QFont.Bold))
        lbl_islem_tipi = QLabel("İşlem Tipi")
        lbl_islem_tipi.setFont(QFont("Arial", 13, QFont.Bold))
        lbl_kisa_tarih = QLabel("Kısa Tarih")
        lbl_kisa_tarih.setFont(QFont("Arial", 13, QFont.Bold))

        filtre_grid_layout.addWidget(lbl_baslangic,    0, 0)
        filtre_grid_layout.addWidget(lbl_bitis,        0, 1)
        filtre_grid_layout.addWidget(lbl_odeme_tipi,   0, 2)
        filtre_grid_layout.addWidget(lbl_islem_tipi,   0, 3)
        filtre_grid_layout.addWidget(lbl_kisa_tarih,   0, 4)

        # 2. Satır: Inputlar
        filtre_grid_layout.addWidget(self.date_baslangic, 1, 0)
        filtre_grid_layout.addWidget(self.date_bitis,     1, 1)
        filtre_grid_layout.addWidget(self.cmb_odeme_tipi, 1, 2)
        filtre_grid_layout.addWidget(self.cmb_islem_tipi, 1, 3)
        filtre_grid_layout.addWidget(self.cmb_kisa_tarih, 1, 4)

        # Butonları sağa yaslamak için stretch ve butonları ekle
        filtre_grid_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 5)
        
        # Butonları içeren bir container widget oluştur
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)  # Butonlar arası boşluk
        button_layout.addWidget(btn_temizle)
        button_layout.addWidget(btn_filtrele)
        button_container.setLayout(button_layout)
        
        filtre_grid_layout.addWidget(button_container, 1, 6, 1, 2)  # 2 sütun genişliğinde

        # Filtre kutularını ortalamak için kapsayıcı bir layout ekleyin:
        filtre_container = QHBoxLayout()
        filtre_container.addStretch(1)  # Sola stretch ekle
        filtre_container.addLayout(filtre_grid_layout)
        filtre_container.addStretch(1)  # Sağa stretch ekle

        # Filtre alanı için özel bir widget oluştur ve arka planını ayarla
        filtre_widget = QWidget()
        filtre_widget.setLayout(filtre_container)
        filtre_widget.setStyleSheet("background-color: #fff7cc; border-radius: 8px;")  # Açık sarı

        ana_layout.addWidget(filtre_widget)

        # --- ÜST KASA TOPLAM VE KAPAT BUTONU ---
        toplam_layout = QHBoxLayout()
        toplam_layout.setSpacing(0)
        toplam_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_giris = QLabel("Toplam Tutar: 0,00 TL")
        self.lbl_giris.setFont(QFont("Arial", 20, QFont.Bold))  # Küçültüldü
        self.lbl_giris.setAlignment(Qt.AlignCenter)
        self.lbl_giris.setStyleSheet("""
            background: #23b01a;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            border: none;
        """)
        self.lbl_giris.setFixedHeight(60)  # Biraz küçültüldü
        self.lbl_giris.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        btn_kapat = QPushButton("❌ KAPAT")
        btn_kapat.setFont(QFont("Arial", 14, QFont.Bold))  # Küçültüldü
        btn_kapat.setStyleSheet("""
            background: #c62828;
            color: white;
            border-radius: 10px;
            border: 2px solid #eee;
            font-weight: bold;
        """)
        btn_kapat.setFixedHeight(60)  # Biraz küçültüldü
        btn_kapat.setFixedWidth(200)  # Daha kısa
        btn_kapat.clicked.connect(self.close)

        toplam_layout.addWidget(self.lbl_giris, stretch=1)
        toplam_layout.addSpacing(18)
        toplam_layout.addWidget(btn_kapat, stretch=0)

        ana_layout.addLayout(toplam_layout)
        ana_layout.addSpacing(0)  # Arada boşluk olmasın

        # --- ALTTAKİ TABLO VE BAŞLIK ---
        lbl_islem_detay = QLabel("İşlem Detayları")
        lbl_islem_detay.setFont(QFont("Arial", 12, QFont.Bold))  # Küçültüldü
        lbl_islem_detay.setStyleSheet("margin:0;padding:0;color:#222;")
        ana_layout.addWidget(lbl_islem_detay)

        self.table = QTableWidget(13, 5)  # Sütun sayısını 5'e düşür
        self.table.setFont(QFont("Arial", 12))  # Küçültüldü
        self.table.setHorizontalHeaderLabels(["Tarih", "Ödeme Tipi", "Açıklama", "Ödeme Tutarı", "İşlem Tipi"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 13px;  /* Küçültüldü */
                background: #fafafa;
                border: 1px solid #bdbdbd;
                gridline-color: #bdbdbd;
            }
            QHeaderView::section {
                background: #ededed;
                color: #222;
                font-weight: bold;
                font-size: 12px;  /* Küçültüldü */
                border: 1px solid #bdbdbd;
                padding: 4px;
            }
        """)

        # Sütun genişliklerini eşit yap
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        # Eğer tabloyu ana layout'a eklemediyseniz:
        ana_layout.addWidget(self.table)

        # Filtrele butonuna tıklama olayını bağla
        btn_filtrele.clicked.connect(self.load_transactions)
        
        # Temizle butonuna tıklama olayını bağla
        btn_temizle.clicked.connect(self.clear_filters)

        # Kutuların arka planını beyaz yap
        filtre_widget.setStyleSheet("""
            background-color: #fff7cc; border-radius: 8px;
        """)
        self.date_baslangic.setStyleSheet("background-color: white;")
        self.date_bitis.setStyleSheet("background-color: white;")
        self.cmb_odeme_tipi.setStyleSheet("background-color: white;")
        self.cmb_islem_tipi.setStyleSheet("background-color: white;")
        self.cmb_kisa_tarih.setStyleSheet("background-color: white;")

        # Başlangıç tarihi için takvim stilini ayarla
        calendar_baslangic = self.date_baslangic.calendarWidget()
        calendar_baslangic.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QCalendarWidget {
                min-width: 380px;
                min-height: 320px;
            }
            QCalendarWidget QToolButton {
                background-color: #1976d2;
                color: black; /* Ay ve yıl siyah */
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
            }
            QCalendarWidget QToolButton#qt_calendar_monthbutton {
                qproperty-icon: none; /* Aşağı oku kaldır */
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #1976d2;
            }
            QCalendarWidget QSpinBox {
                font-size: 16px;
                color: #1976d2;
                background: white;
                selection-background-color: #1976d2;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 16px;
                font-weight: 1000;
                color: black; /* Günler siyah */
                background-color: white;
                selection-background-color: #1976d2;
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #1976d2; }
            QCalendarWidget QTableView {
                border-width: 0px;
            }
            QCalendarWidget QHeaderView::section {
                color: #1976d2;
                background: white;
                font-weight: bold;
                font-size: 19px;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #ccc;
            }
        """)

        # Bitiş tarihi için takvim stilini ayarla
        calendar_bitis = self.date_bitis.calendarWidget()
        calendar_bitis.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QCalendarWidget {
                min-width: 380px;
                min-height: 320px;
            }
            QCalendarWidget QToolButton {
                background-color: #1976d2;
                color: black; /* Ay ve yıl siyah */
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
            }
            QCalendarWidget QToolButton#qt_calendar_monthbutton {
                qproperty-icon: none; /* Aşağı oku kaldır */
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #1976d2;
            }
            QCalendarWidget QSpinBox {
                font-size: 16px;
                color: #1976d2;
                background: white;
                selection-background-color: #1976d2;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 16px;
                font-weight: 1000;
                color: black; /* Günler siyah */
                background-color: white;
                selection-background-color: #1976d2;
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #1976d2; }
            QCalendarWidget QTableView {
                border-width: 0px;
            }
            QCalendarWidget QHeaderView::section {
                color: #1976d2;
                background: white;
                font-weight: bold;
                font-size: 15px;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #ccc;
            }
        """)

        self.setLayout(ana_layout)
        # Odağı başka bir elemana vererek tarih alanındaki seçimi kaldır
        self.setFocus()

    def load_transactions(self):
        """Kasa işlemlerini yükler ve tabloya ekler."""
        try:
            # Tarih filtrelerini al
            start_date = self.date_baslangic.date().toString("yyyy-MM-dd")
            end_date = self.date_bitis.date().toString("yyyy-MM-dd")
            
            # İşlem tipi filtresini al
            islem_tipi = self.cmb_islem_tipi.currentText()
            
            # İşlem tipini veritabanı formatına çevir
            if islem_tipi == "Servis İşlemi":
                islem_tipi = "SERVIS"
            elif islem_tipi == "Normal İşlemi":
                islem_tipi = "TEKLIF"
            else:
                islem_tipi = None
            
            # Ödeme tipi filtresini al
            odeme_tipi = self.cmb_odeme_tipi.currentText() if self.cmb_odeme_tipi.currentText() else None
            
            # Verileri getir
            transactions = get_kasa_transactions(
                start_date=start_date,
                end_date=end_date,
                islem_tipi=islem_tipi,
                odeme_tipi=odeme_tipi
            )
            
            # Tabloyu temizle
            self.table.setRowCount(0)
            
            # Toplam tutarları hesapla
            toplam_tutar = 0
            
            # Verileri tabloya ekle
            for row_idx, transaction in enumerate(transactions):
                self.table.insertRow(row_idx)
                
                # Tarih
                tarih = datetime.strptime(transaction[0], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")
                self.table.setItem(row_idx, 0, QTableWidgetItem(tarih))
                
                # Ödeme Tipi
                self.table.setItem(row_idx, 1, QTableWidgetItem(transaction[1] or ""))
                
                # Açıklama
                self.table.setItem(row_idx, 2, QTableWidgetItem(transaction[2] or ""))
                
                # Ödeme Tutarı
                tutar = float(transaction[3])
                self.table.setItem(row_idx, 3, QTableWidgetItem(f"{tutar:,.2f}"))
                toplam_tutar += tutar
                
                # İşlem Tipi
                islem_tipi = "Servis İşlemi" if transaction[4] == "SERVIS" else "Teklif İşlemi"
                self.table.setItem(row_idx, 4, QTableWidgetItem(islem_tipi))
            
            # Toplam tutarı güncelle
            self.lbl_giris.setText(f"Toplam Tutar: {toplam_tutar:,.2f} TL")
            
            # Alt bilgiyi güncelle
            alt_bilgi = QLabel(f'<span style="color:#222;">{len(transactions)} kayıt</span> | <b>Toplam {len(transactions)} kayıt listeleniyor</b>')
            alt_bilgi.setFont(QFont("Arial", 12))
            alt_bilgi.setStyleSheet("margin-top: 8px;")
            
            # Eğer önceki alt bilgi varsa kaldır
            for i in reversed(range(self.layout().count())):
                widget = self.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and widget != self.lbl_giris:
                    widget.deleteLater()
            
            self.layout().addWidget(alt_bilgi)
            
        except Exception as e:
            print(f"Hata: {str(e)}")
            # Hata durumunda kullanıcıya bilgi ver
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Hata", f"Veriler yüklenirken bir hata oluştu:\n{str(e)}")

    def clear_filters(self):
        """Filtreleri temizler ve verileri yeniden yükler."""
        self.date_baslangic.setDate(QDate.currentDate())
        self.date_bitis.setDate(QDate.currentDate().addDays(1))  # Bitiş tarihini yarına ayarla
        self.cmb_islem_tipi.setCurrentIndex(0)
        self.cmb_odeme_tipi.setCurrentIndex(0)
        self.cmb_kisa_tarih.setCurrentIndex(0)
        self.load_transactions()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CaseTotalsForm()
    form.show()
    sys.exit(app.exec_())