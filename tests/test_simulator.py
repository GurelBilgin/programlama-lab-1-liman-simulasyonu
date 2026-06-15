import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from liman_simulasyonu.csv_loader import liman_yukle, tirlari_oku
from liman_simulasyonu.models import Gemi, TIR, Yuk
from liman_simulasyonu.simulator import Liman


class ModelTestleri(unittest.TestCase):
    def test_tir_yukleri_dogru_olusturulur(self):
        tir = TIR(1, "41ABC001", "Almanya", 2, 1, 70, 15000)
        yukler = tir.yukleri_olustur()

        self.assertEqual(len(yukler), 3)
        self.assertEqual(sum(yuk.agirlik for yuk in yukler), 70)
        self.assertEqual(tir.hesaplanan_yuk_miktari, 70)

    def test_gemi_kapasite_ve_ulke_kontrolu_yapar(self):
        gemi = Gemi(1, "Mavi Deniz", 50, "Almanya", "001")
        uygun_yuk = Yuk(20, "Almanya", "41ABC001")
        uygunsuz_yuk = Yuk(20, "Fransa", "34DEF002")

        self.assertTrue(gemi.yuk_alabilir_mi(uygun_yuk))
        self.assertFalse(gemi.yuk_alabilir_mi(uygunsuz_yuk))

        gemi.yuk_yukle(uygun_yuk)
        self.assertEqual(gemi.mevcut_yuk, 20)
        self.assertEqual(gemi.kalan_kapasite, 30)


class LimanTestleri(unittest.TestCase):
    def test_tir_bosaltma_istife_yuk_ekler(self):
        liman = Liman()
        liman.tir_ekle(TIR(1, "41ABC001", "Almanya", 1, 1, 50, 1000))

        adet, ton = liman.tum_tirlari_bosalt()

        self.assertEqual(adet, 2)
        self.assertEqual(ton, 50)
        self.assertEqual(liman.toplam_bekleyen_yuk_adedi, 2)
        self.assertEqual(liman.toplam_bekleyen_yuk_tonu, 50)

    def test_gemi_sadece_uygun_ulke_yuklerini_alir(self):
        liman = Liman()
        liman.tir_ekle(TIR(1, "41ABC001", "Almanya", 1, 1, 50, 1000))
        liman.tir_ekle(TIR(2, "34DEF002", "Fransa", 1, 0, 20, 800))
        liman.tum_tirlari_bosalt()

        gemi = Gemi(3, "Mavi Deniz", 50, "Almanya", "001")
        adet, ton = liman.gemiyi_yukle(gemi)

        self.assertEqual(adet, 2)
        self.assertEqual(ton, 50)
        self.assertEqual(gemi.mevcut_yuk, 50)
        self.assertEqual(liman.toplam_bekleyen_yuk_adedi, 1)

    def test_simulasyon_sonucu_ozet_dondurur(self):
        liman = Liman()
        liman.tir_ekle(TIR(1, "41ABC001", "Almanya", 2, 1, 70, 15000))
        liman.gemi_ekle(Gemi(2, "Mavi Deniz", 120, "Almanya", "001"))

        sonuc = liman.calistir()

        self.assertEqual(sonuc.indirilen_yuk_adedi, 3)
        self.assertEqual(sonuc.indirilen_yuk_tonu, 70)
        self.assertEqual(sonuc.yuklenen_yuk_tonu, 70)
        self.assertEqual(sonuc.bekleyen_yuk_adedi, 0)
        self.assertGreater(len(sonuc.olay_gunlugu), 0)

    def test_istif_kapasitesi_dolarsa_hata_verir(self):
        liman = Liman(istif_kapasitesi=1)
        liman.tir_ekle(TIR(1, "41ABC001", "Almanya", 2, 0, 40, 1000))

        with self.assertRaises(RuntimeError):
            liman.tum_tirlari_bosalt()


class CSVTestleri(unittest.TestCase):
    def test_csv_dosyalarindan_liman_olusturulur(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            olaylar = tmp / "olaylar.csv"
            gemiler = tmp / "gemiler.csv"

            olaylar.write_text(
                "gelis_zamani,plaka,ulke,ton_20_adet,ton_30_adet,yuk_miktari,maliyet\n"
                "1,41ABC001,Almanya,1,1,50,1000\n",
                encoding="utf-8",
            )
            gemiler.write_text(
                "gelis_zamani,ad,kapasite,gidecek_ulke\n"
                "2,Mavi Deniz,100,Almanya\n",
                encoding="utf-8",
            )

            liman = liman_yukle(olaylar, gemiler)
            sonuc = liman.calistir()

            self.assertEqual(len(liman.tirlar), 1)
            self.assertEqual(len(liman.gemiler), 1)
            self.assertEqual(sonuc.yuklenen_yuk_tonu, 50)

    def test_tir_csv_okuma(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            yol = Path(tmp_dir) / "olaylar.csv"
            yol.write_text(
                "gelis_zamani,plaka,ulke,ton_20_adet,ton_30_adet,yuk_miktari,maliyet\n"
                "1,41ABC001,Almanya,2,0,40,1500\n",
                encoding="utf-8",
            )

            tirlar = tirlari_oku(yol)

            self.assertEqual(len(tirlar), 1)
            self.assertEqual(tirlar[0].plaka, "41ABC001")
            self.assertEqual(tirlar[0].hesaplanan_yuk_miktari, 40)


if __name__ == "__main__":
    unittest.main()
