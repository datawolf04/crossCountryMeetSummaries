# import re
# import os
# from openpyxl import load_workbook
import pandas as pd
import scrapeMileSplit

##############################################################
## class for reading results tables and loading them into the database
class writeMeetToDatabase:
    def __init__(self, meetID):
        self.meetID = meetID

    def identifyRaceInfo(self,res):
        def getGender():
            while True:
                try:
                    gen = input("Enter B or G:  ")
                    if gen.lower() == 'b':
                        gender = 'Boys'
                    elif gen.lower() == 'g':
                        gender = 'Girls'
                    else:
                        raise ValueError(f'Input {gen} not recognized. Enter `B` or `G`.')
                    return gender
                except ValueError as e:
                    print(e)

        def getLevel():
            while True:
                try:
                    lev = input("Enter V, JV, or F:  ")
                    if lev.lower() == 'v':
                        level = 'Varsity'
                    elif lev.lower() == 'jv':
                        level = 'JV'
                    elif lev.lower() == 'f':
                        level = 'Freshmen'
                    else:
                        raise ValueError(f'Input {lev} not recognized. Enter `V` or `JV`.')
                    return level
                except ValueError as e:
                    print(e)

        ## Print the head of the results sheet, enter metadata about race and return it properly formatted.            
        print(res.head(5))
        gender = getGender()
        level = getLevel()
        distance = float(input("Enter race length in km:  "))
        return gender, level, distance

    def getMeetData(self, meeturl, meetID):
        meetPage = scrapeMileSplit(url=meeturl)
        tids = meetPage.getTableIDs()
        return tids

    def getRaceTable(self,raceID):
        indivResult = self.meetPage.getRaceResults(raceID)
        gender, level, dist = self.identifyRaceInfo(indivResult)
        raceID = self.meetID + raceID
        indexEntry = pd.DataFrame({
            'raceID': raceID, 
            'gender': gender, 
            'level': level, 
            'raceLength': dist})
        print(indexEntry)
            # Write raceID, gender, level, distance to race index sheet
            # Add race result table to new sheet


 
allMeetInfo = pd.read_csv('meetInfo2025.csv')
toRecord = [p and not r for p,r in zip(allMeetInfo.Posted, allMeetInfo.Recorded)]

meetInfoToRecord = allMeetInfo[toRecord]
"""
seasonResults = 'meetResults2025.xlsx'
if not os.path_exists(seasonResults):
    writer = pd.ExcelWriter(seasonResults, engine='xlsxwriter')

for i in range(postedMeets.shape[0]):
    meetDate, meetLocation, meeturl, meetBoysRecord, meetGirlsRecord, meetPosted, meetRecorded = postedMeets.iloc[i]
    meetTitle = meeturl.split('https://nc.milesplit.com/meets/')[1].split('/results')[0]
    meetTitle = re.sub(r'\d+', '', meetTitle).rstrip('-')
    meetID = "m" + meetDate.strftime("%y%m%d") + meetTitle

"""

""" 
writer = pd.ExcelWriter("bccResults2025.xlsx", engine='xlsxwriter')
df1.to_excel(writer, sheet_name='Sheet1', index=False)
"""
