from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QDialog,QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QSizePolicy, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_car_list
from add_car import AddCarForm  # En üste ekleyin
from servis_kayitlari import ServisKayitlariForm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import datetime
import sqlite3

class CarListForm(QDialog):
    def __init__(self, dashboard_ref=None):
        super().__init__()
        self.dashboard_ref = dashboard_ref  # Dashboard referansı
        self.setWindowTitle("Araç Listesi")
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.85)
        yukseklik = int(ekran.height() * 0.85)
        self.setFixedSize(genislik, yukseklik)
        # Ortalamak için:
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
        btn_yeni_arac = self.stil_buton("YENİ ARAÇ EKLE", 'fa5s.plus', '#1976d2')
        btn_yeni_arac.clicked.connect(self.yeni_arac_ekle_ac)  # <-- Bağlantı EKLENDİ
        buton_layout.addWidget(btn_yeni_arac)
        btn_duzenle = self.stil_buton("KAYDI DÜZENLE", 'fa5s.edit', '#0288d1')
        btn_duzenle.clicked.connect(self.kaydi_duzenle_ac)
        buton_layout.addWidget(btn_duzenle)
        btn_sil = self.stil_buton("KAYDI SİL", 'fa5s.trash', '#b71c1c')
        btn_sil.clicked.connect(self.kaydi_sil_ac)
        buton_layout.addWidget(btn_sil)
        btn_servis_kayitlari = self.stil_buton("SERVİS KAYITLARI", 'fa5s.book', '#455a64')
        btn_servis_kayitlari.clicked.connect(self.servis_kayitlari_ac)
        buton_layout.addWidget(btn_servis_kayitlari)
        btn_pdf = self.stil_buton("PDF AKTAR", 'fa5s.file-pdf', '#388e3c')
        btn_pdf.clicked.connect(self.pdf_aktar)  # PDF aktar butonuna bağlantı eklendi
        buton_layout.addWidget(btn_pdf)
        buton_layout.addStretch()
        btn_kapat = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')
        btn_kapat.clicked.connect(self.sayfayi_kapat)
        buton_layout.addWidget(btn_kapat)

        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(8)
        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı veya Plaka ile ara...")
        self.filtre_input.setMinimumHeight(32)
        self.filtre_input.setStyleSheet("""
            font-size: 13px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            padding: 4px 10px;
            background: #fffbe8;
        """)
        btn_filtrele = QPushButton(icon('fa5s.search', color='#1976d2'), "Filtrele")
        btn_filtrele.setMinimumHeight(32)
        btn_filtrele.setStyleSheet("""
            font-size: 13px; font-weight: 700; background: #e3f2fd; border-radius: 6px; padding: 4px 12px;
        """)
        btn_temizle = QPushButton(icon('fa5s.sync', color='#fbc02d'), "Temizle")
        btn_temizle.setMinimumHeight(32)
        btn_temizle.setStyleSheet("""
            font-size: 13px; font-weight: 700; background: #fffde7; border-radius: 6px; padding: 4px 12px;
        """)
        btn_filtrele.clicked.connect(self.filtrele_araclar)
        btn_temizle.clicked.connect(self.filtreyi_temizle)
        filtre_layout.addWidget(self.filtre_input)
        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)
        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Cari Kodu", "Cari Adı / Ünvanı", "Araç Plakası", "Araç Tipi", "Model Yılı", "Marka", "Model"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

        # Veritabanından verileri yükle
        self.load_data_to_table()

        ana_layout.addWidget(self.table)

        self.setLayout(ana_layout)

    def load_data_to_table(self, filter_query=None):
        conn = None
        try:
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            if filter_query:
                # JOIN cariler tablosu ve filtreleme
                cursor.execute("""
                    SELECT
                        a.cari_kodu, c.cari_ad_unvan, a.plaka, a.arac_tipi, a.model_yili, a.marka, a.model
                    FROM araclar a
                    LEFT JOIN cariler c ON a.cari_kodu = c.cari_kodu
                    WHERE
                        a.cari_kodu LIKE ? OR
                        c.cari_ad_unvan LIKE ? OR
                        a.plaka LIKE ?
                """, (f'%{filter_query}%', f'%{filter_query}%', f'%{filter_query}%'))
                data = cursor.fetchall()
            else:
                # Tüm verileri yükle
                cursor.execute("""
                    SELECT
                        a.cari_kodu, c.cari_ad_unvan, a.plaka, a.arac_tipi, a.model_yili, a.marka, a.model
                    FROM araclar a
                    LEFT JOIN cariler c ON a.cari_kodu = c.cari_kodu
                """)
                data = cursor.fetchall()

            self.table.setRowCount(len(data))
            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    self.table.setItem(row, col, QTableWidgetItem(str(value) if value is not None else ""))
        except Exception as e:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Araç listesi yüklenirken hata oluştu:\n{e}")
            data = [] # Hata durumunda boş liste ata
        finally:
            if conn:
                conn.close()

    def filtrele_araclar(self):
        filter_text = self.filtre_input.text().strip()
        self.load_data_to_table(filter_text)

    def filtreyi_temizle(self):
        self.filtre_input.clear()
        self.load_data_to_table()

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

    def sayfayi_kapat(self):
        self.hide()
        if self.dashboard_ref:
            self.dashboard_ref.show()

    def yeni_arac_ekle_ac(self):
        def tabloyu_guncelle():
            self.load_data_to_table()
        self.add_car_form = AddCarForm(dashboard_ref=self, on_saved=tabloyu_guncelle)
        self.add_car_form.setWindowModality(Qt.ApplicationModal)
        self.add_car_form.setWindowFlag(Qt.Window)
        result = self.add_car_form.exec_()  # Modal olarak aç
        if result == QDialog.Accepted:
            self.load_data_to_table()

    def servis_kayitlari_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir araç seçin!")
            return
        cari_ad = self.table.item(selected_row, 1).text()
        plaka = self.table.item(selected_row, 2).text()
        arac_tipi = self.table.item(selected_row, 3).text()
        model_yili = self.table.item(selected_row, 4).text()
        marka = self.table.item(selected_row, 5).text()
        model = self.table.item(selected_row, 6).text()
        form = ServisKayitlariForm(cari_ad, plaka, arac_tipi, model_yili, marka, model, self)
        form.exec_()

    def kaydi_sil_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir araç seçin!")
            return

        plaka = self.table.item(selected_row, 2).text()
        cari_ad = self.table.item(selected_row, 1).text()
        marka = self.table.item(selected_row, 5).text()
        model = self.table.item(selected_row, 6).text()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Kaydı Sil")
        msg.setText(
            f"Araç Plakası: {plaka}\n"
            f"Cari Adı: {cari_ad}\n"
            f"Marka/Model: {marka} {model}\n\n"
            "Bu aracı silmek istediğinize emin misiniz?"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        sonuc = msg.exec_()

        if sonuc == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("oto_servis.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM araclar WHERE plaka = ?", (plaka,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Başarılı", "Araç kaydı silindi.")
                self.load_data_to_table()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Silme işlemi sırasında hata oluştu:\n{e}")

    def kaydi_duzenle_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir araç seçin!")
            return

        # Seçili aracın tüm bilgilerini al
        cari_kodu = self.table.item(selected_row, 0).text()
        cari_ad = self.table.item(selected_row, 1).text()
        plaka = self.table.item(selected_row, 2).text()
        arac_tipi = self.table.item(selected_row, 3).text()
        model_yili = self.table.item(selected_row, 4).text()
        marka = self.table.item(selected_row, 5).text()
        model = self.table.item(selected_row, 6).text()

        # Veritabanından araç detaylarını al
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                cari_kodu, plaka, arac_tipi, model_yili, marka, model,
                motor_no, sasi_no, yakit_cinsi, aciklama, motor_hacmi, motor_gucu_kw
            FROM araclar 
            WHERE plaka = ?
        """, (plaka,))
        arac_detay = cursor.fetchone()
        conn.close()

        if arac_detay:
            # AddCarForm'u düzenleme modunda aç
            def tabloyu_guncelle():
                self.load_data_to_table()

            self.add_car_form = AddCarForm(
                dashboard_ref=self,
                on_saved=tabloyu_guncelle,
                edit_mode=True,
                car_data={
                    "cari_kodu": arac_detay[0],
                    "plaka": arac_detay[1],
                    "arac_tipi": arac_detay[2],
                    "model_yili": arac_detay[3],
                    "marka": arac_detay[4],
                    "model": arac_detay[5],
                    "motor_no": arac_detay[6],
                    "sasi_no": arac_detay[7],
                    "yakit_cinsi": arac_detay[8],
                    "aciklama": arac_detay[9],
                    "motor_hacmi": arac_detay[10],
                    "motor_gucu_kw": arac_detay[11]
                }
            )
            self.add_car_form.setWindowModality(Qt.ApplicationModal)
            self.add_car_form.setWindowFlag(Qt.Window)
            result = self.add_car_form.exec_()
            if result == QDialog.Accepted:
                self.load_data_to_table()
        else:
            QMessageBox.warning(self, "Uyarı", "Araç detayları bulunamadı!")

    def pdf_aktar(self):
        try:
            # Türkçe karakter desteği için font kaydı
            font_path = os.path.join(os.path.dirname(__file__), "arial-unicode-ms.ttf")
            try:
                pdfmetrics.registerFont(TTFont("ArialUnicode", font_path))
                font_name = "ArialUnicode"
            except Exception as e:
                print(f"Hata: Arial Unicode MS fontu yüklenemedi: {e}. Varsayılan font kullanılacak.")
                font_name = "Helvetica" # Varsayılan font
                QMessageBox.warning(self, "Uyarı", f"Arial Unicode MS fontu yüklenemedi ({e}). PDF'de Türkçe karakter sorunları yaşanabilir.")

            # PDF dosya adı: {tarih}_arac_listesi.pdf
            tarih = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            default_name = f"{tarih}_arac_listesi.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", default_name, "PDF Files (*.pdf)")
            if not path:
                return

            # PDF oluştur
            doc = SimpleDocTemplate(path, pagesize=A4)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Turkish', fontName=font_name, fontSize=12, leading=16))
            styles.add(ParagraphStyle(name='TurkishTitle', fontName=font_name, fontSize=16, leading=20, alignment=1))
            styles.add(ParagraphStyle(name='TurkishHeader', fontName=font_name, fontSize=14, leading=18, alignment=1))

            elements = []

            # Başlık
            elements.append(Paragraph("ARAÇ LİSTESİ", styles['TurkishTitle']))
            elements.append(Spacer(1, 12))

            # Tarih bilgisi
            elements.append(Paragraph(f"Oluşturulma Tarihi: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Turkish']))
            elements.append(Spacer(1, 12))

            # Tablo başlıkları
            headers = ["Cari Kodu", "Cari Adı / Ünvanı", "Araç Plakası", "Araç Tipi", "Model Yılı", "Marka", "Model"]
            data = [headers]

            # Tablo verileri
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                data.append(row_data)

            # Tablo oluştur
            t = Table(data, repeatRows=1, colWidths=[70, 120, 80, 70, 70, 70, 70])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
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

            # PDF'i oluştur
            doc.build(elements)
            QMessageBox.information(self, "Başarılı", "Araç listesi başarıyla PDF olarak kaydedildi.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken bir hata oluştu:\n{str(e)}")

# Dashboard'dan açarken:
# self.car_list_form = CarListForm(self)
# self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CarListForm()
    form.show()
    sys.exit(app.exec_())