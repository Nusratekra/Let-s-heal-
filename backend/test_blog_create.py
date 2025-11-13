import pytest
import time
import requests
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------- Auto install matching ChromeDriver ----------------
chromedriver_autoinstaller.install()

# ---------------- Fixture for Chrome WebDriver ----------------
@pytest.fixture(scope="module")
def driver():
    """Setup and teardown Chrome WebDriver"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

# ---------------- Debug Function ----------------
def debug_page(driver, page_name):
    """Debug function to see what's actually on the page"""
    print(f"\n=== DEBUGGING {page_name.upper()} ===")
    print(f"Current URL: {driver.current_url}")
    print(f"Page title: {driver.title}")

    # Buttons
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\nFound {len(buttons)} buttons:")
    for i, button in enumerate(buttons):
        text = button.text.strip()
        if text:
            print(f" {i+1}. '{text}'")

    # Input fields
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"\nFound {len(inputs)} input fields:")
    for i, input_field in enumerate(inputs):
        name = input_field.get_attribute('name')
        id_attr = input_field.get_attribute('id')
        placeholder = input_field.get_attribute('placeholder')
        type_attr = input_field.get_attribute('type')
        print(f" {i+1}. name='{name}', id='{id_attr}', type='{type_attr}', placeholder='{placeholder}'")

    # Textareas
    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    print(f"\nFound {len(textareas)} textareas:")
    for i, textarea in enumerate(textareas):
        name = textarea.get_attribute('name')
        id_attr = textarea.get_attribute('id')
        placeholder = textarea.get_attribute('placeholder')
        print(f" {i+1}. name='{name}', id='{id_attr}', placeholder='{placeholder}'")

    # Screenshot
    driver.save_screenshot(f"debug_{page_name}.png")
    print(f"✓ Screenshot saved: debug_{page_name}.png")

# ---------------- Test Backend Connection ----------------
def test_backend_is_running():
    backend_url = "http://127.0.0.1:8000/api/login/"
    print("\nChecking backend status...")
    try:
        response = requests.get(backend_url, timeout=5)
        assert response.status_code in [200, 301, 302, 404, 405]
        print("✓ Backend reachable (status:", response.status_code, ")")
    except Exception as e:
        pytest.fail(f"Backend not reachable: {e}")

# ---------------- Login as Customer ----------------
def test_login_customer(driver):
    print("\nLogging in as Customer...")
    frontend_url = "http://localhost:5173/login"
    driver.get(frontend_url)

    wait = WebDriverWait(driver, 15)

    # Wait for email and password inputs
    email_input = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
    password_input = wait.until(EC.visibility_of_element_located((By.NAME, "password")))

    # Fill credentials
    email_input.clear()
    email_input.send_keys("maliharimi01@uap-bd.edu")
    password_input.clear()
    password_input.send_keys("123456")

    # Select Customer role
    customer_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Customer')]"))
    )
    customer_button.click()
    time.sleep(1)  # Let React render

    # Click Sign In
    signin_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign in as Customer')]"))
    )
    signin_btn.click()
    print("✓ Login submitted, waiting for redirect...")

    # Wait for redirect
    wait.until(lambda d: d.current_url != frontend_url)
    current_url = driver.current_url
    print(f"Redirected to: {current_url}")

    # Assert login success
    assert any(x in current_url.lower() for x in ["dashboard", "home", "profile", "blog"]), \
        f"Login failed — still on {current_url}"

# ---------------- Navigate to Blog Page ----------------
def test_navigate_to_blog(driver):
    print("\nNavigating to Blog page...")
    blog_url = "http://localhost:5173/blog-posts"
    driver.get(blog_url)
    time.sleep(2)
    debug_page(driver, "blog_page")
    wait = WebDriverWait(driver, 10)

    # Click Create Post
    create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Create Post')]")))
    create_btn.click()
    print("✓ Clicked Create Post button")

    # Wait for create post page
    time.sleep(2)
    debug_page(driver, "create_post_page")

# ---------------- Fill and Submit Blog Post Form ----------------
def test_fill_create_post_form(driver):
    print("\nFilling create post form...")
    wait = WebDriverWait(driver, 15)

    # Fill Title
    title_input = wait.until(EC.visibility_of_element_located((By.ID, "blog_title")))
    title_input.clear()
    title_input.send_keys("Healing Through Writing - My Therapy Journey")
    print("✓ Title filled")

    # Select Author Type
    try:
        author_type_identity = driver.find_element(By.ID, "author-type-identity")
        author_type_identity.click()
        print("✓ Author type selected: Identity")
    except Exception as e:
        print(f"⚠ Author type selection skipped: {e}")

    # Fill Author Name
    try:
        author_name = driver.find_element(By.ID, "blog_author_name")
        author_name.clear()
        author_name.send_keys("Nabila")
        print("✓ Author name filled")
    except Exception as e:
        print(f"⚠ Author name field not found: {e}")

    # Fill Content
    content_input = wait.until(EC.visibility_of_element_located((By.ID, "blog_content")))
    content_input.clear()
    blog_content = """Writing has always been my therapy. In this post, I share how journaling helped me heal from anxiety and rediscover my inner peace. 
Through daily writing exercises, I learned to process my emotions and understand myself better. The act of putting thoughts on paper created space for self-reflection and growth. 
This journey taught me that healing is possible through self-expression and consistent practice."""
    content_input.send_keys(blog_content)
    print("✓ Content filled")

    # Click Publish Button
    publish_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Publish Post')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", publish_button)
    time.sleep(2)
    publish_button.click()
    print("✓ Publish button clicked")

    # -------- Handle alert --------
    try:
        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
        print(f"Alert detected: {alert.text}")
        alert.accept()
        print("✓ Alert accepted")
    except:
        print("⚠ No alert appeared")

    # Wait for redirect
    time.sleep(3)
    current_url = driver.current_url
    print(f"Final URL after publishing: {current_url}")

    # Check success
    if any(x in current_url.lower() for x in ["blog", "posts"]):
        print("SUCCESS: Blog post created and redirected to blog page!")
    else:
        print("⚠ Blog post may not have been created properly")
        driver.save_screenshot("blog_creation_error.png")

    # Final assertion
    assert "blog" in current_url.lower(), f"Expected to be on blog page, but on: {current_url}"