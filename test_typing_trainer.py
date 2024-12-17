import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import os
import json
import time
from typing_trainer import TypingTrainer


class TestTypingTrainer(unittest.TestCase):
    def setUp(self):
        # Создаем корневой элемент Tkinter, но не отображаем его
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем окно
        self.trainer = TypingTrainer(self.root)

    def tearDown(self):
        # Закрываем Tkinter после теста
        self.root.destroy()
        if os.path.exists("progress.json"):
            os.remove("progress.json")  # Удаляем файл прогресса после теста

    def test_generate_tests_for_level(self):
        level_text = "фыва"
        tests = self.trainer.generate_tests_for_level(level_text)
        self.assertEqual(len(tests), 5)
        for test in tests:
            self.assertCountEqual(test, level_text)  # Проверка, что символы корректно перемешаны

    def test_save_and_load_progress(self):
        self.trainer.cur_lvl = 2
        self.trainer.cur_test = 3
        self.trainer.save_progress()

        # Создаем новый экземпляр и проверяем загрузку прогресса
        new_trainer = TypingTrainer(self.root)
        new_trainer.load_progress()
        self.assertEqual(new_trainer.cur_lvl, 2)
        self.assertEqual(new_trainer.cur_test, 3)

    def test_check_input_correct(self):
        # Настраиваем уровень и тестовые данные
        self.trainer.cur_lvl = 0
        self.trainer.cur_test = 1
        self.trainer.generated_tests[0] = ["фыва"]

        # Устанавливаем текст для проверки
        self.trainer.input_entry.insert(0, "фыва")
        self.trainer.start_time = time.time() - 1  # Симулируем 1 секунду времени

        with patch('tkinter.messagebox.showinfo') as mock_info:
            self.trainer.check_input(None)
            self.assertEqual(self.trainer.cur_test, 2)  # Переход к следующему тесту

    def test_time_up(self):
        self.trainer.cur_lvl = 0
        self.trainer.cur_test = 1
        self.trainer.generated_tests[0] = ["фыва"]

        with patch('tkinter.messagebox.showwarning') as mock_warning:
            self.trainer.time_up()
            mock_warning.assert_called_once_with(
                "Время истекло", "Вы не успели завершить тест! Начните уровень заново."
            )
            self.assertEqual(self.trainer.cur_test, 1)  # Проверка сброса текущего теста

    def test_highlight_key(self):
        char = "ф"
        self.trainer.highlight_key(char)
        self.assertEqual(self.trainer.keyboard_buttons[char].cget("bg"), "#ffdd57")


if __name__ == '__main__':
    unittest.main()
