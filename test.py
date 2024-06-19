import cv2
import numpy as np

class BlumCryptoBot:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.lower_green = np.array([40, 150, 150])
        self.upper_green = np.array([80, 255, 255])

    def capture_screen(self):
        ret, frame = self.capture.read()
        return frame

    def detect_green(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=1)
        return mask

    def find_contours(self, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def process_frame(self, frame):
        mask = self.detect_green(frame)
        contours = self.find_contours(mask)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                cv2.drawContours(frame, [contour], 0, (0, 255, 0), 2)
        return frame

    def run(self):
        while True:
            frame = self.capture_screen()
            processed_frame = self.process_frame(frame)
            cv2.imshow('frame', processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    bot = BlumCryptoBot()
    bot.run()