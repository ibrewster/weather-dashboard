import glob
import os

import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# === CONFIGURATION ===
DASHBOARD_URL = "http://10.27.81.207:8123/dashboard-weather/0?kiosk="
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1MTU5Zjk0YTA2YTU0NmJjYmIyNGM5NGE4MjExODY1MyIsImlhdCI6MTc2MTY4NzcxNSwiZXhwIjoyMDc3MDQ3NzE1fQ.LavjahxRcnTuvnbYeRjQkDPNdY0QnT2GaRS_xWytI2k"
IMG_PATH = "/tmp/dashboard.png"
KINDLE_HOST = "root@192.168.15.244"
KINDLE_IMG_PATH = "/mnt/us/dashboard.png"
KINDLE_SCRIPT = "/mnt/us/show_dashboard.sh"
PROFILE_DIR = "/root/weatherDashboard/selenium-profile"

#service = Service(
#    log_output="/root/weatherDashboard/chromedriver.log",
#    log_level="DEBUG"
#)


# Clean up stale Chrome singleton locks before launching
for lock_file in glob.glob(f"{PROFILE_DIR}/Singleton*"):
    os.remove(lock_file)

# === SETUP HEADLESS BROWSER ===

options = Options()
options.add_argument(f"--user-data-dir={PROFILE_DIR}")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=600,939")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

try:
    # === LOAD DASHBOARD WITH TOKEN ===
    driver.get(DASHBOARD_URL)

    # Wait for dashboard to load
    time.sleep(5)

    # Take screenshot
    driver.save_screenshot(IMG_PATH)
finally:
    driver.quit()

# === PUSH TO KINDLE ===
subprocess.run(["/usr/bin/convert", "/tmp/dashboard.png", "-colorspace", "Gray", "/tmp/dashboard-gray.png"])
subprocess.run(["scp", "/tmp/dashboard-gray.png", f"kindle:{KINDLE_IMG_PATH}"])
#subprocess.run(["ssh", "kindle", "eips -c"])
subprocess.run(["ssh", "kindle", f"eips -g {KINDLE_IMG_PATH}"])

print("Dashboard updated and pushed to Kindle.")
