from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QGroupBox, QGridLayout, QTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QDateTime
from qtawesome import icon
import sys
from database_progress import add_islem, load_service_operations  # İşlem ekleme ve yükleme fonksiyonlarını içe aktarın

class ServiceUpdateForm(QWidget):
    def __init__(self):
        super().__init__()
        self.servis_id = None  # Düzenlenen servis ID'sini tutmak için
        self.pending_operations = []  # Yeni işlemleri geçici olarak tutmak için
        self.deleted_operations = []  # Silinecek işlemler için liste
        self.existing_operations = []  # Var olan işlemler
        self.setWindowTitle("İş Emri Formu")
        self.init_ui()

    def init_ui(self):
        # Ekran boyutlarına göre pencereyi orantılı ayarla
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.95)
        yukseklik = int(ekran.height() * 0.90)
        self.setFixedSize(genislik, yukseklik)
        x = (ekran.width() - genislik) // 2
        y = (ekran.height() - yukseklik) // 2 - 20
        self.move(x, y)

        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(10)

        # Üst başlıklar
        header_layout = QHBoxLayout()
        lbl_arac = QLabel("Araç - Cari Bilgileri")
        lbl_arac.setStyleSheet("font-size: 17px; font-weight: bold; background: #444; color: #fff; padding: 8px 18px; border-radius: 6px;")
        lbl_islem = QLabel("İşlem ve Özet Bilgileri")
        lbl_islem.setStyleSheet("font-size: 17px; font-weight: bold; background: #444; color: #fff; padding: 8px 18px; border-radius: 6px;")
        header_layout.addWidget(lbl_arac, 2)
        header_layout.addWidget(lbl_islem, 5)
        ana_layout.addLayout(header_layout)

        # Orta alan: Sol (Araç-Cari), Sağ (İşlem)
        orta_layout = QHBoxLayout()
        orta_layout.setSpacing(10)

        # Sol panel (Araç ve Cari Bilgileri)
        sol_panel = QVBoxLayout()
        sol_panel.setSpacing(10)

        group_cari = QGroupBox("Cari ve Araç Bilgilerini Giriniz")
        cari_layout = QGridLayout()
        cari_layout.setVerticalSpacing(8)
        cari_layout.setHorizontalSpacing(6)

        cari_layout.addWidget(QLabel("Cari Kodu"), 0, 0)
        self.txt_cari_kodu = QLineEdit()
        cari_layout.addWidget(self.txt_cari_kodu, 0, 1)

        cari_layout.addWidget(QLabel("Cari Adı / Ünvanı"), 1, 0)
        self.txt_cari_unvan = QLineEdit()
        cari_layout.addWidget(self.txt_cari_unvan, 1, 1)

        cari_layout.addWidget(QLabel("Telefon"), 2, 0)
        self.txt_telefon = QLineEdit()
        cari_layout.addWidget(self.txt_telefon, 2, 1)

        cari_layout.addWidget(QLabel("Cari Tipi *"), 3, 0)
        self.cmb_cari_tipi = QComboBox()
        self.cmb_cari_tipi.addItems(["Bireysel", "Kurumsal"])
        cari_layout.addWidget(self.cmb_cari_tipi, 3, 1)
        btn_cari_sec = QPushButton(icon('fa5s.user-check', color='#1976d2'), "Seç")
        btn_cari_sec.setMaximumWidth(60)
        cari_layout.addWidget(btn_cari_sec, 3, 2)

        cari_layout.addWidget(QLabel("Plaka *"), 4, 0)
        self.txt_plaka = QLineEdit()
        cari_layout.addWidget(self.txt_plaka, 4, 1)

        cari_layout.addWidget(QLabel("Araç Tipi *"), 5, 0)
        self.cmb_arac_tipi = QComboBox()
        self.cmb_arac_tipi.addItems(["Otomobil", "Kamyonet", "Motosiklet"])
        cari_layout.addWidget(self.cmb_arac_tipi, 5, 1)

        cari_layout.addWidget(QLabel("Model Yılı"), 6, 0)
        self.txt_model_yili = QLineEdit()
        cari_layout.addWidget(self.txt_model_yili, 6, 1)

        cari_layout.addWidget(QLabel("Marka"), 7, 0)
        self.txt_marka = QLineEdit()
        cari_layout.addWidget(self.txt_marka, 7, 1)

        cari_layout.addWidget(QLabel("Model"), 8, 0)
        self.txt_model = QLineEdit()
        cari_layout.addWidget(self.txt_model, 8, 1)
        btn_model_sec = QPushButton(icon('fa5s.car', color='#1976d2'), "Seç")
        btn_model_sec.setMaximumWidth(60)
        cari_layout.addWidget(btn_model_sec, 8, 2)

        group_cari.setLayout(cari_layout)
        sol_panel.addWidget(group_cari)

        # Geçmiş servis kayıtları
        group_gecmis = QGroupBox("Geçmiş Servis Kayıtları")
        gecmis_layout = QVBoxLayout()
        self.tbl_gecmis = QTableWidget(0, 3)
        self.tbl_gecmis.setHorizontalHeaderLabels(["Tarih", "Tutar", "Durum"])
        self.tbl_gecmis.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_gecmis.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_gecmis.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_gecmis.setAlternatingRowColors(True)
        self.tbl_gecmis.setFixedHeight(120)
        gecmis_layout.addWidget(self.tbl_gecmis)
        group_gecmis.setLayout(gecmis_layout)
        sol_panel.addWidget(group_gecmis)

        orta_layout.addLayout(sol_panel, 2)

        # Sağ panel (İşlem ve özet)
        sag_panel = QVBoxLayout()
        sag_panel.setSpacing(10)

        group_islem = QGroupBox("İşlem Bilgilerini Giriniz")
        islem_layout = QHBoxLayout()
        self.txt_islem_aciklama = QLineEdit()
        self.txt_islem_aciklama.setPlaceholderText("İşlem Açıklaması")
        self.txt_islem_tutar = QLineEdit()
        self.txt_islem_tutar.setPlaceholderText("İşlem Tutarı")
        self.txt_aciklama = QLineEdit()
        self.txt_aciklama.setPlaceholderText("Açıklama")
        self.txt_kdv_oran = QLineEdit()
        self.txt_kdv_oran.setPlaceholderText("KDV Oranı (%)")
        self.txt_kdv_oran.setText("20")
        btn_ekle = QPushButton(icon('fa5s.plus-circle', color='#43a047'), "Ekle")
        btn_ekle.setMinimumWidth(80)
        btn_ekle.clicked.connect(self.islem_ekle)  # Ekle butonuna tıklama olayı bağlandı
        islem_layout.addWidget(self.txt_islem_aciklama, 2)
        islem_layout.addWidget(self.txt_islem_tutar, 1)
        islem_layout.addWidget(self.txt_aciklama, 2)
        islem_layout.addWidget(self.txt_kdv_oran, 1)
        islem_layout.addWidget(btn_ekle, 1)
        group_islem.setLayout(islem_layout)
        sag_panel.addWidget(group_islem)

        # İşlem tablosu
        self.tbl_islemler = QTableWidget(0, 4)
        self.tbl_islemler.setHorizontalHeaderLabels(["İşlem Açıklaması", "Tutar", "KDV Oranı", "Açıklama"])
        self.tbl_islemler.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_islemler.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_islemler.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_islemler.setAlternatingRowColors(True)
        sag_panel.addWidget(self.tbl_islemler, 5)

        orta_layout.addLayout(sag_panel, 5)
        ana_layout.addLayout(orta_layout)

        # Alt panel
        alt_layout = QHBoxLayout()
        alt_layout.setSpacing(10)

        # İşlem özeti
        group_ozet = QGroupBox("İşlem Özeti")
        ozet_layout = QVBoxLayout()
        self.lbl_islem_sayisi = QLabel("Toplam İşlem Sayısı\n0")
        self.lbl_islem_sayisi.setStyleSheet("font-size: 14px;")
        self.lbl_islem_tutar = QLabel("Toplam İşlem Tutarı\n0,00")
        self.lbl_islem_tutar.setStyleSheet("font-size: 14px;")
        ozet_layout.addWidget(self.lbl_islem_sayisi)
        ozet_layout.addWidget(self.lbl_islem_tutar)
        group_ozet.setLayout(ozet_layout)
        group_ozet.setFixedWidth(140)
        alt_layout.addWidget(group_ozet)

        alt_layout.addStretch(1)

        # Alt butonlar
        btn_guncelle = QPushButton(icon('fa5s.edit', color='#0288d1'), "GÜNCELLE")
        btn_guncelle.setMinimumHeight(40)
        btn_guncelle.clicked.connect(self.guncelle_servis)  # Güncelle butonuna tıklama olayı bağlandı
        btn_islemleri_temizle = QPushButton(icon('fa5s.trash', color='#b71c1c'), "İŞLEMİ SİL")
        btn_islemleri_temizle.setMinimumHeight(40)
        btn_islemleri_temizle.clicked.connect(self.islem_sil)  # <-- Bağlantı eklendi
        btn_pdf = QPushButton(icon('fa5s.file-pdf', color='#388e3c'), "PDF AKTAR")
        btn_pdf.setMinimumHeight(40)
        btn_kapat = QPushButton(icon('fa5s.times', color='#b71c1c'), "SAYFAYI KAPAT")
        btn_kapat.setMinimumHeight(40)
        alt_layout.addWidget(btn_guncelle)
        alt_layout.addWidget(btn_islemleri_temizle)
        alt_layout.addWidget(btn_pdf)
        alt_layout.addWidget(btn_kapat)

        ana_layout.addLayout(alt_layout)

        # Alt bilgi (tarih/saat)
        alt_bilgi_layout = QHBoxLayout()
        alt_bilgi_layout.addStretch(1)
        now = QDateTime.currentDateTime()
        lbl_tarih = QLabel(now.toString("dd.MM.yyyy"))
        lbl_saat = QLabel(now.toString("HH:mm"))
        lbl_tarih.setStyleSheet("color: #444; font-size: 13px;")
        lbl_saat.setStyleSheet("color: #444; font-size: 13px;")
        alt_bilgi_layout.addWidget(lbl_tarih)
        alt_bilgi_layout.addWidget(QLabel("|"))
        alt_bilgi_layout.addWidget(lbl_saat)
        ana_layout.addLayout(alt_bilgi_layout)

        self.setLayout(ana_layout)

    def load_operations(self):
        """Servis açıldığında mevcut işlemleri yükle."""
        if self.servis_id:
            self.existing_operations = load_service_operations(self.servis_id)
            self.tbl_islemler.setRowCount(0)
            for islem in self.existing_operations:
                row = self.tbl_islemler.rowCount()
                self.tbl_islemler.insertRow(row)
                # islem = (id, açıklama, tutar, kdv, açıklama)
                for col, val in enumerate(islem[1:]):  # id hariç
                    self.tbl_islemler.setItem(row, col, QTableWidgetItem(str(val)))
            self.guncelle_islem_ozeti()

    def islem_ekle(self):
        """Yeni bir işlem ekler ve tabloyu günceller."""
        islem_aciklama = self.txt_islem_aciklama.text()
        islem_tutari = self.txt_islem_tutar.text()
        kdv_orani = self.txt_kdv_oran.text()
        aciklama = self.txt_aciklama.text()

        # Girdi doğrulama
        if not islem_aciklama or not islem_tutari or not kdv_orani:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm gerekli alanları doldurun!")
            return

        try:
            islem_tutari = float(islem_tutari)
            kdv_orani = float(kdv_orani)
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir tutar ve KDV oranı girin!")
            return

        # İşlemi geçici listeye ekle
        self.pending_operations.append((islem_aciklama, islem_tutari, kdv_orani, aciklama))

        # İşlemler tablosunu güncelle
        row_count = self.tbl_islemler.rowCount()
        self.tbl_islemler.insertRow(row_count)
        self.tbl_islemler.setItem(row_count, 0, QTableWidgetItem(islem_aciklama))
        self.tbl_islemler.setItem(row_count, 1, QTableWidgetItem(f"{islem_tutari:.2f}"))
        self.tbl_islemler.setItem(row_count, 2, QTableWidgetItem(f"{kdv_orani:.2f}"))
        self.tbl_islemler.setItem(row_count, 3, QTableWidgetItem(aciklama))

        # İşlem özetini güncelle
        self.guncelle_islem_ozeti()

        # Alanları temizle
        self.txt_islem_aciklama.clear()
        self.txt_islem_tutar.clear()
        self.txt_aciklama.clear()
        self.txt_kdv_oran.setText("20")

    def guncelle_servis(self):
        from database_progress import delete_islem_by_id

        # Silinecek işlemleri veritabanından sil
        for islem_id in self.deleted_operations:
            delete_islem_by_id(islem_id)
        self.deleted_operations.clear()

        # Yeni işlemleri ekle
        for islem in self.pending_operations:
            add_islem(self.servis_id, *islem)
        self.pending_operations.clear()

        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Başarılı", "Servis başarıyla güncellendi!")
        self.load_operations()

    def guncelle_islem_ozeti(self):
        """İşlem özetini günceller."""
        toplam_tutar = 0
        toplam_islem = self.tbl_islemler.rowCount()
        for row in range(toplam_islem):
            toplam_tutar += float(self.tbl_islemler.item(row, 1).text())
        self.lbl_islem_sayisi.setText(f"Toplam İşlem Sayısı\n{toplam_islem}")
        self.lbl_islem_tutar.setText(f"Toplam İşlem Tutarı\n{toplam_tutar:.2f}")

    def islem_sil(self):
        selected_row = self.tbl_islemler.currentRow()
        if selected_row >= 0:
            if selected_row < len(self.existing_operations):
                silinecek_islem = self.existing_operations[selected_row]
                self.deleted_operations.append(silinecek_islem[0])  # id
                del self.existing_operations[selected_row]
            else:
                idx = selected_row - len(self.existing_operations)
                if idx < len(self.pending_operations):
                    del self.pending_operations[idx]
            self.tbl_islemler.removeRow(selected_row)
            self.guncelle_islem_ozeti()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir işlem seçin!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ServiceUpdateForm()
    form.show()
    sys.exit(app.exec_())