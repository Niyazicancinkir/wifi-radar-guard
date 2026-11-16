import asyncio
import threading
import time

from bleak import BleakClient

YAZMA = "0000fff3-0000-1000-8000-00805f9b34fb"  

ACIK = bytes([0x7E, 0x00, 0x04, 0xF0, 0x00, 0x01, 0xFF, 0x00, 0xEF])
KAPALI = bytes([0x7E, 0x00, 0x04, 0x00, 0x00, 0x00, 0xFF, 0x00, 0xEF])

KIRMIZI = (255, 0, 0)
MAVI = (0, 0, 255)


def renk_komutu(r, g, b):
    return bytes([0x7E, 0x00, 0x05, 0x03, r, g, b, 0x00, 0xEF])


def parlaklik_komutu(yuzde):
    return bytes([0x7E, 0x00, 0x01, yuzde, 0x00, 0x00, 0x00, 0x00, 0xEF])


class Led:
    def __init__(self, adresler, normal_renk=(255, 255, 255)):
        self.adresler = adresler
        self.normal_renk = tuple(normal_renk)
        self.cihazlar = []
        self.cakar_bitis = 0
        self.dongu = asyncio.new_event_loop()
        threading.Thread(target=self.dongu.run_forever, daemon=True).start()
        self.calistir(self.baglan())

    def calistir(self, gorev):
        return asyncio.run_coroutine_threadsafe(gorev, self.dongu)

    async def baglan(self):
        for adres in self.adresler:
            try:
                cihaz = BleakClient(adres)
                await cihaz.connect(timeout=15)
                self.cihazlar.append(cihaz)
                print("led baglandi:", adres)
            except Exception as e:
                print("led baglanamadi:", adres, type(e).__name__, e)

    async def yaz(self, cihaz, veri):
        try:
            await cihaz.write_gatt_char(YAZMA, veri, response=False)
        except Exception as e:
            print("led hata:", type(e).__name__, e)

    async def hepsine(self, veri):
        for cihaz in self.cihazlar:
            await self.yaz(cihaz, veri)

    async def cakar_dongusu(self):
        await self.hepsine(ACIK)
        await self.hepsine(parlaklik_komutu(100))
        sira = 0
        while time.time() < self.cakar_bitis:
            # bir serit kirmiziyken digeri mavi, her turda yer degistirirler
            for i, cihaz in enumerate(self.cihazlar):
                if (i + sira) % 2 == 0:
                    await self.yaz(cihaz, renk_komutu(*KIRMIZI))
                else:
                    await self.yaz(cihaz, renk_komutu(*MAVI))
            sira += 1
            await asyncio.sleep(0.25)
        await self.hepsine(renk_komutu(*self.normal_renk))

    def cakar(self, sure):
        zaten_caliyor = time.time() < self.cakar_bitis
        self.cakar_bitis = time.time() + sure
        if not zaten_caliyor:
            self.calistir(self.cakar_dongusu())

    def durdur(self):
        self.cakar_bitis = 0

    def renk(self, r, g, b):
        self.calistir(self.hepsine(renk_komutu(r, g, b)))

    async def ayril(self):
        for cihaz in self.cihazlar:
            try:
                await cihaz.disconnect()
            except Exception:
                pass

    def kapat(self):
        self.durdur()
        time.sleep(0.4)
        self.calistir(self.ayril()).result(timeout=5)


if __name__ == "__main__":
    import json

    with open("radar_config.json", encoding="utf-8") as f:
        ayar = json.load(f)["led"]

    led = Led(ayar["adresler"], ayar.get("normal_renk", (255, 255, 255)))
    time.sleep(8) 
    print("5 saniye polis cakari")
    led.cakar(5)
    time.sleep(6)
    led.kapat()
    print("bitti")