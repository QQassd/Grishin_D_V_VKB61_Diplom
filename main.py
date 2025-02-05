import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import logging
from scanner import scan_forms
from tester import run_tests

# Настройка логирования
logging.basicConfig(filename="reports/log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

class SecurityTesterApp:
    def init(self, root):
        self.root = root
        self.root.title("Автоматизированное тестирование безопасности")
        self.root.geometry("600x500")

        # Поле ввода URL
        self.url_label = tk.Label(root, text="Введите URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()

        # Кнопка "Сканировать формы"
        self.scan_button = tk.Button(root, text="🔍 Сканировать формы", command=self.scan_site)
        self.scan_button.pack()

        # Окно для вывода найденных форм
        self.result_text = scrolledtext.ScrolledText(root, width=70, height=10)
        self.result_text.pack()

        # Кнопка "Тестировать уязвимости"
        self.test_button = tk.Button(root, text="🛡 Тестировать уязвимости", command=self.start_testing)
        self.test_button.pack()

        # Окно логов
        self.log_text = scrolledtext.ScrolledText(root, width=70, height=10)
        self.log_text.pack()
        self.update_logs()

    def scan_site(self):
        """Запускает сканирование сайта"""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Ошибка", "Введите URL!")
            return

        self.result_text.delete(1.0, tk.END)
        forms = scan_forms(url)

        if forms:
            for form in forms:
                self.result_text.insert(tk.END, f"Форма: {form['action']} ({form['method']})\n")
                for field in form["inputs"]:
                    self.result_text.insert(tk.END, f"  Поле: {field['name']} ({field['type']})\n")
                self.result_text.insert(tk.END, "-" * 50 + "\n")
        else:
            self.result_text.insert(tk.END, "Формы не найдены.\n")

    def start_testing(self):
        """Запускает тестирование уязвимостей в отдельном потоке"""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Ошибка", "Введите URL!")
            return

        threading.Thread(target=self.run_tests_thread, args=(url,), daemon=True).start()

    def run_tests_thread(self, url):
        """Функция для тестирования в потоке"""
        messagebox.showinfo("Тестирование", "Начинаем тестирование. Смотрите логи.")
        run_tests(url)
        messagebox.showinfo("Готово", "Тестирование завершено!")

    def update_logs(self):
        """Обновляет лог в окне"""
        try:
            with open("reports/log.txt", "r", encoding="utf-8") as log_file:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, log_file.read())
        except FileNotFoundError:
            self.log_text.insert(tk.END, "Логов пока нет...\n")

        # Обновляем логи каждую секунду
        self.root.after(1000, self.update_logs)

if name == "main":
    root = tk.Tk()
    app = SecurityTesterApp(root)
    root.mainloop()
