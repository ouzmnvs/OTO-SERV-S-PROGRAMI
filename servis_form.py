from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QFrame, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from cari_select_list import CariSelectListForm  # CariSelectListForm'u içe aktarın
from car_select_list import CarSelectListForm  # CarSelectListForm'u içe aktarın
from database_progress import add_servis, add_islem  # Servis ekleme fonksiyonunu içe aktarın
from datetime import datetime
class ServisForm(QDialog):  # QWidget yerine QDialog kullanıyoruz
    def __init__(self, dashboard_ref=None):
        super().__init__()
        self.dashboard_ref = dashboard_ref
        self.setWindowTitle("İş Emri Formu")
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

        # Cari ve Araç Bilgilerini Giriniz (Sadece cari ile ilgili kısım güncellendi)
        bilgi_layout.addWidget(self._label("Cari Kodu", label_style), 0, 0)
        self.cari_kodu = QLineEdit()
        self.cari_kodu.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.cari_kodu, 0, 1)

        bilgi_layout.addWidget(self._label("Cari Adı / Ünvanı", label_style), 1, 0)
        self.cari_unvan = QLineEdit()
        self.cari_unvan.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.cari_unvan, 1, 1)

        bilgi_layout.addWidget(self._label("Telefon", label_style), 2, 0)
        self.telefon = QLineEdit()
        self.telefon.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.telefon, 2, 1)

        bilgi_layout.addWidget(self._label("Cari Tipi *", label_style), 3, 0)
        self.cari_tipi = QComboBox()
        self.cari_tipi.setStyleSheet(input_style)
        self.cari_tipi.addItems(["", "Bireysel","Kurumsal"])
        bilgi_layout.addWidget(self.cari_tipi, 3, 1)

        sec_btn = QPushButton(icon('fa5s.user-check', color='black'), "Seç")
        sec_btn.setMinimumHeight(36)
        sec_btn.setStyleSheet("font-size:16px; font-weight:700; padding:6px 18px;")
        sec_btn.clicked.connect(self.open_cari_select_list)  # "Seç" butonuna metodu bağlayın
        bilgi_layout.addWidget(sec_btn, 3, 2)

        bilgi_layout.addWidget(self._label("Plaka *", label_style), 4, 0)
        self.plaka = QLineEdit()
        self.plaka.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.plaka, 4, 1)

        bilgi_layout.addWidget(self._label("Araç Tipi *", label_style), 5, 0)
        self.arac_tipi = QComboBox()
        self.arac_tipi.setStyleSheet(input_style)
        self.arac_tipi.addItems(["", "Otomobil", "Kamyonet", "Minibüs", "Diğer"])
        bilgi_layout.addWidget(self.arac_tipi, 5, 1)

        bilgi_layout.addWidget(self._label("Model Yılı", label_style), 6, 0)
        self.model_yili = QLineEdit()
        self.model_yili.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.model_yili, 6, 1)

        bilgi_layout.addWidget(self._label("Marka", label_style), 7, 0)
        self.marka = QLineEdit()
        self.marka.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.marka, 7, 1)

        bilgi_layout.addWidget(self._label("Model", label_style), 8, 0)
        self.model = QLineEdit()
        self.model.setStyleSheet(input_style)
        bilgi_layout.addWidget(self.model, 8, 1)

        arac_sec_btn = QPushButton(icon('fa5s.car', color='blue'), "Seç")
        arac_sec_btn.setMinimumHeight(36)
        arac_sec_btn.setStyleSheet("font-size:16px; font-weight:700; padding:6px 18px;")
        arac_sec_btn.clicked.connect(self.open_car_select_list)  # "Seç" butonuna metodu bağlayın
        bilgi_layout.addWidget(arac_sec_btn, 8, 2)

        bilgi_group.setLayout(bilgi_layout)
        sol_panel.addWidget(bilgi_group)

        # Geçmiş Servis Kayıtları
        gecmis_group = QGroupBox("Geçmiş Servis Kayıtları")
        gecmis_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        gecmis_layout = QVBoxLayout()
        self.gecmis_table = QTableWidget(0, 3)
        self.gecmis_table.setHorizontalHeaderLabels(["Tarih", "Tutar", "Durum"])
        self.gecmis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.gecmis_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gecmis_table.setAlternatingRowColors(True)
        self.gecmis_table.setStyleSheet("""
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
        gecmis_layout.addWidget(self.gecmis_table)
        gecmis_group.setLayout(gecmis_layout)
        sol_panel.addWidget(gecmis_group)

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

        # İşlem Bilgileri Girişi
        islem_group = QGroupBox("İşlem Bilgilerini Giriniz")
        islem_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        islem_layout = QGridLayout()
        islem_layout.setVerticalSpacing(12)
        islem_layout.setHorizontalSpacing(8)

        islem_layout.addWidget(self._label("İşlem Açıklaması", label_style), 0, 0)
        self.islem_aciklama = QLineEdit()
        self.islem_aciklama.setStyleSheet(input_style)
        islem_layout.addWidget(self.islem_aciklama, 0, 1)

        islem_layout.addWidget(self._label("İşlem Tutarı", label_style), 0, 2)
        self.islem_tutar = QLineEdit()
        self.islem_tutar.setStyleSheet(input_style)
        islem_layout.addWidget(self.islem_tutar, 0, 3)

        islem_layout.addWidget(self._label("Açıklama", label_style), 0, 4)
        self.islem_ek_aciklama = QLineEdit()
        self.islem_ek_aciklama.setStyleSheet(input_style)
        islem_layout.addWidget(self.islem_ek_aciklama, 0, 5)

        islem_layout.addWidget(self._label("KDV Oranı (%)", label_style), 0, 6)
        self.kdv_orani = QLineEdit()
        self.kdv_orani.setStyleSheet(input_style)
        self.kdv_orani.setPlaceholderText("20")  # Varsayılan KDV oranı
        islem_layout.addWidget(self.kdv_orani, 0, 7)

        btn_islem_ekle = QPushButton(icon('fa5s.plus-circle', color='green'), "Ekle")
        btn_islem_ekle.setMinimumHeight(36)
        btn_islem_ekle.setStyleSheet("font-size:16px; font-weight:700; padding:6px 18px;")
        btn_islem_ekle.clicked.connect(self.islem_ekle)  # İşlem ekleme işlevini bağlayın
        islem_layout.addWidget(btn_islem_ekle, 0, 8)  # "Ekle" butonunu en sağa taşı

        islem_group.setLayout(islem_layout)
        sag_panel.addWidget(islem_group)

        # İşlem Listesi Tablosu
        self.islem_table = QTableWidget(0, 4)  # Sütun sayısını 4'e çıkarıyoruz
        self.islem_table.setHorizontalHeaderLabels(["İşlem Açıklaması", "Tutar", "KDV Oranı", "Açıklama"])  # "KDV Oranı" eklendi
        self.islem_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.islem_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.islem_table.setAlternatingRowColors(True)
        self.islem_table.setStyleSheet("""
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
        sag_panel.addWidget(self.islem_table)

        # İşlem Özeti ve Alt Butonlar
        alt_layout = QHBoxLayout()
        alt_layout.setSpacing(10)

        # İşlem Özeti
        ozet_group = QGroupBox("İşlem Özeti")
        ozet_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #333;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        ozet_layout = QVBoxLayout()
        self.lbl_islem_sayisi = QLabel("Toplam İşlem Sayısı\n0")
        self.lbl_islem_sayisi.setStyleSheet("font-size: 15px; background: #fffde7; padding: 6px;")
        self.lbl_islem_tutar = QLabel("Toplam İşlem Tutarı\n0,00")
        self.lbl_islem_tutar.setStyleSheet("font-size: 15px; background: #e0f7fa; padding: 6px;")
        ozet_layout.addWidget(self.lbl_islem_sayisi)
        ozet_layout.addWidget(self.lbl_islem_tutar)
        ozet_group.setLayout(ozet_layout)
        alt_layout.addWidget(ozet_group, 1)

        # Alt Butonlar
        btn_emri_olustur = self._buton("EMRİ OLUŞTUR", 'fa5s.save', 'deepskyblue')
        btn_emri_olustur.clicked.connect(self.emri_olustur)  # <-- Ekle
        btn_islemleri_temizle = self._buton("İŞLEMLERİ TEMİZLE", 'fa5s.sync', '#fbc02d')
        btn_pdf_aktar = self._buton("PDF AKTAR", 'fa5s.file-pdf', '#388e3c')
        btn_sayfa_kapat = self._buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')
        btn_sayfa_kapat.clicked.connect(self.sayfayi_kapat)  # <-- Ekle
        alt_layout.addWidget(btn_emri_olustur, 2)
        alt_layout.addWidget(btn_islemleri_temizle, 2)
        alt_layout.addWidget(btn_pdf_aktar, 2)
        alt_layout.addWidget(btn_sayfa_kapat, 2)

        sag_panel.addLayout(alt_layout)

        # Alt bilgi
        alt_bilgi = QLabel("10.03.2025    |    01:23")
        alt_bilgi.setStyleSheet("font-size: 14px; color: #444; padding: 6px 0 0 8px;")
        sag_panel.addWidget(alt_bilgi)

        ana_layout.addLayout(sag_panel, 4)
        self.setLayout(ana_layout)

    def open_cari_select_list(self):
        """Cari seçme penceresini açar."""
        self.cari_select_form = CariSelectListForm(parent_form=self)
        self.cari_select_form.show()

    def open_car_select_list(self):
        """Araç seçme penceresini açar."""
        if not self.cari_kodu.text().strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir cari seçin!")
            return

        cari_kodu = self.cari_kodu.text().strip()
        self.car_select_form = CarSelectListForm(parent_form=self, cari_kodu=cari_kodu)
        self.car_select_form.show()

    def set_cari_bilgileri(self, cari_kodu, cari_unvani, telefon, cari_tipi):
        """Cari bilgilerini doldurur."""
        self.cari_kodu.setText(cari_kodu)
        self.cari_unvan.setText(cari_unvani)
        self.telefon.setText(telefon)
        self.cari_tipi.setCurrentText(cari_tipi)

    def set_arac_bilgileri(self, plaka, arac_tipi, model_yili, marka, model):
        """Araç bilgilerini doldurur."""
        self.plaka.setText(plaka)
        self.arac_tipi.setCurrentText(arac_tipi)
        self.model_yili.setText(model_yili)
        self.marka.setText(marka)
        self.model.setText(model)

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
    def sayfayi_kapat(self):
        """Servis formunu kapatır ve dashboard ekranına geri döner."""
        self.close()  # QDialog'da close() kullanılır
        if self.dashboard_ref:
            self.dashboard_ref.show()  # Dashboard ekranını tekrar göster

    def islem_ekle(self):
        """İşlem bilgilerini tabloya ekler."""
        # Cari ve araç seçimi kontrolü
        if not self.cari_kodu.text().strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir cari seçin!")
            return
        if not self.plaka.text().strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir araç seçin!")
            return

        # Formdaki bilgileri al
        islem_aciklama = self.islem_aciklama.text().strip()
        islem_tutari = self.islem_tutar.text().strip()
        kdv_orani = self.kdv_orani.text().strip() or "20"  # Varsayılan KDV oranı
        aciklama = self.islem_ek_aciklama.text().strip()

        # Gerekli alanların doldurulup doldurulmadığını kontrol et
        if not islem_aciklama or not islem_tutari:
            QMessageBox.warning(self, "Uyarı", "Lütfen gerekli alanları doldurun!")
            return

        try:
            # KDV oranını float'a dönüştür
            kdv_orani = float(kdv_orani)

            # İşlemi tabloya ekle
            row_count = self.islem_table.rowCount()
            self.islem_table.insertRow(row_count)
            self.islem_table.setItem(row_count, 0, QTableWidgetItem(islem_aciklama))
            self.islem_table.setItem(row_count, 1, QTableWidgetItem(islem_tutari))
            self.islem_table.setItem(row_count, 2, QTableWidgetItem(str(kdv_orani)))  # KDV Oranı sütununa ekleme
            self.islem_table.setItem(row_count, 3, QTableWidgetItem(aciklama))

            # İşlem özetini güncelle
            self.guncelle_islem_ozeti()

            # Formu temizle
            self.islem_aciklama.clear()
            self.islem_tutar.clear()
            self.kdv_orani.clear()
            self.islem_ek_aciklama.clear()

            print("İşlem başarıyla eklendi")
        except ValueError:
            QMessageBox.warning(self, "Hata", "KDV Oranı geçerli bir sayı olmalıdır!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {e}")

    def guncelle_islem_ozeti(self):
        """İşlem özetini günceller."""
        toplam_tutar = 0
        toplam_islem = self.islem_table.rowCount()

        for row in range(toplam_islem):
            tutar_item = self.islem_table.item(row, 1)
            if tutar_item:
                toplam_tutar += float(tutar_item.text())

        self.lbl_islem_sayisi.setText(f"Toplam İşlem Sayısı\n{toplam_islem}")
        self.lbl_islem_tutar.setText(f"Toplam İşlem Tutarı\n{toplam_tutar:.2f}")

    def emri_olustur(self):
        """Cari ve araç bilgileriyle servis oluşturur ve işlemleri bu servise bağlar."""
        cari_kodu = self.cari_kodu.text().strip()
        plaka = self.plaka.text().strip()
        servis_tarihi = datetime.now().strftime("%d.%m.%Y")  # O anki tarihi al
        aciklama = "Servis oluşturuldu."  # Servis açıklaması

        # Gerekli alanların doldurulup doldurulmadığını kontrol et
        if not cari_kodu or not plaka:
            uyari = UyariPenceresi("Lütfen cari kodu ve plaka bilgilerini doldurun!", self)
            uyari.exec_()
            return

        # İşlem tablosunun boş olup olmadığını kontrol et
        toplam_islem = self.islem_table.rowCount()
        if toplam_islem == 0:
            uyari = UyariPenceresi("Lütfen en az bir işlem ekleyin!", self)
            uyari.exec_()
            return

        # Servis ve işlemleri kaydet
        servis_id = add_servis(cari_kodu, plaka, servis_tarihi, aciklama)
        for row in range(toplam_islem):
            islem_aciklama = self.islem_table.item(row, 0).text()
            islem_tutari = float(self.islem_table.item(row, 1).text())
            kdv_orani = float(self.islem_table.item(row, 2).text())
            add_islem(servis_id, islem_aciklama, islem_tutari, kdv_orani, aciklama)

        # Formu temizle
        self.islem_table.setRowCount(0)
        self.guncelle_islem_ozeti()
        self.cari_kodu.clear()
        self.plaka.clear()
        self.cari_unvan.clear()
        self.telefon.clear()
        self.cari_tipi.setCurrentIndex(0)
        self.arac_tipi.setCurrentIndex(0)
        self.model_yili.clear()
        self.marka.clear()
        self.model.clear()

        # Bilgilendirme penceresini göster
        bilgi = BilgilendirmePenceresi(self)
        bilgi.exec_()

class BilgilendirmePenceresi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bilgilendirme")
        self.setFixedSize(350, 120)
        layout = QVBoxLayout()
        label = QLabel("Emir oluşturuldu, açık servislerde görüntüleyebilirsiniz.")
        label.setStyleSheet("font-size: 15px; padding: 12px;")
        label.setWordWrap(True)
        layout.addWidget(label)

        # Tamam butonunu sağa yasla ve küçült
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_tamam = QPushButton("Tamam")
        btn_tamam.setFixedSize(80, 28)
        btn_tamam.clicked.connect(self.accept)
        btn_layout.addWidget(btn_tamam)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

class UyariPenceresi(QDialog):
    def __init__(self, mesaj, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Uyarı")
        self.setFixedSize(350, 120)
        layout = QVBoxLayout()
        label = QLabel(mesaj)
        label.setStyleSheet("font-size: 15px; padding: 12px;")
        label.setWordWrap(True)
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_tamam = QPushButton("Tamam")
        btn_tamam.setFixedSize(80, 28)
        btn_tamam.clicked.connect(self.accept)
        btn_layout.addWidget(btn_tamam)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ServisForm()
    form.show()
    sys.exit(app.exec_())