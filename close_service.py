from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QDateEdit, QToolButton, QMenu, QMessageBox, QDialog, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from qtawesome import icon
import sys
from database_progress import load_closed_services, get_service_full_details  # get_service_full_details'i ekleyin
from odeme_al import OdemeAlForm
from database_progress import delete_service
from pdf_oluşturucu import mevcut_pdf_duzenle

class CloseServiceForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tüm İşlemler")
        self.init_ui()
        self.setWindowIcon(icon('fa5s.file')) # Add a file icon
    def init_ui(self):
        # Base resolution for scaling
        BASE_WIDTH = 1366
        BASE_HEIGHT = 768
        
        # Get current screen dimensions
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        screen_width = ekran.width()
        screen_height = ekran.height()
        
        # Calculate scaling factors
        width_scale = screen_width / BASE_WIDTH
        height_scale = screen_height / BASE_HEIGHT
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        genislik = int(BASE_WIDTH * scale * 0.85)
        yukseklik = int(BASE_HEIGHT * scale * 0.85)
        self.setFixedSize(genislik, yukseklik)
        
        # Center window
        x = (screen_width - genislik) // 2
        y = (screen_height - yukseklik) // 2 - 40
        self.move(x, y)

        # Ana layout
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(int(screen_height * 0.01))  # Reduced spacing

        # Üst butonlar
        buton_layout = QHBoxLayout()
        buton_layout.setSpacing(int(screen_width * 0.008))  # Reduced spacing

        # Buton boyutları için dinamik değerler
        btn_height = int(screen_height * 0.035)  # Reduced from 0.04
        btn_width = int(screen_width * 0.035)   # Reduced from 0.04
        btn_font_size = int(screen_height * 0.012)  # Reduced from 0.014

        btn_kaydi_sil = self.stil_buton("KAYDI SİL", 'fa5s.trash', '#f44336', btn_height, btn_width, btn_font_size)
        btn_detay_goruntule = self.stil_buton("DETAY GÖRÜNTÜLE", 'fa5s.info-circle', '#455a64', btn_height, btn_width, btn_font_size)
        btn_odeme_al = self.stil_buton("ÖDEME AL", 'fa5s.money-bill', '#43a047', btn_height, btn_width, btn_font_size)
        btn_pdf_aktar = self.stil_buton("PDF AKTAR", 'fa5s.file-pdf', '#0288d1', btn_height, btn_width, btn_font_size)
        btn_sayfayi_kapat = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c', btn_height, btn_width, btn_font_size)

        buton_layout.addWidget(btn_kaydi_sil)
        buton_layout.addWidget(btn_detay_goruntule)
        buton_layout.addWidget(btn_odeme_al)
        buton_layout.addWidget(btn_pdf_aktar)
        buton_layout.addWidget(btn_sayfayi_kapat)
        
        btn_odeme_al.clicked.connect(self.odeme_al_ac)
        btn_kaydi_sil.clicked.connect(self.kaydi_sil)
        btn_pdf_aktar.clicked.connect(self.pdf_aktar)
        btn_sayfayi_kapat.clicked.connect(self.close)
        
        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(int(screen_width * 0.008))  # Reduced spacing

        # Input alanları için dinamik boyutlar
        input_height = int(screen_height * 0.025)  # Reduced from 0.028
        input_font_size = int(screen_height * 0.012)  # Reduced from 0.014

        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı, Plaka veya Telefon")
        self.filtre_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: {input_font_size}px;
                padding: {int(input_height * 0.2)}px {int(input_height * 0.3)}px;
                border: 1.5px solid #bbb;
                border-radius: {int(input_height * 0.15)}px;
                background: #fffbe8;
                min-height: {input_height}px;
            }}
        """)
        filtre_layout.addWidget(self.filtre_input)

        # Tarih seçimi için başlangıç ve bitiş tarihleri
        self.baslangic_tarihi = QDateEdit()
        self.baslangic_tarihi.setDate(QDate.currentDate())
        self.baslangic_tarihi.setCalendarPopup(True)
        self.baslangic_tarihi.setDisplayFormat("dd.MM.yyyy")
        self.baslangic_tarihi.setFixedSize(int(screen_width * 0.06), input_height)
        self.baslangic_tarihi.setStyleSheet(f"""
            QDateEdit {{
                font-size: {input_font_size}px;
                padding: {int(input_height * 0.2)}px {int(input_height * 0.3)}px;
                border: 1.5px solid #bbb;
                border-radius: {int(input_height * 0.15)}px;
                background: #fff;
            }}
            QDateEdit::drop-down {{
                width: {int(input_height * 0.75)}px;
            }}
        """)
        filtre_layout.addWidget(self.baslangic_tarihi)

        self.bitis_tarihi = QDateEdit()
        self.bitis_tarihi.setDate(QDate.currentDate())
        self.bitis_tarihi.setCalendarPopup(True)
        self.bitis_tarihi.setDisplayFormat("dd.MM.yyyy")
        self.bitis_tarihi.setFixedSize(int(screen_width * 0.06), input_height)
        self.bitis_tarihi.setStyleSheet(f"""
            QDateEdit {{
                font-size: {input_font_size}px;
                padding: {int(input_height * 0.2)}px {int(input_height * 0.3)}px;
                border: 1.5px solid #bbb;
                border-radius: {int(input_height * 0.15)}px;
                background: #fff;
            }}
            QDateEdit::drop-down {{
                width: {int(input_height * 0.75)}px;
            }}
        """)
        filtre_layout.addWidget(self.bitis_tarihi)

        btn_filtrele = self.stil_buton("Filtrele", 'fa5s.search', '#1976d2', btn_height, btn_width, btn_font_size)
        btn_temizle = self.stil_buton("Temizle", 'fa5s.sync', '#fbc02d', btn_height, btn_width, btn_font_size)

        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)

        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = QTableWidget(4, 8)
        self.table.setHorizontalHeaderLabels(["Araç Plakası", "Araç Tipi", "Cari Kodu", "Cari Ünvanı", "Telefon", "Tarih", "Tutar", "Aracı Getiren"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        # Tablo için dinamik font boyutu
        table_font_size = int(screen_height * 0.016)  # Increased from 0.011
        self.table.setStyleSheet(f"""
            QTableWidget {{
                font-size: {table_font_size}px;
                alternate-background-color: #f5f5f5;
                background: #fff;
            }}
            QHeaderView::section {{
                background: #ececec;
                font-weight: bold;
                font-size: {int(table_font_size * 1.5)}px;  /* Increased font size for headers */
                border: 1.5px solid #bbb;
                padding: {int(table_font_size * 0.4)}px;
            }}
        """)

        ana_layout.addWidget(self.table)

        # Alt bilgi ve tarih bilgisi için yatay layout
        alt_bilgi_layout = QHBoxLayout()

        # Alt bilgi için dinamik font boyutu
        alt_bilgi_font_size = int(screen_height * 0.011)  # Reduced from 0.012
        alt_bilgi = QLabel("Servis kapatma detayları")
        alt_bilgi.setStyleSheet(f"""
            font-size: {alt_bilgi_font_size}px;
            color: #444;
            padding: {int(alt_bilgi_font_size * 0.4)}px 0 0 {int(alt_bilgi_font_size * 0.5)}px;
        """)
        alt_bilgi.setAlignment(Qt.AlignLeft)
        alt_bilgi_layout.addWidget(alt_bilgi)

        self.alt_bilgi_tarih = QLabel("")
        self.alt_bilgi_tarih.setStyleSheet(f"""
            font-size: {alt_bilgi_font_size}px;
            color: #444;
            padding: {int(alt_bilgi_font_size * 0.4)}px 0 0 {int(alt_bilgi_font_size * 0.5)}px;
        """)
        self.alt_bilgi_tarih.setAlignment(Qt.AlignRight)
        alt_bilgi_layout.addWidget(self.alt_bilgi_tarih)

        ana_layout.addLayout(alt_bilgi_layout)

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

    def stil_buton(self, text, icon_name, color, height, width, font_size):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(height)
        btn.setMinimumWidth(width)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: {font_size}px;
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
        for row, (servis_id, arac_tipi, cari_kodu, cari_unvan, telefon, plaka, tarih, kapanis_tutar, arac_getiren_kisi, islem_sayisi) in enumerate(closed_services):
            item_plaka = QTableWidgetItem(plaka or "")
            item_plaka.setData(Qt.UserRole, servis_id)
            self.table.setItem(row, 0, item_plaka)
            self.table.setItem(row, 1, QTableWidgetItem(arac_tipi or ""))
            self.table.setItem(row, 2, QTableWidgetItem(cari_kodu or ""))
            self.table.setItem(row, 3, QTableWidgetItem(cari_unvan or ""))
            self.table.setItem(row, 4, QTableWidgetItem(telefon or ""))
            self.table.setItem(row, 5, QTableWidgetItem(tarih or ""))
            self.table.setItem(row, 6, QTableWidgetItem(f"{(kapanis_tutar or 0):,.2f}"))
            self.table.setItem(row, 7, QTableWidgetItem(arac_getiren_kisi or ""))

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

            odeme_form = OdemeAlForm(
                servis_id=servis_id,
                cari_kodu=cari_kodu,
                cari_ad_unvan=cari_ad_unvan,
                telefon=telefon,
                toplam_tutar=toplam_tutar,
                parent=self,
                plaka=plaka,
                odeme_kaynagi="SERVIS",
                kaynak_id=servis_id
            )
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

    def get_next_service_number(self):
        """Veritabanından son servis numarasını alır ve bir sonraki numarayı döndürür."""
        import sqlite3
        try:
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(CAST(id AS INTEGER)) FROM servisler")
            last_number = cursor.fetchone()[0]
            if last_number is None:
                return "000001"
            next_number = int(last_number) + 1
            return f"{next_number:06d}"  # 6 haneli, başında sıfır olan format
        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
            return "000001"
        finally:
            conn.close()

    def pdf_aktar(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        try:
            # Seçili satırdan servis ID'sini al
            servis_id = self.table.item(selected_row, 0).data(Qt.UserRole)
            
            # Servis detaylarını getir
            detaylar = get_service_full_details(servis_id)
            if not detaylar:
                QMessageBox.warning(self, "Uyarı", "Servis detayları bulunamadı!")
                return

            # Servis, cari ve araç bilgilerini al
            servis = detaylar["servis"]
            cari = detaylar["cari"]
            arac = detaylar["arac"]
            islemler = detaylar["islemler"]

            # İş emri numarasını 6 haneli formatta hazırla
            is_emri_no = f"{int(servis['id']):06d}"

            # Toplam tutarları ve KDV'yi işlemlere göre hesapla
            toplam_kdv_haric = sum(islem['islem_tutari'] for islem in islemler)-sum(islem['kdv_tutari'] for islem in islemler)
            kdv_tutari_genel = sum(islem['kdv_tutari'] for islem in islemler)
            genel_toplam = toplam_kdv_haric + kdv_tutari_genel

            # İşlemleri PDF için hazırla
            islem_texts = []
            y_baslangic = 155  # 92.5 * 1.67
            satir_yuksekligi = 6  # 3.5 * 1.67

            for i, islem in enumerate(islemler, 1):
                islem_texts.extend([
                    (10, y_baslangic - (i * satir_yuksekligi), str(i)),
                    (30, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_aciklama']} {islem['aciklama']}"),
                    (114.5, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari'] / islem['miktar']:.2f}"),  # Birim fiyat = işlem tutarı / miktar
                    (136, y_baslangic - (i * satir_yuksekligi), str(islem['miktar'])),  # Miktar bilgisini ekle
                    (148, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari']:.2f}"),
                    (170, y_baslangic - (i * satir_yuksekligi), f"{islem['kdv_orani']:.1f}%"),  # KDV oranını yüzde olarak göster
                    (184, y_baslangic - (i * satir_yuksekligi), f"{islem['islem_tutari']:.2f}")
                ])

            # Vergi numarası kontrolü
            vergi_no = cari.get('vergi_no', '')
            if vergi_no is None:
                vergi_no = ''

            # PDF için eklemeler sözlüğünü oluştur
            eklemeler = {
                'text': [
                    (159, 259.6, is_emri_no),  # İş emri numarası 6 haneli formatta
                    (90, 259.6, f"{servis['plaka']}"),
                ]
            }

            # Cari ad unvanını bölme mantığı
            cari_ad_unvan = cari.get('cari_ad_unvan', '')
            cari_ad_unvan_lines = self.split_cari_ad_unvan(cari_ad_unvan)

            # Her satırı PDF'e ekle (cari adı için font boyutu 8)
            for i, line in enumerate(cari_ad_unvan_lines):
                eklemeler['text'].append((45, 250 - (i * 5), line, 8))

            # Diğer bilgileri ekle (font 9)
            eklemeler['text'].extend([
                (50, 237, f"{cari.get('cep_telefonu', '')}", 9),
                (50, 232, f"{vergi_no}", 9),
                (50, 223, f"{arac.get('arac_tipi', '')}", 9),
                (50, 217.2, f"{arac.get('marka', '')} {arac.get('model', '')}", 9),
                (50, 211, f"{arac.get('model_yili', '')}", 9),
                (120, 223, f"{arac.get('sasi_no', '')}", 9),
                (120, 218, f"{arac.get('motor_no', '')}", 9),
                (58, 204, f"{servis['servis_tarihi']}", 9),
                (58, 192, f"{servis['servis_tarihi']}", 9),
                (25, 181, f"{servis.get('aciklama', '')}", 9),
                (175, 68, f"{toplam_kdv_haric:,.2f} TL", 9),
                (175, 63, f"{kdv_tutari_genel:,.2f} TL", 9),
                (175, 58, f"{genel_toplam:,.2f} TL", 9)
            ])

            # İşlemleri eklemeler listesine ekle (font 9)
            for item in islem_texts:
                if len(item) == 3:
                    eklemeler['text'].append((*item, 9))
                else:
                    eklemeler['text'].append(item)

            # Dosya kaydetme dialogunu göster
            default_filename = f"servis_{is_emri_no}_{servis['plaka']}_{servis['servis_tarihi']}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "PDF Dosyasını Kaydet",
                default_filename,
                "PDF Dosyaları (*.pdf)"
            )

            if file_path:
                # PDF'i oluştur
                mevcut_pdf_duzenle("classiccar.pdf", file_path, eklemeler, font_size=10)
                QMessageBox.information(self, "Başarılı", f"PDF dosyası oluşturuldu:\n{file_path}")
            else:
                QMessageBox.information(self, "Bilgi", "PDF oluşturma işlemi iptal edildi.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken bir hata oluştu:\n{str(e)}")

    def split_cari_ad_unvan(self, text, max_words=7, max_chars=40):
        words = text.split()
        lines = []
        line_words = []
        line_length = 0

        for word in words:
            line_words.append(word)
            line_length += len(word) + 1  # +1 boşluk için
            # Satırı bitirme koşulu: 7 kelime olduysa veya satır uzunluğu 40 karakteri geçtiyse
            if len(line_words) == max_words or line_length > max_chars:
                lines.append(' '.join(line_words))
                line_words = []
                line_length = 0

        if line_words:
            lines.append(' '.join(line_words))
        return lines

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
                s.servis_tutar,
                s.arac_getiren_kisi,
                (SELECT COUNT(*) FROM islemler WHERE servis_id = s.id) as islem_sayisi
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