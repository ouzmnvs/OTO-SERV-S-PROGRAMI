from PyQt5.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QDateEdit, QComboBox, QTextEdit
)
from PyQt5.QtCore import Qt, QDate, QSize
from qtawesome import icon
from cari_select_list import CariSelectListForm  # Cari seçim formunu import et
import sys
import sqlite3

class AddNewOfferForm(QDialog):
    def __init__(self, parent=None):  # parent parametresi eklendi
        super().__init__(parent)
        self.parent = parent  # Ana pencere referansını sakla
        self.setWindowTitle("Teklif Ekle")
        self.setFixedSize(800, 700)
        
        # Ana widget ve layout
        self.main_layout = QVBoxLayout(self)
        
        # Üst butonları oluştur
        self.create_top_buttons()
        
        # Form elemanlarını oluştur
        self.create_form()

        # Buton bağlantılarını ekle
        self.setup_connections()
        self.setWindowIcon(icon('fa5s.file')) # Add a file icon  
    def setup_connections(self):
        # İptal butonuna tıklandığında pencereyi kapat
        self.btn_cancel.clicked.connect(self.close_window)
        # Cari arama butonu bağlantısı
        self.btn_cari_search.clicked.connect(self.open_cari_select)
        # Plaka seç butonuna tıklama olayını bağla
        self.btn_plaka_search.clicked.connect(self.open_add_car)
        # Kaydet butonuna tıklama olayını bağla
        self.btn_save.clicked.connect(self.save_teklif)

    def close_window(self):
        self.close()  # Mevcut pencereyi kapat
        if self.parent:
            self.parent.show()  # Ana pencereyi göster

    def create_top_buttons(self):
        # Üst butonlar için container
        top_button_layout = QHBoxLayout()
        
        # Kaydet butonu
        self.btn_save = QPushButton(icon('fa5s.save', color='white'), "Kaydet")
        self.btn_save.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #2196F3;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
                min-height: 40px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        # İptal butonu
        self.btn_cancel = QPushButton(icon('fa5s.times-circle', color='white'), "İptal")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #F44336;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
                min-height: 40px;
                color: white;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)
        
        # Butonların ikonlarını büyüt
        icon_size = 32  # İkon boyutu 24'ten 32'ye çıkarıldı
        self.btn_save.setIconSize(QSize(icon_size, icon_size))
        self.btn_cancel.setIconSize(QSize(icon_size, icon_size))
        
        # Butonları layout'a ekle
        top_button_layout.addWidget(self.btn_save)
        top_button_layout.addWidget(self.btn_cancel)
        top_button_layout.addStretch()  # Sağa doğru boşluk ekler
        
        # Layout için margin ayarla
        top_button_layout.setContentsMargins(10, 10, 10, 20)
        
        # Ana layout'a üst butonları ekle
        self.main_layout.addLayout(top_button_layout)

    def create_form(self):
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(2)
        form_layout.setVerticalSpacing(5)
        
        # Genel input stili
        input_style = """
            QLineEdit, QDateEdit, QComboBox {
                max-width: 400px;  /* Input genişliği azaltıldı */
                min-height: 25px;  /* Input yüksekliği ayarlandı */
            }
            QTextEdit {
                background-color: #FFFFD7;
            }
            QPushButton {
                max-width: 25px;
                min-height: 25px;
                padding: 3px;
            }
        """
        self.setStyleSheet(input_style)

        # Ödeme Vade için özel stil
        odeme_vade_style = """
            QLineEdit {
                max-width: 80px;
                min-height: 25px;
            }
        """
        
        # Cari Seçiniz bölümü
        lbl_cari = QLabel("Cari Seç")
        lbl_cari.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        
        self.txt_cari = QLineEdit()
        self.txt_cari.setReadOnly(True)  # Salt okunur yap
        
        # Cari seç butonu
        self.btn_cari_search = QPushButton(icon('fa5s.search', color='white'), "Cari Seç")
        
        # Buton container'ı
        cari_btn_container = QWidget()
        cari_btn_layout = QHBoxLayout(cari_btn_container)
        cari_btn_layout.setContentsMargins(0, 0, 0, 0)
        cari_btn_layout.setSpacing(2)
        
        # Cari seç butonunu container'a ekle
        cari_btn_layout.addWidget(self.btn_cari_search)
        
        # Grid'e elemanları yerleştir
        form_layout.addWidget(lbl_cari, 0, 0)
        form_layout.addWidget(self.txt_cari, 0, 1)
        form_layout.addWidget(cari_btn_container, 0, 2)

        # Plaka
        lbl_plaka = QLabel("Plaka")
        lbl_plaka.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.txt_plaka = QLineEdit()

        # Plaka butonları için container
        plaka_btn_container = QWidget()
        plaka_btn_layout = QHBoxLayout(plaka_btn_container)
        plaka_btn_layout.setContentsMargins(0, 0, 0, 0)
        plaka_btn_layout.setSpacing(2)

        # Plaka seç butonu
        self.btn_plaka_search = QPushButton(icon('fa5s.search', color='white'), "Araç Seç")

        # Butonları container'a ekle
        plaka_btn_layout.addWidget(self.btn_plaka_search)

        # Grid'e elemanları yerleştir
        form_layout.addWidget(lbl_plaka, 1, 0)
        form_layout.addWidget(self.txt_plaka, 1, 1)
        form_layout.addWidget(plaka_btn_container, 1, 2)

        # Teklif No
        lbl_teklif_no = QLabel("Teklif No")
        lbl_teklif_no.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.txt_teklif_no = QLineEdit()
        self.txt_teklif_no.setReadOnly(True)  # Salt okunur yap
        self.txt_teklif_no.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;  /* Gri arka plan */
                color: #333333;
                font-weight: bold;
            }
        """)
        # Otomatik teklif numarası ata
        self.txt_teklif_no.setText(self.get_next_teklif_no())
        form_layout.addWidget(lbl_teklif_no, 2, 0)
        form_layout.addWidget(self.txt_teklif_no, 2, 1)

        # Teklif Tarihi
        lbl_teklif_tarih = QLabel("Teklif Tarihi")
        lbl_teklif_tarih.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.date_teklif_tarih = QDateEdit()
        self.date_teklif_tarih.setCalendarPopup(True)
        self.date_teklif_tarih.setDate(QDate.currentDate())
        form_layout.addWidget(lbl_teklif_tarih, 3, 0)
        form_layout.addWidget(self.date_teklif_tarih, 3, 1)

        # Geçerlilik Tarihi
        lbl_gecerlilik_tarih = QLabel("Geçerlilik Tarihi")
        lbl_gecerlilik_tarih.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.date_gecerlilik_tarih = QDateEdit()
        self.date_gecerlilik_tarih.setCalendarPopup(True)
        # Geçerlilik tarihini 1 ay sonrası olarak ayarla
        current_date = QDate.currentDate()
        one_month_later = current_date.addMonths(1)
        self.date_gecerlilik_tarih.setDate(one_month_later)
        form_layout.addWidget(lbl_gecerlilik_tarih, 4, 0)
        form_layout.addWidget(self.date_gecerlilik_tarih, 4, 1)

        # Ödeme Şekli
        lbl_odeme_sekli = QLabel("Ödeme Şekli")
        lbl_odeme_sekli.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.cmb_odeme_sekli = QComboBox()
        self.cmb_odeme_sekli.addItems(["Nakit", "Kredi Kartı", "Havale"])
        form_layout.addWidget(lbl_odeme_sekli, 5, 0)
        form_layout.addWidget(self.cmb_odeme_sekli, 5, 1)

        # Ödeme Vade (Gün)
        lbl_odeme_vade = QLabel("Ödeme Vade (Gün)")
        lbl_odeme_vade.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.txt_odeme_vade = QLineEdit()
        self.txt_odeme_vade.setStyleSheet("""
            QLineEdit {
                max-width: 60px;  /* Genişlik azaltıldı */
                min-height: 25px;
            }
        """)
        form_layout.addWidget(lbl_odeme_vade, 6, 0)
        form_layout.addWidget(self.txt_odeme_vade, 6, 1)

        # Teklif Veren Personel
        lbl_personel = QLabel("Teklif Veren Personel")
        lbl_personel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.txt_personel = QLineEdit()
        form_layout.addWidget(lbl_personel, 7, 0)
        form_layout.addWidget(self.txt_personel, 7, 1)

        # Teklif Alan
        lbl_teklif_alan = QLabel("Teklif Alan")
        lbl_teklif_alan.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.txt_teklif_alan = QLineEdit()
        form_layout.addWidget(lbl_teklif_alan, 8, 0)
        form_layout.addWidget(self.txt_teklif_alan, 8, 1)

        # Açıklama
        lbl_aciklama = QLabel("Açıklama")
        lbl_aciklama.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        self.txt_aciklama = QTextEdit()
        self.txt_aciklama.setStyleSheet("background-color: #FFFFD7;")
        form_layout.addWidget(lbl_aciklama, 9, 0)
        form_layout.addWidget(self.txt_aciklama, 9, 1, 1, 2)

        # İkon boyutunu tanımla
        icon_size = QSize(12, 12)
        
        # Modern buton stilleri
        modern_search_button_style = """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 80px;
                min-height: 24px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """
        
        # Butonlara stil uygula
        self.btn_plaka_search.setStyleSheet(modern_search_button_style)
        self.btn_cari_search.setStyleSheet(modern_search_button_style)
        
        # Buton ikonlarının rengini beyaz yap
        self.btn_plaka_search.setIcon(icon('fa5s.search', color='white'))
        self.btn_cari_search.setIcon(icon('fa5s.search', color='white'))
        
        # QDateEdit için stil güncelleme
        date_style = """
            QDateEdit {
                color: black;
                font-size: 12px;
            }
            QCalendarWidget QToolButton {
                color: black;
                font-size: 12px;
                font-weight: bold;
            }
            QCalendarWidget QMenu {
                color: black;
                font-size: 12px;
            }
            QCalendarWidget {
                min-width: 250px;
                min-height: 250px;
            }
            QCalendarWidget QAbstractItemView {
                font-size: 12px;
            }
        """

        # Tarih alanlarına stili uygula
        self.date_teklif_tarih.setStyleSheet(date_style)
        self.date_gecerlilik_tarih.setStyleSheet(date_style)
        
        # Ana layout'a form layout'u ekle
        self.main_layout.addLayout(form_layout)

    def open_cari_select(self):
        """Cari seçim penceresini aç"""
        self.cari_select = CariSelectListForm(parent_form=self)
        self.cari_select.show()

    def set_cari_bilgileri(self, cari_kodu, cari_unvani, telefon, cari_tipi):
        """Seçilen cari bilgilerini forma doldur"""
        self.txt_cari.setText(cari_unvani)  # Sadece cari ünvanını göster
        self.cari_kodu = cari_kodu  # Cari kodunu sakla

    def open_add_car(self):
        """Araç seçme penceresini aç"""
        if not hasattr(self, 'cari_kodu') or not self.cari_kodu:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Lütfen önce cari seçiniz!")
            return
            
        from car_select_list import CarSelectListForm
        self.car_select_form = CarSelectListForm(parent_form=self, cari_kodu=self.cari_kodu)
        self.car_select_form.show()

    def set_plaka_bilgisi(self, plaka):
        """Seçilen plaka bilgisini forma doldur"""
        self.txt_plaka.setText(plaka)

    def set_arac_bilgileri(self, plaka, arac_tipi, model_yili, marka, model):
        """Seçilen araç bilgilerini forma doldur"""
        self.txt_plaka.setText(plaka)  # Plaka bilgisini doldur

    def save_teklif(self):
        """Teklif bilgilerini veritabanına kaydet"""
        # Gerekli alanların dolu olup olmadığını kontrol et
        if not self.txt_cari.text() or not self.txt_plaka.text() or not self.txt_teklif_no.text():
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Lütfen zorunlu alanları doldurunuz!")
            return

        try:
            # Veritabanına kaydet
            from database_progress import add_teklif
            
            # Vade günü kontrolü
            odeme_vade_gun = 0  # Default to 0
            if self.txt_odeme_vade.text().strip():  # Eğer boş değilse
                try:
                    odeme_vade_gun = int(self.txt_odeme_vade.text())
                except ValueError:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Uyarı", "Vade günü sayısal bir değer olmalıdır!")
                    return
            
            teklif_id = add_teklif(
                teklif_no=self.txt_teklif_no.text(),
                cari_kodu=self.cari_kodu,  # Daha önce sakladığımız cari_kodu
                plaka=self.txt_plaka.text(),
                teklif_tarihi=self.date_teklif_tarih.date().toString("yyyy-MM-dd"),
                gecerlilik_tarihi=self.date_gecerlilik_tarih.date().toString("yyyy-MM-dd"),
                odeme_sekli=self.cmb_odeme_sekli.currentText(),
                odeme_vade_gun=odeme_vade_gun,  # None veya sayısal değer
                teklif_veren_personel=self.txt_personel.text(),
                teklif_alan=self.txt_teklif_alan.text(),
                aciklama=self.txt_aciklama.toPlainText()
            )

            # Başarılı mesajı göster
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Başarılı", "Teklif başarıyla kaydedildi!")
            
            # Ana pencereyi güncelle
            if self.parent:
                self.parent.load_teklif_data()  # Ana penceredeki tabloyu güncelle
            
            # Pencereyi kapat
            self.close_window()

        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Hata", f"Teklif kaydedilirken bir hata oluştu: {str(e)}")

    def get_next_teklif_no(self):
        """Veritabanından son teklif numarasını alır ve bir sonraki numarayı döndürür."""
        try:
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(CAST(teklif_no AS INTEGER)) FROM teklifler")
            last_number = cursor.fetchone()[0]
            if last_number is None:
                return "00001"
            # Ensure last_number is treated as an integer, defaulting to 0 if None
            next_number = int(last_number or 0) + 1
            return f"{next_number:05d}"  # 5 haneli, başında sıfır olan format
        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
            return "00001"
        finally:
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddNewOfferForm()
    window.show()
    sys.exit(app.exec_())