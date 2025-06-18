from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from src.utils.seleniumUtils import search
from src.utils.screenshot import take_screenshot

import time
import asyncio
import io
import sys

# from src.utils.seleniumUtils import waitForElement
def send_log(socketio, sid, message):
    print(message)
    socketio.emit("test_result", message, to=sid)

def run_test(socketio, sid, CS_CODE):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--force-device-scale-factor=0.45")  # scale 75%
        options.add_experimental_option('detach', True)
        driver = webdriver.Chrome(options=options)
        
        driver.get('https://nsscsposminiapp-dev.counterservice.co.th/sale/index.html#/miniapp')
        send_log(socketio, sid, "✅ เข้าหน้าเว็บสำเร็จ")
        driver.maximize_window()

        result = test_case_error(driver, socketio, sid, CS_CODE)
        if result == "Test passed! True Group Error":
            result = test_case_success(driver, socketio, sid, CS_CODE)

        send_log(socketio, sid, result)
    except Exception as e:
        send_log(socketio, sid, f"❌ Test failed: {e}")

def test_case_error(driver, socketio, sid, CS_CODE):
    try:
        send_log(socketio, sid, "🚀 เริ่มทดสอบ True Group Error")
        time.sleep(5)
        send_log(socketio, sid, "✅ โหลดหน้าเว็บสำเร็จ")
        time.sleep(15)
        iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe')
        send_log(socketio, sid, f"📌 พบทั้งหมด {len(iframes)} iframes")
        if len(iframes) < 2:
            raise ValueError("❌ ไม่พบ iframe ที่ต้องการ (ต้องมี 2)")
        
        # ดึง iframe ตัวแรกและตัวที่สอง
        iframe_onetouch = iframes[0]
        iframe_subpage = iframes[1]

        # สลับไปยัง iframe ตัวแรก
        driver.switch_to.frame(iframe_onetouch)
        send_log(socketio, sid, f"✅ สลับไปยัง iframe หลักสำเร็จ")

        time.sleep(5)
        buttons = driver.find_elements(By.CLASS_NAME,'main-card-container')

        if (len(buttons) < 3) :
            raise ValueError("❌ ไม่พบปุ่มที่ต้องการคลิก")
        send_log(socketio, sid, f"✅ คลิกปุ่มสำเร็จ")
        buttons[2].click()

        # กลับไปที่หน้าเริ่มต้นและสลับไปยัง iframeSubPage
        driver.switch_to.default_content() # ออกจาก iframe แรก
        driver.switch_to.frame(iframe_subpage) # เข้า iframe ตัวที่สอง
        send_log(socketio, sid, f"✅ สลับไปยัง iframe ย่อยสำเร็จ")

        nestedIframes = driver.find_elements(By.CSS_SELECTOR,'iframe')
        send_log(socketio, sid, f"📌 พบ iframe ซ้อนกัน: {len(nestedIframes)} iframe")

        if (len(nestedIframes) > 0) :
            driver.switch_to.frame(nestedIframes[0])
            send_log(socketio, sid, f"✅ เข้าไปใน nested iframe สำเร็จ")
        time.sleep(10)

        send_log(socketio, sid, f"❌ ไม่เข้าไปใน nested iframe")
        # 🔍 หา input field
        input_fields = driver.find_elements(By.CLASS_NAME,'text-field-input')
        if len(input_fields) < 0 :
            raise ValueError("❌ ไม่พบ input field")
        send_log(socketio, sid, f"✅ พบ input field")
        take_screenshot(driver,"test_case_error",CS_CODE)

        time.sleep(5)
        actions = ActionChains(driver)
        actions.move_to_element(input_fields[0]).send_keys('123').perform()
        send_log(socketio, sid, f"✅ ป้อนค่า 123 ใน input field - Ref1")
        take_screenshot(driver,"test_case_error",CS_CODE)

        time.sleep(2)
        actions.send_keys(Keys.ENTER).perform()
        send_log(socketio, sid, f"✅ กดปุ่ม Enter สำเร็จ")

        time.sleep(2)
        actions.move_to_element(input_fields[1]).send_keys('123').perform()
        send_log(socketio, sid, f"✅ ป้อนค่า 123 ใน input field - Ref2")
        take_screenshot(driver,"test_case_error",CS_CODE)

        time.sleep(2)
        actions.send_keys(Keys.ENTER).perform()
        send_log(socketio, sid, f"✅ กดปุ่ม Enter สำเร็จ")

        time.sleep(10)
        message_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".messageCode-alert"))
        )

        # ดึงข้อความจาก element
        message_text = message_element.text
        send_log(socketio, sid, f"=>" + message_text)
        message_error = ["[ COUN90000 ]", "[ NSS999999 ]"]
        
        found = False
        for error in message_error:
            if error in message_text:
                send_log(socketio, sid, f"✅ พบ Error code: {error}")
                take_screenshot(driver,"test_case_error",CS_CODE)
                result = "Test passed! True Group Error"
                found = True
                break  # ถ้าเจอ error ตัวใดตัวหนึ่งแล้ว ไม่ต้องวนต่อ

        if not found:
            send_log(socketio, sid, "❌ ไม่พบข้อความที่ต้องการ")
            take_screenshot(driver,"test_case_error",CS_CODE)
            result = "Test failed! True Group Error"
            driver.quit()
        
        send_log(socketio, sid, result)
        return result
    except Exception as e:
        error_msg = f"Test failed: {e}"
        send_log(socketio, sid, error_msg)
        driver.quit()
        return error_msg

def test_case_success(driver, socketio, sid, CS_CODE):
    try:
        driver.refresh()
        time.sleep(5)
        send_log(socketio, sid, "\n")
        send_log(socketio, sid, f"🚀 เริ่มทดสอบ True Group Success")
        time.sleep(5)
        send_log(socketio, sid, f'✅ โหลดหน้าเว็บสำเร็จ')
        iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe')
        send_log(socketio, sid, f"📌 พบทั้งหมด {len(iframes)} iframes")

        if len(iframes) < 2:
            raise ValueError(f"❌ ไม่พบ iframe ที่ต้องการ (ต้องมี 2)")
        
        # ดึง iframe ตัวแรกและตัวที่สอง
        iframe_onetouch = iframes[0]
        iframe_subpage = iframes[1]

        # สลับไปยัง iframe ตัวแรก
        driver.switch_to.frame(iframe_onetouch)
        send_log(socketio, sid, f"✅ สลับไปยัง iframe หลักสำเร็จ")

        time.sleep(5)
        buttons = driver.find_elements(By.CLASS_NAME,'main-card-container')

        if (len(buttons) < 3) :
            raise ValueError("❌ ไม่พบปุ่มที่ต้องการคลิก")
        send_log(socketio, sid, f"✅ คลิกปุ่มสำเร็จ")
        buttons[2].click()
        time.sleep(10)

        # กลับไปที่หน้าเริ่มต้นและสลับไปยัง iframeSubPage
        driver.switch_to.default_content() # ออกจาก iframe แรก
        driver.switch_to.frame(iframe_subpage) # เข้า iframe ตัวที่สอง
        send_log(socketio, sid, f"✅ สลับไปยัง iframe ย่อยสำเร็จ")

        nestedIframes = driver.find_elements(By.CSS_SELECTOR,'iframe')
        send_log(socketio, sid, f"📌 พบ iframe ซ้อนกัน: {len(nestedIframes)} iframe")

        if (len(nestedIframes) > 0) :
            driver.switch_to.frame(nestedIframes[0])
            send_log(socketio, sid, f"✅ เข้าไปใน nested iframe สำเร็จ")
        time.sleep(10)

        send_log(socketio, sid, f"❌ ไม่เข้าไปใน nested iframe")
        # 🔍 หา input field
        input_fields = driver.find_elements(By.CLASS_NAME,'text-field-input')
        if len(input_fields) < 0 :
            raise ValueError("❌ ไม่พบ input field")
        send_log(socketio, sid, f"✅ พบ input field")
        take_screenshot(driver,"test_case_success",CS_CODE)

        time.sleep(5)
        actions = ActionChains(driver)
        actions.move_to_element(input_fields[0]).send_keys('700072215').perform()
        send_log(socketio, sid, f"✅ ป้อนค่า 700072215 ใน input field - Ref1")
        take_screenshot(driver,"test_case_success",CS_CODE)

        time.sleep(2)
        actions.send_keys(Keys.ENTER).perform()
        send_log(socketio, sid, f"✅ กดปุ่ม Enter สำเร็จ")

        time.sleep(2)
        actions.move_to_element(input_fields[1]).send_keys('700072215').perform()
        send_log(socketio, sid, f"✅ ป้อนค่า 700072215 ใน input field - Ref2")
        take_screenshot(driver,"test_case_success",CS_CODE)

        time.sleep(2)
        actions.send_keys(Keys.ENTER).perform()
        send_log(socketio, sid, f"✅ กดปุ่ม Enter สำเร็จ")

        driver.switch_to.default_content()
        send_log(socketio, sid, f"🔄 กลับไปที่ root page")

        newIframes = driver.find_elements(By.CSS_SELECTOR,'iframe')
        send_log(socketio, sid, f"📌 พบ iframes : {len(newIframes)} iframe")

        # XPATH ของปุ่ม 'แก้ไข'
        xpath_selector = '//*[@id="headlessui-dialog-panel-:rl:"]/div/div[4]/div/button[1]'
        # รันการค้นหา
        edit_success = search(driver, newIframes, xpath_selector, 700, socketio=socketio, sid=sid, CS_CODE=CS_CODE)

        # แสดงผลลัพธ์
        if edit_success:
            send_log(socketio, sid, f"✅ คลิกปุ่ม 'แก้ไข' สำเร็จ")
        else:
            send_log(socketio, sid, f"❌ ไม่สามารถคลิกปุ่ม 'แก้ไข' ได้")
            driver.quit()
            return "Failed"

        driver.switch_to.frame(iframe_subpage) # เข้า iframe ตัวที่สอง
        send_log(socketio, sid, f"✅ สลับไปยัง iframe ย่อยสำเร็จ")
        time.sleep(2)
        # 🔍 หา input field
        input_fields_price = driver.find_elements(By.CLASS_NAME,'text-field-price-card-input-box')
        if len(input_fields_price) < 0 :
            raise ValueError("❌ ไม่พบ input field price")
        send_log(socketio, sid, f"✅ พบ input field price {len(input_fields_price)} input")

        # actions = ActionChains(driver)
        actions.move_to_element(input_fields_price[0]).send_keys('100').perform()
        send_log(socketio, sid, f"✅ ป้อนค่า 100 ใน input field price")
        take_screenshot(driver,"test_case_success",CS_CODE)

        driver.switch_to.default_content()
        send_log(socketio, sid, f"🔄 กลับไปที่ root page")

        newIframes = driver.find_elements(By.CSS_SELECTOR,'iframe')
        send_log(socketio, sid, f"📌 พบ iframes : {len(newIframes)} iframe")

        xpath_confirm = '//*[@id="root"]/div/div/div/div/div[1]/div/div[20]/div[4]/div[2]/div/div/button'
        # รันการค้นหา
        edit_success = search(driver, newIframes, xpath_confirm, 700, socketio=socketio, sid=sid, CS_CODE=CS_CODE)

        # แสดงผลลัพธ์
        if edit_success:
            send_log(socketio, sid, f"✅ คลิกปุ่ม 'ยืนยันการทำรายการ' สำเร็จ")
        else:
            send_log(socketio, sid, f"❌ ไม่สามารถคลิกปุ่ม 'ยืนยันการทำรายการ' ได้")
            driver.quit()
            return "Failed"

        xpath_submit = '//*[@id="headlessui-dialog-panel-:ro:"]/div/div[4]/div/button[3]'
        # รันการค้นหา
        take_screenshot(driver,"test_case_success",CS_CODE)
        submit_success = search(driver, newIframes, xpath_submit, 700, socketio=socketio, sid=sid, CS_CODE=CS_CODE)

        # แสดงผลลัพธ์
        if submit_success:
            send_log(socketio, sid, f"✅ คลิกปุ่ม 'ยืนยัน' สำเร็จ")
        else:
            send_log(socketio, sid, f"❌ ไม่สามารถคลิกปุ่ม 'ยืนยัน' ได้")
            driver.quit()
            return "Failed"
            
        result = "Test passed! True Group Success"
        send_log(socketio, sid, result)
        driver.quit()
        return result
    except Exception as e:
        error_msg = f"Test failed: {e}"
        send_log(socketio, sid, error_msg)
        driver.quit()
        return error_msg
    
