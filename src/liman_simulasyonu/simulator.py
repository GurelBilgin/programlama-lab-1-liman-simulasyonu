"""Liman simülasyonunun ana iş kuralları."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Deque

from .models import Gemi, TIR, Yuk


@dataclass
class SimulasyonSonucu:
    """Simülasyon sonunda oluşan özet bilgiler."""

    indirilen_yuk_adedi: int = 0
    indirilen_yuk_tonu: int = 0
    yuklenen_yuk_adedi: int = 0
    yuklenen_yuk_tonu: int = 0
    bekleyen_yuk_adedi: int = 0
    bekleyen_yuk_tonu: int = 0
    toplam_maliyet: float = 0.0
    olay_gunlugu: list[str] = field(default_factory=list)


class Liman:
    """TIR, gemi ve istif alanlarını yöneten simülasyon sınıfı."""

    def __init__(self, istif_kapasitesi: int = 750, vinc_sayisi: int = 20) -> None:
        if istif_kapasitesi <= 0:
            raise ValueError("İstif kapasitesi pozitif olmalıdır.")
        if vinc_sayisi <= 0:
            raise ValueError("Vinç sayısı pozitif olmalıdır.")

        self.istif_kapasitesi = istif_kapasitesi
        self.vinc_sayisi = vinc_sayisi
        self.tirlar: list[TIR] = []
        self.gemiler: list[Gemi] = []
        self.istif_20: Deque[Yuk] = deque()
        self.istif_30: Deque[Yuk] = deque()
        self.olay_gunlugu: list[str] = []
        self._gemi_sayac = 0

    def tir_ekle(self, tir: TIR) -> None:
        self.tirlar.append(tir)
        self.tirlar.sort(key=lambda item: item.gelis_zamani)

    def gemi_ekle(self, gemi: Gemi) -> None:
        self.gemiler.append(gemi)
        self.gemiler.sort(key=lambda item: (item.gelis_zamani, item.numara))

    def yeni_gemi(self, gelis_zamani: int, ad: str, kapasite: int, gidecek_ulke: str) -> Gemi:
        """Sıralı numara üretip yeni gemi nesnesi oluşturur."""

        self._gemi_sayac += 1
        return Gemi(
            gelis_zamani=gelis_zamani,
            ad=ad,
            kapasite=kapasite,
            gidecek_ulke=gidecek_ulke,
            numara=f"{self._gemi_sayac:03d}",
        )

    @property
    def toplam_bekleyen_yuk_adedi(self) -> int:
        return len(self.istif_20) + len(self.istif_30)

    @property
    def toplam_bekleyen_yuk_tonu(self) -> int:
        return sum(yuk.agirlik for yuk in self.istif_20) + sum(yuk.agirlik for yuk in self.istif_30)

    def istif_dolu_mu(self) -> bool:
        return self.toplam_bekleyen_yuk_adedi >= self.istif_kapasitesi

    def _istife_ekle(self, yuk: Yuk) -> None:
        if self.istif_dolu_mu():
            raise RuntimeError("İstif alanı dolu olduğu için yeni yük alınamadı.")
        if yuk.agirlik == 20:
            self.istif_20.append(yuk)
        elif yuk.agirlik == 30:
            self.istif_30.append(yuk)
        else:
            raise ValueError("Sadece 20 ton ve 30 ton yükler desteklenir.")

    def tir_yuklerini_indir(self, tir: TIR) -> tuple[int, int]:
        """Bir TIR'ın yüklerini istif alanına indirir."""

        if tir.yuk_indirildi:
            return 0, 0

        indirilen_adet = 0
        indirilen_ton = 0
        for yuk in tir.yukleri_olustur():
            self._istife_ekle(yuk)
            indirilen_adet += 1
            indirilen_ton += yuk.agirlik

        tir.yuk_indirildi = True
        self.olay_gunlugu.append(
            f"{tir.gelis_zamani}. zamanda {tir.plaka} plakalı TIR'dan "
            f"{indirilen_adet} adet / {indirilen_ton} ton yük indirildi."
        )
        return indirilen_adet, indirilen_ton

    def tum_tirlari_bosalt(self) -> tuple[int, int]:
        toplam_adet = 0
        toplam_ton = 0
        for tir in self.tirlar:
            adet, ton = self.tir_yuklerini_indir(tir)
            toplam_adet += adet
            toplam_ton += ton
        return toplam_adet, toplam_ton

    def _uygun_yuku_bul_ve_cikar(self, gemi: Gemi) -> Yuk | None:
        """Geminin hedef ülkesine ve kapasitesine uygun ilk yükü istiften çıkarır."""

        for istif in (self.istif_30, self.istif_20):
            for index, yuk in enumerate(istif):
                if gemi.yuk_alabilir_mi(yuk):
                    uygun_yuk = yuk
                    del istif[index]
                    return uygun_yuk
        return None

    def gemiyi_yukle(self, gemi: Gemi) -> tuple[int, int]:
        """Verilen gemiyi uygun yüklerle doldurur."""

        yuklenen_adet = 0
        yuklenen_ton = 0
        kullanilan_vinc = 0

        while kullanilan_vinc < self.vinc_sayisi:
            yuk = self._uygun_yuku_bul_ve_cikar(gemi)
            if yuk is None:
                break
            gemi.yuk_yukle(yuk)
            yuklenen_adet += 1
            yuklenen_ton += yuk.agirlik
            kullanilan_vinc += 1

        self.olay_gunlugu.append(
            f"{gemi.gelis_zamani}. zamanda {gemi.numara} numaralı {gemi.ad} gemisine "
            f"{yuklenen_adet} adet / {yuklenen_ton} ton yük yüklendi. "
            f"Doluluk: %{gemi.doluluk_orani * 100:.1f}"
        )
        return yuklenen_adet, yuklenen_ton

    def tum_gemileri_yukle(self) -> tuple[int, int]:
        toplam_adet = 0
        toplam_ton = 0
        for gemi in self.gemiler:
            adet, ton = self.gemiyi_yukle(gemi)
            toplam_adet += adet
            toplam_ton += ton
        return toplam_adet, toplam_ton

    def calistir(self) -> SimulasyonSonucu:
        """Simülasyonu baştan sona çalıştırır ve özet sonuç döndürür."""

        indirilen_adet, indirilen_ton = self.tum_tirlari_bosalt()
        yuklenen_adet, yuklenen_ton = self.tum_gemileri_yukle()

        toplam_maliyet = sum(tir.maliyet for tir in self.tirlar)
        bekleyen_adet = self.toplam_bekleyen_yuk_adedi
        bekleyen_ton = self.toplam_bekleyen_yuk_tonu

        self.olay_gunlugu.append(
            f"Simülasyon tamamlandı. Bekleyen yük: {bekleyen_adet} adet / {bekleyen_ton} ton."
        )

        return SimulasyonSonucu(
            indirilen_yuk_adedi=indirilen_adet,
            indirilen_yuk_tonu=indirilen_ton,
            yuklenen_yuk_adedi=yuklenen_adet,
            yuklenen_yuk_tonu=yuklenen_ton,
            bekleyen_yuk_adedi=bekleyen_adet,
            bekleyen_yuk_tonu=bekleyen_ton,
            toplam_maliyet=toplam_maliyet,
            olay_gunlugu=list(self.olay_gunlugu),
        )
