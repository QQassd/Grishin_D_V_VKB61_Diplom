import time
import requests
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from scanner import scan_forms

# Настраиваем логирование
logging.basicConfig(filename="reports/log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Функция для загрузки пейлоадов из файлов
def load_payloads(file_path: str) -> list[str]:
    """Загружает строки из файла и возвращает список пейлоадов"""
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

# Функция для проверки уязвимости через Selenium
def test_form(driver, url: str, form: dict, payloads: list[str], vuln_type: str):
    """Проверяет форму на уязвимости, отправляя пейлоады"""
    driver.get(url)
    time.sleep(2)  # Даем время странице загрузиться

    # Ищем форму по action
    action_url = form["action"]
    inputs = form["inputs"]

    for payload in payloads:
        try:
            # Заполняем все поля формы тестовыми данными
            for input_tag in inputs:
                if input_tag["name"]:
                    input_element = driver.find_element(By.NAME, input_tag["name"])
                    input_element.clear()
                    input_element.send_keys(payload)

            # Отправляем форму
            driver.find_element(By.XPATH, "//form").submit()
            time.sleep(2)

            # Проверяем ответ на наличие инъекции
            if vuln_type == "SQL":
                error_signs = ["SQL syntax", "mysql_fetch", "You have an error in your SQL"]
                page_source = driver.page_source
                if any(sign in page_source for sign in error_signs):
                    logging.info(f"SQL Injection найдена в {action_url} с payload: {payload}")

            elif vuln_type == "XSS":
                if payload in driver.page_source:
                    logging.info(f"XSS найдена в {action_url} с payload: {payload}")
            
	    elif vuln_type == "Path_traversal":
                if payload in driver.page_source:
                    logging.info(f"Path_traversal найдена в {action_url} с payload: {payload}")
        
	except Exception as e:
            logging.error(f"Ошибка при тестировании {action_url}: {str(e)}")

# Основная функция тестирования
def run_tests(target_url: str):
    """Запускает тестирование на SQLi и XSS"""
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"))

    forms = scan_forms(target_url)
    sql_payloads = load_payloads("payloads/sql_injection.txt")
    xss_payloads = load_payloads("payloads/xss.txt")
    path_trav_payloads = load_payloads("payloads/path_trav.txt")

    for form in forms:
        test_form(driver, target_url, form, sql_payloads, "SQL")
        test_form(driver, target_url, form, xss_payloads, "XSS")
	test_form(driver, target_url, form, path_trav_payloads, "Path_trav")

    driver.quit()
    logging.info("Тестирование завершено.")

# Тестируем сканер
if __name__ == "main":
    target = "http://localhost:3000"
    run_tests(target)
