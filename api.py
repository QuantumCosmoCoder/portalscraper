from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route('/get_homeworks', methods=['GET'])
def get_homeworks():
    number = int(request.args.get('count', 5))

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-dev-shm-usage')

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        wait = WebDriverWait(driver, 15)

        driver.get("https://www.lviscampuscare.org/")
        WebDriverWait(driver, 15).until(lambda d: len(d.window_handles) > 1)

        main_window = driver.current_window_handle
        for handle in driver.window_handles:
            if handle != main_window:
                driver.switch_to.window(handle)
                break

        user_id_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserID")))
        user_id_input.send_keys("P4712")

        continue_button = wait.until(EC.element_to_be_clickable((By.ID, "showRight")))
        continue_button.click()

        password_input = wait.until(EC.visibility_of_element_located((By.ID, "password")))
        password_input.send_keys("123456")

        login_button = wait.until(EC.element_to_be_clickable((By.ID, "btnLogin")))
        login_button.click()

        WebDriverWait(driver, 15).until(EC.url_contains("Parent"))

        driver.get("https://www.lviscampuscare.org/Parent/Assignment")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

        results = []
        i = 0
        row_index = 0

        while i < number and row_index < len(rows):
            row = rows[row_index]
            row_index += 1
            try:
                columns = row.find_elements(By.TAG_NAME, "td")
                if len(columns) < 5 or "View" not in columns[4].text:
                    continue

                date = columns[1].text.strip()
                subject = columns[2].text.strip()
                title = columns[3].text.strip()
                view_td = columns[4]

                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(view_td))
                    driver.execute_script("arguments[0].click();", view_td)
                except (ElementClickInterceptedException, ElementNotInteractableException):
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", view_td)

                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "popAssignment")))
                popup = driver.find_element(By.ID, "popAssignment")
                info = popup.text.strip()

                close_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.close")))
                close_btn.click()
                WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, "popAssignment")))

                results.append({
                    "date": date,
                    "subject": subject,
                    "title": title,
                    "info": info
                })
                i += 1

            except TimeoutException as e:
                print(f"Timeout on row {row_index}: {e}")
            except Exception as e:
                print(f"Error on row {row_index}: {e}")

        return jsonify(results)

    except WebDriverException as e:
        return jsonify({"error": f"WebDriver error occurred: {e}"})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
