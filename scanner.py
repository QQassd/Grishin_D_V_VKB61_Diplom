from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

# Конфигурация WebDriver (используем Chrome)
def get_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Запуск без GUI
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    service = Service("/usr/local/bin/chromedriver")  # Путь к ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Функция для сканирования форм на странице
def scan_forms(url: str) -> list[dict]:
    """Сканирует страницу и возвращает список найденных форм"""
    driver = get_driver()
    driver.get(url)
    time.sleep(2)  # Даем время странице загрузиться

    soup = BeautifulSoup(driver.page_source, "html.parser")
    forms = soup.find_all("form")
    result = []

    for form in forms:
        form_data = {
            "action": form.get("action"),
            "method": form.get("method", "GET").upper(),
            "inputs": []
        }

        # Собираем все поля формы
        for input_tag in form.find_all("input"):
            form_data["inputs"].append({
                "name": input_tag.get("name"),
                "type": input_tag.get("type", "text")
            })
        
        result.append(form_data)

    driver.quit()
    return result

# Тестируем сканер
if name == "main":
    target_url = "http://localhost:3000"
    forms = scan_forms(target_url)

    for form in forms:
        print(f"Форма: {form['action']} ({form['method']})")
        for field in form["inputs"]:
            print(f"  Поле: {field['name']} ({field['type']})")
