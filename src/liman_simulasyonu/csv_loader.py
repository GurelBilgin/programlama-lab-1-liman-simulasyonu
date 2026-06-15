"""CSV dosyalarından simülasyon verilerini okuyan yardımcı fonksiyonlar."""

from __future__ import annotations

import csv
from pathlib import Path

from .models import TIR
from .simulator import Liman


def _int_deger(row: dict[str, str], alan: str, varsayilan: int = 0) -> int:
    deger = row.get(alan, "")
    if deger is None or deger == "":
        return varsayilan
    return int(deger)


def _float_deger(row: dict[str, str], alan: str, varsayilan: float = 0.0) -> float:
    deger = row.get(alan, "")
    if deger is None or deger == "":
        return varsayilan
    return float(deger)


def tirlari_oku(dosya_yolu: str | Path) -> list[TIR]:
    """TIR olaylarını CSV dosyasından okur."""

    yol = Path(dosya_yolu)
    if not yol.exists():
        raise FileNotFoundError(f"TIR olay dosyası bulunamadı: {yol}")

    tirlar: list[TIR] = []
    with yol.open("r", encoding="utf-8-sig", newline="") as csv_file:
        okuyucu = csv.DictReader(csv_file)
        for row in okuyucu:
            tirlar.append(
                TIR(
                    gelis_zamani=_int_deger(row, "gelis_zamani"),
                    plaka=row["plaka"],
                    ulke=row["ulke"],
                    ton_20_adet=_int_deger(row, "ton_20_adet"),
                    ton_30_adet=_int_deger(row, "ton_30_adet"),
                    yuk_miktari=_int_deger(row, "yuk_miktari"),
                    maliyet=_float_deger(row, "maliyet"),
                )
            )
    return tirlar


def gemileri_oku(dosya_yolu: str | Path, liman: Liman) -> None:
    """Gemi kayıtlarını CSV dosyasından okuyup limana ekler."""

    yol = Path(dosya_yolu)
    if not yol.exists():
        raise FileNotFoundError(f"Gemi dosyası bulunamadı: {yol}")

    with yol.open("r", encoding="utf-8-sig", newline="") as csv_file:
        okuyucu = csv.DictReader(csv_file)
        for row in okuyucu:
            gemi = liman.yeni_gemi(
                gelis_zamani=_int_deger(row, "gelis_zamani"),
                ad=row["ad"],
                kapasite=_int_deger(row, "kapasite"),
                gidecek_ulke=row["gidecek_ulke"],
            )
            liman.gemi_ekle(gemi)


def liman_yukle(olaylar_csv: str | Path, gemiler_csv: str | Path) -> Liman:
    """CSV dosyalarını okuyup çalıştırmaya hazır Liman nesnesi oluşturur."""

    liman = Liman()
    for tir in tirlari_oku(olaylar_csv):
        liman.tir_ekle(tir)
    gemileri_oku(gemiler_csv, liman)
    return liman
