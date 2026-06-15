"""Komut satırı arayüzü."""

from __future__ import annotations

import argparse
from pathlib import Path

from .csv_loader import liman_yukle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Liman yükleme simülasyonu")
    parser.add_argument("--olaylar", default="data/olaylar.csv", help="TIR olayları CSV dosyası")
    parser.add_argument("--gemiler", default="data/gemiler.csv", help="Gemi kayıtları CSV dosyası")
    parser.add_argument("--gunluk", action="store_true", help="Olay günlüğünü ayrıntılı yazdır")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    olaylar = Path(args.olaylar)
    gemiler = Path(args.gemiler)

    try:
        liman = liman_yukle(olaylar, gemiler)
        sonuc = liman.calistir()
    except (FileNotFoundError, ValueError, RuntimeError) as hata:
        print(f"Hata: {hata}")
        return 1

    print("Liman simülasyonu tamamlandı.")
    print(f"İndirilen yük: {sonuc.indirilen_yuk_adedi} adet / {sonuc.indirilen_yuk_tonu} ton")
    print(f"Yüklenen yük: {sonuc.yuklenen_yuk_adedi} adet / {sonuc.yuklenen_yuk_tonu} ton")
    print(f"Bekleyen yük: {sonuc.bekleyen_yuk_adedi} adet / {sonuc.bekleyen_yuk_tonu} ton")
    print(f"Toplam maliyet: {sonuc.toplam_maliyet:.2f}")

    if args.gunluk:
        print("\nOlay günlüğü:")
        for olay in sonuc.olay_gunlugu:
            print(f"- {olay}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
