import json
import threading
import time
from collections import deque

import pygame

from ag import Pinger, gateway_bul, sinyal_oku
from dedektor import Dedektor
from ekran import Ekran
from led import Led
from ses import Ses
from supurge import YONLER, Supurge
from telegram import Telegram


class Radar:
    def __init__(self, ayar, pinger):
        self.ayar = ayar
        self.pinger = pinger
        self.calisiyor = True
        self.sinyal = None
        self.alarm_sayisi = 0
        self.foto_cek = False
        self.mesajlar = []
        self.ham = deque(maxlen=300)
        self.filtreli = deque(maxlen=300)

        self.d = Dedektor(ayar["z_threshold"], kalibrasyon_sn=ayar["calib_s"], alarm_sn=ayar["alarm_s"])
        self.ses = Ses()
        self.ekran = Ekran()
        v = ayar["vacuum"]
        self.supurge = Supurge(v["ip"], v["token"], v["did"])
        self.led = Led(ayar["led"]["adresler"], ayar["led"]["normal_renk"])
        self.telegram = Telegram(ayar["telegram"]["token"], ayar["telegram"]["chat_id"])

    def log(self, mesaj):
        self.mesajlar.append(time.strftime("%H:%M:%S") + "  " + mesaj)
        self.mesajlar = self.mesajlar[-3:]

    def alarm_ver(self, sebep):
        self.alarm_sayisi += 1
        self.ses.cal()
        self.supurge.saldir(self.ayar["vacuum"]["attack"])
        self.led.cakar(self.ayar["alarm_s"])
        self.foto_cek = True
        self.log(f"ALARM #{self.alarm_sayisi}  {sebep}")

    def olcum_dongusu(self):
        while self.calisiyor:
            baslangic = time.perf_counter()
            ping = self.pinger.ping()
            if self.d.guncelle(ping, self.sinyal):
                self.alarm_ver(f"z={self.d.z:.1f}")
            self.ham.append(ping if ping is not None else 250)
            if self.d.durum == "KALIBRASYON":
                son = sorted(list(self.ham)[-24:])
                self.filtreli.append(son[len(son) // 4])
            else:
                self.filtreli.append(self.d.filtreli)
            bekle = 0.05 - (time.perf_counter() - baslangic)
            if bekle > 0:
                time.sleep(bekle)

    def sinyal_dongusu(self):
        while self.calisiyor:
            self.sinyal = sinyal_oku()
            time.sleep(0.5)

    def tus(self, tus):
        if tus == pygame.K_c:
            self.d.kalibre_et()
            self.log("yeniden kalibrasyon")
        elif tus == pygame.K_f:
            self.d.filtre_acik = not self.d.filtre_acik
            self.log("filtre " + ("ACIK" if self.d.filtre_acik else "KAPALI"))
        elif tus == pygame.K_SPACE:
            if self.d.alarm():
                self.alarm_ver("elle test")
        elif tus == pygame.K_m:
            self.ses.sessiz_degistir()
        elif tus == pygame.K_s:
            self.supurge.durdur()
            self.led.durdur()
        elif tus == pygame.K_h:
            threading.Thread(target=self.supurge.sarja_gonder, daemon=True).start()

    def calistir(self):
        self.log(f"basladi, hedef {self.pinger.ip}")
        threading.Thread(target=self.olcum_dongusu, daemon=True).start()
        threading.Thread(target=self.sinyal_dongusu, daemon=True).start()

        while self.calisiyor:
            for olay in pygame.event.get():
                if olay.type == pygame.QUIT:
                    self.calisiyor = False
                elif olay.type == pygame.KEYDOWN:
                    if olay.key == pygame.K_ESCAPE:
                        self.calisiyor = False
                    else:
                        self.tus(olay.key)

            basili = pygame.key.get_pressed()
            if basili[pygame.K_UP]:
                self.supurge.elle_yon = YONLER["forward"]
            elif basili[pygame.K_DOWN]:
                self.supurge.elle_yon = YONLER["backward"]
            elif basili[pygame.K_LEFT]:
                self.supurge.elle_yon = YONLER["left"]
            elif basili[pygame.K_RIGHT]:
                self.supurge.elle_yon = YONLER["right"]
            else:
                self.supurge.elle_yon = None

            foto = self.foto_cek
            self.ekran.ciz(self.d, self.ham, self.filtreli, self.sinyal, self.alarm_sayisi,
                           self.mesajlar, self.ses.sessiz)

            if foto:
                self.foto_cek = False
                pygame.image.save(self.ekran.ekran, "alarm.png")
                self.telegram.alarm(self.alarm_sayisi, self.d.z, self.ham[-1], self.sinyal, "alarm.png")

        self.supurge.kapat()
        self.led.kapat()
        pygame.quit()


if __name__ == "__main__":
    with open("radar_config.json", encoding="utf-8") as f:
        ayar = json.load(f)
    Radar(ayar, Pinger(gateway_bul())).calistir()