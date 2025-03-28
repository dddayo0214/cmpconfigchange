import tkinter as tk
from tkinter import filedialog, messagebox, Label, Button
import winreg
import pygame
import os
from pynput import keyboard
import threading
import time
import winsound
import pyttsx3

class ChangeYourVoice:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows 游標修改器")
        self.root.geometry("800x600")

        pygame.mixer.init()
        self.keypress_sound = None
        self.volume_level = 0.5

        self.cursor_types = {
            "Arrow": "arrow",
            "Hand": "hand2",
            "Wait": "watch",
            "Help": "question_arrow",
            "Crosshair": "cross",
            "IBeam": "xterm"
        }

        self.cursor_paths = {}

        self.create_widgets()

    def choose_cursor(self, cursor_key):
        """讓使用者選擇游標文件"""
        file_path = filedialog.askopenfilename(
            title=f"選擇 {cursor_key} 游標",
            filetypes=[("游標文件", "*.cur;*.ani")]
        )

        if file_path:
            self.cursor_paths[cursor_key] = file_path
            self.labels[cursor_key].config(text=f"{cursor_key}: {file_path.split('/')[-1]}")
            self.preview_frame.config(cursor=f"@{file_path}")  # 預覽游標

    def apply_cursors(self):
        """將選擇的游標寫入 Windows 註冊表，並重啟 explorer.exe"""
        if not self.cursor_paths:
            messagebox.showwarning("提示", "請先選擇游標！")
            return

        key = r"Control Panel\Cursors"

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
                for cursor_key, cursor_path in self.cursor_paths.items():
                    winreg.SetValueEx(reg_key, cursor_key, 0, winreg.REG_SZ, cursor_path)

            messagebox.showinfo("成功", "游標方案已變更！請等待刷新桌面。")

            os.system("taskkill /f /im explorer.exe")
            time.sleep(1)  # 等待一點時間，讓 explorer 確實終止
            os.system("start explorer.exe")
        except Exception as e:
            messagebox.showerror("錯誤", f"變更失敗: {e}")

    def choose_sound(self):
        """讓使用者選擇音效檔案"""
        global keypress_sound
        file_path = filedialog.askopenfilename(
            title="選擇音效",
            filetypes=[("音效文件", "*.wav;*.mp3;*.ogg")]
        )
        
        if file_path:
            self.keypress_sound = pygame.mixer.Sound(file_path)
            self.keypress_sound.set_volume(self.volume_level)  # 設定初始音量
            self.keyboard_label.config(text=f"選擇的音效: {file_path.split('/')[-1]}")

    def choose_alart_sound(self):
        """讓使用者選擇音效檔案"""
        global keypress_sound
        self.alartsound_path = filedialog.askopenfilename(
            title="選擇音效",
            filetypes=[("音效文件", "*.wav;*.mp3;*.ogg")]
        )

        key = r"AppEvents\Schemes\Apps\.Default\SystemAsterisk\.Current"

        if self.alartsound_path:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "", 0, winreg.REG_SZ, self.alartsound_path)
            print("系統警示音已變更為:", self.alartsound_path)
            self.alart_sound = pygame.mixer.Sound(self.alartsound_path)
            self.alart_label.config(text=f"選擇的音效: {self.alartsound_path.split('/')[-1]}")

    def adjust_keyboard_volume(self, val):
        self.volume_level = float(val) 
        if self.keypress_sound:
            self.keypress_sound.set_volume(self.volume_level)

    def play_sound(self, key):
        if self.keypress_sound:
            self.keypress_sound.play()

    def play_alart_sound(self):
        self.alart_sound.play()
        # engine = pyttsx3.init()
        # engine.say("警告！這是一個警示音。")
        # engine.runAndWait()

    def play_alart(self):
        alart_thread = threading.Thread(target=self.play_alart_sound, daemon=True)
        alart_thread.start()

    def start_keyboard_listener(self):
        with keyboard.Listener(on_press=self.play_sound) as listener:
            listener.join()

    def create_widgets(self):
        listener_thread = threading.Thread(target=self.start_keyboard_listener, daemon=True)
        listener_thread.start()

        self.labels = {}  # 儲存游標名稱標籤
        for idx, (cursor_key, cursor_name) in enumerate(self.cursor_types.items()):
            Label(self.root, text=f"{cursor_key} 游標:").grid(row=idx, column=0, sticky="w", padx=10, pady=5)
            
            self.labels[cursor_key] = Label(self.root, text="未選擇", fg="gray")
            self.labels[cursor_key].grid(row=idx, column=1, sticky="w")

            Button(self.root, text="選擇", command=lambda key=cursor_key: self.choose_cursor(key)).grid(row=idx, column=2, padx=5)

        # 預覽區域
        self.preview_frame = Label(self.root, text="游標預覽", width=20, height=2, bg="lightgray")
        self.preview_frame.grid(row=len(self.cursor_types), column=0, columnspan=3, pady=20)

        # 套用按鈕
        self.apply_btn = Button(self.root, text="套用游標方案", command=self.apply_cursors, font=("Arial", 12), bg="green", fg="white")
        self.apply_btn.grid(row=len(self.cursor_types) + 1, column=0, columnspan=3, pady=10)

        self.keyboard_label = tk.Label(self.root, text="未選擇鍵盤音效", fg="gray")
        self.keyboard_label.grid(row=0, column=6, columnspan=3, pady=10)

        self.choose_btn = tk.Button(self.root, text="選擇音效", command=self.choose_sound)
        self.choose_btn.grid(row=2, column=6, columnspan=3, pady=10)

        self.volume_slider = tk.Scale(self.root, from_=0, to=1, resolution=0.01, orient="horizontal", label="音量", command=self.adjust_keyboard_volume)
        self.volume_slider.set(self.volume_level)
        self.volume_slider.grid(row=4, column=6, columnspan=3, pady=10)

        self.alart_label = tk.Label(self.root, text="未選擇警示音音效", fg="gray")
        self.alart_label.grid(row=0, column=10, columnspan=3, pady=10)

        self.alart_choose_btn = tk.Button(self.root, text="選擇音效", command=self.choose_alart_sound)
        self.alart_choose_btn.grid(row=2, column=10, columnspan=3, pady=10)

        self.alart_play_btn = tk.Button(self.root, text="播放警示音", command=self.play_alart)
        self.alart_play_btn.grid(row=4, column=10, columnspan=3, pady=10)

        self.apply_alart = Label(self.root, text="以上設定可能需要重啟電腦", font=("Arial", 12), bg="black", fg="red")
        self.apply_alart.grid(row=10, column=0, columnspan=3, pady=10)

        self.root.bind("<KeyPress>", self.play_sound)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChangeYourVoice(root)
    root.mainloop()
