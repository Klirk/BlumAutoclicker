import tkinter as tk
import threading
import cv2
import numpy as np
import pyautogui
import time
import keyboard
import mss
import pygetwindow as gw


class BotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Controller")

        # Установка ширины окна
        self.root.geometry("200x100")  # Измените ширину и высоту по своему усмотрению

        self.start_button = tk.Button(root, text="Start - F5", command=self.start_bot, width=20)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop - F6", command=self.stop_bot, width=20)
        self.stop_button.pack(pady=10)

        self.running = False
        self.setup_hotkeys()
        self.window_title_start = "TelegramDesktop"
        self.window = None

    def setup_hotkeys(self):
        keyboard.add_hotkey('F5', self.start_bot)
        keyboard.add_hotkey('F6', self.stop_bot)

    def find_window(self):
        windows = gw.getAllTitles()
        print("All windows:", windows)  # Output all window titles for debugging
        for window in windows:
            if window.startswith(self.window_title_start):
                return gw.getWindowsWithTitle(window)[0]
        return None

    def capture_screen(self):
        self.window = self.find_window()
        if self.window:
            left, top, right, bottom = self.window.left, self.window.top, self.window.right, self.window.bottom
            width = right - left
            height = bottom - top

            # Изменяем область захвата, отступая от краев
            offset_x = 10  # отступ в пикселях по горизонтали
            offset_y = 20  # отступ в пикселях по вертикали
            left += offset_x
            top += offset_y
            right -= offset_x
            bottom -= offset_y

            # Уменьшаем область захвата сверху
            top += int(height * 0.6)  # Убираем более половины сверху

            # Убираем снизу и сверху
            top += 50
            bottom -= 50

            # Пересчёт ширины и высоты после изменения координат
            width = right - left
            height = bottom - top

            # Проверка на положительные значения ширины и высоты
            if width <= 0 or height <= 0:
                print(f"Invalid capture area: width={width}, height={height}")
                return None, None, None

            with mss.mss() as sct:
                monitor = {"top": top, "left": left, "width": width, "height": height}
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                return frame, left, top
        else:
            print(f"Window starting with '{self.window_title_start}' not found")
            return None, None, None

    def detect_green_particles(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        lower_green = np.array([35, 50, 50])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        return mask

    def detect_bombs(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        lower_bomb = np.array([0, 0, 0])
        upper_bomb = np.array([180, 255, 50])
        mask = cv2.inRange(hsv, lower_bomb, upper_bomb)
        return mask

    def find_contours(self, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def click_on_particles(self, contours, bomb_contours, offset_left, offset_top):
        # Сортировка контуров по координате y в порядке возрастания (снизу вверх)
        contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[1] + cv2.boundingRect(x)[3] // 2)
        for contour in contours:
            if cv2.contourArea(contour) > 50:  # Filter out small areas
                x, y, w, h = cv2.boundingRect(contour)
                click_x = offset_left + x + w // 2
                click_y = offset_top + y + h // 2
                # Проверка на пересечение с бомбой
                overlap = False
                for bomb in bomb_contours:
                    if cv2.pointPolygonTest(bomb, (x + w // 2, y + h // 2), False) >= 0:
                        overlap = True
                        break
                if not overlap:
                    print(f"Clicking at: ({click_x}, {click_y})")  # Log for debugging
                    pyautogui.click(click_x, click_y)

    def bot_loop(self):
        while self.running:
            frame, offset_left, offset_top = self.capture_screen()
            if frame is None:
                time.sleep(0.01)
                continue

            green_mask = self.detect_green_particles(frame)
            bomb_mask = self.detect_bombs(frame)

            green_contours = self.find_contours(green_mask)
            bomb_contours = self.find_contours(bomb_mask)

            self.click_on_particles(green_contours, bomb_contours, offset_left, offset_top)

    def start_bot(self):
        if not self.running:
            self.running = True
            self.bot_thread = threading.Thread(target=self.bot_loop)
            self.bot_thread.start()

    def stop_bot(self):
        self.running = False
        if hasattr(self, 'bot_thread'):
            self.bot_thread.join()


if __name__ == "__main__":
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()
