import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "nimda666!"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    if os.environ.get("CI"):
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    service = Service(log_output=open(os.devnull, "w"))
    d = webdriver.Chrome(options=options, service=service)
    d.implicitly_wait(5)
    yield d
    d.quit()


def login(driver):
    driver.get(BASE_URL + "/login.php")
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 10).until(EC.url_contains("index.php"))


def test_tambah_kontak(driver):
    """Test Case 1: Tambah kontak baru"""
    login(driver)
    driver.get(BASE_URL + "/create.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "name")))
    driver.find_element(By.NAME, "name").send_keys("Selenium Test User")
    driver.find_element(By.NAME, "email").send_keys("selenium@test.com")
    driver.find_element(By.NAME, "phone").send_keys("08123456789")
    driver.find_element(By.NAME, "title").send_keys("Tester")
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    WebDriverWait(driver, 10).until(EC.url_contains("index.php"))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#employee tbody tr")))
    time.sleep(1)
    search_box = driver.find_element(By.CSS_SELECTOR, "#employee_filter input")
    search_box.send_keys("Selenium Test User")
    time.sleep(1)
    rows = driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")
    assert any("Selenium Test User" in row.text for row in rows), \
        "Kontak 'Selenium Test User' tidak ditemukan setelah penambahan"


def test_akses_profil(driver):
    """Test Case 2: Akses halaman profil"""
    login(driver)
    driver.get(BASE_URL + "/profil.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
    h2_text = driver.find_element(By.TAG_NAME, "h2").text
    assert "Profil" in h2_text, f"Judul halaman tidak mengandung 'Profil', ditemukan: '{h2_text}'"


def test_edit_kontak(driver):
    """Test Case 3: Edit kontak pertama"""
    login(driver)
    driver.get(BASE_URL + "/index.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#employee tbody tr")))
    time.sleep(1)
    edit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#employee tbody tr:first-child a.btn-success"))
    )
    driver.execute_script("arguments[0].click();", edit_btn)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "name")))
    name_field = driver.find_element(By.NAME, "name")
    name_field.clear()
    name_field.send_keys("Updated Selenium Name")
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    WebDriverWait(driver, 10).until(EC.url_contains("index.php"))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#employee tbody tr")))
    time.sleep(1)
    assert "Updated Selenium Name" in driver.page_source, \
        "Nama 'Updated Selenium Name' tidak ditemukan setelah edit"


def test_hapus_kontak(driver):
    """Test Case 4: Hapus kontak Selenium Test User"""
    login(driver)
    driver.get(BASE_URL + "/index.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#employee_filter input")))
    driver.find_element(By.CSS_SELECTOR, "#employee_filter input").send_keys("Selenium Test User")
    time.sleep(1)
    delete_btn = driver.find_element(By.CSS_SELECTOR, "#employee tbody tr a.btn-danger")
    driver.execute_script("arguments[0].click();", delete_btn)
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    driver.switch_to.alert.accept()
    WebDriverWait(driver, 10).until(EC.url_contains("index.php"))
    time.sleep(1)
    assert "Selenium Test User" not in driver.page_source, \
        "Kontak 'Selenium Test User' masih ada setelah dihapus"


def test_pencarian_kontak(driver):
    """Test Case 5: Pencarian kontak berdasarkan nama"""
    login(driver)
    driver.get(BASE_URL + "/index.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#employee_filter input")))
    driver.find_element(By.CSS_SELECTOR, "#employee_filter input").send_keys("Ikram")
    time.sleep(1.5)
    rows = driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")
    assert len(rows) > 0, "Tidak ada hasil pencarian untuk 'Ikram'"
    assert any("Ikram" in row.text for row in rows), \
        "Kontak 'Ikram' tidak ditemukan dalam hasil pencarian"
