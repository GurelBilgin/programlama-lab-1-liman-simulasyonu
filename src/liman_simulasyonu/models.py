"""Simülasyonda kullanılan temel veri modelleri."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Yuk:
    """İstif alanında bekleyen tek bir yük birimini temsil eder."""

    agirlik: int
    hedef_ulke: str
    kaynak_plaka: str

    def __post_init__(self) -> None:
        if self.agirlik <= 0:
            raise ValueError("Yük ağırlığı pozitif olmalıdır.")
        if not self.hedef_ulke.strip():
            raise ValueError("Hedef ülke boş bırakılamaz.")
        if not self.kaynak_plaka.strip():
            raise ValueError("Kaynak plaka boş bırakılamaz.")


@dataclass
class TIR:
    """Limana gelen ve yüklerini indiren TIR bilgisini tutar."""

    gelis_zamani: int
    plaka: str
    ulke: str
    ton_20_adet: int
    ton_30_adet: int
    yuk_miktari: int = 0
    maliyet: float = 0.0
    yuk_indirildi: bool = False

    def __post_init__(self) -> None:
        if self.gelis_zamani < 0:
            raise ValueError("Geliş zamanı negatif olamaz.")
        if not self.plaka.strip():
            raise ValueError("Plaka boş bırakılamaz.")
        if not self.ulke.strip():
            raise ValueError("Ülke boş bırakılamaz.")
        if self.ton_20_adet < 0 or self.ton_30_adet < 0:
            raise ValueError("Yük adetleri negatif olamaz.")
        if self.yuk_miktari < 0:
            raise ValueError("Yük miktarı negatif olamaz.")
        if self.maliyet < 0:
            raise ValueError("Maliyet negatif olamaz.")

    @property
    def hesaplanan_yuk_miktari(self) -> int:
        """TIR üzerindeki toplam yükü ton cinsinden döndürür."""

        return self.ton_20_adet * 20 + self.ton_30_adet * 30

    def yukleri_olustur(self) -> list[Yuk]:
        """TIR üzerindeki yükleri tekil yük birimlerine dönüştürür."""

        yukler: list[Yuk] = []
        yukler.extend(Yuk(20, self.ulke, self.plaka) for _ in range(self.ton_20_adet))
        yukler.extend(Yuk(30, self.ulke, self.plaka) for _ in range(self.ton_30_adet))
        return yukler


@dataclass
class Gemi:
    """Limana gelen ve hedef ülkesine uygun yükleri alan gemi."""

    gelis_zamani: int
    ad: str
    kapasite: int
    gidecek_ulke: str
    numara: str
    yukler: list[Yuk] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.gelis_zamani < 0:
            raise ValueError("Geliş zamanı negatif olamaz.")
        if not self.ad.strip():
            raise ValueError("Gemi adı boş bırakılamaz.")
        if self.kapasite <= 0:
            raise ValueError("Gemi kapasitesi pozitif olmalıdır.")
        if not self.gidecek_ulke.strip():
            raise ValueError("Gidecek ülke boş bırakılamaz.")
        if not self.numara.strip():
            raise ValueError("Gemi numarası boş bırakılamaz.")

    @property
    def mevcut_yuk(self) -> int:
        """Gemideki toplam yük miktarını ton cinsinden döndürür."""

        return sum(yuk.agirlik for yuk in self.yukler)

    @property
    def kalan_kapasite(self) -> int:
        """Geminin alabileceği kalan yük miktarını döndürür."""

        return self.kapasite - self.mevcut_yuk

    @property
    def doluluk_orani(self) -> float:
        """Geminin doluluk oranını 0-1 aralığında döndürür."""

        return self.mevcut_yuk / self.kapasite

    def yuk_alabilir_mi(self, yuk: Yuk) -> bool:
        """Verilen yükün gemiye alınıp alınamayacağını kontrol eder."""

        return yuk.hedef_ulke.casefold() == self.gidecek_ulke.casefold() and yuk.agirlik <= self.kalan_kapasite

    def yuk_yukle(self, yuk: Yuk) -> None:
        """Uygun yükü gemiye yükler."""

        if not self.yuk_alabilir_mi(yuk):
            raise ValueError("Yük gemi hedefiyle uyumlu değil veya kapasite yetersiz.")
        self.yukler.append(yuk)
