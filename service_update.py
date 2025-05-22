from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import add_islem, load_service_operations, delete_service, update_servis

class ServiceUpdateForm(QDialog):
    def __init__(self):
        super().__init__()
        self.servis_id = None
        self.pending_operations = []
        self.deleted_operations = []
        self.existing_operations = []
        self.setWindowTitle("İş Emri Güncelle")
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.82)
        yukseklik = int(ekran.height() * 0.82)
        self.setFixedSize(genislik, yukseklik)
        x = (ekran.width() - genislik) // 2
        y = (ekran.height() - yukseklik) // 2 - 40
        if y < 0:
            y = 0
        self.move(x, y)
        self.init_ui()

    def init_ui(self):
        ana_layout = QHBoxLayout()
        ana_layout.setSpacing(12)

        # Sol Panel: Araç ve Cari Bilgileri
        sol_panel = QVBoxLayout()
        sol_panel.setSpacing(10)

        # Başlık
        lbl_sol_baslik = QLabel("Araç - Cari Bilgileri")
        lbl_sol_baslik.setStyleSheet("""
            background-color: #333;
            color: white;
            font: bold 18px;
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        sol_panel.addWidget(lbl_sol_baslik)

        # Bilgi Girişi
        bilgi_group = QGroupBox("Cari ve Araç Bilgilerini Giriniz")
        bilgi_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 12px;
                top: 2px;
                padding: 0 4px;
            }
        """)
        bilgi_layout = QGridLayout()
        bilgi_layout.setVerticalSpacing(12)
        bilgi_layout.setHorizontalSpacing(8)

        label_style = "font-size: 16px; font-weight: 600; color: #222;"
        input_style = """
            QLineEdit, QComboBox {
                font-size: 17px;
                padding: 7px 10px;
                border-radius: 6px;
                border: 1.5px solid #bbb;
                background: #fafbfc;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #1976d2;
                background: #fff;
            }
        """

        bilgi_layout.addWidget(self._label("Cari Kodu", label_style), 0, 0)
        self.txt_cari_kodu = QLineEdit()
        self.txt_cari_kodu.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_cari_kodu, 0, 1)

        bilgi_layout.addWidget(self._label("Cari Adı / Ünvanı", label_style), 1, 0)
        self.txt_cari_unvan = QLineEdit()
        self.txt_cari_unvan.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_cari_unvan, 1, 1)

        bilgi_layout.addWidget(self._label("Telefon", label_style), 2, 0)
        self.txt_telefon = QLineEdit()
        self.txt_telefon.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_telefon, 2, 1)

        bilgi_layout.addWidget(self._label("Cari Tipi *", label_style), 3, 0)
        self.cmb_cari_tipi = QComboBox()
        self.cmb_cari_tipi.setStyleSheet(input_style)
        self.cmb_cari_tipi.addItems(["", "Bireysel", "Kurumsal"])
        bilgi_layout.addWidget(self.cmb_cari_tipi, 3, 1)

        bilgi_layout.addWidget(self._label("Plaka *", label_style), 4, 0)
        self.txt_plaka = QLineEdit()
        self.txt_plaka.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_plaka, 4, 1)

        bilgi_layout.addWidget(self._label("Araç Tipi *", label_style), 5, 0)
        self.cmb_arac_tipi = QComboBox()
        self.cmb_arac_tipi.setStyleSheet(input_style)
        self.cmb_arac_tipi.addItems(["", "Otomobil", "Kamyonet", "Minibüs", "Diğer"])
        bilgi_layout.addWidget(self.cmb_arac_tipi, 5, 1)

        bilgi_layout.addWidget(self._label("Model Yılı", label_style), 6, 0)
        self.txt_model_yili = QLineEdit()
        self.txt_model_yili.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_model_yili, 6, 1)

        bilgi_layout.addWidget(self._label("Marka", label_style), 7, 0)
        self.txt_marka = QLineEdit()
        self.txt_marka.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_marka, 7, 1)

        bilgi_layout.addWidget(self._label("Model", label_style), 8, 0)
        self.txt_model = QLineEdit()
        self.txt_model.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.txt_model, 8, 1)

        bilgi_group.setLayout(bilgi_layout)
        sol_panel.addWidget(bilgi_group)

        sol_panel.addStretch(1)
        ana_layout.addLayout(sol_panel, 2)

        # Sağ Panel: İşlem ve Özet Bilgileri
        sag_panel = QVBoxLayout()
        sag_panel.setSpacing(10)

        # Sağ başlık
        lbl_sag_baslik = QLabel("İşlem ve Özet Bilgileri")
        lbl_sag_baslik.setStyleSheet("""
            background-color: #333;
            color: white;
            font: bold 18px;
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        sag_panel.addWidget(lbl_sag_baslik)

        # --- İşlem Ekleme Alanı ---
        islem_ekle_layout = QHBoxLayout()
        self.input_islem_aciklama = QLineEdit()
        self.input_islem_aciklama.setPlaceholderText("İşlem Açıklaması")
        self.input_islem_aciklama.setMinimumWidth(180)
        self.input_islem_tutar = QLineEdit()
        self.input_islem_tutar.setPlaceholderText("Tutar")
        self.input_islem_tutar.setMinimumWidth(80)
        self.input_islem_kdv = QLineEdit()
        self.input_islem_kdv.setPlaceholderText("KDV (%)")
        self.input_islem_kdv.setMinimumWidth(60)
        self.input_islem_kdv.setText("20")  # Varsayılan olarak 20
        self.input_islem_ek_aciklama = QLineEdit()
        self.input_islem_ek_aciklama.setPlaceholderText("Ek Açıklama")
        self.input_islem_ek_aciklama.setMinimumWidth(120)
        btn_islem_ekle = QPushButton(icon('fa5s.plus', color='#43a047'), "İŞLEM EKLE")
        btn_islem_ekle.setMinimumHeight(38)
        btn_islem_ekle.clicked.connect(self.islem_ekle)

        islem_ekle_layout.addWidget(self.input_islem_aciklama)
        islem_ekle_layout.addWidget(self.input_islem_tutar)
        islem_ekle_layout.addWidget(self.input_islem_kdv)
        islem_ekle_layout.addWidget(self.input_islem_ek_aciklama)
        islem_ekle_layout.addWidget(btn_islem_ekle)
        sag_panel.addLayout(islem_ekle_layout)
        # --- İşlem Ekleme Alanı Sonu ---

        # İşlem Listesi Tablosu
        self.tbl_islemler = QTableWidget(0, 5)
        self.tbl_islemler.setHorizontalHeaderLabels([
            "Açıklama", "Tutar", "KDV (%)", "KDV Tutarı", "Ek Açıklama"
        ])
        self.tbl_islemler.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_islemler.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_islemler.setAlternatingRowColors(True)
        self.tbl_islemler.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                alternate-background-color: #f5f5f5;
                background: #fff;
            }
            QHeaderView::section {
                background: #ececec;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #bbb;
                padding: 6px;
            }
        """)
        sag_panel.addWidget(self.tbl_islemler)

        # Alt Butonlar
        alt_layout = QHBoxLayout()
        alt_layout.setSpacing(10)
        btn_kaydi_sil = self._buton("KAYDI SİL", 'fa5s.trash', '#b71c1c')
        btn_kaydi_sil.clicked.connect(self.kaydi_sil)
        btn_islem_sil = self._buton("İŞLEMİ SİL", 'fa5s.trash', '#b71c1c')
        btn_islem_sil.clicked.connect(self.islem_sil)
        btn_pdf = self._buton("PDF AKTAR", 'fa5s.file-pdf', '#388e3c')
        btn_pdf.clicked.connect(self.pdf_aktar)
        btn_kaydet = self._buton("KAYDET", 'fa5s.save', '#0288d1')
        btn_kaydet.clicked.connect(self.kaydet_servis)
        btn_kapat = self._buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')
        btn_kapat.clicked.connect(self.reject)
        alt_layout.addWidget(btn_kaydi_sil)
        alt_layout.addWidget(btn_islem_sil)
        alt_layout.addWidget(btn_pdf)
        alt_layout.addWidget(btn_kaydet)
        alt_layout.addWidget(btn_kapat)
        sag_panel.addLayout(alt_layout)

        ana_layout.addLayout(sag_panel, 4)
        self.setLayout(ana_layout)

    def _label(self, text, style):
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        return lbl

    def _buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(48)
        btn.setMinimumWidth(170)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                font-weight: 800;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                padding: 8px 18px;
            }}
            QPushButton:hover {{
                background: #e0e0e0;
            }}
        """)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return btn

    # --- Fonksiyonlarınız aynı kalacak ---

    def set_service_details(self, details):
        self.servis_id = details["servis"]["id"]
        self.txt_cari_kodu.setText(details["cari"].get("cari_kodu", ""))
        self.txt_cari_unvan.setText(details["cari"].get("cari_ad_unvan", ""))
        self.txt_telefon.setText(details["cari"].get("cep_telefonu", ""))
        self.cmb_cari_tipi.setCurrentText(details["cari"].get("cari_tipi", ""))
        self.txt_plaka.setText(details["arac"].get("plaka", ""))
        self.cmb_arac_tipi.setCurrentText(details["arac"].get("arac_tipi", ""))
        self.txt_model_yili.setText(str(details["arac"].get("model_yili", "")))
        self.txt_marka.setText(details["arac"].get("marka", ""))
        self.txt_model.setText(details["arac"].get("model", ""))
        self.tbl_islemler.setRowCount(len(details["islemler"]))
        self.existing_operations = []
        for row, islem in enumerate(details["islemler"]):
            self.tbl_islemler.setItem(row, 0, QTableWidgetItem(islem["islem_aciklama"]))
            self.tbl_islemler.setItem(row, 1, QTableWidgetItem(f"{islem['islem_tutari']:.2f}"))
            self.tbl_islemler.setItem(row, 2, QTableWidgetItem(f"{islem['kdv_orani']:.2f}"))
            self.tbl_islemler.setItem(row, 3, QTableWidgetItem(islem["aciklama"]))
            self.existing_operations.append((
                islem["id"],
                islem["islem_aciklama"],
                islem["islem_tutari"],
                islem["kdv_orani"],
                islem["aciklama"]
            ))

    def islem_sil(self):
        selected_row = self.tbl_islemler.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir işlem seçin!")
            return
        islem_aciklama = self.tbl_islemler.item(selected_row, 0).text()
        islem_tutar = self.tbl_islemler.item(selected_row, 1).text()
        kdv_orani = self.tbl_islemler.item(selected_row, 2).text()
        aciklama = self.tbl_islemler.item(selected_row, 3).text()
        mesaj = (
            f"İşlem Açıklaması: {islem_aciklama}\n"
            f"Tutar: {islem_tutar}\n"
            f"KDV Oranı: {kdv_orani}\n"
            f"Açıklama: {aciklama}\n\n"
            "Bu işlemi silmek istediğinize emin misiniz?"
        )
        yanit = QMessageBox.question(self, "İşlem Sil", mesaj, QMessageBox.Yes | QMessageBox.No)
        if yanit != QMessageBox.Yes:
            return
        if selected_row < len(self.existing_operations):
            from database_progress import delete_islem_by_id
            silinecek_islem = self.existing_operations[selected_row]
            delete_islem_by_id(silinecek_islem[0])
            del self.existing_operations[selected_row]
        else:
            idx = selected_row - len(self.existing_operations)
            if idx < len(self.pending_operations):
                del self.pending_operations[idx]
        self.tbl_islemler.removeRow(selected_row)

    def kaydi_sil(self):
        yanit = QMessageBox.question(
            self, "Onay", "Bu servisi ve tüm işlemlerini silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if yanit == QMessageBox.Yes:
            delete_service(self.servis_id)
            QMessageBox.information(self, "Başarılı", "Servis ve işlemleri silindi.")
            self.accept()

    def kaydet_servis(self):
        cari_kodu = self.txt_cari_kodu.text()
        plaka = self.txt_plaka.text()
        aciklama = ""  # Açıklama alanınız varsa ekleyin
        update_servis(self.servis_id, cari_kodu, plaka, aciklama)
        for islem in self.pending_operations:
            add_islem(self.servis_id, *islem)
        self.pending_operations.clear()
        QMessageBox.information(self, "Başarılı", "Servis başarıyla kaydedildi!")
        self.accept()

    def pdf_aktar(self):
        QMessageBox.information(self, "PDF", "PDF oluşturma işlemi burada yapılacak.")

    def islem_ekle(self):
        aciklama = self.input_islem_aciklama.text().strip()
        try:
            tutar = float(self.input_islem_tutar.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Hatalı Giriş", "Tutar sayısal olmalı!")
            return
        try:
            kdv = float(self.input_islem_kdv.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Hatalı Giriş", "KDV oranı sayısal olmalı!")
            return
        ek_aciklama = self.input_islem_ek_aciklama.text().strip()
        if not aciklama:
            QMessageBox.warning(self, "Eksik Bilgi", "İşlem açıklaması giriniz!")
            return
        kdv_tutari = tutar * kdv / 100
        row = self.tbl_islemler.rowCount()
        self.tbl_islemler.insertRow(row)
        self.tbl_islemler.setItem(row, 0, QTableWidgetItem(aciklama))
        self.tbl_islemler.setItem(row, 1, QTableWidgetItem(f"{tutar:.2f}"))
        self.tbl_islemler.setItem(row, 2, QTableWidgetItem(f"{kdv:.2f}"))
        self.tbl_islemler.setItem(row, 3, QTableWidgetItem(f"{kdv_tutari:.2f}"))
        self.tbl_islemler.setItem(row, 4, QTableWidgetItem(ek_aciklama))
        self.pending_operations.append((aciklama, tutar, kdv, kdv_tutari, ek_aciklama))
        # Alanları temizle
        self.input_islem_aciklama.clear()
        self.input_islem_tutar.clear()
        self.input_islem_kdv.setText("20")
        self.input_islem_ek_aciklama.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ServiceUpdateForm()
    form.show()
    sys.exit(app.exec_())