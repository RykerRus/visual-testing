import pathlib
import sys
import time

import pytest
from webium import BasePage

from five_mistakes import Image
from five_mistakes import support

BASIC_GUEST_URLS = ['/login']


class TestExample(object):
    @pytest.mark.parametrize('url', BASIC_GUEST_URLS)
    @pytest.mark.layout_test
    def test_basic_url_test(self, url, driver, domain_staging, domain_production, screenshots_cache, show_results):
        links = dict(
                production=domain_production + url,
                staging=domain_staging + url)
        for key, url_page in links.items():
            "start procedure"
            page = BasePage(url=url_page, driver=driver)
            page.open()
            support.doc_ready_state(driver)
            support.ajax_complite(driver)
            support.remove_focus(driver)
            driver.execute_script("scrollTo(0,0);")
            time.sleep(1)
            screenshots_cache[key] = Image(driver.get_screenshot_as_png())
            "end procedure"
        flag, screenshots = screenshots_cache["staging"].compare(screenshots_cache["production"], show_results=show_results)
        print(flag, screenshots)
        screenshots_cache["diff"] = screenshots["diff"].tobase64
        screenshots_cache["staging"] = screenshots["imageA"].tobase64
        screenshots_cache["production"] = screenshots["imageB"].tobase64
        assert flag, f"Найдены отличия"

    @pytest.mark.compare_test_image
    @pytest.mark.parametrize("data", [
                                        "no_mistake_cat",
                                        "mistake_cat",
                                        "mistake_jpg_zip",
                                        "all_mistake"
                                        ])
    def test_compare(self, data, screenshots_cache, show_results):
        file_name = data
        with open(f"./example/smoke/first/{file_name}" + ".png", "rb") as f:
            imageA = Image(f.read())
        with open(f"./example/smoke/second/{file_name}" + ".png", "rb") as f:
            imageB = Image(f.read())
        flag, screenshots = imageA.compare(imageB, show_results=show_results)
        print(flag, screenshots)
        screenshots_cache["diff"] = screenshots["diff"].tobase64
        screenshots_cache["staging"] = screenshots["imageA"].tobase64
        screenshots_cache["production"] = screenshots["imageB"].tobase64
        if not flag:
            imageA.save_in_file(f'./example/smoke/result/first_{file_name}' + ".png")
            imageB.save_in_file(f'./example/smoke/result/second_{file_name}' + ".png")
        assert flag, f"Найдены отличия файлов {data}"
    
    @pytest.mark.full_screenshote_join
    def test_full_screenshote_join(self, driver, screenshots_cache, show_results):
        driver.get("https://www.teploluxe.ru")
        support.doc_ready_state(driver)
        support.ajax_complite(driver)
        time.sleep(1)
        img = None
        support.hide_elements(driver, elements=["class=_wc-module", "class=scrollup"])
        for screenshote in support.screenshots_generator(driver):
            if img is None:
                img = Image(screenshote)
                support.hide_elements(driver, elements=["class=header"])
            else:
                img += Image(screenshote)
        if show_results:
            img.show_img()
        screenshots_cache["staging"] = img.tobase64
        assert img.save_in_file(r'./example/smoke/result/full_screenshote_join.png')
    
    @pytest.mark.full_screenshote_resize_pc
    def test_full_screenshote_resize_pc(self, driver, screenshots_cache, show_results):
        driver.get("https://www.teploluxe.ru")
        
        support.doc_ready_state(driver)
        support.ajax_complite(driver)
        
        time.sleep(2)
        
        total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
        driver.set_window_size(1920, total_height)
        img = Image(driver.get_screenshot_as_png())
        if show:
            img.show_img()
        screenshots_cache["staging"] = img.tobase64
        assert img.save_in_file(r'./example/smoke/result/full_screenshote_resize_pc.png')


    @pytest.mark.full_screenshote_resize_mobile
    def test_full_screenshote_resize_pc(self, driver, screenshots_cache, browser, show_results):
        if not browser in ("iphone", "ipad"):
            pytest.skip("no mobile browser")
        driver.get("https://www.teploluxe.ru")
        support.doc_ready_state(driver)
        support.ajax_complite(driver)
        heightscroll = 0
        flag = True
        while flag:  # Прокрутка страницы т.к. при эмуляции страница рендарится после попадения в область видимости
            height = driver.execute_script('return $(document).height()')
            heightscroll += 500
            if heightscroll < height:
                height -= heightscroll
                flag = False
            driver.execute_script(f'window.scrollTo(0, {heightscroll})')
            time.sleep(0.1)
        viewport_width = driver.execute_script("return document.body.clientWidth")
        height = driver.execute_script('return $(document).height()')
        width = driver.execute_script('return $(document).width()')
        driver.set_window_size(width, height)
        time.sleep(2)
        img = Image(driver.get_screenshot_as_png())
        if show_results:
            img.show_img()
        screenshots_cache["staging"] = img.tobase64
        assert img.save_in_file(f'./example/smoke/result/full_screenshote_resize_{browser}.png')
        
if __name__ == "__main__":
    pass
