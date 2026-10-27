from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QDateEdit, QApplication, QSizePolicy, QDesktopWidget, QGridLayout, QSpacerItem, QHeaderView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
from database_progress import get_kasa_transactions, get_kasa_ozeti
from datetime import datetime
from qtawesome import icon  # qtawesome kütüphanesini ekleyin

class CaseTotalsForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kasa Toplamları")
        
        # Base resolution for scaling
        BASE_WIDTH = 1366
        BASE_HEIGHT = 768
        
        # Get current screen dimensions
        ekran = QDesktopWidget().screenGeometry()
        screen_width = ekran.width()
        screen_height = ekran.height()
        
        # Calculate scaling factors
        width_scale = screen_width / BASE_WIDTH
        height_scale = screen_height / BASE_HEIGHT
        
        # Use the smaller scale to maintain aspect ratio
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        genislik = int(BASE_WIDTH * scale * 0.85)
        yukseklik = int(BASE_HEIGHT * scale * 0.85)
        
        self.setFixedSize(genislik, yukseklik)
        x = (screen_width - genislik) // 2
        y = (screen_height - yukseklik) // 2 - 40
        if y < 0:
            y = 0
        self.move(x, y)
        
        self.init_ui()
        self.load_transactions()  # Başlangıçta verileri yükle
        self.setWindowIcon(icon('fa5s.file')) # Add a file icon

    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(12)
        ana_layout.setContentsMargins(18, 12, 18, 12)

        # Üst filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(12)

        # Font sizes based on screen scaling
        screen_height = QDesktopWidget().screenGeometry().height()
        font_label_size = int(screen_height * 0.017)  # ~13px at 768p
        font_combo_size = int(screen_height * 0.017)  # ~13px at 768p
        font_btn_size = int(screen_height * 0.014)    # ~11px at 768p

        font_label = QFont("Arial", font_label_size, QFont.Bold)
        font_combo = QFont("Arial", font_combo_size)
        font_btn = QFont("Arial", font_btn_size, QFont.Bold)

        # Input field sizes
        input_width = int(self.width() * 0.15)  # 15% of window width
        input_height = int(self.height() * 0.08)  # 8% of window height

        lbl_baslangic = QLabel("Başlangıç")
        lbl_baslangic.setFont(font_label)
        self.date_baslangic = QDateEdit(QDate.currentDate())
        self.date_baslangic.setFont(font_combo)
        self.date_baslangic.setCalendarPopup(True)
        self.date_baslangic.setDisplayFormat("dd.MM.yyyy")
        self.date_baslangic.setFixedWidth(input_width)
        self.date_baslangic.setFixedHeight(input_height)

        lbl_bitis = QLabel("Bitiş")
        lbl_bitis.setFont(font_label)
        self.date_bitis = QDateEdit(QDate.currentDate())
        self.date_bitis.setFont(font_combo)
        self.date_bitis.setCalendarPopup(True)
        self.date_bitis.setDisplayFormat("dd.MM.yyyy")
        self.date_bitis.setFixedWidth(input_width)
        self.date_bitis.setFixedHeight(input_height)

        self.cmb_odeme_tipi = QComboBox()
        self.cmb_odeme_tipi.setFont(font_combo)
        self.cmb_odeme_tipi.addItems(["", "Nakit", "Kredi Kartı", "Havale"])
        self.cmb_odeme_tipi.setFixedWidth(input_width)
        self.cmb_odeme_tipi.setFixedHeight(input_height)

        self.cmb_islem_tipi = QComboBox()
        self.cmb_islem_tipi.setFont(font_combo)
        self.cmb_islem_tipi.addItems(["", "Servis İşlemi", "Teklif İşlemi"])
        self.cmb_islem_tipi.setFixedWidth(input_width)
        self.cmb_islem_tipi.setFixedHeight(input_height)

        self.cmb_kisa_tarih = QComboBox()
        self.cmb_kisa_tarih.setFont(font_combo)
        self.cmb_kisa_tarih.addItems([
             "" ,"Bugün", "Bu Hafta", "Bu Ay", "Bu Yıl", "Tümü"
        ])
        self.cmb_kisa_tarih.setFixedWidth(input_width)
        self.cmb_kisa_tarih.setFixedHeight(input_height)

        # Add labels for comboboxes
        lbl_odeme_tipi = QLabel("Ödeme Tipi")
        lbl_odeme_tipi.setFont(font_label)
        lbl_islem_tipi = QLabel("İşlem Tipi")
        lbl_islem_tipi.setFont(font_label)
        lbl_kisa_tarih = QLabel("Kısa Tarih")
        lbl_kisa_tarih.setFont(font_label)

        # Button sizes
        btn_width = int(self.width() * 0.08)   # 8% of window width
        btn_height = int(self.height() * 0.08)  # 8% of window height

        btn_temizle = QPushButton("🧹 Temizle")
        btn_temizle.setFont(font_btn)
        btn_temizle.setFixedWidth(btn_width)
        btn_temizle.setFixedHeight(btn_height)
        btn_temizle.setStyleSheet("background: #ffe082; color: #333; border-radius: 8px; font-weight: bold;")

        btn_filtrele = QPushButton("🔍 Filtrele")
        btn_filtrele.setFont(font_btn)
        btn_filtrele.setFixedWidth(btn_width)
        btn_filtrele.setFixedHeight(btn_height)
        btn_filtrele.setStyleSheet("background: #1976d2; color: #fff; border-radius: 8px; font-weight: bold;")

        # Grid layout for filter area
        filtre_grid_layout = QGridLayout()
        filtre_grid_layout.setHorizontalSpacing(12)
        filtre_grid_layout.setVerticalSpacing(6)

        # Add labels and inputs to grid
        filtre_grid_layout.addWidget(lbl_baslangic,    0, 0)
        filtre_grid_layout.addWidget(lbl_bitis,        0, 1)
        filtre_grid_layout.addWidget(lbl_odeme_tipi,   0, 2)
        filtre_grid_layout.addWidget(lbl_islem_tipi,   0, 3)
        filtre_grid_layout.addWidget(lbl_kisa_tarih,   0, 4)

        filtre_grid_layout.addWidget(self.date_baslangic, 1, 0)
        filtre_grid_layout.addWidget(self.date_bitis,     1, 1)
        filtre_grid_layout.addWidget(self.cmb_odeme_tipi, 1, 2)
        filtre_grid_layout.addWidget(self.cmb_islem_tipi, 1, 3)
        filtre_grid_layout.addWidget(self.cmb_kisa_tarih, 1, 4)

        # Add stretch and buttons
        filtre_grid_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 5)
        
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addWidget(btn_temizle)
        button_layout.addWidget(btn_filtrele)
        button_container.setLayout(button_layout)
        
        filtre_grid_layout.addWidget(button_container, 1, 6, 1, 2)

        # Center the filter area
        filtre_container = QHBoxLayout()
        filtre_container.addStretch(1)
        filtre_container.addLayout(filtre_grid_layout)
        filtre_container.addStretch(1)

        filtre_widget = QWidget()
        filtre_widget.setLayout(filtre_container)
        filtre_widget.setStyleSheet("background-color: #fff7cc; border-radius: 8px;")

        ana_layout.addWidget(filtre_widget)

        # Total amount and close button
        toplam_layout = QHBoxLayout()
        toplam_layout.setSpacing(0)
        toplam_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_giris = QLabel("Toplam Tutar: 0,00 TL")
        self.lbl_giris.setFont(QFont("Arial", int(screen_height * 0.026), QFont.Bold))  # ~20px at 768p
        self.lbl_giris.setAlignment(Qt.AlignCenter)
        self.lbl_giris.setStyleSheet("""
            background: #23b01a;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            border: none;
        """)
        self.lbl_giris.setFixedHeight(int(self.height() * 0.08))  # 8% of window height
        self.lbl_giris.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        btn_kapat = QPushButton("❌ KAPAT")
        btn_kapat.setFont(QFont("Arial", int(screen_height * 0.018), QFont.Bold))  # ~14px at 768p
        btn_kapat.setStyleSheet("""
            background: #c62828;
            color: white;
            border-radius: 10px;
            border: 2px solid #eee;
            font-weight: bold;
        """)
        btn_kapat.setFixedHeight(int(self.height() * 0.08))  # 8% of window height
        btn_kapat.setFixedWidth(int(self.width() * 0.15))  # 15% of window width
        btn_kapat.clicked.connect(self.close)

        toplam_layout.addWidget(self.lbl_giris, stretch=1)
        toplam_layout.addSpacing(18)
        toplam_layout.addWidget(btn_kapat, stretch=0)

        ana_layout.addLayout(toplam_layout)
        ana_layout.addSpacing(0)

        # Table section
        lbl_islem_detay = QLabel("İşlem Detayları")
        lbl_islem_detay.setFont(QFont("Arial", int(screen_height * 0.016), QFont.Bold))  # ~12px at 768p
        lbl_islem_detay.setStyleSheet("margin:0;padding:0;color:#222;")
        ana_layout.addWidget(lbl_islem_detay)

        self.table = QTableWidget(13, 5)
        self.table.setFont(QFont("Arial", int(screen_height * 0.016)))  # ~12px at 768p
        self.table.setHorizontalHeaderLabels(["Tarih", "Ödeme Tipi", "Açıklama", "Ödeme Tutarı", "İşlem Tipi"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                font-size: {int(screen_height * 0.017)}px;  /* ~13px at 768p */
                background: #fafafa;
                border: 1px solid #bdbdbd;
                gridline-color: #bdbdbd;
            }}
            QHeaderView::section {{
                background: #ededed;
                color: #222;
                font-weight: bold;
                font-size: {int(screen_height * 0.016)}px;  /* ~12px at 768p */
                border: 1px solid #bdbdbd;
                padding: 4px;
            }}
        """)

        # Set column widths
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        ana_layout.addWidget(self.table)

        # Alt bilgi (her yüklemede yalnızca metni güncellenir)
        self.alt_bilgi = QLabel("")
        self.alt_bilgi.setFont(QFont("Arial", 12))
        self.alt_bilgi.setStyleSheet("margin-top: 8px;")
        ana_layout.addWidget(self.alt_bilgi)

        # Connect button signals
        btn_filtrele.clicked.connect(self.load_transactions)
        btn_temizle.clicked.connect(self.clear_filters)
        self.cmb_kisa_tarih.currentIndexChanged.connect(self.kisa_tarih_sec)

        # Set styles for filter inputs
        filtre_widget.setStyleSheet("""
            background-color: #fff7cc; border-radius: 8px;
        """)
        self.date_baslangic.setStyleSheet("background-color: white;")
        self.date_bitis.setStyleSheet("background-color: white;")
        self.cmb_odeme_tipi.setStyleSheet("background-color: white;")
        self.cmb_islem_tipi.setStyleSheet("background-color: white;")
        self.cmb_kisa_tarih.setStyleSheet("background-color: white;")

        # Set calendar styles
        calendar_style = """
            QWidget {
                background-color: white;
            }
            QCalendarWidget {
                min-width: 380px;
                min-height: 320px;
            }
            QCalendarWidget QToolButton {
                background-color: #1976d2;
                color: black;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
            }
            QCalendarWidget QToolButton#qt_calendar_monthbutton {
                qproperty-icon: none;
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
                color: black;
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
        """

        self.date_baslangic.calendarWidget().setStyleSheet(calendar_style)
        self.date_bitis.calendarWidget().setStyleSheet(calendar_style)

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
            elif islem_tipi == "Teklif İşlemi":
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
                
                # Tarih ('2025-06-13 11:51:13' -> '13.06.2025 11:51'; farklı biçimde kaydedilmişse olduğu gibi)
                t = str(transaction[0] or "")
                tarih = f"{t[8:10]}.{t[5:7]}.{t[:4]} {t[11:16]}".strip() if len(t) >= 10 and t[4] == "-" and t[7] == "-" else t
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
            self.alt_bilgi.setText(f'<span style="color:#222;">{len(transactions)} kayıt</span> | <b>Toplam {len(transactions)} kayıt listeleniyor</b>')
            if not transactions:
                # Kasa varsayılan olarak bugünü gösterir; eski tarihli ödemeler (ör. yeni yüklenen veritabanında) görünmez
                adet, ilk, son = get_kasa_ozeti()
                if adet:
                    self.alt_bilgi.setText(
                        f'<span style="color:#b71c1c;"><b>Seçilen tarih aralığında ödeme yok.</b> Kasada toplam {adet} ödeme kayıtlı '
                        f'({self._tarih_tr(ilk)} - {self._tarih_tr(son)}). Tümünü görmek için Kısa Tarih\'ten <b>Tümü</b>\'nü seçin.</span>'
                    )

        except Exception as e:
            print(f"Hata: {str(e)}")
            # Hata durumunda kullanıcıya bilgi ver
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Hata", f"Veriler yüklenirken bir hata oluştu:\n{str(e)}")

    @staticmethod
    def _tarih_tr(iso):
        return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}" if iso and len(iso) >= 10 else (iso or "-")

    def kisa_tarih_sec(self):
        """Kısa tarih seçimine (Bugün / Bu Hafta / Bu Ay / Bu Yıl / Tümü) göre tarih aralığını ayarlar ve listeler."""
        bugun = QDate.currentDate()
        bitis = bugun
        secim = self.cmb_kisa_tarih.currentText()
        if secim == "Tümü":
            _, ilk, son = get_kasa_ozeti()
            baslangic = QDate.fromString(ilk, "yyyy-MM-dd") if ilk else bugun
            son_tarih = QDate.fromString(son, "yyyy-MM-dd") if son else bugun
            bitis = max(bugun, son_tarih) if son_tarih.isValid() else bugun
            if not baslangic.isValid():
                baslangic = bugun
        else:
            baslangic = {
                "Bugün": bugun,
                "Bu Hafta": bugun.addDays(1 - bugun.dayOfWeek()),  # Pazartesi
                "Bu Ay": QDate(bugun.year(), bugun.month(), 1),
                "Bu Yıl": QDate(bugun.year(), 1, 1),
            }.get(secim)
        if baslangic is None:
            return
        self.date_baslangic.setDate(baslangic)
        self.date_bitis.setDate(bitis)
        self.load_transactions()

    def clear_filters(self):
        """Filtreleri temizler ve verileri yeniden yükler."""
        self.cmb_kisa_tarih.blockSignals(True)
        self.cmb_kisa_tarih.setCurrentIndex(0)
        self.cmb_kisa_tarih.blockSignals(False)
        self.date_baslangic.setDate(QDate.currentDate())
        self.date_bitis.setDate(QDate.currentDate())
        self.cmb_islem_tipi.setCurrentIndex(0)
        self.cmb_odeme_tipi.setCurrentIndex(0)
        self.load_transactions()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CaseTotalsForm()
    form.show()
    sys.exit(app.exec_())