import os
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# MongoDB setup
mongo_uri = 'mongodb+srv://SerojGym:Vespucci10@BIGClust99.gvypm8v.mongodb.net/gym_data?retryWrites=true&w=majority'

# Function to collect gym data
def collect_gym_data(driver):
    driver.get("https://connect2concepts.com/connect2/?type=circle&key=2A2BE0D8-DF10-4A48-BEDD-B3BC0CD628E7")
    WebDriverWait(driver, 40).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "circleChart")))

    data = []
    circle_charts = driver.find_elements(By.CLASS_NAME, "circleChart")
    for chart in circle_charts:
        facility_info_element = chart.find_element(By.XPATH, './following-sibling::div')
        facility_name = facility_info_element.text.split('\n')[0]
        data_percent = chart.get_attribute('data-percent')
        last_count = chart.get_attribute('data-lastcount')
        is_closed = chart.get_attribute('data-isclosed')

        try:
            updated_info = facility_info_element.text
            updated_time = updated_info.split('Updated: ')[1].strip()
        except Exception as e:
            print(f"Error extracting updated time: {e}")
            updated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if "Marino Center - 3rd Floor Weight Room" in facility_name or "SquashBusters - 4th Floor" in facility_name:
            data.append({
                'facility': facility_name,
                'attendance_percent': data_percent,
                'last_count': last_count,
                'is_closed': 'Yes' if is_closed else 'No',
                'timestamp': updated_time
            })

    return data

# Function to save data to MongoDB
def save_data_to_mongodb(data, client):
    db = client['gym_data']
    collection = db['attendance_records']
    if data:
        collection.insert_many(data)

# Configure Chrome options for headless mode
chrome_options = Options()
chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' )
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

# Set up Chrome service
chrome_executable_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
chrome_service = Service(executable_path=chrome_executable_path)

# Main execution
try:
    with MongoClient(mongo_uri) as client:
        # Initialize WebDriver with configured options
        with webdriver.Chrome(service=chrome_service, options=chrome_options) as driver:
            gym_data = collect_gym_data(driver)
            save_data_to_mongodb(gym_data, client)
except Exception as e:
    print(f"An error occurred: {e}")
