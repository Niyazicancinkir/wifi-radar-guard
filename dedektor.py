import statistics
from collections import deque

class Dedektor:
    def __init__(self, esik=3.5, hz=20, kalibrasyon_sn=6.0, alarm_sn=7.4, pencere=24, ust_uste=4):
        self.esik = esik
        self.kalibrasyon_ornek = int(kalibrasyon_sn * hz)
        self.alarm_ornek = int(alarm_sn * hz)
        self.sessiz_ornek = int(1.5 * hz)
        self.pencere_boyu = pencere
        self.ust_uste = ust_uste
        self.filtre_acik = True
        self.kalibre_et()

    def kalibre_et(self):
        self.durum = "KALIBRASYON"
        self.k_pingler = []
        self.k_sinyaller = []
        self.pencere = deque(maxlen=self.pencere_boyu)
        self.sayac = 0
        self.kalan = 0
        self.z = 0.0
        self.filtreli = 0.0

    def filtrele(self,ping):
        self.pencere.append(ping)
        sirali = sorted(self.pencere)
        return sirali[len(sirali) // 4]

    def kalibrasyonu_bitir(self):
        self.ham_ort = statistics.mean(self.k_pingler)
        self.ham_std = max(statistics.pstdev(self.k_pingler), 0.02)

        filtreliler = [self.filtrele(p) for p in self.k_pingler][self.pencere_boyu:]
        self.ort = statistics.mean(filtreliler)
        self.std = max(statistics.pstdev(filtreliler), 0.1 * self.ort, 0.3)

        if self.k_sinyaller:
            self.sinyal_ort = statistics.mean(self.k_sinyaller)
            self.sinyal_std = max(statistics.pstdev(self.k_sinyaller), 1.5)
        else:
            self.sinyal_ort = None

        self.durum = "HAZIR"
        self.kalan = self.sessiz_ornek


    def guncelle(self,ping,sinyal=None):
        if ping is None:
            ping = 250.0

        if self.durum == "KALIBRASYON":
            self.k_pingler.append(ping)
            if sinyal is not None:
                self.k_sinyaller.append(sinyal)
            if len(self.k_pingler) >= self.kalibrasyon_ornek:
                self.kalibrasyonu_bitir()
            return False

        self.filtreli = self.filtrele(ping)
        if self.filtre_acik:
            z_ping = abs(self.filtreli - self.ort) / self.std
            z_sinyal = 0.0
            if self.sinyal_ort is not None and sinyal is not None:
                z_sinyal = abs(sinyal - self.sinyal_ort) / self.sinyal_std
            self.z = max(z_ping, z_sinyal)
        else:
            self.z = abs(ping - self.ham_ort) / self.ham_std

        if self.durum == "ALARM":
            self.kalan -= 1
            if self.kalan <= 0:
                self.durum = "HAZIR"
                self.kalan = self.sessiz_ornek
                self.sayac = 0
            return False

        if self.kalan > 0:
            self.kalan -= 1
            return False

        if self.z > self.esik:
            self.sayac += 1
        else:
            self.sayac = 0
            self.ort += 0.004 * (self.filtreli - self.ort)  # bos odayi yavasca ogrenmeye devam et

        if self.sayac >= self.ust_uste or (not self.filtre_acik and self.sayac >= 1):
            self.alarm()
            return True
        return False

    def alarm(self):
        if self.durum == "KALIBRASYON":
            return False
        self.durum = "ALARM"
        self.kalan = self.alarm_ornek
        return True


if __name__ == "__main__":
    import random

    d = Dedektor()
    for i in range(600):
        ping = random.gauss(3.0, 0.35)
        if random.random() < 0.04:
            ping += random.uniform(6, 30)   # komsu modem sicramasi
        if 300 <= i < 340:
            ping += random.gauss(3.5, 1.2)  # biri hattan geciyor
        if d.guncelle(ping):
            print(f"ornek {i}: ALARM  z={d.z:.1f}")
        if i % 50 == 0:
            print(f"ornek {i}: {d.durum}  filtreli={d.filtreli:.2f}  z={d.z:.2f}")