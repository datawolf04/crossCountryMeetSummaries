from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd


class scrapeMileSplit:
    def __init__(self,url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        # Optional: Set window size for consistent rendering in headless mode
        chrome_options.add_argument("window-size=1920x1080") 
        chrome_options.add_argument("--disable-gpu") # Recommended for headless on some systems

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Wait for a specific element (e.g., an element containing the JSON data)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "eventTable")))

        page_source = driver.page_source
        self.soup = BeautifulSoup(page_source, 'html.parser')

        # Now you can parse the soup for the loaded JSON or other dynamic content
        driver.quit()

    def getTableIDs(self):
        allTables = self.soup.find_all('table')
        tableIDs = []
        for t in allTables:
            if 'id' in t.attrs:
                firstRow = t.find_all('th')
                firstRow_text = [ele.text.strip() for ele in firstRow]
                if 'Athlete' in firstRow_text:
                    tableIDs.append(t['id'])
        return tableIDs

    def getRaceResults(self,raceID):
        thisTable = self.soup.find('table', id=raceID)
        rows = thisTable.find_all('tr')
        individualResults = []
        for row in rows:
            cols = row.find_all(['td','th'])
            cols_text = [ele.text.strip() for ele in cols]
            while len(cols_text) < 7:
                cols_text.append('')
            individualResults.append(cols_text)
            colNames = individualResults[0]
            colNames[3] = 'Grade'
            indivResDf = pd.DataFrame(individualResults[1:], columns=colNames)
        return indivResDf
