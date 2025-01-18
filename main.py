from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys


filename: str = "suno_download_music.txt"


script = """
let data_links = document.querySelectorAll(".react-aria-GridListItem");
let dataKeys = [];
data_links.forEach(link => {
    dataKeys.push(link.getAttribute("data-key"));
});
return dataKeys;
"""

def alreadyDownloaded() -> dict:
    file_dict = {}
    entries = os.listdir('music/')
    for entry in entries:
        file = entry.split('.')
        file_dict[file[0]] = 0
    return file_dict

def move_music() -> None:
    files = os.listdir('.')
    for file in files:
        if file.endswith('.mp3'):
            os.rename(file, os.path.join("music", file))


if not os.path.exists('music'):
    os.makedirs("music")
    print(f"Created Music Folder")
else:
    print(f"Music Folder Found")

move_music()

downloaded_files = alreadyDownloaded()
print(f"Already Downloaded Songs: {len(downloaded_files)}")


def sign_in(driver):
    phone_number_field = driver.find_element(By.NAME, "identifier")
    phone_number_field.send_keys("6204593386")
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/div[3]/form/button[2]").click()
    print("Waiting for user to enter the OTP")
    time.sleep(30)
    return True

def get_links(driver) -> list[str]:
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
            if any(isAlreadyDownloaded(key, downloaded_files) for key in data):
                download_data(list())
                data = alreadyDownloaded()
                createDownloadedFile(filename=filename , data=data)
                print("One or more files are already downloaded. Stopping the script.")
                sys.exit()
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
            with open(f"music/{data_key}.mp3", "wb") as file:
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

def isAlreadyDownloaded(file: str , files_dict: dict) -> bool:
    return file in files_dict

def createDownloadedFile(filename: str, data: dict) -> None:
    with open(filename, 'a') as f:
        for key , value in data.items():
            f.writelines(f"{key}\n")
    print(f'{filename} created with music metadata')

def download_file2(data_key): 
        url = f"https://cdn1.suno.ai/{data_key}.mp3"
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"music/{data_key}.mp3", "wb") as file:
                file.write(response.content)
            print(f"Successfully downloaded {data_key}.mp3")
        else:
            print(f"Failed to download {url}, status code: {response.status_code}")
    
def downloadFromFile() -> None:
    if not os.path.isfile("suno_download_music.txt"):
        print(f" Music Metadata not present | Can't proceed with downloading")
        return
    with open(filename , 'r') as f:
        files = f.readlines()

    for file in files:
        download_file2(file.strip())

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'downloadFromFile':
        downloadFromFile()
    else:
        driver = Driver(uc=True)
        url = "https://suno.com/me"
        driver.uc_open_with_reconnect(url, 10)
        sign_in(driver)
        get_links(driver)
        data = alreadyDownloaded()
        createDownloadedFile(filename=filename , data=data)
        print(f"Script Completed")
        driver.quit()
