from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
   QDialog, QTableWidget, QTableWidgetItem, QLabel, QWidget, QSpacerItem, QSizePolicy, QDesktopWidget, QHeaderView, QMessageBox
)
from qtawesome import icon  # qtawesome kütüphanesini ekleyin
import sys
from database_progress import load_teklifler, delete_teklif, get_teklif_id_by_no, get_teklif_details
from PyQt5.QtCore import Qt
from pdf_oluşturucu import mevcut_pdf_duzenle
import os
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4


class AddOfferForm(QMainWindow):  # Sınıf adı AddOfferForm olarak değiştirildi
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oto Servis Programı")
        self.resize_or_center()  # Pencereyi yeniden boyutlandır ve ortala

        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Üst butonlar
        self.create_top_buttons()
        # Buton bağlantısını ekle
        self.setup_connections()
        
        # Arama alanı
        self.create_search_area()

        # Tablo
        self.create_table()

        # Alt bilgi
        self.create_footer()

        # Verileri yükle
        self.load_teklif_data()

    def resize_or_center(self):
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.85)
        yukseklik = int(ekran.height() * 0.85)
        self.resize(genislik, yukseklik)
        x = (ekran.width() - genislik) // 2
        y = (ekran.height() - yukseklik) // 2 - 40
        self.move(x, y)

    def create_top_buttons(self):
        button_layout = QHBoxLayout()

        # Butonları stil_buton fonksiyonu ile oluştur
        self.btn_new_entry = self.stil_buton("YENİ TEKLİF EKLE", 'fa5s.plus-circle', '#0288d1')
        self.btn_edit = self.stil_buton("TEKLİF  DÜZENLE", 'fa5s.edit', '#fbc02d')
        self.btn_delete = self.stil_buton("TEKLİF  SİL", 'fa5s.trash', '#b71c1c')
        self.btn_view_details = self.stil_buton("PDF AKTAR", 'fa5s.file-pdf', '#43a047')
        self.btn_odeme_al = self.stil_buton("ÖDEME AL", 'fa5s.money-bill', '#43a047')  # Ödeme al butonu eklendi
        self.btn_close = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')

        # Butonları layout'a ekle
        for btn in [
            self.btn_new_entry, self.btn_edit,
            self.btn_delete, self.btn_view_details, self.btn_odeme_al, self.btn_close
        ]:
            button_layout.addWidget(btn)

        self.main_layout.addLayout(button_layout)

    def stil_buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(80)
        btn.setMinimumWidth(150)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                font-weight: bold;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 6px;
                padding: 18px 18px;
            }}
            QPushButton:hover {{
                background: #e0e0e0;
            }}
        """)
        return btn

    def create_search_area(self):
        search_layout = QHBoxLayout()

        # Arama giriş alanı
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari Kodu, Cari Adı, Plaka veya Telefon")
        self.search_input.setStyleSheet("""
            font-size: 16px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            padding: 8px 12px;
            background: #fffbe8;  /* Sarı arka plan */
        """)

        # Filtrele ve Temizle butonları
        self.btn_filter = self.stil_buton("Filtrele", 'fa5s.search', '#1976d2')
        self.btn_clear = self.stil_buton("Temizle", 'fa5s.sync', '#fbc02d')

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_filter)
        search_layout.addWidget(self.btn_clear)

        self.main_layout.addLayout(search_layout)

    def create_table(self):
        self.table = QTableWidget()

        # Tablo başlıkları
        headers = [
            "Teklif No", "Cari Kodu", "Cari Ünvanı", "Plaka", 
            "Teklif Tarihi", "Geçerlilik Tarihi", "Teklif Alan Kişi", "Durum","Teklif Tutarı"
        ]

        # Sütun sayısını başlıkların uzunluğuna göre ayarla
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Tablo özellikleri
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 18px;  /* Font boyutu artırıldı */
                alternate-background-color: #f5f5f5;
                background: #fff;
            }
            QHeaderView::section {
                background: #ececec;
                font-weight: bold;
                font-size: 16px;  /* Başlık font boyutu */
                border: 1px solid #bbb;
                padding: 6px;
            }
        """)

        self.main_layout.addWidget(self.table)

    def create_footer(self):
        footer_layout = QHBoxLayout()

        self.footer_label = QLabel()
        self.footer_label.setStyleSheet("font-size: 14px;")
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        footer_layout.addSpacerItem(spacer)
        footer_layout.addWidget(self.footer_label)

        self.main_layout.addLayout(footer_layout)

    def setup_connections(self):
        # Yeni teklif ekle butonuna tıklama olayını bağla
        self.btn_new_entry.clicked.connect(self.open_add_new_offer)
        # Teklif düzenle butonuna tıklama olayını bağla
        self.btn_edit.clicked.connect(self.open_edit_teklif)
        # Teklif sil butonuna tıklama olayını bağla
        self.btn_delete.clicked.connect(self.delete_selected_teklif)
        # Ödeme al butonuna tıklama olayını bağla
        self.btn_odeme_al.clicked.connect(self.odeme_al_ac)
        # PDF Aktar butonuna tıklama olayını bağla
        self.btn_view_details.clicked.connect(self.pdf_aktar_teklif)

    def open_add_new_offer(self):
        from add_new_offer import AddNewOfferForm
        # self.hide() satırı kaldırıldı
        self.new_offer_window = AddNewOfferForm(parent=self)
        self.new_offer_window.show()

    def open_edit_teklif(self):
        """Seçili teklifi düzenlemek için teklif formunu açar"""
        # Seçili satırı kontrol et
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Lütfen bir teklif seçiniz!")
            return

        # Seçili satırın bilgilerini al
        row = selected_rows[0].row()
        teklif_no = self.table.item(row, 0).text()

        try:
            # Veritabanından teklif detaylarını al
            from database_progress import get_teklif_details, get_teklif_id_by_no
            from teklif_form import TeklifForm
            
            # Teklif detaylarını al
            teklif_details = get_teklif_details(teklif_no)
            if not teklif_details:
                raise Exception("Teklif detayları bulunamadı!")

            # Teklif ID'sini al
            teklif_id = get_teklif_id_by_no(teklif_no)
            if not teklif_id:
                raise Exception("Teklif ID bulunamadı!")

            # Teklif formunu aç
            self.teklif_form = TeklifForm(dashboard_ref=self, teklif_id=teklif_id, teklif_no=teklif_no)
            self.teklif_form.show()
            self.hide()  # Ana pencereyi gizle

        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Hata", f"Teklif düzenlenirken bir hata oluştu: {str(e)}")

    def delete_selected_teklif(self):
        """Seçili teklifi siler."""
        # Seçili satırı kontrol et
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir teklif seçiniz!")
            return

        # Seçili satırın bilgilerini al
        row = selected_rows[0].row()
        teklif_no = self.table.item(row, 0).text()

        # Silme işlemi için onay al
        reply = QMessageBox.question(
            self, 
            "Teklif Silme Onayı",
            f"{teklif_no} numaralı teklifi silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Teklif ID'sini al
                teklif_id = get_teklif_id_by_no(teklif_no)
                if not teklif_id:
                    raise Exception("Teklif ID bulunamadı!")

                # Teklifi sil
                delete_teklif(teklif_id)
                
                # Tablodan satırı kaldır
                self.table.removeRow(row)
                
                # Başarı mesajı göster
                QMessageBox.information(self, "Başarılı", "Teklif başarıyla silindi.")
                
                # Tabloyu güncelle
                self.load_teklif_data()

            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Teklif silinirken bir hata oluştu: {str(e)}")

    def odeme_al_ac(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir teklif seçin!")
            return

        try:
            teklif_no = self.table.item(selected_row, 0).text()
            cari_kodu = self.table.item(selected_row, 1).text()
            cari_ad_unvan = self.table.item(selected_row, 2).text()
            plaka = self.table.item(selected_row, 3).text()
            toplam_tutar = float(self.table.item(selected_row, 7).text().replace(",", "").replace(" TL", ""))

            # Teklif ID'sini al
            teklif_id = get_teklif_id_by_no(teklif_no)
            if not teklif_id:
                raise Exception("Teklif ID bulunamadı!")

            from odeme_al import OdemeAlForm
            odeme_form = OdemeAlForm(
                servis_id=None,  # Teklif için servis_id null
                cari_kodu=cari_kodu,
                cari_ad_unvan=cari_ad_unvan,
                telefon="",  # Teklif için telefon bilgisi yok
                toplam_tutar=toplam_tutar,
                parent=self,
                plaka=plaka,
                odeme_kaynagi="TEKLIF",
                kaynak_id=teklif_id
            )
            if odeme_form.exec_() == QDialog.Accepted:
                self.load_teklif_data()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {e}")

    def pdf_aktar_teklif(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen PDF oluşturmak için bir teklif seçiniz!")
            return

        row = selected_rows[0].row()
        teklif_no = self.table.item(row, 0).text()

        try:
            # Veritabanından teklif detaylarını al
            detaylar = get_teklif_details(teklif_no)
            if not detaylar:
                QMessageBox.warning(self, "Uyarı", "Teklif detayları bulunamadı!")
                return

            # Teklif, cari ve araç bilgilerini al
            teklif = detaylar["teklif"]
            cari = detaylar["cari"]
            arac = detaylar["arac"]
            islemler = detaylar["islemler"]

            # Bilgileri kontrol et ve göster
            print("\n=== TEKLİF DETAYLARI ===")
            print(f"Teklif No: {teklif['teklif_no']}")
            print(f"Plaka: {teklif['plaka']}")
            print(f"\n=== CARİ BİLGİLERİ ===")
            print(f"Cari Adı Ünvanı: {cari['cari_ad_unvan']}")
            print(f"Cep Telefonu: {cari['cep_telefonu']}")
            print(f"\n=== İŞLEMLER ===")
            for islem in islemler:
                print(f"İşlem: {islem['islem_aciklama']} - Tutar: {islem['islem_tutari']:,.2f} TL")

            # KDV ve Toplam hesaplamaları
            genel_toplam = teklif["toplam_tutar"]
            kdv_orani = 0.20  # %20 KDV
            kdv_haric_toplam = genel_toplam / (1 + kdv_orani)
            kdv_tutari = genel_toplam - kdv_haric_toplam

            print(f"\n=== TUTAR BİLGİLERİ ===")
            print(f"KDV Hariç Toplam: {kdv_haric_toplam:,.2f} TL")
            print(f"KDV Tutarı: {kdv_tutari:,.2f} TL")
            print(f"Genel Toplam: {genel_toplam:,.2f} TL")

            # İşlemleri PDF için hazırla
            islem_texts = []
            y_baslangic = 119.5  # İlk işlem satırının Y koordinatı
            satir_yuksekligi = 3.5  # Her işlem satırı arasındaki Y mesafesi

            for i, islem in enumerate(islemler, 1):
                islem_texts.extend([
                    # Sıra No
                    (7.5, y_baslangic - (i - 1) * satir_yuksekligi, str(i)),
                    # İşlem Açıklaması
                    (29.5, y_baslangic - (i - 1) * satir_yuksekligi, islem["islem_aciklama"]),
                    # Miktarı
                    (77.5, y_baslangic - (i - 1) * satir_yuksekligi, "1"),
                    # Birimi
                    (87.5, y_baslangic - (i - 1) * satir_yuksekligi, "ADET"),
                    # Birim Fiyat
                    (96.5, y_baslangic - (i - 1) * satir_yuksekligi, f"{islem['islem_tutari']:,.2f}"),
                    # İsk.%
                    (112, y_baslangic - (i - 1) * satir_yuksekligi, "0.0%"),
                    # Toplam Fiyat
                    (120, y_baslangic - (i - 1) * satir_yuksekligi, f"{islem['islem_tutari']:,.2f}")
                ])

            # PDF için eklemeler sözlüğünü oluştur
            eklemeler = {
                'text': [
                    # 🔴 Teklif No & Plaka (PDF sağ üst tarafı)
                    (115, 160.8, str(teklif["teklif_no"])),  # Teklif No
                    (39, 145, f"{teklif['plaka']}"),  # Plaka

                    # 🔵 Cari Bilgileri
                    (39, 155.5, f"{cari['cari_ad_unvan']}"),
                    (39, 142, f"{cari['cep_telefonu']}"),


                    # 🟣 Tarihler
                    (110, 164, f"{teklif['teklif_tarihi']}"),
                    (96.8, 157.5, f"Teklif Geçerlilik: {teklif['gecerlilik_tarihi']}"),

                    # 🧾 Tutar Bilgileri (Sağ alt)
                    (114, 51.5, f"₺ {kdv_haric_toplam:,.2f} TL"),
                    (114, 49, f"₺ {0} TL"),
                    (114, 46.3, f"₺ {kdv_haric_toplam:,.2f} TL"),

                    (114, 43.9, f"₺ {kdv_tutari:,.2f} TL"),
                    (114, 40.8, f"₺ {genel_toplam:,.2f} TL")
                ]
            }

            # İşlemleri eklemeler listesine ekle
            eklemeler['text'].extend(islem_texts)

            # PDF'i oluştur
            output_filename = f"teklif_{teklif['teklif_no']}_{teklif['teklif_tarihi']}.pdf"
            mevcut_pdf_duzenle("teklif.pdf", output_filename, eklemeler, font_size=6)
            QMessageBox.information(self, "Başarılı", f"PDF dosyası oluşturuldu: {output_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken bir hata oluştu: {str(e)}")

    def load_teklif_data(self):
        """Teklif verilerini veritabanından yükler ve tabloya ekler"""
        from database_progress import load_teklifler
        
        # Verileri getir
        teklifler = load_teklifler()
        
        # Tabloyu temizle
        self.table.setRowCount(0)
        
        # Verileri tabloya ekle
        for row_idx, teklif in enumerate(teklifler):
            self.table.insertRow(row_idx)
            
            # Hücreleri doldur
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(teklif[0])))  # Teklif No
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(teklif[1])))  # Cari Kodu
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(teklif[2])))  # Cari Ünvanı
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(teklif[3])))  # Plaka
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(teklif[4])))  # Teklif Tarihi
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(teklif[5])))  # Geçerlilik Tarihi
            self.table.setItem(row_idx, 6, QTableWidgetItem(str(teklif[6])))  # Teklif Alan
            self.table.setItem(row_idx, 7, QTableWidgetItem(str(teklif[7])))  # Teklif Tutarı
            
            # Durum hücresini oluştur ve stilini ayarla
            durum_item = QTableWidgetItem(str(teklif[8]))  # Teklif Durumu
            if teklif[8] == "Geçerlilik tarihi doldu":
                durum_item.setForeground(Qt.red)
            else:
                durum_item.setForeground(Qt.darkGreen)
            self.table.setItem(row_idx, 8, durum_item)

        # Footer'ı güncelle
        toplam_tutar = sum(float(teklif[7] or 0) for teklif in teklifler)
        self.footer_label.setText(f"{len(teklifler)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:,.2f} TL")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddOfferForm()
    window.show()
    sys.exit(app.exec_())