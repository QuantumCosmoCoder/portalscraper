from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# User input for number of assignments
try:
    number = int(input('Enter the number of latest homeworks you wish to see: '))
except ValueError:
    print("❌ Please enter a valid number.")
    exit()

uid = str(input('Enter your UID:'))
pwd = str(input('Enter your password:'))

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    print("✅ Headless browser launched successfully.")
except WebDriverException as e:
    print(f"Failed to launch browser: {e}")
    raise

try:
    driver.get("https://www.lviscampuscare.org/")
    print("Main portal page loaded.")

    WebDriverWait(driver, 15).until(lambda d: len(d.window_handles) > 1)
    print("Popup window detected.")

    main_window = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != main_window:
            driver.switch_to.window(handle)
            print("Switched to popup window.")
            break

    wait = WebDriverWait(driver, 15)

    # User ID
    user_id_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserID")))
    user_id_input.send_keys(str(uid))
    print("User ID entered.")

    continue_button = wait.until(EC.element_to_be_clickable((By.ID, "showRight")))
    continue_button.click()
    print("Clicked continue to go to password page.")

    # Password
    password_input = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    password_input.send_keys(str(pwd))
    print("Password entered.")

    login_button = wait.until(EC.element_to_be_clickable((By.ID, "btnLogin")))
    login_button.click()
    print("Login button clicked.")

    # Wait for parent dashboard to load
    WebDriverWait(driver, 15).until(EC.url_contains("Parent"))
    print("Login successful. Navigating to assignment page.")

    # Step: Go to assignment page
    driver.get("https://www.lviscampuscare.org/Parent/Assignment")
    print("Assignment page loaded.")

    # Wait for assignments to be visible
    assignment_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))  # adjust if needed
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    count = 0
    print("\n📚 Assignments Found:")
    for row in rows:
        if count >= number:
            break
        columns = row.find_elements(By.TAG_NAME, "td")

        if len(columns) >= 5:
            serial = columns[0].text.strip()
            date = columns[1].text.strip()
            subject = columns[2].text.strip()
            title = columns[3].text.strip()
            print(f"- Serial no: {serial} | Date: {date} | Subject: {subject} | Title: {title}")

            view_td = columns[4]
            driver.execute_script("arguments[0].click();", view_td)

            # Wait for the popup div to appear
            wait.until(EC.visibility_of_element_located((By.ID, "popAssignment")))
            popup = driver.find_element(By.ID, "popAssignment")
            print("Details:\n", popup.text.strip())

            # Close the popup
            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.close")))
            close_btn.click()

            # Wait for popup to disappear
            wait.until(EC.invisibility_of_element_located((By.ID, "popAssignment")))
            count += 1


except WebDriverException as e:
    print(f"WebDriver error occurred: {e}")
except Exception as e:
    print(f"Unexpected error occurred: {e}")
finally:
    print("\nClosing browser.")
    driver.quit()
