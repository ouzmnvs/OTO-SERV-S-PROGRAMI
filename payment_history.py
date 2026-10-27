from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QDateEdit,
    QDesktopWidget, QFrame, QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, QSize, QDate
from qtawesome import icon
import sys
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import datetime
from odeme_al import OdemeAlForm
from hizli_tablo import HizliTablo

class PaymentHistoryForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ödeme Geçmişi")
        self.resize_and_center()
        self.init_ui()
        self.setWindowIcon(icon('fa5s.file')) # Add a file icon
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
        btn.setMinimumHeight(60)
        btn.setMinimumWidth(60)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 12px;
                font-weight: bold;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 6px;
                padding: 6px 12px;
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

        # Buton bağlantıları
        btn_detay.clicked.connect(self.detay_goruntule)
        btn_pdf.clicked.connect(self.pdf_aktar)
        btn_kapat.clicked.connect(self.close)

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
            font-size: 12px;
            padding: 6px 10px;
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
                font-size: 12px;
                padding: 4px 8px;
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
                font-size: 12px;
                padding: 4px 8px;
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
        
        # Filtreleme ve temizleme butonlarının bağlantılarını ekle
        btn_filtrele.clicked.connect(self.filter_table)
        btn_temizle.clicked.connect(self.clear_filter)
        
        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)
        self.cari_filtre.returnPressed.connect(self.filter_table)
        self.cari_filtre.textChanged.connect(self.filter_table)
        ana_layout.addWidget(filtre_frame)

        # Tablo (binlerce ödemede de hızlı kalması için yalnızca görünen satırları çizer)
        self.table = HizliTablo()
        self.table.sag_hizala(5)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Plaka", "Cari Kodu", "Cari Ünvanı", "Tarih", "Ödeme Tipi", "Alınan Tutar"
        ])

        self.table.setStyleSheet("""
            QTableView {
                gridline-color: #d0d0d0;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #bbb;
            }
        """)
        
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        ana_layout.addWidget(self.table)

        # Alt bilgi
        self.alt_bilgi = QLabel("")
        self.alt_bilgi.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333;
                padding: 8px 0;
            }
        """)
        ana_layout.addWidget(self.alt_bilgi)

        self.setLayout(ana_layout)

        self.baslangic_tarihi.dateChanged.connect(self.bitis_tarihini_guncelle)
        self.baslangic_tarihi.dateChanged.connect(self.filter_table)
        self.bitis_tarihi.dateChanged.connect(self.filter_table)

        self.tum_odemeler = []
        self.load_payments()
        self.tarih_araligini_sifirla()

    def bitis_tarihini_guncelle(self):
        yeni_bitis = self.baslangic_tarihi.date().addDays(7)
        self.bitis_tarihi.setDate(yeni_bitis)

    def load_payments(self):
        """Ödemeleri okur ve mevcut filtreyi uygulayarak tabloya yazar."""
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        # tarih yerel saatle kaydedildiği için olduğu gibi gösterilir ('localtime' dönüşümü saati 3 saat kaydırıyordu)
        cursor.execute("""
            SELECT k.id, k.plaka, k.cari_kodu, k.cari_ad_unvan, k.tarih, k.odeme_tipi, k.tutar, c.cep_telefonu
            FROM KASA k
            LEFT JOIN cariler c ON k.cari_kodu = c.cari_kodu
            ORDER BY k.tarih DESC
        """)
        self.tum_odemeler = cursor.fetchall()
        conn.close()
        # (id, plaka, cari_kodu, cari_ad_unvan, tarih, odeme_tipi, tutar, telefon)
        self.table.kayitlari_yukle(
            self.tum_odemeler,
            hucreler=lambda o: (o[1], o[2], o[3], self.tarih_metni(o[4]), o[5], f"{o[6] or 0:,.2f} TL"),
            kimlik=lambda o: o[0],  # Detay görüntülemede kaydı bulmak için kasa id'si
            arama_alanlari=lambda o: (o[1], o[2], o[3], o[7], o[5]),
        )
        self.filter_table()

    @staticmethod
    def tarih_metni(tarih):
        """'2025-06-17 18:40:04' -> '17.06.2025 18:40:04' (strptime'dan çok daha hızlı; binlerce satırda fark eder)."""
        t = str(tarih or "")
        if len(t) >= 19 and t[4] == "-" and t[7] == "-" and t[10] == " ":
            return f"{t[8:10]}.{t[5:7]}.{t[:4]} {t[11:19]}"
        return t

    def tarih_araligini_sifirla(self):
        """Tarih aralığını tüm ödemeleri kapsayacak şekilde ayarlar (yalnızca metinle arama da çalışsın)."""
        # ISO tarihler metin olarak sıralanabilir; yalnızca en küçük ve en büyük tarih çözülür
        gunler = [str(o[4])[:10] for o in self.tum_odemeler if o[4]]
        tarihler = [QDate.fromString(g, "yyyy-MM-dd") for g in (min(gunler), max(gunler))] if gunler else []
        tarihler = [t for t in tarihler if t.isValid()]
        bugun = QDate.currentDate()
        for tarih_alani in (self.baslangic_tarihi, self.bitis_tarihi):
            tarih_alani.blockSignals(True)
        self.baslangic_tarihi.setDate(min(tarihler + [bugun]))
        self.bitis_tarihi.setDate(max(tarihler + [bugun]))
        for tarih_alani in (self.baslangic_tarihi, self.bitis_tarihi):
            tarih_alani.blockSignals(False)
        self.filter_table()

    def detay_goruntule(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ödeme kaydı seçin!")
            return

        try:
            # Seçili satırdan bilgileri al
            plaka = self.table.item(selected_row, 0).text()
            cari_kodu = self.table.item(selected_row, 1).text()
            cari_ad_unvan = self.table.item(selected_row, 2).text()
            tutar = float(self.table.item(selected_row, 5).text().replace(" TL", "").replace(",", ""))
            kasa_id = self.table.item(selected_row, 0).data(Qt.UserRole)

            # Veritabanından servis_id ve kaynak_id bilgilerini al
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT servis_id, kaynak_id, odeme_kaynagi
                FROM KASA
                WHERE id = ?
            """, (kasa_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                QMessageBox.warning(self, "Uyarı", "Ödeme detayları bulunamadı!")
                return

            servis_id, kaynak_id, odeme_kaynagi = row

            # OdemeAlForm'u aç
            odeme_form = OdemeAlForm(
                servis_id=servis_id,
                cari_kodu=cari_kodu,
                cari_ad_unvan=cari_ad_unvan,
                telefon="",  # Telefon bilgisi yok
                toplam_tutar=tutar,
                parent=self,
                plaka=plaka,
                odeme_kaynagi=odeme_kaynagi,
                kaynak_id=kaynak_id
            )

            # Form alanlarını devre dışı bırak
            for widget in odeme_form.findChildren(QLineEdit):
                widget.setReadOnly(True)
            for widget in odeme_form.findChildren(QComboBox):
                widget.setEnabled(False)
            for widget in odeme_form.findChildren(QDateEdit):
                widget.setEnabled(False)
            for widget in odeme_form.findChildren(QPushButton):
                widget.setEnabled(False)

            odeme_form.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Detay görüntülenirken bir hata oluştu:\n{str(e)}")

    def pdf_aktar(self):
        try:
            # PDF dosya adı: {tarih}_odeme_gecmisi.pdf
            tarih = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_name = f"{tarih}_odeme_gecmisi.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", default_name, "PDF Files (*.pdf)")
            if not path:
                return

            # PDF oluştur (Türkçe karakterler için iş emri PDF'leriyle aynı font)
            from pdf_belgeler import turkce_fontlar, liste_tablosu, para_bicimi
            font_name, _ = turkce_fontlar()
            doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                                    topMargin=15 * mm, bottomMargin=15 * mm)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Turkish', fontName=font_name, fontSize=12, leading=16))
            styles.add(ParagraphStyle(name='TurkishTitle', fontName=font_name, fontSize=16, leading=20, alignment=1))
            styles.add(ParagraphStyle(name='TurkishHeader', fontName=font_name, fontSize=14, leading=18, alignment=1))

            elements = []

            # Başlık
            elements.append(Paragraph("ÖDEME GEÇMİŞİ", styles['TurkishTitle']))
            elements.append(Spacer(1, 12))

            # Tarih bilgisi
            elements.append(Paragraph(f"Oluşturulma Tarihi: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", styles['Turkish']))
            elements.append(Spacer(1, 12))

            # Tablo başlıkları
            headers = ["Plaka", "Cari Kodu", "Cari Ünvanı", "Tarih", "Ödeme Tipi", "Alınan Tutar"]
            data = [headers]

            # Tablo verileri
            toplam_tutar = 0
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item is not None:
                        if col == 3:  # Tarih sütunu - sadece tarih göster
                            try:
                                tarih = datetime.datetime.strptime(item.text(), "%d.%m.%Y %H:%M:%S")
                                row_data.append(tarih.strftime("%d.%m.%Y"))
                            except:
                                row_data.append(item.text())
                        elif col == 5:  # Alınan Tutar sütunu
                            try:
                                tutar = float(item.text().replace(" TL", "").replace(",", ""))
                                toplam_tutar += tutar
                                row_data.append(para_bicimi(tutar))
                            except:
                                row_data.append(item.text())
                        else:
                            row_data.append(item.text())
                    else:
                        row_data.append("")
                data.append(row_data)

            # Tablo oluştur (uzun metinler hücre içinde alt satıra kayar, tablo sayfaya sığar)
            t = liste_tablosu(headers, data[1:], [13, 10, 33, 13, 13, 18], doc.width, sag_hizali={5})
            elements.append(t)

            # Alt bilgiler
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Toplam Kayıt: {self.table.rowCount()}", styles['Turkish']))
            elements.append(Paragraph(f"Toplam Alınan: {para_bicimi(toplam_tutar)}", styles['Turkish']))

            # PDF'i oluştur
            doc.build(elements)
            QMessageBox.information(self, "Başarılı", "Ödeme geçmişi başarıyla PDF olarak kaydedildi.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken bir hata oluştu:\n{str(e)}")

    def filter_table(self):
        """Arama metni (plaka, cari kodu/adı, telefon, ödeme tipi) ve tarih aralığına uyan ödemeleri listeler."""
        if not hasattr(self, "tum_odemeler"):
            return  # Arayüz kurulurken tetiklenen sinyaller
        baslangic = self.baslangic_tarihi.date().toString("yyyy-MM-dd")
        bitis = self.bitis_tarihi.date().toString("yyyy-MM-dd")
        self.table.filtrele(self.cari_filtre.text(), lambda o: baslangic <= str(o[4] or "")[:10] <= bitis)
        odemeler = self.table.gorunen_kayitlar()

        toplam_tutar = sum(o[6] or 0 for o in odemeler)
        gun_farki = self.baslangic_tarihi.date().daysTo(self.bitis_tarihi.date()) + 1
        self.alt_bilgi.setText(
            f"{len(odemeler)} adet kayıt listeleniyor | "
            f"Toplam Alınan: {toplam_tutar:,.2f} TL | "
            f"{gun_farki} Günlük Kayıt"
        )

    def clear_filter(self):
        """Filtrelemeyi temizler ve tüm ödemeleri gösterir"""
        self.cari_filtre.blockSignals(True)
        self.cari_filtre.clear()
        self.cari_filtre.blockSignals(False)
        self.tarih_araligini_sifirla()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaymentHistoryForm()
    window.show()
    sys.exit(app.exec_())