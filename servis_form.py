from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from cari_select_list import CariSelectListForm  # CariSelectListForm'u içe aktarın
from car_select_list import CarSelectListForm  # CarSelectListForm'u içe aktarın

class ServisForm(QWidget):
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

        btn_islem_ekle = QPushButton(icon('fa5s.plus-circle', color='green'), "Ekle")
        btn_islem_ekle.setMinimumHeight(36)
        btn_islem_ekle.setStyleSheet("font-size:16px; font-weight:700; padding:6px 18px;")
        islem_layout.addWidget(btn_islem_ekle, 0, 6)

        btn_islem_temizle = QPushButton(icon('fa5s.sync', color='#fbc02d'), "")
        btn_islem_temizle.setMinimumHeight(36)
        btn_islem_temizle.setStyleSheet("font-size:16px; font-weight:700; padding:6px 18px;")
        islem_layout.addWidget(btn_islem_temizle, 0, 7)

        islem_group.setLayout(islem_layout)
        sag_panel.addWidget(islem_group)

        # İşlem Listesi Tablosu
        self.islem_table = QTableWidget(0, 3)
        self.islem_table.setHorizontalHeaderLabels(["İşlem Açıklaması", "Tutar", "Açıklama"])
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
        self.car_select_form = CarSelectListForm(parent_form=self)
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
        self.close()
        if self.dashboard_ref:
            self.dashboard_ref.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ServisForm()
    form.show()
    sys.exit(app.exec_())