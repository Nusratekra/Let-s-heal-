import pytest
import time
import requests
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Automatically install chromedriver
chromedriver_autoinstaller.install()

# ------------------- Fixtures -------------------
@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

# ------------------- Backend Health Check -------------------
def test_backend_is_running():
    backend_url = "http://127.0.0.1:8000/api/customer_signup"
    print("\nChecking if backend is running...")
    try:
        response = requests.get(backend_url, timeout=5)
        assert response.status_code in [200, 301, 302, 404, 405]
        print("✓ Backend is running!")
    except Exception as e:
        pytest.fail(f"Backend not reachable: {e}")

# ------------------- Customer Signup Test -------------------
def test_customer_signup(driver):
    frontend_url = "http://localhost:5173/signup"
    print("\nStarting customer signup test...")

    driver.get(frontend_url)
    wait = WebDriverWait(driver, 20)

    # Wait for form inputs
    name = wait.until(EC.presence_of_element_located((By.ID, "name")))
    email = driver.find_element(By.ID, "email")
    phone = driver.find_element(By.ID, "phone")
    age = driver.find_element(By.ID, "customer_age")
    password = driver.find_element(By.ID, "password")
    confirm_password = driver.find_element(By.ID, "confirm_password")

    # Choose "Customer" role
    driver.find_element(By.XPATH, "//button[contains(text(), 'Customer')]").click()

    # Fill form
    name.send_keys("Hasnine")
    email.send_keys("22201269@uap-bd.edu")
    phone.send_keys("01711111111")
    age.send_keys("22")
    password.send_keys("123456")        
    confirm_password.send_keys("123456")

    # Optional: select gender
    gender_select = driver.find_element(By.ID, "gender")
    for option in gender_select.find_elements(By.TAG_NAME, "option"):
        if option.text.lower() == "no choice":
            option.click()
            break

    # Submit the form
    submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create Customer Account')]")
    submit_button.click()
    print("Signup form submitted")

    # Wait for redirect to login page (max 20 seconds)
    try:
        wait.until(EC.url_contains("login"))
        current_url = driver.current_url
        print(f"✓ Customer signup successful! Redirected to {current_url}")
    except:
        current_url = driver.current_url
        raise AssertionError(f"Signup failed — still on {current_url}")