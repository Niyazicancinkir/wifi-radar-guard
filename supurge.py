import threading
import time

from miio import Device

YONLER = {"forward": 1, "left": 2, "right": 3, "backward": 4, "stop": 5, "exit": 10}

class Supurge:
    def __init__(self, ip, token, did):
        self.ip = ip
        self.token = token
        self.did = did
        self.cihaz = None
        self.plan = []          # [(yon kodu, bitis zamani)]
        self.elle_yon = None    # ok tuslariyla surus
        self.calisiyor = True
        threading.Thread(target=self.dongu, daemon=True).start()
    
    def baglan(self):
        while self.calisiyor:
            try:
                cihaz = Device(self.ip, self.token)
                cihaz.info()
                self.cihaz = cihaz
                print("supurge baglandi:", self.ip)
                return
            except Exception as e:
                print("supurge baglanamadi:", e)
                time.sleep(3)

    def yon_gonder(self, kod):
        self.cihaz.send("set_properties", [{"did": self.did, "siid": 7, "piid": 16, "value": kod}])

    def dongu(self):
        self.baglan()
        hareket = False
        while self.calisiyor:
            simdi = time.time()
            while self.plan and simdi >= self.plan[0][1]:
                self.plan.pop(0)

            if self.plan:
                kod = self.plan[0][0]
            else:
                kod = self.elle_yon

            try:
                if kod:
                    self.yon_gonder(kod)
                    hareket = True
                elif hareket:
                    self.yon_gonder(YONLER["stop"])
                    self.yon_gonder(YONLER["exit"])
                    hareket = False
            except Exception as e:
                print("supurge hata:", e)
            time.sleep(0.1)

        if hareket:
            self.yon_gonder(YONLER["stop"])
            self.yon_gonder(YONLER["exit"])

        
    def saldir(self,adimlar):
        if self.cihaz is None:
            print("supurge bagli degil")
            return
        if self.plan:
            return  # manevra zaten suruyor
        zaman = time.time()
        yeni_plan = []
        for yon, sure in adimlar:
            zaman += sure
            yeni_plan.append((YONLER[yon], zaman))
        self.plan = yeni_plan

    def durdur(self):
        self.plan = []
        self.elle_yon = None

    def sarja_gonder(self):
        if self.cihaz is None:
            return
        self.durdur()
        time.sleep(0.3)
        self.cihaz.send("action", {"did": "call-3-1", "siid": 3, "aiid": 1, "in": []})

    def kapat(self):
        self.durdur()
        time.sleep(0.3)
        self.calisiyor = False
        time.sleep(0.2)

if __name__ == "__main__":
    import json

    with open("radar_config.json", encoding="utf-8") as f:
        ayar = json.load(f)["vacuum"]

    s = Supurge(ayar["ip"], ayar["token"], ayar["did"])
    while s.cihaz is None:
        time.sleep(0.2)

    print("kisa test manevrasi: sola, saga")
    s.saldir([["left", 0.5], ["right", 0.5]])
    time.sleep(2)
    s.kapat()
    print("bitti")