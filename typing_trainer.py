import tkinter as tk
from tkinter import messagebox
import time
import json
import os
import random

import Levenshtein
import winsound


class TypingTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Тренажер слепой печати")
        self.timer_id = None

        self.levels = [
            "фыва", "олдж", "ячсм", "итёр", "шщзх",
            "цукенг", "гшщзхъ", "йцукен", "фывапрол", "ячсмитьбю"
        ]

        self.generated_tests = [[] for _ in range(len(self.levels))]
        self.cur_lvl = 0
        self.cur_test = 1
        self.count_lvl = 5
        self.start_time = 0
        self.char_timings = []
        self.time_limit = 10
        self.level_stats = []
        self.total_stats = []
        self.correct_chars = 0
        self.total_chars = 0

        self.load_progress()

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.instruction_label = tk.Label(
            self.main_frame,
            text=(
                "Положите указательные пальцы на клавиши 'Ф' и 'Ы' "
                "(или 'J' и 'F' на английской раскладке)"
            ),
            wraplength=400,
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        self.instruction_label.pack(pady=10, fill=tk.BOTH, expand=True)

        self.text_label = tk.Label(
            self.main_frame, text="", font=("Arial", 16),
            anchor="center", bg="#dfe7fd", fg="#333333"
        )
        self.text_label.pack(pady=10, fill=tk.BOTH, expand=True)

        self.input_entry = tk.Entry(
            self.main_frame, font=("Arial", 16), bg="#ffffff", fg="#333333"
        )
        self.input_entry.pack(pady=10, fill=tk.BOTH, expand=True)
        self.input_entry.bind("<Return>", self.check_input)

        self.stats_label = tk.Label(
            self.main_frame, text="", font=("Arial", 12), bg="#f0f0f0"
        )
        self.stats_label.pack(pady=10, fill=tk.BOTH, expand=True)

        self.keyboard_frame = tk.Frame(self.main_frame, bg="#e0e0e0")
        self.keyboard_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.render_keyboard()

        self.root.bind("<Configure>", self.resize_keyboard)

        self.image_frame = tk.Frame(self.root)
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(pady=10, fill=tk.BOTH, expand=True)

        self.next_button = tk.Button(
            self.image_frame, text="Далее", command=self.start_level
        )
        self.next_button.pack(pady=20)

        self.show_level_image()

    def render_keyboard(self):
        keyboard_layout = [
            "йцукенгшщзхъ",
            " фывапролджэ ",
            "  ячсмитьбю  "
        ]
        self.keyboard_buttons = {}
        for row in keyboard_layout:
            frame = tk.Frame(self.keyboard_frame, bg="#e0e0e0")
            frame.pack(fill=tk.BOTH, expand=True)
            for char in row:
                if char.strip():
                    btn = tk.Button(
                        frame, text=char, state=tk.DISABLED,
                        disabledforeground="black", bg="#ffffff", font=("Arial", 12)
                    )
                    btn.pack(side=tk.LEFT, padx=2, pady=2, expand=True, fill=tk.BOTH)
                    self.keyboard_buttons[char] = btn
                else:
                    spacer = tk.Label(frame, text=" ", bg="#e0e0e0")
                    spacer.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH)

    def resize_keyboard(self, event):
        for button in self.keyboard_buttons.values():
            button.config(width=event.width // 100, height=event.height // 300)

    def highlight_key(self, char):
        for button in self.keyboard_buttons.values():
            button.config(bg="#ffffff")
        if char in self.keyboard_buttons:
            self.keyboard_buttons[char].config(bg="#ffdd57")

    def play_key_sound(self):
        winsound.Beep(500, 100)

    def generate_tests_for_level(self, level_text):
        tests = []
        full_set = level_text
        if self.cur_lvl > 0:
            full_set += ''.join(self.levels[:self.cur_lvl])

        for _ in range(self.count_lvl):
            shuffled = ''.join(random.sample(full_set, len(level_text)))
            tests.append(shuffled)
        return tests

    def show_level_image(self):
        self.main_frame.pack_forget()
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        try:
            image_path = "QWERTY-home-keys-position.png"
            level_image = tk.PhotoImage(file=image_path)
            self.image_label.config(image=level_image, text="", compound=tk.CENTER)
            self.image_label.image = level_image
        except Exception:
            self.image_label.config(
                text=f"Уровень {self.cur_lvl + 1}\n(Картинка отсутствует)"
            )

    def time_up(self):
        if self.input_entry.get() != self.generated_tests[self.cur_lvl][self.cur_test - 1]:
            messagebox.showwarning(
                "Время истекло", "Вы не успели завершить тест! Начните уровень заново."
            )
            self.cur_test = 1
            self.start_level()

    def display_level_statistics(self):
        if self.level_stats:
            avg_cpm = sum(stat['cpm'] for stat in self.level_stats) / len(self.level_stats)
            avg_accuracy = sum(stat['accuracy'] for stat in self.level_stats) / len(self.level_stats)

            all_sorted_chars = [
                char for stat in self.level_stats for char in stat['sorted_chars']
            ]
            sorted_by_frequency = {char: 0 for char in all_sorted_chars}
            for char in all_sorted_chars:
                sorted_by_frequency[char] += 1
            sorted_chars = sorted(
                sorted_by_frequency, key=sorted_by_frequency.get, reverse=True
            )

            result_message = (
                f"Результаты уровня {self.cur_lvl + 1}:\n"
                f"Средняя скорость: {avg_cpm:.2f} символов/мин\n"
                f"Средняя точность: {avg_accuracy:.2f}%\n"
                "Порядок клавиш по паузам: " + ", ".join(sorted_chars)
            )
            messagebox.showinfo("Результаты уровня", result_message)

        self.level_stats = []
        self.cur_lvl += 1
        self.cur_test = 1
        self.save_progress()
        self.show_level_image()

    def check_input(self, event):
        entered_text = self.input_entry.get()
        expected_text = self.generated_tests[self.cur_lvl][self.cur_test - 1]
        end_time = time.time()

        # Проверяем, что таймер был установлен
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        duration = end_time - self.start_time
        cpm = len(entered_text) / duration * 60

        self.correct_chars += len(expected_text) - Levenshtein.distance(expected_text, entered_text)
        self.total_chars += len(expected_text)

        if self.char_timings:
            sorted_chars = [c for c, _ in sorted(self.char_timings, key=lambda x: x[1])]
        else:
            sorted_chars = []

        self.accuracy = self.correct_chars / self.total_chars * 100

        if entered_text == expected_text:
            self.level_stats.append({
                'cpm': cpm,
                'accuracy': self.accuracy,
                'sorted_chars': sorted_chars
            })
            self.accuracy = 0
            self.flag = True
            self.cur_test += 1
            self.correct_chars = 0
            self.total_chars = 0
            if self.cur_test > self.count_lvl:
                self.display_level_statistics()
            else:
                self.start_level()

    def start_level(self):
        self.image_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        if self.cur_lvl < len(self.levels):
            if self.cur_test > self.count_lvl:
                self.display_level_statistics()
                return

            if self.cur_lvl < len(self.levels):
                if not self.generated_tests[self.cur_lvl]:
                    self.generated_tests[self.cur_lvl] = self.generate_tests_for_level(
                        self.levels[self.cur_lvl]
                    )

                if self.cur_test - 1 < len(self.generated_tests[self.cur_lvl]):
                    cur_test_text = self.generated_tests[self.cur_lvl][self.cur_test - 1]
                    self.text_label.config(
                        text=(
                            f"Уровень {self.cur_lvl + 1} (Тест {self.cur_test}/{self.count_lvl}): "
                            f"{cur_test_text}"
                        )
                    )

                    self.input_entry.delete(0, tk.END)
                    self.input_entry.focus()
                    self.start_time = time.time()
                    self.char_timings = []
                    self.timer_id = self.root.after(self.time_limit * 1000, self.time_up)
                else:
                    messagebox.showerror("Ошибка", "Не удалось загрузить тест для текущего уровня.")
            else:
                messagebox.showinfo("Поздравляем!", "Вы прошли все уровни!")
                self.cur_lvl = 0
                self.cur_test = 1
                self.save_progress()
        else:
            messagebox.showinfo("Поздравляем!", "Вы прошли все уровни!")

    def track_char(self, event):
        self.play_key_sound()
        current_time = time.time()
        if self.char_timings:
            pause = current_time - self.char_timings[-1][1]
        else:
            pause = 0
        self.char_timings.append((event.char, pause))
        self.highlight_key(event.char)

    def save_progress(self):
        with open("progress.json", "w") as file:
            json.dump({"cur_lvl": self.cur_lvl, "cur_test": self.cur_test}, file)

    def load_progress(self):
        if os.path.exists("progress.json"):
            with open("progress.json", "r") as file:
                data = json.load(file)
                self.cur_lvl = data.get("cur_lvl", 0)
                self.cur_test = data.get("cur_test", 1)


if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = int(screen_width * 0.5)
    height = int(screen_height * 0.5)
    x_offset = (screen_width - width) // 2
    y_offset = (screen_height - height) // 2

    root.geometry(f"{width}x{height}+{x_offset}+{y_offset}")
    root.minsize(400, 300)

    trainer = TypingTrainer(root)
    root.bind("<KeyPress>", trainer.track_char)

    root.mainloop()