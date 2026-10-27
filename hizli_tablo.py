"""
Binlerce satırlık listeler için hızlı tablo.

QTableWidget her hücre için ayrı bir nesne oluşturur; 5.000 satırlık bir listede açılış ve her arama
tuşu eski bilgisayarlarda saniyeye yaklaşır. HizliTablo kayıtları düz bir Python listesinde tutar ve
yalnızca ekranda görünen satırları çizer. Bu projede kullanılan QTableWidget yöntemleri (item,
rowCount, columnCount, currentRow, setCurrentCell, selectedItems, setHorizontalHeaderLabels) aynı
şekilde çalışır; hücre metni item(satir, sutun).text(), satırın kimliği item(satir, 0).data(Qt.UserRole).
"""
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtWidgets import QTableView

from arama import arama_kaydi, arama_sorgusu, kayit_eslesir


class _Hucre:
    """QTableWidgetItem'ın bu projede kullanılan kısmı."""
    __slots__ = ("_metin", "_kimlik", "_satir", "_sutun")

    def __init__(self, metin, kimlik, satir, sutun):
        self._metin, self._kimlik, self._satir, self._sutun = metin, kimlik, satir, sutun

    def text(self):
        return self._metin

    def data(self, rol):
        if rol == Qt.UserRole:
            return self._kimlik
        return self._metin if rol == Qt.DisplayRole else None

    def row(self):
        return self._satir

    def column(self):
        return self._sutun


class _ListeModeli(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.basliklar = []
        self.sag_hizali = set()
        self.satirlar = []  # Görünen satırlar: (hücre metinleri, kimlik)

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.satirlar)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.basliklar)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.satirlar[index.row()][0][index.column()]
        if role == Qt.TextAlignmentRole and index.column() in self.sag_hizali:
            return int(Qt.AlignRight | Qt.AlignVCenter)
        if role == Qt.UserRole:
            return self.satirlar[index.row()][1]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.basliklar[section] if section < len(self.basliklar) else None
        return section + 1  # QTableWidget gibi satır numarası

    def satirlari_ayarla(self, satirlar):
        self.beginResetModel()
        self.satirlar = satirlar
        self.endResetModel()

    def basliklari_ayarla(self, basliklar):
        self.beginResetModel()
        self.basliklar = list(basliklar)
        self.endResetModel()


class HizliTablo(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = _ListeModeli()
        self.setModel(self._model)
        self._kayitlar = []  # (hücre metinleri, kimlik, kayıt, arama kaydı)
        self._gorunen = []
        self._sorgu = arama_sorgusu("")
        self._ek_kosul = None

    def kayitlari_yukle(self, kayitlar, hucreler, kimlik=None, arama_alanlari=None):
        """
        kayitlar: veritabanı satırları. hucreler(kayit) -> sütun metinleri,
        kimlik(kayit) -> item(.., 0).data(Qt.UserRole) değeri, arama_alanlari(kayit) -> aranacak değerler
        (verilmezse hücre metinleri). Mevcut arama ve ek koşul yeniden uygulanır.
        """
        yeni = []
        for kayit in kayitlar:
            metinler = tuple("" if h is None else str(h) for h in hucreler(kayit))
            alanlar = arama_alanlari(kayit) if arama_alanlari else metinler
            yeni.append((metinler, kimlik(kayit) if kimlik else None, kayit, arama_kaydi(*alanlar)))
        self._kayitlar = yeni
        self._uygula()

    def filtrele(self, aranan="", ek_kosul=None):
        """Arama metni (Türkçe harf duyarsız) ve isteğe bağlı ek_kosul(kayit) ile satırları süzer."""
        self._sorgu = arama_sorgusu(aranan)
        self._ek_kosul = ek_kosul
        self._uygula()

    def _uygula(self):
        sorgu, kosul = self._sorgu, self._ek_kosul
        gorunen = [k for k in self._kayitlar if kayit_eslesir(sorgu, k[3]) and (kosul is None or kosul(k[2]))]
        self._gorunen = [k[2] for k in gorunen]
        self._model.satirlari_ayarla([(k[0], k[1]) for k in gorunen])

    def gorunen_kayitlar(self):
        """Filtreden geçen kayıtlar (veritabanı satırları), tablodaki sırayla."""
        return list(self._gorunen)

    def sag_hizala(self, *sutunlar):
        self._model.sag_hizali = set(sutunlar)

    # --- QTableWidget uyumluluğu (bu projede kullanılan kısım)
    def setColumnCount(self, adet):
        basliklar = (self._model.basliklar + [""] * adet)[:adet]
        self._model.basliklari_ayarla(basliklar)

    def setHorizontalHeaderLabels(self, basliklar):
        self._model.basliklari_ayarla(basliklar)

    def rowCount(self):
        return self._model.rowCount()

    def columnCount(self):
        return self._model.columnCount()

    def item(self, satir, sutun):
        if 0 <= satir < len(self._model.satirlar) and 0 <= sutun < self._model.columnCount():
            metinler, kimlik = self._model.satirlar[satir]
            return _Hucre(metinler[sutun], kimlik, satir, sutun)
        return None

    def currentRow(self):
        index = self.currentIndex()
        return index.row() if index.isValid() else -1

    def setCurrentCell(self, satir, sutun):
        self.setCurrentIndex(self._model.index(satir, sutun))

    def selectedItems(self):
        return [self.item(i.row(), i.column()) for i in self.selectedIndexes()]
