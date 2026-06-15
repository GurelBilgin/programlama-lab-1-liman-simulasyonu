# Liman Yükleme Simülasyonu

Bu proje, Programlama Lab 1 dersi Ödev 2 kapsamında geliştirilen liman yükleme/boşaltma simülasyonunun düzenlenmiş ve GitHub'a uygun hâle getirilmiş sürümüdür.

Proje; TIR'lardan gelen 20 tonluk ve 30 tonluk yüklerin istif alanına alınmasını, gemilerin gidecekleri ülkeye uygun yüklerle doldurulmasını ve sürecin olay günlüğü üzerinden takip edilmesini sağlar.

## Özellikler

- TIR, Gemi, Yük ve Liman modelleri
- CSV dosyalarından TIR ve gemi verisi okuma
- Gidecek ülkeye göre yük eşleştirme
- Kapasite ve istif alanı kontrolü
- Komut satırı arayüzü
- Basit Tkinter arayüzü
- Birim testleri
- Modüler Python proje yapısı

## Proje yapısı

```text
.
├── data/
│   ├── gemiler.csv
│   └── olaylar.csv
├── docs/
│   └── README.md
├── src/
│   └── liman_simulasyonu/
│       ├── __init__.py
│       ├── cli.py
│       ├── csv_loader.py
│       ├── gui.py
│       ├── models.py
│       └── simulator.py
├── tests/
│   └── test_simulator.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Kurulum

Python 3.10 veya üzeri önerilir.

```bash
python -m pip install -e .
```

## Komut satırından çalıştırma

```bash
python -m liman_simulasyonu.cli --olaylar data/olaylar.csv --gemiler data/gemiler.csv
```

Paket kurulduktan sonra şu komut da kullanılabilir:

```bash
liman-simulasyonu --olaylar data/olaylar.csv --gemiler data/gemiler.csv
```

## Grafik arayüz ile çalıştırma

```bash
python -m liman_simulasyonu.gui
```

## Testleri çalıştırma

```bash
python -m unittest discover -s tests -v
```

## CSV formatı

### `data/olaylar.csv`

```csv
gelis_zamani,plaka,ulke,ton_20_adet,ton_30_adet,yuk_miktari,maliyet
1,41ABC001,Almanya,2,1,70,15000
```

### `data/gemiler.csv`

```csv
gelis_zamani,ad,kapasite,gidecek_ulke
2,Mavi Deniz,120,Almanya
```
## Hazırlayanlar

* Gürel Bilgin
* Berkay Aras
