from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate
# from database_progress import odeme_al
class OdemeAlForm(QDialog):
    def __init__(self, servis_id, cari_kodu, cari_ad_unvan, telefon, toplam_tutar, parent=None, plaka="", odeme_kaynagi="SERVIS", kaynak_id=None):
        super().__init__(parent)
        self.setWindowTitle("Ödeme Alma Formu")
        self.setFixedSize(400, 400)

        self.servis_id = servis_id
        self.cari_kodu = cari_kodu
        self.cari_ad_unvan = cari_ad_unvan
        self.telefon = telefon
        self.toplam_tutar = toplam_tutar
        self.plaka = plaka
        self.odeme_kaynagi = odeme_kaynagi  # 'SERVIS' veya 'TEKLIF'
        self.kaynak_id = kaynak_id  # servis_id veya teklif_id

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Cari Bilgileri
        layout.addWidget(QLabel("Cari Bilgilerini"))
        layout.addLayout(self._create_label_value("Cari Kodu:", self.cari_kodu))
        layout.addLayout(self._create_label_value("Cari Adı / Ünvanı:", self.cari_ad_unvan))
        layout.addLayout(self._create_label_value("Telefon:", self.telefon))
        layout.addLayout(self._create_label_value("Toplam Tutar:", f"{self.toplam_tutar:.2f} TL"))

        # Ödeme Bilgileri
        layout.addWidget(QLabel("Cari Bilgilerini Giriniz"))

        self.odeme_tarihi = QDateEdit()
        self.odeme_tarihi.setDate(QDate.currentDate())
        self.odeme_tarihi.setCalendarPopup(True)
        layout.addLayout(self._create_label_widget("Ödeme Tarihi:", self.odeme_tarihi))

        self.odeme_tipi = QComboBox()
        self.odeme_tipi.addItems(["Nakit", "Kredi Kartı", "Havale"])
        layout.addLayout(self._create_label_widget("Ödeme Tipi:", self.odeme_tipi))

        self.tutar = QLineEdit()
        layout.addLayout(self._create_label_widget("Tutar:", self.tutar))

        self.aciklama = QLineEdit()
        layout.addLayout(self._create_label_widget("Açıklama:", self.aciklama))

        # Butonlar
        button_layout = QHBoxLayout()
        btn_kaydet = QPushButton("Kaydet")
        btn_kaydet.clicked.connect(self.kaydet)
        button_layout.addWidget(btn_kaydet)

        btn_iptal = QPushButton("İptal")
        btn_iptal.clicked.connect(self.reject)
        button_layout.addWidget(btn_iptal)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _create_label_value(self, label_text, value):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        layout.addWidget(QLabel(value))
        return layout

    def _create_label_widget(self, label_text, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        layout.addWidget(widget)
        return layout

    def kaydet(self):
        try:
            tutar = float(self.tutar.text())
            if tutar <= 0:
                raise ValueError("Tutar sıfırdan büyük olmalıdır.")
            if tutar > self.toplam_tutar:
                raise ValueError("Tutar, toplam tutardan büyük olamaz.")
            
            # Mevcut servis tutarını kontrol et
            import sqlite3
            conn = sqlite3.connect("oto_servis.db")
            cursor = conn.cursor()
            
            if self.odeme_kaynagi == "SERVIS":
                cursor.execute("SELECT servis_tutar FROM servisler WHERE id = ?", (self.servis_id,))
                mevcut_tutar = cursor.fetchone()[0] or 0
                if tutar > mevcut_tutar:
                    raise ValueError(f"Ödeme tutarı kalan borçtan ({mevcut_tutar:.2f} TL) büyük olamaz.")
            elif self.odeme_kaynagi == "TEKLIF":
                cursor.execute("SELECT toplam_tutar FROM teklifler WHERE id = ?", (self.kaynak_id,))
                mevcut_tutar = cursor.fetchone()[0] or 0
                if tutar > mevcut_tutar:
                    raise ValueError(f"Ödeme tutarı kalan borçtan ({mevcut_tutar:.2f} TL) büyük olamaz.")
            
            conn.close()

            # Plaka bilgisini gönder
            odeme_al(
                self.cari_kodu,
                self.servis_id,
                tutar,
                self.odeme_tipi.currentText(),
                self.aciklama.text(),
                self.cari_ad_unvan,
                self.plaka,
                self.odeme_kaynagi,
                self.kaynak_id
            )

            QMessageBox.information(self, "Başarılı", "Ödeme başarıyla kaydedildi.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Hata", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {e}")

def odeme_al(cari_kodu, servis_id, tutar, odeme_tipi, aciklama, cari_ad_unvan, plaka, odeme_kaynagi="SERVIS", kaynak_id=None):
    import sqlite3
    from datetime import datetime
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # kaynak_id None ise servis_id'yi kullan
        if kaynak_id is None:
            kaynak_id = servis_id
            
        cursor.execute("""
            INSERT INTO KASA (servis_id, cari_kodu, cari_ad_unvan, plaka, tarih, tutar, odeme_tipi, aciklama, odeme_kaynagi, kaynak_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (servis_id, cari_kodu, cari_ad_unvan, plaka, tarih, tutar, odeme_tipi, aciklama, odeme_kaynagi, kaynak_id))
        
        # Sadece kalan borcu güncelle
        if odeme_kaynagi == "SERVIS":
            cursor.execute("""
                UPDATE servisler
                SET servis_tutar = servis_tutar - ?
                WHERE id = ?
            """, (tutar, servis_id))
        elif odeme_kaynagi == "TEKLIF" and kaynak_id is not None:
            cursor.execute("""
                UPDATE teklifler
                SET toplam_tutar = toplam_tutar - ?
                WHERE id = ?
            """, (tutar, kaynak_id))
            
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ödeme kaydedilemedi: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    form = OdemeAlForm("SRV001", "CR002", "MUSTAFA CAN", "05332332336", 8500.68)
    form.exec_()