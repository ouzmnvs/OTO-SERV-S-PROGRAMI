from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QSizePolicy, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_cari_list_for_table, load_cari_plakalari
from arama import arama_anahtari
from hizli_tablo import HizliTablo
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
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı, Telefon veya Plaka")
        self.filtre_input.textChanged.connect(self.filtrele)
        self.filtre_input.returnPressed.connect(self.filtrele)
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
        # Cari ekleme formundaki tiplerle aynı olmalı
        self.filtre_combo.addItems(["Tüm Cari Tipleri", "Bireysel", "Kurumsal", "Diğer"])
        self.filtre_combo.currentIndexChanged.connect(self.filtrele)
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

        # Tablo (binlerce caride de hızlı kalması için yalnızca görünen satırları çizer)
        self.table = HizliTablo()
        self.table.sag_hizala(5)
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
            QTableView {
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
        plakalar = load_cari_plakalari()
        self.table.kayitlari_yukle(
            cari_list,
            hucreler=lambda c: (c[0], c[1], c[2], c[3], c[5], f"{(c[4] or 0):.2f}"),
            arama_alanlari=lambda c: (c[0], c[1], c[2], c[5], plakalar.get(c[0])),
        )
        # Kayıt ekleme/düzenleme sonrası yenilemede mevcut filtre korunur
        self.filtrele()

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
            # Türkçe karakterler (Ç, Ü, Ö, Ş, İ...) iş emri PDF'leriyle aynı, düzeltilmiş fontla yazılır
            from pdf_belgeler import turkce_fontlar, liste_tablosu, para_bicimi
            from reportlab.lib.units import mm
            font_name, _ = turkce_fontlar()


            # PDF dosya adı: {tarih}_cari_listesi.pdf
            tarih = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            default_name = f"{tarih}_cari_listesi.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", default_name, "PDF Files (*.pdf)")
            if not path:
                return

            # PDF oluştur
            doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                                    topMargin=15 * mm, bottomMargin=15 * mm)
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

            # Tablo verileri (filtreyle gizlenen satırlar PDF'e alınmaz)
            toplam_tutar = 0
            kayit_sayisi = 0
            for row in range(self.table.rowCount()):
                if self.table.isRowHidden(row):
                    continue
                kayit_sayisi += 1
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item is not None:
                        if col == 5:  # Toplam Tutar sütunu
                            try:
                                tutar = float(item.text().replace(' TL', '').replace(',', '.')) # Para birimi ve virgül kontrolü
                                toplam_tutar += tutar
                                row_data.append(para_bicimi(tutar))  # 1.234,50 TL
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

            # Tablo oluştur (uzun metinler hücre içinde alt satıra kayar, tablo sayfaya sığar)
            t = liste_tablosu(headers, data[1:], [9, 28, 13, 10, 24, 16], doc.width, sag_hizali={5})
            elements.append(t)

            # Alt bilgiler
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Toplam Kayıt: {kayit_sayisi}", styles['Turkish']))
            elements.append(Paragraph(f"Toplam Tutar: {para_bicimi(toplam_tutar)}", styles['Turkish']))


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
        """Arama metni (cari kodu, adı, telefon, açıklama, plaka) ve cari tipine göre listeyi süzer."""
        cari_tipi = arama_anahtari(self.filtre_combo.currentText()) if self.filtre_combo.currentIndex() > 0 else None
        self.table.filtrele(
            self.filtre_input.text(),
            None if cari_tipi is None else (lambda c: arama_anahtari(c[3]) == cari_tipi),
        )
        gorunen = self.table.gorunen_kayitlar()
        toplam_tutar = sum(c[4] or 0 for c in gorunen)
        self.alt_bilgi.setText(
            f"{len(gorunen)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:.2f} TL"
        )

    def temizle(self):
        """Filtreleri temizle ve tüm listeyi göster"""
        self.filtre_input.clear()
        self.filtre_combo.setCurrentIndex(0)
        self.filtrele()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CariListForm()
    form.show()
    sys.exit(app.exec_())