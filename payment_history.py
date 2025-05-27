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
        alt_bilgi = QLabel("5 adet kayıt listeleniyor | Toplam Alınan: 18.711,00 TL | 7 Günlük Kayıt")
        alt_bilgi.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333;
                padding: 8px 0;
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
            SELECT plaka, cari_kodu, cari_ad_unvan, datetime(tarih, 'localtime') as tarih, odeme_tipi, tutar
            FROM KASA
            ORDER BY datetime(tarih) DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                if col_idx == 3:  # tarih sütunu
                    # Tarihi Türkçe formata çevir
                    try:
                        tarih = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                        item = QTableWidgetItem(tarih.strftime("%d.%m.%Y %H:%M:%S"))
                    except:
                        item = QTableWidgetItem(str(value))
                elif col_idx == 5:  # tutar
                    item = QTableWidgetItem(f"{value:,.2f} TL")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

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
            tarih = self.table.item(selected_row, 3).text()
            odeme_tipi = self.table.item(selected_row, 4).text()
            tutar = float(self.table.item(selected_row, 5).text().replace(" TL", "").replace(",", ""))

            # Veritabanından servis_id ve kaynak_id bilgilerini al
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT servis_id, kaynak_id, odeme_kaynagi
                FROM KASA
                WHERE plaka = ? AND cari_kodu = ? AND tarih = ? AND tutar = ?
            """, (plaka, cari_kodu, tarih, tutar))
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

            # PDF oluştur
            doc = SimpleDocTemplate(path, pagesize=A4)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Turkish', fontSize=12, leading=16))
            styles.add(ParagraphStyle(name='TurkishTitle', fontSize=16, leading=20, alignment=1))
            styles.add(ParagraphStyle(name='TurkishHeader', fontSize=14, leading=18, alignment=1))

            elements = []

            # Başlık
            elements.append(Paragraph("ODEME GECMISI", styles['TurkishTitle']))
            elements.append(Spacer(1, 12))

            # Tarih bilgisi
            elements.append(Paragraph(f"Olusturulma Tarihi: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", styles['Turkish']))
            elements.append(Spacer(1, 12))

            # Tablo başlıkları
            headers = ["Plaka", "Cari Kodu", "Cari Unvani", "Tarih", "Odeme Tipi", "Alinan Tutar"]
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
                                row_data.append(f"{tutar:,.2f} TL")
                            except:
                                row_data.append(item.text())
                        else:
                            row_data.append(item.text())
                    else:
                        row_data.append("")
                data.append(row_data)

            # Tablo oluştur
            t = Table(data, repeatRows=1, colWidths=[70, 70, 120, 80, 70, 70])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ('GRID', (0, 0), (-1, -1), 0.7, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)

            # Alt bilgiler
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Toplam Kayit: {self.table.rowCount()}", styles['Turkish']))
            elements.append(Paragraph(f"Toplam Alinan: {toplam_tutar:,.2f} TL", styles['Turkish']))

            # PDF'i oluştur
            doc.build(elements)
            QMessageBox.information(self, "Basarili", "Odeme gecmisi basariyla PDF olarak kaydedildi.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF olusturulurken bir hata olustu:\n{str(e)}")

    def filter_table(self):
        """Tabloyu arama kriterine ve tarih aralığına göre filtreler"""
        search_text = self.cari_filtre.text().strip().lower()
        baslangic_tarihi = self.baslangic_tarihi.date().toPyDate()
        bitis_tarihi = self.bitis_tarihi.date().toPyDate()
        
        # Tüm satırları gizle
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, True)
        
        # Her satırı kontrol et
        visible_rows = 0
        toplam_tutar = 0
        
        for row in range(self.table.rowCount()):
            # Cari Kodu (1), Cari Ünvanı (2) ve Tarih (3) sütunlarını kontrol et
            cari_kodu = self.table.item(row, 1).text().lower()
            cari_unvani = self.table.item(row, 2).text().lower()
            tarih_str = self.table.item(row, 3).text()
            
            try:
                # Tarihi datetime nesnesine çevir
                tarih = datetime.datetime.strptime(tarih_str, "%d.%m.%Y %H:%M:%S").date()
                
                # Tarih aralığı kontrolü
                tarih_uygun = baslangic_tarihi <= tarih <= bitis_tarihi
                
                # Arama metni kontrolü
                arama_uygun = (not search_text or 
                             search_text in cari_kodu or 
                             search_text in cari_unvani)
                
                # Eğer hem tarih hem de arama kriterleri uygunsa satırı göster
                if tarih_uygun and arama_uygun:
                    self.table.setRowHidden(row, False)
                    visible_rows += 1
                    
                    # Toplam tutarı hesapla
                    tutar_str = self.table.item(row, 5).text().replace(" TL", "").replace(",", "")
                    toplam_tutar += float(tutar_str)
                    
            except Exception as e:
                print(f"Tarih dönüştürme hatası: {e}")
                continue
        
        # Alt bilgiyi güncelle
        gun_farki = (bitis_tarihi - baslangic_tarihi).days + 1
        self.findChild(QLabel).setText(
            f"{visible_rows} adet kayıt listeleniyor | "
            f"Toplam Alınan: {toplam_tutar:,.2f} TL | "
            f"{gun_farki} Günlük Kayıt"
        )

    def clear_filter(self):
        """Filtrelemeyi temizler ve tüm satırları gösterir"""
        # Arama alanını temizle
        self.cari_filtre.clear()
        
        # Tarih aralığını varsayılan değerlere sıfırla
        self.baslangic_tarihi.setDate(QDate.currentDate())
        self.bitis_tarihi.setDate(self.baslangic_tarihi.date().addDays(7))
        
        # Tüm satırları göster
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, False)
        
        # Toplam tutarı hesapla
        toplam_tutar = 0
        for row in range(self.table.rowCount()):
            tutar_str = self.table.item(row, 5).text().replace(" TL", "").replace(",", "")
            toplam_tutar += float(tutar_str)
        
        # Alt bilgiyi güncelle
        self.findChild(QLabel).setText(
            f"{self.table.rowCount()} adet kayıt listeleniyor | "
            f"Toplam Alınan: {toplam_tutar:,.2f} TL | "
            f"7 Günlük Kayıt"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaymentHistoryForm()
    window.show()
    sys.exit(app.exec_())