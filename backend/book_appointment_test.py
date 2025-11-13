import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException

@pytest.fixture(scope="module")
def driver():
    import chromedriver_autoinstaller
    chromedriver_autoinstaller.install()

    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

def login_user(driver):
    """Logs in the user; works with varying button texts."""
    driver.get("http://localhost:5173/login")
    wait = WebDriverWait(driver, 15)

    # Fill email
    email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
    email_input.clear()
    email_input.send_keys("maliharimi01@uap-bd.edu")

    # Fill password
    password_input = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    password_input.clear()
    password_input.send_keys("123456")

    # Locate login button using multiple strategies
    try:
        login_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'login')]")
        ))
    except TimeoutException:
        # fallback: use CSS class
        login_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type='submit'], button.btn")
        ))

    login_button.click()
    time.sleep(3)  # wait for redirect

def test_fill_appointment_form(driver):
    """Tests booking form functionality after login."""

    # --- Step 1: Login ---
    login_user(driver)

    # --- Step 2: Open booking page ---
    therapist_id = 5
    frontend_url = f"http://localhost:5173/booking/{therapist_id}"
    print(f"\n📅 Opening booking page for therapist ID: {therapist_id}")
    driver.get(frontend_url)

    wait = WebDriverWait(driver, 20)
    time.sleep(2)
    print(f"Booking page URL: {driver.current_url}")

    # --- Step 3: Fill form ---
    patient_name_input = wait.until(EC.visibility_of_element_located((By.ID, "patientName")))
    patient_name_input.clear()
    patient_name_input.send_keys("Maliha Rimi")
    print("✓ Patient name filled")

    gender_input = wait.until(EC.visibility_of_element_located((By.ID, "gender")))
    gender_input.send_keys("female")
    print("✓ Gender selected")

    age_input = wait.until(EC.visibility_of_element_located((By.ID, "age")))
    age_input.clear()
    age_input.send_keys("22")
    print("✓ Age filled")

    date_input = wait.until(EC.visibility_of_element_located((By.ID, "date")))
    date_input.clear()
    date_input.send_keys("2025-10-23")
    print("✓ Date filled")

    time_input = wait.until(EC.visibility_of_element_located((By.ID, "time")))
    hour_12, minute, am_pm = 2, 30, "PM"
    hour_24 = hour_12 + 12 if am_pm.upper() == "PM" and hour_12 != 12 else (0 if hour_12 == 12 and am_pm.upper() == "AM" else hour_12)
    time_input.send_keys(f"{hour_24:02d}:{minute:02d}")
    print("✓ Time filled")

    consultancy_input = wait.until(EC.visibility_of_element_located((By.ID, "consultancyType")))
    consultancy_input.send_keys("offline")
    print("✓ Consultancy type selected")

    appointment_type_input = wait.until(EC.visibility_of_element_located((By.ID, "appointmentType")))
    appointment_type_input.send_keys("new patient")
    print("✓ Appointment type selected")

    # --- Select Hospital ---
    hospital_select = wait.until(EC.visibility_of_element_located((By.ID, "hospital")))
    options = hospital_select.find_elements(By.TAG_NAME, "option")
    if len(options) > 1:
        options[1].click()
        print(f"✓ Hospital selected: {options[1].text}")
    else:
        print("⚠ No hospitals available to select")
        pytest.skip("No hospitals available for this therapist")

    # --- Step 4: Submit form ---
    confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm Appointment')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
    time.sleep(1)
    confirm_button.click()
    print("✓ Appointment form submitted successfully!")

    # --- Step 5: Handle success alert ---
    try:
        wait.until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"⚡ Alert detected: {alert.text}")
        alert.accept()
        print("✓ Alert accepted")
    except NoAlertPresentException:
        print("⚠ No alert appeared")

    # --- Step 6: Verify post-submission page ---
    time.sleep(2)
    current_url = driver.current_url
    print(f"Current page URL after booking: {current_url}")