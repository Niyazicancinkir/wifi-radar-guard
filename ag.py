import ctypes
import re
import socket
import struct
import subprocess
import time




def gateway_bul():
    cikti = subprocess.run(["route", "print", "-4", "0.0.0.0"], capture_output=True).stdout.decode("utf-8", "ignore")
    bulunan = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)", cikti)
    if bulunan:
        return bulunan.group(1)
    return None



def sinyal_oku():
    cikti = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True).stdout.decode("utf-8", "ignore")
    bulunan = re.search(r":\s*(\d+)\s*%", cikti)
    if bulunan:
        return int(bulunan.group(1))
    return None


class Pinger:
    def __init__(self, ip, timeout_ms=250, boyut=1000):
        self.ip = ip
        self.timeout_ms = timeout_ms
        self.dll = ctypes.WinDLL("iphlpapi")
        self.dll.IcmpCreateFile.restype = ctypes.c_void_p
        self.dll.IcmpSendEcho.restype = ctypes.c_uint32
        self.dll.IcmpSendEcho.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint16,
                                          ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
        self.handle = self.dll.IcmpCreateFile()
        self.adres = struct.unpack("<I", socket.inet_aton(ip))[0]
        self.veri = bytes(boyut)
        self.cevap = ctypes.create_string_buffer(boyut + 128)

    def ping(self):
        baslangic = time.perf_counter()
        sonuc = self.dll.IcmpSendEcho(self.handle, self.adres, self.veri, len(self.veri), None,
                                      self.cevap, len(self.cevap), self.timeout_ms)
        sure = (time.perf_counter() - baslangic) * 1000
        durum = struct.unpack_from("<I", self.cevap, 4)[0]
        if sonuc == 0 or durum != 0:
            return None
        return sure


if __name__ == "__main__":
    gw = gateway_bul()
    print("gateway:", gw)
    p = Pinger(gw)
    for i in range(10):
        print("ping:", p.ping(), "sinyal:", sinyal_oku())
        time.sleep(0.1)