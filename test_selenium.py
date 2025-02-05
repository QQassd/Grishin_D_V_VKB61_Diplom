from selenium import webdriver

# Открываем браузер
driver = webdriver.Chrome()  # Или webdriver.Firefox()
driver.get("http://example.com")

print(driver.title)  # Должно вывести заголовок страницы

driver.quit()
