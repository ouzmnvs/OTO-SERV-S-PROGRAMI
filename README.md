# OTO SERVİS PROGRAMI

## Kurulum

1. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

2. Exe dosyasını oluşturun:
```bash
python build.py
```

3. Oluşturulan exe dosyası `dist` klasöründe bulunacaktır.

## Kullanım

1. `dist` klasöründeki `OTO-SERVIS.exe` dosyasını çalıştırın.
2. Program ilk çalıştığında veritabanını otomatik olarak oluşturacaktır.
3. Veritabanı yedekleri masaüstündeki `OTO-SERVIS-DB` klasöründe saklanacaktır.

## Önemli Notlar

- Program ilk kez çalıştırıldığında veritabanı otomatik olarak oluşturulur.
- Veritabanı yedekleri masaüstündeki `OTO-SERVIS-DB` klasöründe saklanır.
- Veritabanı yolu "VERİTABANI YOLU DEĞİŞTİR" butonu ile değiştirilebilir.
- Veritabanında sorun olması durumunda "VERİTABANI ONAR" butonu kullanılabilir.

## Sistem Gereksinimleri

- Windows 7 veya üzeri
- En az 2GB RAM
- En az 500MB boş disk alanı

## Sorun Giderme

1. Program açılmıyorsa:
   - Antivirüs programınızı kontrol edin
   - Programı yönetici olarak çalıştırmayı deneyin

2. Veritabanı hatası alıyorsanız:
   - "VERİTABANI ONAR" butonunu kullanın
   - Yedeklerden manuel olarak geri yükleme yapın

3. Diğer sorunlar için:
   - Programı kapatıp yeniden açın
   - Bilgisayarı yeniden başlatın
   - Yedeklerden geri yükleme yapın 