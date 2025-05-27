from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QSizePolicy, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_cari_list_for_table  # Cari bilgilerini yüklemek için fonksiyonu içe aktarın
# from odeme_al import OdemeAlForm
from add_cari import AddCariForm  # En üste ekleyin
from edit_cari import EditCariForm
from cari_servis_hareketleri import CariServisHareketleriForm
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PyQt5.QtWidgets import QFileDialog
import datetime
import os

class CariListForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cari Listesi")
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.85)
        yukseklik = int(ekran.height() * 0.85)
        self.setFixedSize(genislik, yukseklik)
        x = (ekran.width() - genislik) // 2
        y = (ekran.height() - yukseklik) // 2 - 40
        if y < 0:
            y = 0
        self.move(x, y)
        self.init_ui()
        self.setWindowIcon(icon('fa5s.file')) # Add a file icon
    def init_ui(self):
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(10)

        # Üst butonlar
        buton_layout = QHBoxLayout()
        buton_layout.setSpacing(10)
        btn_yeni_cari = self.stil_buton("YENİ CARİ EKLE", 'fa5s.plus-circle', '#43a047')
        btn_yeni_cari.clicked.connect(self.yeni_cari_ekle_ac)
        buton_layout.addWidget(btn_yeni_cari)
        btn_duzenle = self.stil_buton("KAYDI DÜZENLE", 'fa5s.edit', '#0288d1')
        btn_duzenle.clicked.connect(self.kaydi_duzenle_ac)
        buton_layout.addWidget(btn_duzenle)
        btn_sil = self.stil_buton("KAYDI SİL", 'fa5s.trash', '#b71c1c')
        btn_sil.clicked.connect(self.kaydi_sil_ac)
        buton_layout.addWidget(btn_sil)

        btn_servis_hareket = self.stil_buton("SERVİS HAREKETLERİ", 'fa5s.exchange-alt', '#455a64')
        btn_servis_hareket.clicked.connect(self.servis_hareketleri_ac)
        buton_layout.addWidget(btn_servis_hareket)

        # buton_layout.addWidget(self.stil_buton("ÖDEME AL", 'fa5s.money-bill-wave', '#fbc02d'))
        # buton_layout.addWidget(self.stil_buton("ÖDEME YAP", 'fa5s.wallet', '#ff9800'))
        btn_pdf = self.stil_buton("PDF AKTAR", 'fa5s.file-pdf', '#388e3c')
        btn_pdf.clicked.connect(self.pdf_aktar)
        buton_layout.addWidget(btn_pdf)
        buton_layout.addStretch()
        btn_kapat = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')
        btn_kapat.clicked.connect(self.close)
        buton_layout.addWidget(btn_kapat)

        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(8)
        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı,plaka")
        self.filtre_input.setMinimumHeight(32)
        self.filtre_input.setStyleSheet("""
            font-size: 13px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            padding: 4px 10px;
            background: #fffbe8;
        """)
        filtre_layout.addWidget(self.filtre_input)

        self.filtre_combo = QComboBox()
        self.filtre_combo.setMinimumHeight(32)
        self.filtre_combo.setStyleSheet("""
            font-size: 13px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            padding: 4px 10px;
            background: #fffbe8;
        """)
        self.filtre_combo.addItems(["Cari Tipi *", "Müşteri", "Tedarikçi"])
        filtre_layout.addWidget(self.filtre_combo)

        btn_filtrele = QPushButton(icon('fa5s.search', color='#1976d2'), "Filtrele")
        btn_filtrele.setMinimumHeight(32)
        btn_filtrele.setStyleSheet("""
            font-size: 13px; font-weight: 700; background: #e3f2fd; border-radius: 6px; padding: 4px 12px;
        """)
        btn_filtrele.clicked.connect(self.filtrele)
        btn_temizle = QPushButton(icon('fa5s.sync', color='#fbc02d'), "Temizle")
        btn_temizle.setMinimumHeight(32)
        btn_temizle.setStyleSheet("""
            font-size: 13px; font-weight: 700; background: #fffde7; border-radius: 6px; padding: 4px 12px;
        """)
        btn_temizle.clicked.connect(self.temizle)
        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)
        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Cari Kodu", "Cari Adı / Ünvanı", "Telefon No", "Cari Tipi", "Açıklama", "Toplam Tutar"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Açıklama en geniş

        # Diğer sütunları biraz daha geniş yap
        header.setDefaultSectionSize(140)  # Tüm sütunlar için varsayılan genişlik
        header.resizeSection(0, 150)  # Cari Kodu
        header.resizeSection(1, 200)  # Cari Adı / Ünvanı
        header.resizeSection(2, 140)  # Telefon No
        header.resizeSection(3, 120)  # Cari Tipi
        header.resizeSection(5, 120)  # Toplam Tutar

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                alternate-background-color: #f5f5f5;
                background: #fff;
            }
            QHeaderView::section {
                background: #ececec;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #bbb;
                padding: 8px;
            }
        """)

        ana_layout.addWidget(self.table)

        # Alt bilgi
        self.alt_bilgi = QLabel("")
        self.alt_bilgi.setStyleSheet("font-size: 12px; color: #444; padding: 4px 0 0 6px;")
        ana_layout.addWidget(self.alt_bilgi)

        self.setLayout(ana_layout)

        # Verileri yükle
        self.load_cari_list_to_table()

    def load_cari_list_to_table(self):
        """Veritabanından cari bilgilerini tabloya yükler."""
        cari_list = load_cari_list_for_table()  # (cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi, toplam_tutar, aciklama)
        self.table.setRowCount(len(cari_list))

        toplam_tutar = 0
        for row, (cari_kodu, cari_ad_unvan, cep_telefonu, cari_tipi, toplam_tutar_cari, aciklama) in enumerate(cari_list):
            self.table.setItem(row, 0, QTableWidgetItem(cari_kodu))
            self.table.setItem(row, 1, QTableWidgetItem(cari_ad_unvan))
            self.table.setItem(row, 2, QTableWidgetItem(cep_telefonu))
            self.table.setItem(row, 3, QTableWidgetItem(cari_tipi))
            self.table.setItem(row, 5, QTableWidgetItem(f"{toplam_tutar_cari:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(aciklama))
            toplam_tutar += toplam_tutar_cari

        self.alt_bilgi.setText(
            f"{len(cari_list)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:.2f} TL"
        )

    def stil_buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(150)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 13px;
                font-weight: 800;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background: #e0e0e0;
            }}
        """)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return btn

#     def odeme_al(self):
#         selected_row = self.table.currentRow()
#         if selected_row == -1:
#             QMessageBox.warning(self, "Uyarı", "Lütfen bir cari seçin!")
#             return

#         cari_kodu = self.table.item(selected_row, 0).text()
#         cari_ad_unvan = self.table.item(selected_row, 1).text()
#         telefon = self.table.item(selected_row, 2).text()
#         bakiye = float(self.table.item(selected_row, 4).text())

#         odeme_form = OdemeAlForm(cari_kodu, cari_ad_unvan, telefon, bakiye, self)
#         if odeme_form.exec_() == QDialog.Accepted:
#             self.load_cari_list_to_table()

    def yeni_cari_ekle_ac(self):
        try:
            self.add_cari_form = AddCariForm()
            self.add_cari_form.setWindowModality(Qt.ApplicationModal)
            self.add_cari_form.setWindowFlag(Qt.Window)
            self.add_cari_form.setWindowTitle("Yeni Cari Ekle")
            
            # Modal olarak aç ve sonucu kontrol et
            if self.add_cari_form.exec_() == QDialog.Accepted:
                # Yeni cari eklendiğinde listeyi güncelle
                self.load_cari_list_to_table()
                QMessageBox.information(self, "Başarılı", "Yeni cari başarıyla eklendi ve liste güncellendi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Yeni cari eklenirken bir hata oluştu:\n{str(e)}")

    def kaydi_duzenle_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cari seçin!")
            return
        cari_kodu = self.table.item(selected_row, 0).text()
        dialog = EditCariForm(cari_kodu, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_cari_list_to_table()

    def kaydi_sil_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cari seçin!")
            return

        cari_kodu = self.table.item(selected_row, 0).text()
        cari_ad_unvan = self.table.item(selected_row, 1).text()
        cep_telefonu = self.table.item(selected_row, 2).text()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Kaydı Sil")
        msg.setText(
            f"Cari Kodu: {cari_kodu}\n"
            f"Cari Adı/Ünvanı: {cari_ad_unvan}\n"
            f"Telefon: {cep_telefonu}\n\n"
            "Bu cariyi silmek istediğinize emin misiniz?"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        sonuc = msg.exec_()

        if sonuc == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("oto_servis.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cariler WHERE cari_kodu = ?", (cari_kodu,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Başarılı", "Cari kaydı silindi.")
                self.load_cari_list_to_table()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Silme işlemi sırasında hata oluştu:\n{e}")

    def pdf_aktar(self):
        try:
            # Türkçe karakter desteği için font kaydı
            # font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
            # pdfmetrics.registerFont(TTFont("DejaVu", font_path))
            font_path = os.path.join(os.path.dirname(__file__), "arial-unicode-ms.ttf")
            try:
                pdfmetrics.registerFont(TTFont("ArialUnicode", font_path))
                font_name = "ArialUnicode"
            except Exception as e:
                print(f"Hata: Arial Unicode MS fontu yüklenemedi: {e}. Varsayılan font kullanılacak.")
                font_name = "Helvetica" # Varsayılan font
                QMessageBox.warning(self, "Uyarı", f"Arial Unicode MS fontu yüklenemedi ({e}). PDF'de Türkçe karakter sorunları yaşanabilir.")


            # PDF dosya adı: {tarih}_cari_listesi.pdf
            tarih = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            default_name = f"{tarih}_cari_listesi.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", default_name, "PDF Files (*.pdf)")
            if not path:
                return

            # PDF oluştur
            doc = SimpleDocTemplate(path, pagesize=A4)
            styles = getSampleStyleSheet()
            # styles.add(ParagraphStyle(name='Turkish', fontName='DejaVu', fontSize=12, leading=16))
            # styles.add(ParagraphStyle(name='TurkishTitle', fontName='DejaVu', fontSize=16, leading=20, alignment=1))
            # styles.add(ParagraphStyle(name='TurkishHeader', fontName='DejaVu', fontSize=14, leading=18, alignment=1))
            styles.add(ParagraphStyle(name='Turkish', fontName=font_name, fontSize=12, leading=16))
            styles.add(ParagraphStyle(name='TurkishTitle', fontName=font_name, fontSize=16, leading=20, alignment=1))
            styles.add(ParagraphStyle(name='TurkishHeader', fontName=font_name, fontSize=14, leading=18, alignment=1))


            elements = []

            # Başlık
            elements.append(Paragraph("CARİ LİSTESİ", styles['TurkishTitle']))
            elements.append(Spacer(1, 12))

            # Tarih bilgisi
            elements.append(Paragraph(f"Oluşturulma Tarihi: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Turkish']))
            elements.append(Spacer(1, 12))

            # Tablo başlıkları
            headers = ["Cari Kodu", "Cari Adı / Ünvanı", "Telefon No", "Cari Tipi", "Açıklama", "Toplam Tutar"]
            data = [headers]

            # Tablo verileri
            toplam_tutar = 0
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item is not None:
                        if col == 5:  # Toplam Tutar sütunu
                            try:
                                tutar = float(item.text().replace(' TL', '').replace(',', '.')) # Para birimi ve virgül kontrolü
                                toplam_tutar += tutar
                                row_data.append(f"{tutar:,.2f} TL".replace('.', ',')) # Formatı Türkçe yap
                            except ValueError: # Dönüştürme hatası olursa
                                row_data.append(item.text()) # Orjinal metni kullan
                            except Exception as e:
                                print(f"Hata oluştu: {e}")
                                row_data.append(item.text())
                        else:
                            row_data.append(item.text())
                    else:
                        row_data.append("")
                data.append(row_data)

            # Tablo oluştur
            t = Table(data, repeatRows=1, colWidths=[70, 120, 80, 70, 150, 70])
            t.setStyle(TableStyle([
                # ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
                # ('FONTNAME', (0, 0), (-1, 0), 'DejaVu'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
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
            elements.append(Paragraph(f"Toplam Kayıt: {self.table.rowCount()}", styles['Turkish']))
            elements.append(Paragraph(f"Toplam Tutar: {toplam_tutar:,.2f} TL".replace('.', ','), styles['Turkish'])) # Formatı Türkçe yap


            # PDF'i oluştur
            doc.build(elements)
            QMessageBox.information(self, "Başarılı", "Cari listesi başarıyla PDF olarak kaydedildi.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken bir hata oluştu:\n{str(e)}")

    def servis_hareketleri_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cari seçin!")
            return

        cari_kodu = self.table.item(selected_row, 0).text()
        cari_ad = self.table.item(selected_row, 1).text()

        # Yeni form oluştur
        form = CariServisHareketleriForm(cari_kodu, cari_ad, self)
        form.exec_()

    def filtrele(self):
        """Cari listesini filtrele"""
        arama_metni = self.filtre_input.text().strip().lower()
        if not arama_metni:
            self.load_cari_list_to_table()
            return

        # Tüm satırları gizle
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, True)

        # Filtreleme yap
        toplam_tutar = 0
        gorunen_satir = 0
        for row in range(self.table.rowCount()):
            cari_kodu = self.table.item(row, 0).text().lower()
            cari_adi = self.table.item(row, 1).text().lower()
            
            if arama_metni in cari_kodu or arama_metni in cari_adi:
                self.table.setRowHidden(row, False)
                toplam_tutar += float(self.table.item(row, 5).text())
                gorunen_satir += 1

        self.alt_bilgi.setText(
            f"{gorunen_satir} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:.2f} TL"
        )

    def temizle(self):
        """Filtreleri temizle ve tüm listeyi göster"""
        self.filtre_input.clear()
        self.filtre_combo.setCurrentIndex(0)
        self.load_cari_list_to_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CariListForm()
    form.show()
    sys.exit(app.exec_())