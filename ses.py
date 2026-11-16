import os

import pygame

class Ses:
    def __init__(self, siren_dosya="polis-emre.mp3", sonra_dosya="modem-gidiyor.mp3"):
        pygame.mixer.pre_init(44100, -16, 1, 256)
        pygame.mixer.init()
        self.kanal = pygame.mixer.Channel(0)
        self.sessiz = False
        self.siren = self.yukle(siren_dosya)
        self.sonra = self.yukle(sonra_dosya)

    def yukle(self,dosya):
        if dosya and os.path.exists(dosya):
            ses = pygame.mixer.Sound(dosya)
            print(f"ses yuklendi: {dosya} ({ses.get_length():.1f} sn)")
            return ses
        print("ses dosyasi yok:", dosya)
        return None

    def cal(self):
        if self.sessiz or self.siren is None:
            return
        if self.kanal.get_busy():
            return 
        self.kanal.play(self.siren)
        if self.sonra:
            self.kanal.queue(self.sonra)

    def sessiz_degistir(self):
        self.sessiz = not self.sessiz
        if self.sessiz:
            self.kanal.stop()
        return self.sessiz

if __name__ == "__main__":
    import time

    s = Ses()
    s.cal()
    while s.kanal.get_busy():
        time.sleep(0.1)
    print("bitti")
