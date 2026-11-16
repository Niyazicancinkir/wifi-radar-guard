import pygame

SIYAH = (0, 0, 0)
BEYAZ = (255, 255, 255)
GRI = (110, 110, 110)
YESIL = (0, 200, 0)
SARI = (230, 200, 0)
KIRMIZI = (200, 0, 0)


class Ekran:
    def __init__(self,genislik=900,yukseklik=520):
        pygame.init()
        self.genislik = genislik
        self.yukseklik = yukseklik
        self.ekran = pygame.display.set_mode((genislik, yukseklik))
        pygame.display.set_caption("Wi-Fi Radar")
        self.yazi = pygame.font.SysFont("consolas", 20)
        self.buyuk = pygame.font.SysFont("consolas", 64, bold=True)
        self.saat = pygame.time.Clock()

    def yaz(self, metin, x, y, renk = BEYAZ, font=None):
        if font is None:
            font = self.yazi
        self.ekran.blit(font.render(metin, True, renk), (x, y))


    def cizgi(self, degerler, x, y, g, y_yuk, ust, renk):
        if len(degerler) < 2:
            return
        noktalar = []
        for i, v in enumerate(degerler):
            px = x + i * g / (len(degerler) - 1)
            py = y + y_yuk - min(v, ust) / ust * y_yuk
            noktalar.append((px, py))
        pygame.draw.lines(self.ekran, renk, False, noktalar, 2)

    def ciz(self, d, ham, filtreli, sinyal, alarm_sayisi, mesajlar, sessiz=False):
        if d.durum == "ALARM":
            self.ekran.fill(KIRMIZI)
        else:
            self.ekran.fill(SIYAH)

        if d.durum == "KALIBRASYON":
            self.yaz("KALIBRASYON...", 20, 15, SARI, self.buyuk)
        elif d.durum == "ALARM":
            self.yaz("ALARM!", 20, 15, BEYAZ, self.buyuk)
        else:
            self.yaz("TEMIZ", 20, 15, YESIL, self.buyuk)

        son_ping = ham[-1] if ham else 0
        self.yaz(f"ping: {son_ping:.2f} ms   filtreli: {d.filtreli:.2f} ms", 20, 100)
        self.yaz(f"z: {d.z:.2f}   esik: {d.esik}   sinyal: {sinyal}", 20, 125)
        filtre = "ACIK" if d.filtre_acik else "KAPALI"
        ses = "KAPALI" if sessiz else "ACIK"
        self.yaz(f"alarm: {alarm_sayisi}   filtre: {filtre}   ses: {ses}", 20, 150)

        # ping grafigi: gri = ham, yesil = filtreli
        gx, gy, gg, gy_yuk = 20, 190, self.genislik - 40, 200
        pygame.draw.rect(self.ekran, GRI, (gx, gy, gg, gy_yuk), 1)
        son = list(filtreli)[-100:] or [1]
        ust = max(max(son) * 2, 2)
        self.cizgi(list(ham), gx, gy, gg, gy_yuk, ust, GRI)
        self.cizgi(list(filtreli), gx, gy, gg, gy_yuk, ust, YESIL)
        self.yaz(f"{ust:.0f} ms", gx + 5, gy + 5, GRI)

        soluk = BEYAZ if d.durum == "ALARM" else GRI
        for i, m in enumerate(mesajlar[-3:]):
            self.yaz(m, 20, 405 + i * 22, soluk)
        self.yaz("C kalibrasyon  F filtre  SPACE test  M ses  oklar  S dur  H sarj  ESC", 20, 485, soluk)

        pygame.display.flip()
        self.saat.tick(30)



if __name__ == "__main__":
    import random
    from collections import deque

    from dedektor import Dedektor

    e = Ekran()
    d = Dedektor()
    ham = deque(maxlen=300)
    filtreli = deque(maxlen=300)
    i = 0
    while i < 400:
        for olay in pygame.event.get():
            if olay.type == pygame.QUIT:
                i = 9999
        for _ in range(2):
            ping = random.gauss(3.0, 0.35)
            if 250 <= i < 290:
                ping += 4
            d.guncelle(ping)
            ham.append(ping)
            filtreli.append(d.filtreli if d.durum != "KALIBRASYON" else ping)
            i += 1
        e.ciz(d, ham, filtreli, None, 0, ["test mesaji"])
    pygame.quit()        