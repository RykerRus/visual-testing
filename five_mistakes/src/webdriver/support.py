def remove_focus(driver):
    driver.execute_script("document.activeElement.blur();")


def doc_ready_state(driver, wait=10):
    from selenium.webdriver.support.ui import WebDriverWait
    import time
    try:
        WebDriverWait(driver, wait).until(
            lambda x: x.execute_script("return document.readyState") == "complete")
    except TimeoutError:
        pass
    except Exception:
        time.sleep(4)


def ajax_complite(driver, wait=10):
    from selenium.webdriver.support.ui import WebDriverWait
    try:
        WebDriverWait(driver, wait).until(
            lambda x: x.execute_script("return jQuery.active == 0"))
    except Exception:
        pass
    
@property
def getBoundingClientRect(self):
    try:
        return self.Test.driver.execute_script("return arguments[0].getBoundingClientRect();", self.find(message="find to getBoundingClientRect"))
    except Exception as e:
        print(e, type(e))
        
def screenshots_generator(driver):
    import cv2
    import numpy as np
    import time
    print("start")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    rectangles = []
    top_height = 0
    screenshote = cv2.imdecode(np.asarray(bytearray(driver.get_screenshot_as_png()), dtype=np.uint8), flags=cv2.IMREAD_COLOR)
    yield screenshote
    flag = True
    while flag:
        total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
        top_height += viewport_height
        if top_height >= viewport_height:
            driver.execute_script("window.scrollTo({0}, {1})".format(0, top_height))
            time.sleep(1)
        screenshote = cv2.imdecode(np.asarray(bytearray(driver.get_screenshot_as_png()), dtype=np.uint8), flags=cv2.IMREAD_COLOR)
        if top_height + viewport_height > total_height:
            y0 = total_height - top_height
            y1 = viewport_height
            screenshote = screenshote[y0:y1, :]
            flag = False
        elif top_height + viewport_height == total_height:
            flag = False
        yield screenshote
    else:
        print("end")
            

def hide_elements(driver, elements:list):
    if elements is not None:
        try:
            for e in elements:
                sp_xpath = e.split('=')
                if 'id=' in e.lower():
                    driver.execute_script(
                        "document.getElementById('{}').setAttribute('style', 'opacity: 0;');".format(
                            sp_xpath[1]))
                elif 'class=' in e.lower():
                    driver.execute_script(
                        "document.getElementsByClassName('{}')[0].setAttribute('style', 'opacity: 0;');".format(
                            sp_xpath[1]))
                else:
                    print('For Hiding Element works with ID and Class Selector only')
        except Exception as Error:
            print('Error : ', str(Error))