"""Basit Tkinter arayüzü."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from .csv_loader import liman_yukle


class LimanSimulasyonuGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Liman Yükleme Simülasyonu")
        self.geometry("760x520")

        self.olaylar_path = tk.StringVar(value="data/olaylar.csv")
        self.gemiler_path = tk.StringVar(value="data/gemiler.csv")

        self._arayuz_olustur()

    def _arayuz_olustur(self) -> None:
        frm = tk.Frame(self, padx=12, pady=12)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="TIR olayları CSV:").grid(row=0, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.olaylar_path, width=70).grid(row=0, column=1, padx=6)
        tk.Button(frm, text="Seç", command=self._olaylar_sec).grid(row=0, column=2)

        tk.Label(frm, text="Gemiler CSV:").grid(row=1, column=0, sticky="w", pady=6)
        tk.Entry(frm, textvariable=self.gemiler_path, width=70).grid(row=1, column=1, padx=6)
        tk.Button(frm, text="Seç", command=self._gemiler_sec).grid(row=1, column=2)

        tk.Button(frm, text="Simülasyonu Başlat", command=self._simulasyonu_baslat).grid(
            row=2, column=0, columnspan=3, pady=12
        )

        self.sonuc_alani = scrolledtext.ScrolledText(frm, height=22, wrap="word")
        self.sonuc_alani.grid(row=3, column=0, columnspan=3, sticky="nsew")

        frm.rowconfigure(3, weight=1)
        frm.columnconfigure(1, weight=1)

    def _olaylar_sec(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV dosyası", "*.csv"), ("Tüm dosyalar", "*.*")])
        if path:
            self.olaylar_path.set(path)

    def _gemiler_sec(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV dosyası", "*.csv"), ("Tüm dosyalar", "*.*")])
        if path:
            self.gemiler_path.set(path)

    def _simulasyonu_baslat(self) -> None:
        try:
            liman = liman_yukle(Path(self.olaylar_path.get()), Path(self.gemiler_path.get()))
            sonuc = liman.calistir()
        except Exception as hata:  # Tkinter tarafında kullanıcıya hata göstermek için genel yakalama.
            messagebox.showerror("Hata", str(hata))
            return

        self.sonuc_alani.delete("1.0", tk.END)
        self.sonuc_alani.insert(tk.END, "Liman simülasyonu tamamlandı.\n\n")
        self.sonuc_alani.insert(tk.END, f"İndirilen yük: {sonuc.indirilen_yuk_adedi} adet / {sonuc.indirilen_yuk_tonu} ton\n")
        self.sonuc_alani.insert(tk.END, f"Yüklenen yük: {sonuc.yuklenen_yuk_adedi} adet / {sonuc.yuklenen_yuk_tonu} ton\n")
        self.sonuc_alani.insert(tk.END, f"Bekleyen yük: {sonuc.bekleyen_yuk_adedi} adet / {sonuc.bekleyen_yuk_tonu} ton\n")
        self.sonuc_alani.insert(tk.END, f"Toplam maliyet: {sonuc.toplam_maliyet:.2f}\n\n")
        self.sonuc_alani.insert(tk.END, "Olay günlüğü:\n")
        for olay in sonuc.olay_gunlugu:
            self.sonuc_alani.insert(tk.END, f"- {olay}\n")


def main() -> None:
    app = LimanSimulasyonuGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
