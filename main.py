from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

driver = Driver(uc=True)
url = "https://suno.com/me"

script = """
let data_links = document.querySelectorAll(".react-aria-GridListItem");
let dataKeys = [];
data_links.forEach(link => {
    dataKeys.push(link.getAttribute("data-key"));
});
return dataKeys;
"""

driver.uc_open_with_reconnect(url, 10)

def sign_in(driver: Driver):
    phone_number_field = driver.find_element(By.NAME, "identifier")
    phone_number_field.send_keys("6204593386")
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/div[3]/form/button[2]").click()
    print("Waiting for user to enter the OTP")
    time.sleep(30)
    return True

def get_links(driver: Driver) -> list[str]:
    print("Reloading page")
    driver.open("https://suno.com/me")
    print("Page Reloaded")
    time.sleep(1)
    count: int = 0
    try:
        button = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/div[1]/button[2]")
        while button and not is_button_disabled(button):
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'react-aria-GridList')))
            time.sleep(3)
            temp_data = driver.execute_script(script)
            data = set(temp_data)
            print(f"Downloading Songs from Page {count}")
            print(f"Number of songs in Page {len(data)}")
            download_data(list(data))
            button.click()
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/div[1]/button[2]')))
            count += 1
    except Exception as e:
        print(f"Unable to find the next page button: {e}")

def download_data(data_keys: list[str]) -> None:
    def download_file(data_key): 
        url = f"https://cdn1.suno.ai/{data_key}.mp3"
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"{data_key}.mp3", "wb") as file:
                file.write(response.content)
            print(f"Successfully downloaded {data_key}.mp3")
        else:
            print(f"Failed to download {url}, status code: {response.status_code}")

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_file, data_key) for data_key in data_keys]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred during download: {e}")

def is_button_disabled(button_element):
    return button_element.get_attribute('disabled') is not None

sign_in(driver)
get_links(driver)
print(f'Script Completed')
driver.quit()

