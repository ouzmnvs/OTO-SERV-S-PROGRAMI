from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QDateEdit, QToolButton, QMenu, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QDate
from qtawesome import icon
import sys
from database_progress import load_closed_services  # Kapalı servisleri yüklemek için fonksiyonu içe aktarın
from odeme_al import OdemeAlForm
from database_progress import delete_service  # En üste ekleyin

class CloseServiceForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tüm İşlemler")
        self.init_ui()

    def init_ui(self):
        # Ekran boyutlarına göre pencereyi orantılı ayarla
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.86)
        yukseklik = int(ekran.height() * 0.86)
        self.setFixedSize(genislik, yukseklik)
        x = (ekran.width() - genislik) // 2
        y = (ekran.height() - yukseklik) // 2 - 40
        self.move(x, y)

        # Ana layout
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(15)

        # Üst butonlar
        buton_layout = QHBoxLayout()
        buton_layout.setSpacing(10)
        btn_kaydi_sil = self.stil_buton("KAYDI SİL", 'fa5s.trash', '#f44336')
        btn_detay_goruntule = self.stil_buton("DETAY GÖRÜNTÜLE", 'fa5s.info-circle', '#455a64')
        btn_odeme_al = self.stil_buton("ÖDEME AL", 'fa5s.money-bill', '#43a047')
        btn_pdf_aktar = self.stil_buton("PDF AKTAR", 'fa5s.file-pdf', '#0288d1')
        btn_sayfayi_kapat = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')

        buton_layout.addWidget(btn_kaydi_sil)
        buton_layout.addWidget(btn_detay_goruntule)
        buton_layout.addWidget(btn_odeme_al)
        buton_layout.addWidget(btn_pdf_aktar)
        buton_layout.addWidget(btn_sayfayi_kapat)
        btn_odeme_al.clicked.connect(self.odeme_al_ac)  # Doğru bağlantı
        btn_kaydi_sil.clicked.connect(self.kaydi_sil)  # Kaydı sil fonksiyonunu bağla
        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(10)

        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı, Plaka veya Telefon")
        self.filtre_input.setStyleSheet("""
            font-size: 16px;
            padding: 8px 12px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            background: #fffbe8;  /* Sarı arka plan */
        """)
        filtre_layout.addWidget(self.filtre_input)

        # Tarih seçimi için başlangıç ve bitiş tarihleri
        self.baslangic_tarihi = QDateEdit()
        self.baslangic_tarihi.setDate(QDate.currentDate())
        self.baslangic_tarihi.setCalendarPopup(True)  # Takvim açılır pencere özelliği
        self.baslangic_tarihi.setDisplayFormat("dd.MM.yyyy")
        self.baslangic_tarihi.setFixedSize(150, 40)  # Genişlik: 150px, Yükseklik: 40px
        self.baslangic_tarihi.setStyleSheet("""
            QDateEdit {
                font-size: 16px;  /* Yazı boyutunu artır */
                padding: 6px 10px;  /* İç boşluk */
                border: 1.5px solid #bbb;
                border-radius: 6px;
                background: #fff;
            }
            QDateEdit::drop-down {
                width: 30px;  /* Açılır ok genişliği */
            }
        """)
        filtre_layout.addWidget(self.baslangic_tarihi)

        self.bitis_tarihi = QDateEdit()
        self.bitis_tarihi.setDate(QDate.currentDate())
        self.bitis_tarihi.setCalendarPopup(True)  # Takvim açılır pencere özelliği
        self.bitis_tarihi.setDisplayFormat("dd.MM.yyyy")
        self.bitis_tarihi.setFixedSize(150, 40)  # Genişlik: 150px, Yükseklik: 40px
        self.bitis_tarihi.setStyleSheet("""
            QDateEdit {
                font-size: 16px;  /* Yazı boyutunu artır */
                padding: 6px 10px;  /* İç boşluk */
                border: 1.5px solid #bbb;
                border-radius: 6px;
                background: #fff;
            }
            QDateEdit::drop-down {
                width: 30px;  /* Açılır ok genişliği */
            }
        """)
        filtre_layout.addWidget(self.bitis_tarihi)

        btn_filtrele = self.stil_buton("Filtrele", 'fa5s.search', '#1976d2')
        btn_temizle = self.stil_buton("Temizle", 'fa5s.sync', '#fbc02d')

        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)

        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = QTableWidget(4, 7)
        self.table.setHorizontalHeaderLabels(["Araç Plakası", "Araç Tipi", "Cari Kodu", "Cari Ünvanı", "Telefon", "Tarih", "Tutar"])
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

        # Örnek veriler
        veriler = [
            ["34 AA 001", "Arazi, SUV & Pikap", "CR002", "MUSTAFA CAN", "05323323636", "8.03.2025", "2.000,00"],
            ["06 AA 001", "Otomobil", "CR001", "FATİH ÖZ", "05552221122", "8.03.2025", "12.219,21"],
            ["34 AA 001", "Arazi, SUV & Pikap", "CR002", "MUSTAFA CAN", "05323323636", "7.03.2025", "13.750,68"],
            ["06 AA 001", "Otomobil", "CR001", "FATİH ÖZ", "05552221122", "7.03.2025", "1.750,36"]
        ]
        for row, veri in enumerate(veriler):
            for col, deger in enumerate(veri):
                item = QTableWidgetItem(deger)
                if col == 6:  # Tutar sütunu
                    item.setForeground(Qt.red)  # Tüm tutarları kırmızı yap
                self.table.setItem(row, col, item)

        ana_layout.addWidget(self.table)

               # Alt bilgi ve tarih bilgisi için yatay layout
        alt_bilgi_layout = QHBoxLayout()

        alt_bilgi = QLabel("4 adet kayıt listeleniyor | Toplam Tutar: 29.720,25 TL")
        alt_bilgi.setStyleSheet("font-size: 14px; color: #444; padding: 6px 0 0 8px;")
        alt_bilgi.setAlignment(Qt.AlignLeft)
        alt_bilgi_layout.addWidget(alt_bilgi)

        self.alt_bilgi_tarih = QLabel("")  # Dinamik olarak güncellenecek
        self.alt_bilgi_tarih.setStyleSheet("font-size: 14px; color: #444; padding: 6px 0 0 8px;")
        self.alt_bilgi_tarih.setAlignment(Qt.AlignRight)
        alt_bilgi_layout.addWidget(self.alt_bilgi_tarih)

        ana_layout.addLayout(alt_bilgi_layout)

        # İlk tarih bilgisi güncellemesi
        self.update_alt_bilgi_tarih()

        self.setLayout(ana_layout)

        # Başlangıç tarihi değişince bitiş tarihini otomatik 7 gün sonrası yap
        self.baslangic_tarihi.dateChanged.connect(self.bitis_tarihini_guncelle)

        self.load_closed_services_to_table()

    def update_alt_bilgi_tarih(self):
        """Başlangıç ve bitiş tarihlerini alt bilgiye yansıt."""
        baslangic = self.baslangic_tarihi.date().toString("dd.MM.yyyy")
        
        # Bitiş tarihine 7 gün ekle
        bitis_tarihi = self.bitis_tarihi.date().addDays(7)
        bitis = bitis_tarihi.toString("dd.MM.yyyy")
        
        self.alt_bilgi_tarih.setText(f"{baslangic} - {bitis} Tarihleri arasında 7 günlük kayıt sonuçları.")
        
        # Güncellenen bitiş tarihini QDateEdit'e de yansıt
        self.bitis_tarihi.setDate(bitis_tarihi)

        # Başlangıç tarihındaki takvim ayarları
        self.baslangic_tarihi.setDate(QDate.currentDate())
        baslangic_takvim = self.baslangic_tarihi.calendarWidget()
        baslangic_takvim.setFixedSize(400, 300)  # Genişlik: 400px, Yükseklik: 300px
        baslangic_takvim.setStyleSheet("""
            QCalendarWidget QToolButton {
                font-size: 16px;  /* Yazı boyutunu büyüt */
                font-weight: bold;  /* Kalın yazı */
                color: black;  /* Siyah yazı rengi */
                
                border: none;
                margin: 2px;
                padding: 4px;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e0e0e0;  /* Hover sırasında daha koyu gri */
            }
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                font-size: 16px;  /* Ok düğmelerinin yazı boyutunu büyüt */
            }
            QCalendarWidget QToolButton::menu-indicator {
                image: none;  /* Menü göstergesini kaldır */
            }
            QCalendarWidget QTableView {
                font-size: 19px;  /* Günlerin yazı boyutunu büyüt */
                font-weight: bold;  /* Günlerin yazılarını kalınlaştır */
                color: black;  /* Siyah yazı rengi */
                background-color: #fff;  /* Beyaz arka plan */
                selection-background-color: #0078d7;  /* Seçili gün arka planı (mavi) */
                selection-color: white;  /* Seçili gün yazı rengi */
            }                           
            QCalendarWidget QHeaderView::section {
                background-color: #f0f0f0;  /* Gün başlıkları arka planı */
                color: black;
                font-size: 20px;  /* Gün başlıklarının yazı boyutunu büyüt */
                font-weight: bold;
            }
        """)
        

        # Bitiş tarihindeki takvim ayarları
        self.bitis_tarihi.setDate(self.baslangic_tarihi.date().addDays(7))  # Bitiş tarihi başlangıç tarihine 7 gün eklenerek ayarlanır
        bitis_takvim = self.bitis_tarihi.calendarWidget()
        bitis_takvim.setFixedSize(400, 300)  # Genişlik: 400px, Yükseklik: 300px
        bitis_takvim.setStyleSheet("""
            QCalendarWidget QToolButton {
                font-size: 18px;  /* Yazı boyutunu büyüt */
                font-weight: bold;  /* Kalın yazı */
                color: black;  /* Siyah yazı rengi */
                
                border: none;
                margin: 2px;
                padding: 4px;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e0e0e0;  /* Hover sırasında daha koyu gri */
            }
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                font-size: 18px;  /* Ok düğmelerinin yazı boyutunu büyüt */
            }
            QCalendarWidget QToolButton::menu-indicator {
                image: none;  /* Menü göstergesini kaldır */
            }
            QCalendarWidget QTableView {
                font-size: 19px;  /* Günlerin yazı boyutunu büyüt */
                font-weight: bold;  /* Günlerin yazılarını kalınlaştır */
                color: black;  /* Siyah yazı rengi */
                background-color: #fff;  /* Beyaz arka plan */
                selection-background-color: #0078d7;  /* Seçili gün arka planı (mavi) */
                selection-color: white;  /* Seçili gün yazı rengi */
            }
            QCalendarWidget QHeaderView::section {
                background-color: #f0f0f0;  /* Gün başlıkları arka planı */
                color: black;
                font-size: 20px;  /* Gün başlıklarının yazı boyutunu büyüt */
                font-weight: bold;
            }
        """)

    def bitis_tarihini_guncelle(self):
        yeni_bitis = self.baslangic_tarihi.date().addDays(7)
        self.bitis_tarihi.setDate(yeni_bitis)

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

    def load_closed_services_to_table(self):
        closed_services = load_closed_services_with_kapanis_tutari()
        self.table.setRowCount(len(closed_services))
        for row, (servis_id, arac_tipi, cari_kodu, cari_unvan, telefon, plaka, tarih, kapanis_tutar) in enumerate(closed_services):
            item_plaka = QTableWidgetItem(plaka or "")
            item_plaka.setData(Qt.UserRole, servis_id)
            self.table.setItem(row, 0, item_plaka)
            self.table.setItem(row, 1, QTableWidgetItem(arac_tipi or ""))
            self.table.setItem(row, 2, QTableWidgetItem(cari_kodu or ""))
            self.table.setItem(row, 3, QTableWidgetItem(cari_unvan or ""))
            self.table.setItem(row, 4, QTableWidgetItem(telefon or ""))
            self.table.setItem(row, 5, QTableWidgetItem(tarih or ""))
            self.table.setItem(row, 6, QTableWidgetItem(f"{(kapanis_tutar or 0):,.2f}"))

    def odeme_al_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        try:
            servis_id = self.table.item(selected_row, 0).data(Qt.UserRole)
            plaka = self.table.item(selected_row, 0).text()  # Plaka sütunu
            arac_tipi = self.table.item(selected_row, 1).text()
            cari_kodu = self.table.item(selected_row, 2).text()
            cari_ad_unvan = self.table.item(selected_row, 3).text()
            telefon = self.table.item(selected_row, 4).text()
            toplam_tutar = float(self.table.item(selected_row, 6).text().replace(",", "").replace(" TL", ""))

            odeme_form = OdemeAlForm(servis_id, cari_kodu, cari_ad_unvan, telefon, toplam_tutar, self, plaka=plaka)
            if odeme_form.exec_() == QDialog.Accepted:
                self.load_closed_services_to_table()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {e}")

    def kaydi_sil(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return
        servis_id = self.table.item(selected_row, 0).data(Qt.UserRole)
        yanit = QMessageBox.question(self, "Onay", "Seçili servisi silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if yanit == QMessageBox.Yes:
            delete_service(servis_id)
            self.load_closed_services_to_table()
            QMessageBox.information(self, "Başarılı", "Servis kaydı silindi.")

class OpenServiceForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Açık Servisler")
        self.setGeometry(100, 100, 600, 400)  # Pencere boyutlarını ayarlayın
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Örnek bir içerik
        lbl = QLabel("Açık Servisler Listesi")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl)

        self.setLayout(layout)

def load_closed_services_with_kapanis_tutari():
    """Kapalı servisleri servis_tutarı ile birlikte döndürür."""
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.id,
                a.arac_tipi,
                s.cari_kodu,
                c.cari_ad_unvan,
                c.cep_telefonu,
                s.plaka,
                s.servis_tarihi,
                s.servis_tutar
            FROM servisler s
            LEFT JOIN cariler c ON s.cari_kodu = c.cari_kodu
            LEFT JOIN araclar a ON s.plaka = a.plaka
            WHERE s.servis_durumu = 'Kapalı'
            ORDER BY s.id DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CloseServiceForm()
    form.show()
    sys.exit(app.exec_())