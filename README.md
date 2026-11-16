# Wi-Fi Radar

Laptopun Wi-Fi bağlantısındaki bozulmadan odaya biri girdiğini anlayan bir alarm sistemi.
Biri modemle laptop arasındaki hattan geçince:

- siren çalar
- Xiaomi S20 robot süpürge hedefe doğru sürülür
- BLEDOM LED şeritler polis çakarına döner
- Telegram'a alarm ekranının fotoğrafı ile mesaj gider

## Nasıl çalışıyor

Laptop modeme saniyede 20 kez ping atar. İnsan vücudu Wi-Fi sinyalini zayıflattığı için biri hattan geçince ping süresi
yükselir ve sinyal gücü düşer. Program ilk 6 saniyede boş odayı ölçer (kalibrasyon), sonra her ölçümün bu normalden
ne kadar saptığına (z-score) bakar. Sapma eşiği art arda birkaç ölçüm boyunca geçerse alarm verir.

## Dosyalar

| Dosya | Ne yapar |
|---|---|
| `ag.py` | Modemi bulur, ping atar, Wi-Fi sinyalini okur |
| `dedektor.py` | Kalibrasyon, filtre ve z-score ile alarm kararı |
| `supurge.py` | Robot süpürgeye yerel ağdan bağlanır ve sürer |
| `ses.py` | Siren ve alarm seslerini çalar |
| `ekran.py` | Durum, ping grafiği ve olay mesajlarını gösteren pencere |
| `telegram.py` | Alarm anında Telegram botuna mesaj ve fotoğraf gönderir |
| `led.py` | BLEDOM LED şeritleri Bluetooth ile kırmızı/mavi çakar yapar |
| `main.py` | Hepsini birleştirir ve tuşları dinler |

## Kurulum

```bash
py -m pip install pygame python-miio==0.5.12 requests pycryptodome bleak
copy radar_config.example.json radar_config.json
```

`radar_config.json` dosyasını doldur:

- `vacuum`: robotun yerel IP'si, 32 karakterlik token'ı ve `did` numarası
- `led`: LED şeritlerin Bluetooth adresleri
- `telegram`: BotFather'dan alınan bot token'ı ve chat_id

chat_id'yi bulmak için botuna Telegram'dan bir mesaj at, `chat_id` alanı boşken `py telegram.py` çalıştır.

## Çalıştırma

```bash
py main.py
```

Açılınca 6 saniye odada kimse hareket etmesin, kalibrasyon yapılıyor.

| Tuş | İş |
|---|---|
| C | Yeniden kalibrasyon |
| F | Filtreyi aç/kapa |
| SPACE | Alarmı elle tetikle |
| M | Sesi kapat/aç |
| Oklar | Süpürgeyi elle sür |
| S | Süpürgeyi ve LED'leri durdur |
| H | Süpürgeyi şarja gönder |
| ESC | Çıkış |

Her modül tek başına da çalıştırılıp test edilebilir, örneğin `py ag.py` ya da `py dedektor.py`.

## Gereksinimler

- Windows, Wi-Fi'a bağlı bir laptop (Ethernet ile algılama çalışmaz)
- Bluetooth (LED'ler için). Telefondaki LED uygulaması kapalı olmalı, şeritler aynı anda tek cihaza bağlanır
- Robot süpürge ile aynı yerel ağ
