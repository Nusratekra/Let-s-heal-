import pytest
import time
import requests
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chromedriver_autoinstaller.install()

@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

def test_backend_is_running():
    backend_url = "http://127.0.0.1:8000/api/login"
    print("\nChecking if backend is running...")
    try:
        response = requests.get(backend_url, timeout=5)
        assert response.status_code in [200, 301, 302, 404,405]
        print("✓ Backend is running!")
    except Exception as e:
        pytest.fail(f"Backend not reachable: {e}")

def test_customer_login(driver):
    frontend_url = "http://localhost:5173/login"
    print("\nStarting login test...")

    driver.get(frontend_url)
    wait = WebDriverWait(driver, 15)

    # Wait for login form
    email = wait.until(EC.presence_of_element_located((By.NAME, "email")))
    password = driver.find_element(By.NAME, "password")

    # Choose "Customer" role
    driver.find_element(By.XPATH, "//button[contains(text(), 'Customer')]").click()

    # Fill credentials
    email.send_keys("maliharimi01@uap-bd.edu")
    password.send_keys("123456")

    # Click Sign In
    driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in as Customer')]").click()
    print("✓ Login form submitted")

    # Wait for redirect
    time.sleep(3)
    current_url = driver.current_url

    # Check if redirected to dashboard
    assert "dashboard" in current_url.lower() or "home" in current_url.lower(), \
        f"Login failed — still on {current_url}"

    print(f"✓ Login successful! Redirected to {current_url}")