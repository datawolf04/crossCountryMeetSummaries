from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import re
# from datetime import date

def getMeetID(url, theDate):
    meetTitle = url.split('https://nc.milesplit.com/meets/')[1].split('/results')[0]
    meetTitle = re.sub(r'\d+', '', meetTitle).rstrip('-')
    meetID = "m" + theDate.strftime("%y%m%d") + meetTitle
    return meetID

class scrapeMileSplit:
    def __init__(self,url,meetDate):
        self.url = url
        self.meetID = getMeetID(url, meetDate)
        self.raceIDs = self.getTableIDs()
        self.results = self.allRaceResults()
        self.page = self.getPage()
    
    def getPage(self):
        url = self.url
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
        page = BeautifulSoup(page_source, 'html.parser')

        # Now you can parse the soup for the loaded JSON or other dynamic content
        driver.quit()
        return page

    def getTableIDs(self):
        self.page = self.getPage()
        allTables = self.page.find_all('table')
        tableIDs = []
        for t in allTables:
            if 'id' in t.attrs:
                firstRow = t.find_all('th')
                firstRow_text = [ele.text.strip() for ele in firstRow]
                if 'Athlete' in firstRow_text:
                    tableIDs.append(t['id'])
        return tableIDs

    def getIndividualResults(self,raceID):
        thisTable = self.page.find('table', id=raceID)
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
    
    def allRaceResults(self):
        allRes = []
        for rid in self.raceIDs:
            allRes.append(self.getIndividualResults(rid))
        return allRes

if __name__ == "__main__":
    from datetime import date

    testURL = 'https://nc.milesplit.com/meets/687737-light-up-the-night-2025/results'
    tstMeetDate = date(2025, 8, 16)

    tst = scrapeMileSplit(testURL, tstMeetDate) 
