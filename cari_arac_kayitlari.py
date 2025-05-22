from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from qtawesome import icon

class AracListesiForm(QDialog):
    def __init__(self, cari_kodu, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Araç Listesi")
        self.setFixedSize(600, 400)
        self.cari_kodu = cari_kodu
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Üst butonlar
        buton_layout = QHBoxLayout()
        buton_layout.addWidget(QPushButton(icon('fa5s.file-import', color='#1976d2'), "Bilgileri Aktar"))
        buton_layout.addWidget(QPushButton(icon('fa5s.times', color='#b71c1c'), "İptal"))
        buton_layout.addWidget(QPushButton(icon('fa5s.plus-circle', color='#43a047'), "Yeni Ekle"))
        layout.addLayout(buton_layout)

        # Tablo
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Araç Plakası", "Araç Tipi", "Model Yılı", "Marka", "Model", "Son Kapalı Servis Tutarı"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_araclar()

    def load_araclar(self):
        from database_progress import load_car_list_by_cari_with_last_closed_service_info
        araclar = load_car_list_by_cari_with_last_closed_service_info(self.cari_kodu)
        self.table.setRowCount(len(araclar))
        for row, (plaka, arac_tipi, model_yili, marka, model, son_kapali_servis_tutar, son_kapali_servis_tarihi) in enumerate(araclar):
            self.table.setItem(row, 0, QTableWidgetItem(plaka))
            self.table.setItem(row, 1, QTableWidgetItem(arac_tipi))
            self.table.setItem(row, 2, QTableWidgetItem(str(model_yili)))
            self.table.setItem(row, 3, QTableWidgetItem(marka))
            self.table.setItem(row, 4, QTableWidgetItem(model))
            self.table.setItem(row, 5, QTableWidgetItem(f"{son_kapali_servis_tutar:,.2f}" if son_kapali_servis_tutar else "0,00"))
            # Eğer tarih de göstermek isterseniz, yeni bir sütun ekleyebilirsiniz.

def load_car_list_by_cari_with_last_closed_service(cari_kodu):
    import sqlite3
    try:
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                a.plaka, a.arac_tipi, a.model_yili, a.marka, a.model,
                (
                    SELECT s.servis_kapanis_tutari
                    FROM SERVİSLER s
                    WHERE s.plaka = a.plaka AND s.servis_durumu = 'Kapalı'
                    ORDER BY s.servis_tarihi DESC
                    LIMIT 1
                ) as son_kapali_servis_tutar
            FROM ARAÇLAR a
            WHERE a.cari_kodu = ?
        """, (cari_kodu,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()