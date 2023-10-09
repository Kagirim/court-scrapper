from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import pandas as pd
from pyvirtualdisplay import Display


page_count = 0

# dates to be scraped
start_date = datetime(2020, 1, 1)
end_date = datetime(2023, 10, 4)

# create a list of dates to be scraped
dates = []
for n in range(int((end_date - start_date).days)):
    dates.append(start_date + timedelta(n))

# Create a virtual display
display = Display(visible=0, size=(800, 600))
display.start()

# create webdriver object and Navigate to the application home page
driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get(url="https://eapps.courts.state.va.us/CJISWeb/circuit.jsp")

def navigate_to_main_menu():
    # Get the search dropdown
    search_dropdown = driver.find_element(By.NAME, "whichsystem")
    search_dropdown = Select(search_dropdown)

    # Select the search dropdown option
    search_dropdown.select_by_value("107C1Loudoun Circuit Court")

    # Submit the search form
    search_button = driver.find_element(By.ID, "courtSubmit").click()

def navigate_to_case_list(current_date):
    # navigate to main menu
    try:
        navigate_to_main_menu()
    except:
        pass

    # Get the date textbox and enter the date
    date_textbox = driver.find_element(By.ID, "selectCheck")
    date_textbox.clear()
    date_textbox.send_keys(current_date.strftime("%m/%d/%Y"))
    driver.find_element(By.ID, "hearSubmit").click()

    # check if there are items in case
    try:
        # get the case rows
        case_table = driver.find_element_by_xpath("//table[@class='nameList' and @id='count']")
        case_table_body = case_table.find_element(By.TAG_NAME, "tbody")
        case_table_rows = case_table_body.find_elements(By.TAG_NAME, "tr")

    except:
        back_button = driver.find_element(By.XPATH, "//input[@value='Main Menu']")
        back_button.click()
        return None

    return case_table_rows

def get_case_info(cases):
    if cases is None:
        return None

    cases_list = []

    # select the caselink and navigate to the case info page
    for case in cases:
        try:
            case_link = case.find_element(By.TAG_NAME, "a")
        except:
            continue
        
        case_link.click()

        # get the page source and extract data
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        cases_list.append(soup)

        # click on the back button with value Main Menu
        back_button = driver.find_element(By.XPATH, "//input[@value='Main Menu']")
        back_button.click()

    return cases_list

def extract_data(cases_list):
    if cases_list is None:
        return None

    info_dict = {}
    case_info = []
    for case in cases_list:
        # get the td inside the tr with id = "BackgroundWhite"
        background_white_tr = case.find("tr", {"id": "BackgroundWhite"})
        table_data = background_white_tr.find_all('td', {'nowrap': '', 'valign': 'top'})

        # get the case info
        for data in table_data:
            # get the label and value
            label = data.find('div', {'id': 'fontBold'}).strip()
            value = label.text.strip()
            
            # save the data in the dictionary
            info_dict[label] = value
        
if __name__ == "__main__":
    all_cases = []
    for current_date in dates:
        # navigate to case list
        case_table_rows = navigate_to_case_list(current_date)
        if case_table_rows is None:

            continue
        
        # get the case info
        case_info = get_case_info(case_table_rows)

        # extract the data
        all_cases.append(extract_data(case_info))

        print(f"Scraping {current_date.strftime('%m/%d/%Y')}")

    # store the data in a dataframe
    all_cases = [item for sublist in all_cases for item in sublist]
    case_info_df = pd.DataFrame(all_cases)
    case_info_df.to_csv("case_info.csv", index=False)

    # close the driver
    driver.close()