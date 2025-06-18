from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from src.utils.screenshot import take_screenshot
import time

def send_log(socketio, sid, message):
    if socketio and sid:
        socketio.emit('test_result', message, room=sid)
    print(message)

def wait_for_element(driver, xpath_selector, socketio=None, sid=None, timeout=10):    
    """ รอจนกว่า element จะปรากฏและมองเห็นได้ """
    send_log(socketio, sid, f"⏳ รอ element: {xpath_selector}")

    try:
        # รอให้ element ปรากฏใน DOM
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath_selector))
        )

        # รอให้ element มองเห็นได้ (visibility)
        visible_element = WebDriverWait(driver, timeout).until(
            EC.visibility_of(element)
        )

        send_log(socketio, sid, f"✅ พบและมองเห็น element: {xpath_selector}")
        return visible_element
    except TimeoutException:
        send_log(socketio, sid, f"❌ Timeout: ไม่พบ element {xpath_selector} ภายใน {timeout} วินาที")
        return None

def click_with_wait(driver, xpath_selector, socketio=None, sid=None, timeout=10):
    """ รอและคลิก element ตาม XPATH ที่กำหนด """
    try:
        # รอให้ element ปรากฏ
        element = wait_for_element(driver, xpath_selector, socketio, sid)
        if not element:
            send_log(socketio, sid, f"❌ ไม่สามารถคลิกได้: ไม่พบ element {xpath_selector}")
            return False

        # รอให้ element พร้อมใช้งาน
        WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.XPATH, xpath_selector)))

        # เลื่อนหน้าไปยัง element
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

        # คลิก element (ใช้ JavaScript เพื่อ bypass ปัญหาคลิกไม่ได้)
        driver.execute_script("arguments[0].click();", element)

        send_log(socketio, sid, f"✅ คลิก {xpath_selector} สำเร็จ")
        return True
    except TimeoutException:
        send_log(socketio, sid, f"❌ Timeout: ไม่พบ {xpath_selector} ภายใน {timeout} วินาที")
    except NoSuchElementException:
        send_log(socketio, sid, f"❌ ไม่พบ {xpath_selector}")
    except ElementNotInteractableException:
        send_log(socketio, sid, f"❌ {xpath_selector} ไม่สามารถคลิกได้")
    except Exception as e:
        send_log(socketio, sid, f"❌ ไม่สามารถคลิก {xpath_selector}: {str(e)}")

def search(driver, iframes, xpath_selector, wait_time, socketio=None, sid=None, CS_CODE=None):
    """ ค้นหาและคลิก element ภายใน iframes """
    # time.sleep(wait_time / 1000)  # Convert ms to seconds
    time.sleep(10)
    print(CS_CODE)

    for index, iframe in enumerate(iframes):
        try:
            driver.switch_to.frame(iframe)# สลับไปยัง iframe
            send_log(socketio, sid, f"✅ ลองเข้า iframe ที่ {index + 1}")

            element = wait_for_element(driver, xpath_selector, socketio, sid)
            if element:
                take_screenshot(driver, name="test_case_success", CS_CODE=CS_CODE)
                send_log(socketio, sid, f"✅ พบ element ใน iframe ที่ {index + 1}")
                success = click_with_wait(driver, xpath_selector, socketio, sid) # คลิก element
                if success:
                    return True # ออกจาก loop เมื่อพบและคลิกสำเร็จ

        except (NoSuchElementException, TimeoutException):
            send_log(socketio, sid, f"❌ ไม่พบ element ใน iframe ที่ {index + 1}, ลอง iframe ถัดไป")

        finally:
            driver.switch_to.default_content() # กลับไปที่ default content หลังจากแต่ละ iframe

    send_log(socketio, sid, "❌ ไม่พบ element ในทุก iframe")
    return False

