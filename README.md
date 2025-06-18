# NSS Automate Test System

ระบบ Flask + Selenium + Pytest พร้อม WebSocket สำหรับดู Screenshot แบบ Real-Time

## วิธีติดตั้ง (Setup)

สร้าง virtual environment (แนะนำ)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

## ติดตั้ง dependencies
pip install -r requirements.txt

##รันเซิร์ฟเวอร์
python app.py

📁 โครงสร้างระบบ
app.py - รัน Flask server
src/browser_test/ - เทสด้วย Selenium
src/utils/ - ฟังก์ชันช่วย เช่น screenshot
templates/index.html - หน้า UI แสดงผลแบบ real-time