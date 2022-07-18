import re
import time
import uuid
import random
import pathlib
import pyperclip
import pandas as pd
import datetime

from os import listdir
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from ws_blaster.utils import open_driver, save_uploadedfile

class Blaster:
    
    def __init__(self, user_path):
        self.user_path = pathlib.Path(user_path)
        self.contacts_df = pd.DataFrame()
        self.contact_numbers = []
        self.messages = []
        self.files_to_blast_paths = []
        self.driver_dict = {}
        self.sent = 0

    @property
    def columns(self) -> list:
        """
        Get all the columns in the passed dataframe
        """
        if isinstance(self.contacts_df, pd.DataFrame):
            return self.contacts_df.columns.tolist()
    
    @property
    def phone_numbers(self) -> list:
        """
        Return a list of all the phone numbers to blast to 
        """
        return self.contact_numbers
    
    @property
    def contact_numbers_info(self) -> dict:
        """
        Returns a dictionary of the number of phone numbers and a sample of 5 numbers
        """
        info_dict = {
            "len_phone_numbers":len(set(self.contact_numbers)),
            "sample_of_5": random.sample(self.contact_numbers, 5)
        }
        return info_dict

    def clean_numbers(self, col: str) -> list:
        """
        Clean numbers to required format for whatsapp search

        df: Dataframe [pandas dataframe]
        col: Column name containing the numbers to blast [str]
        
        Returns dataframe with cleaned numbers
        """
        self.contacts_df[col] = self.contacts_df[col].astype(str)
        self.contacts_df[col] = [re.sub("[^0-9]", "", x) for x in self.contacts_df[col]]
        self.contacts_df = self.contacts_df[self.contacts_df[col] != '']
        self.contacts_df[col] = ['60' + x if (x[0] == '1' and 8 < len(x) < 11) else x for x in self.contacts_df[col]]
        self.contacts_df[col] = ['6' + x if (x[0] == '0' and 9 < len(x) < 12) else x for x in self.contacts_df[col]]
        self.contacts_df[col] = ['' if (x[2] != '1' or len(x) > 12 or len(x) < 11) else x for x in self.contacts_df[col]]
        self.contacts_df = self.contacts_df[self.contacts_df[col] != '']
        self.contacts_df = self.contacts_df.drop_duplicates(subset = col)
        self.contact_numbers = self.contacts_df[col].to_list()
        return self.contact_numbers

    def extract_from_file(self, file):
        # TODO: Extend for other file formats
        """
        Currently only accepts csv files.
        """
        self.contacts_df = pd.read_csv(file)
    
    def save_files_to_blast(self, uploaded_files):
        """
        Saves all the uplaoded files to a `tmp` file with a unique uuid
        """
        self.save_path = pathlib.Path("./tmp") / uuid.uuid1()
        self.save_path.mkdir(parents=True, exist_ok=True)
        for uploaded_file in uploaded_files:
            self.files_to_blast_paths.append(self.save_path / uploaded_file.name)
            save_uploadedfile(uploaded_file, uploaded_file.name, self.save_path)

    def add_message_variations_to_blast(self, message):
        """
        Append all the variations of a message to send to a list to be used later.
        """
        self.messages.append(message)
    
    def setup_drivers_in_account(self, platform, headless=False):
        """
        Load the driver for all whats app accounts under platform
        """
        driver_path = self.user_path / platform 
        for acc in  listdir(driver_path):
            data_dir = "user-data-dir=" + str(driver_path / acc)
            driver = open_driver(data_dir, headless=headless)
            self.driver_dict[acc] = driver
            time.sleep(10)
    
    def _select_elm(self, driver, xpath, wait):
        """
        Get the selenium object associated with the element in the DOM Tree
        """
        elm = WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return elm

    def nav_to_number(self, phone_number, sleep=5):
        """
        Navigate to the given URL and open a chat for a given phone number
        """
        acc = random.choice(list(self.driver_dict.keys()))
        driver = self.driver_dict[acc]
        url = 'https://web.whatsapp.com/send?phone=' + str(phone_number)
        driver.get(url)
        driver.execute_script("window.onbeforeunload = function() {};")
        time.sleep(sleep)
        return acc, driver
    
    def send_file(self, driver, file, sleep=2):
        """
        Send the requested files in the chat 
        """
        f = driver.find_element_by_css_selector("input[type='file']").send_keys(file)
        self._select_elm(driver, '//*[@class="_165_h _2HL9j"]', 5).click()
        time.sleep(sleep)
    
    def send_message(self, driver, message, sleep=2):
        """
        Send the message in the chat
        """
        self._select_elm(driver, '//*[@class="p3_M1"]', 6).click()
        pyperclip.copy(message)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(sleep)
        self._select_elm(driver, '//*[@data-testid="send"]', 5).click()
    
    def check_if_unavailable(self):
        """
        Check if the number is unavailable in the chat 
        """
        pass
    
    def apply_random_wait(self, count):
        """
        Apply some random wait time to lower the risk of accounts gettig banned
        """
        # if count % 300 == 0 and count != 0:
        #     time.sleep(random.randint(500,1000))
        # elif count % 10 == 0 and count!= 0:
        #     time.sleep(random.randint(5,10))
        #     return 'Numbers gone through: ' + str(count) + ', Messages sent: ' + str(count) + ', Time elapsed: ' + str(datetime.now() - self.start)[:7]
        # else:
        #     time.sleep(random.randint(2,5))        
        pass

    def close(self):
        for available_drivers in self.driver_dict.values():
            available_drivers.quit()




    

