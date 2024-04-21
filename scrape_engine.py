import selenium
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse  # For URL encoding
import json

SBR_WEBDRIVER = 'insert bright data unique private sbr webdrive'
position_without_salary_info = []

import csv

all_positions = []

with open('positions_above_300.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if row[0] != "position":
            all_positions.append(row[0])


def scrape_salary_for_position(position):
    encoded_position = urllib.parse.quote(position)  # URL-encode the position
    url = f'https://www.indeed.com/career/{encoded_position}/salaries'

    print(f'Navigating to {url}')
    with Remote(ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome'), options=ChromeOptions()) as driver:
        driver.get(url)
        # error_element = driver.find_element_by_css_selector("h1[style*='border-right']")
        # error_message = driver.find_element_by_css_selector("div > h2")
        # if "404" in error_element.text and "Page not found" in error_message.text:
        #     print("404 Error Page Found")
        # else:
        #     print("Page is valid"
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'css-hy3rce')))
        except:
            print(f"Could not find salary information for {position}")
            position_without_salary_info.append(position)
            return None, None
        html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    salary_range = {}
    salary_experience = {}

    try:
        average_salary = soup.find('div', class_='css-hy3rce').get_text(strip=True)
        low_salary = soup.find('div', class_='css-12dzqpd').find_all('div', class_='css-u74ql7')[0].get_text(strip=True)
        high_salary = soup.find('div', class_='css-12dzqpd').find_all('div', class_='css-u74ql7')[1].get_text(
            strip=True)

        # Extracting the salary amount from the strings
        salary_range['Low'] = low_salary.split('$')[1]
        salary_range['Average'] = average_salary.split('$')[1]
        salary_range['High'] = high_salary.split('$')[1]
        experience_table = soup.find('div', {'data-testid': 'salary-by-experience-table'})
        if experience_table:
            rows = experience_table.find_all('tr')
            for row in rows[1:]:  # Skip the header row
                columns = row.find_all('td')
                experience = columns[0].get_text(strip=True)
                salary = columns[1].get_text(strip=True)[1:] if columns[1].get_text(strip=True) != '-' else columns[
                    1].get_text(strip=True)
                salary_experience[experience] = salary

        print(f"Position: {position}")
        print(salary_range)
        print(f"Salary Information: {salary_experience}")
        position_salary_dict[position] = salary_experience
        min_max_salary[position]=salary_range
        with open(position_salary_json, 'w') as json_file:
            json.dump(position_salary_dict, json_file)
        with open(min_max_json, 'w') as json_file:
            json.dump(min_max_salary, json_file)
    except AttributeError:
        print(f"Could not find salary information for {position}")
        # position_without_salary_info.append(position)
        # return None, None
    print()


    return salary_range, salary_experience


position_salary_json = 'position_salary.json'
min_max_json = 'min_max_salary.json'
position_salary_dict = {}
min_max_salary = {}
# positions=["data analyst", "software engineer","project manger"]


# Reading the JSON file and converting it into a dictionary
with open(position_salary_json, 'r') as json_file:
    data = json.load(json_file)

# Now 'data' is a dictionary containing the contents of the JSON file



for position in all_positions:
    if position in data:
        continue
    scrape_salary_for_position(position)
