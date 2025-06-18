# utils/screenshot.py
import time
import os

def take_screenshot(driver, name="screenshot", CS_CODE=None, folder="screenshots"):
    # ✅ ถ้ามี test_id ให้รวม path เข้าไปในโฟลเดอร์
    if CS_CODE:
        folder = os.path.join(folder, str(CS_CODE))

    os.makedirs(folder, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    filepath = os.path.join(folder, filename)

    driver.save_screenshot(filepath)
    return filepath