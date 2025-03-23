import time
import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import subprocess

def install_chrome_and_driver():
    # Install Google Chrome and ChromeDriver on Render
    subprocess.run(['apt-get', 'update'], check=True)
    subprocess.run(['apt-get', 'install', '-y', 'google-chrome-stable'], check=True)
    subprocess.run(['apt-get', 'install', '-y', 'chromium-chromedriver'], check=True)

def get_dfreference():
    # Install Chrome and ChromeDriver
    install_chrome_and_driver()

    # Setup for headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without opening a browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (headless mode)
    
    # Use the ChromeDriver installed via apt
    service = Service("/usr/lib/chromium-browser/chromedriver")
    
    # Setup webdriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open website
    driver.get("https://www.locoloader.com/pricing/")
    time.sleep(5)  # Allow page to load
    
    # Extract API call details
    logs = driver.get_log("performance")
    driver.quit()

    braintree_url = None
    headers = {}
    payload = {}

    for entry in logs:
        try:
            log_data = json.loads(entry["message"])["message"]
            if "Network.requestWillBeSent" in log_data["method"]:
                request = log_data["params"]["request"]
                url = request["url"]
                if "three_d_secure/lookup" in url:
                    braintree_url = url
                    headers = request.get("headers", {})
                    if "postData" in request:
                        payload = json.loads(request["postData"])
                    break
        except Exception as e:
            continue
    
    if braintree_url:
        response = requests.post(braintree_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("dfreference")
        else:
            return "Error: Failed to fetch dfreference"
    return "Error: Braintree request not found"

# Run script
dfreference = get_dfreference()
print("dfreference:", dfreference)
