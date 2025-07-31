# Kaza Bildirim Botu (Accident Report Bot)

Bu Telegram botu kaza bildirimlerini toplamak için tasarlanmıştır. Kullanıcılar konum, telefon numarası ve fotoğraf göndererek kaza bildirimi yapabilirler.

## Özellikler

- 🚨 Kaza bildirimi başlatma
- 📍 Konum paylaşımı
- 📱 Telefon numarası paylaşımı
- 📷 Fotoğraf gönderimi
- 👨‍💼 Admin bildirimleri

## Kurulum

### Yerel Geliştirme

1. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Bot token'ınızı ayarlayın:
```bash
export BOT_TOKEN="your_bot_token_here"
export ADMIN_CHAT_ID="your_admin_chat_id"
```

3. Botu çalıştırın:
```bash
python kaza.py
```

### Render Deployment

1. Bu repository'yi GitHub'a push edin
2. Render.com'da yeni bir Web Service oluşturun
3. GitHub repository'nizi bağlayın
4. Environment variables'ları ayarlayın:
   - `BOT_TOKEN`: Telegram bot token'ınız
   - `ADMIN_CHAT_ID`: Admin chat ID'niz
   - `WEBHOOK_URL`: Render app URL'niz + /webhook

5. Deploy edin ve webhook'u ayarlayın:
   - App URL'niz + `/set_webhook` endpoint'ini ziyaret edin

## Kullanım

1. Bot'a `/start` komutu gönderin
2. "🚨 Kaza Bildir" butonuna tıklayın
3. Konumunuzu paylaşın
4. Telefon numaranızı paylaşın
5. Kaza fotoğrafını gönderin

## Dosya Yapısı

- `kaza.py`: Orijinal bot kodu (yerel çalıştırma için)
- `app.py`: Web deployment için Flask wrapper
- `requirements.txt`: Python dependencies
- `Procfile`: Render deployment konfigürasyonu
- `runtime.txt`: Python versiyonu

## Environment Variables

- `BOT_TOKEN`: Telegram bot token'ı
- `ADMIN_CHAT_ID`: Admin chat ID'si
- `WEBHOOK_URL`: Webhook URL'si (Render otomatik ayarlar)
- `PORT`: Port numarası (Render otomatik ayarlar) 