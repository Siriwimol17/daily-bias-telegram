# Daily Bias XAUUSD + US100 → Telegram

Automation ที่วิเคราะห์ Daily Bias ของ XAUUSD และ US100 แล้วส่งเข้า Telegram ทุก 4 ชั่วโมง

## วิธีติดตั้ง (ทำครั้งเดียว)

### 1. สร้าง Telegram Bot
1. เปิด Telegram → ค้นหา `@BotFather`
2. พิมพ์ `/newbot` แล้วทำตามขั้นตอน
3. คัดลอก **Bot Token**

### 2. หา Chat ID
1. ส่งข้อความอะไรก็ได้ให้ bot ที่สร้างไว้
2. เปิดลิงก์นี้ในเบราว์เซอร์ (แทน TOKEN ด้วยของจริง):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
3. หา `"chat":{"id": ตัวเลข}` → นั่นคือ Chat ID

### 3. ใส่ Secrets ใน GitHub
1. ไปที่ repo นี้ → **Settings** → **Secrets and variables** → **Actions**
2. กด **New repository secret** แล้วเพิ่ม 2 ตัว:
   - Name: `TELEGRAM_BOT_TOKEN`  → ใส่ Bot Token
   - Name: `TELEGRAM_CHAT_ID`   → ใส่ Chat ID

### 4. ทดสอบ
1. ไปที่แท็บ **Actions**
2. เลือก workflow **Daily Bias Telegram**
3. กด **Run workflow** → **Run workflow**
4. รอสักครู่ แล้วดูว่ามีข้อความเข้า Telegram หรือไม่

## ตารางเวลา (โดยประมาณ)

| UTC       | เวลาไทย   |
|-----------|-----------|
| 00:00     | 07:00     |
| 04:00     | 11:00     |
| 08:00     | 15:00     |
| 12:00     | 19:00     |
| 16:00     | 23:00     |
| 20:00     | 03:00     |

## หมายเหตุ
- ใช้ `GC=F` (Gold Futures) เป็น proxy ของ XAUUSD
- ใช้ `NQ=F` (Nasdaq Futures) เป็น proxy ของ US100
- ข้อมูลเป็นแค่ตัวช่วยตัดสินใจ ยังต้องยืนยันด้วยตาและ CISD บนชาร์ตจริง
