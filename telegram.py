import threading
import time

import requests


class Telegram:
    def __init__(self, token, chat_id):
        self.adres = f"https://api.telegram.org/bot{token}/"
        self.chat_id = chat_id
        self.acik = bool(token and chat_id)
        if not self.acik:
            print("telegram kapali (radar_config.json icinde token / chat_id yok)")

    def gonder(self, metin, foto=None):
        if self.acik:
            threading.Thread(target=self._gonder, args=(metin, foto), daemon=True).start()

    def _gonder(self, metin, foto):
        try:
            if foto:
                with open(foto, "rb") as f:
                    cevap = requests.post(self.adres + "sendPhoto", data={"chat_id": self.chat_id, "caption": metin},
                                          files={"photo": f}, timeout=15)
            else:
                cevap = requests.post(self.adres + "sendMessage", data={"chat_id": self.chat_id, "text": metin},
                                      timeout=15)
            if not cevap.ok:
                print("telegram hata:", cevap.text[:120])
        except Exception as e:
            print("telegram gonderilemedi:", type(e).__name__)

    def alarm(self, alarm_no, z, ping, sinyal, foto=None):
        metin = (f"DİKKAT 🚨 ALARM #{alarm_no}\n"
                 f"Odaya biri yaklasti!\n\n"
                 f"Zaman: {time.strftime('%d.%m.%Y %H:%M:%S')}\n"
                 f"z-score: {z:.1f}\n"
                 f"Ping: {ping:.2f} ms\n"
                 f"Sinyal: {sinyal}\n\n"
                 f"Siren caldi, supurge yola cikti.")
        self.gonder(metin, foto)


def chat_id_bul(token):
    cevap = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=15).json()
    if not cevap.get("ok"):
        print("token hatali:", cevap.get("description"))
        return
    bulundu = False
    for guncelleme in cevap["result"]:
        mesaj = guncelleme.get("message")
        if mesaj:
            print("chat_id:", mesaj["chat"]["id"], "-", mesaj["chat"].get("first_name"))
            bulundu = True

if __name__ == "__main__":
    import json

    with open("radar_config.json", encoding="utf-8") as f:
        ayar = json.load(f).get("telegram", {})

    if ayar.get("token") and not ayar.get("chat_id"):
        chat_id_bul(ayar["token"])
    else:
        t = Telegram(ayar.get("token"), ayar.get("chat_id"))
        t.alarm(1, 7.3, 6.42, 78)
        time.sleep(5)
        print("test mesaji gonderildi, telegrami kontrol et")