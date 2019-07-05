import imutils
from skimage.measure import compare_ssim
import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class Image:
    def __init__(self, image):
        self.image = self._get_ndarray(image)

    def __str__(self):
        return f"< {type(self)} | self.image = {type(self.image)}>"
    
    def __add__(self, other):
        return Image(np.concatenate((self.image, other.image), axis=0))

    def __iadd__(self, other):
        return Image(np.concatenate((self.image, other.image), axis=0))

    def compare(self, other, accuracy=0.9999, show_results=False) -> tuple:
        """
        :param other: это второй экземпляр класса five_mistake.Image
        :param accuracy:Это значение может попадать в диапазон [-1, 1] со значением
            “идеальное совпадение”.
        :param show_results: :type bool:
        :return :type list: list[0] = status, list[1] = dict screenshots, dict_keys: imageA, imageB diff
        """
        grayA = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(other.image, cv2.COLOR_BGR2GRAY)
        (score, diff) = compare_ssim(grayA, grayB, full=True)
        score = round(score, 6)
        if score < accuracy:
            diff = (diff * 255).astype("uint8")
            """print(f"SSIM разница между изображениями: {score} \n"
                  f"Заданная точность {self.accuracy}\n"
                  f"delta {score - self.accuracy}")"""
            cnts = self._get_contours(diff=diff)
            self.draw_rectangle_mistake(cnts, self, other)
            if show_results:
                cv2.imshow("Original", self.image)
                cv2.imshow("Modified", other.image)
                cv2.imshow("Diff", diff)
                cv2.waitKey(0)
            print("diff", diff)
            return (False, {"imageA": self, "imageB": other, "diff": Image(diff)})
        else:
            return (True, {"imageA": self, "imageB": other, "diff": Image(diff)})

    @staticmethod
    def draw_rectangle_mistake(contours: list, imageA, imageB) -> None:
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(imageA.image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(imageB.image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    def save_in_file(self, filename) -> bool:
        assert isinstance(self.image, np.ndarray)
        return cv2.imwrite(filename, self.image)

    def get_image(self, encode="png"):
        try:
            assert isinstance(self.image, np.ndarray)
        except AssertionError as e:
            raise TypeError(f"TypeError: screenshot mast be type np.ndarray not {type(self.image)}")
        return self._render_opencv(self.image, encode=encode)
    
    def show_img(self):
        scale_percent = 40  # percent of original size
        width = int(self.image.shape[1] * scale_percent / 100)
        height = int(self.image.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        resized = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)
        cv2.imshow("show", resized)
        cv2.waitKey(0)

    @staticmethod
    def _get_contours(diff: np.ndarray) -> list:
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return imutils.grab_contours(cnts)

    @staticmethod
    def _get_ndarray(img) -> np.ndarray:
        if isinstance(img, np.ndarray):
            return img
        return cv2.imdecode(np.asarray(bytearray(img), dtype=np.uint8), flags=cv2.IMREAD_COLOR)

    @staticmethod
    def _render_opencv(img: np.ndarray, encode="png"):
        if not isinstance(img, np.ndarray):
            print(f"np.ndarray object is required, not ' {type(img)}'")
            return None
        retval, buf = cv2.imencode(ext=".%s" % encode, img=img)
        if not retval:
            print(f"Error: status render False")
            return None
        return buf

    @property
    def tobase64(self):
        import base64
        try:
            assert isinstance(self.image, np.ndarray)
        except AssertionError as e:
            raise TypeError(f"TypeError: screenshot mast be type np.ndarray not {type(self.image)}")
        buf = self._render_opencv(self.image, encode="png").tostring()
        return base64.b64encode(buf)
