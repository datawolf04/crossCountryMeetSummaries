import os
import re
from openpyxl import Workbook 
import pandas as pd
from scrapeMileSplit import scrapeMileSplit

def getMeetTitle(url):
    meetTitle = url.split('https://nc.milesplit.com/meets/')[1].split('/results')[0]
    meetTitle = re.sub(r'\d+', '', meetTitle).strip('-')
    return meetTitle

##############################################################
## function for reading results tables and loading them into the database
def writeMeetToDatabase(url,meetDate,boysRecord,girlsRecord):
    boysRes = 'meetResultsBoys2025.xlsx'
    girlsRes = 'meetResultsGirls2025.xlsx'

    def writeWB(fName):   
        # create new excel file
        df_empty = pd.DataFrame()
        df_empty.to_excel(fName, sheet_name='MeetIndex')

    def initializeWB():
        if not os.path.exists(boysRes):
            writeWB(boysRes)
        if not os.path.exists(girlsRes):
            writeWB(girlsRes)

    def inputRaceInfo(raceRes):
        '''
        This function allows the user to input race information based on the first few rows of the results.
        It collects/outputs the gender, level, and race distance
        '''
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
        print(raceRes.head(5))
        gender = getGender()
        level = getLevel()
        distance = float(input("Enter race length in km:  "))
        return gender, level, distance

    def getRaceInfo(res):
        indivResult = res
        gender, level, dist = inputRaceInfo(indivResult)
        return gender, level, dist

    mTitle = getMeetTitle(url)
    meetScrape = scrapeMileSplit(url,meetDate)
    raceIDs = meetScrape.raceIDs
    allResults = meetScrape.results

    # Make empty WB if does not exist
    initializeWB()

    for res, rid in zip(allResults,raceIDs):
        gen, lev, dist = getRaceInfo(res)
        mark = res.Mark
        Time = [(60*float(m.split(':')[0]) + float(m.split(':')[1])) for m in mark]
        res['Time'] = Time

        # Get correct filename and load the workbook
        if gen == "Boys":
            fName = boysRes
            courseRecord = boysRecord
        elif gen == "Girls":
            fName = girlsRes
            courseRecord = girlsRecord

        raceSheetName = mTitle + gen + lev
        
        raceIndexEntry = pd.DataFrame([[raceSheetName, mTitle, gen, lev, dist, courseRecord]],
            columns=['SheetName', 'MeetTitle', 'Gender', 'Level', 'Distance', 'Record'])
        
        # Make new sheet and write race results to it.
        wb = Workbook()
        with pd.ExcelWriter(fName, engine='openpyxl',mode='a',if_sheet_exists='overlay') as writer:
            writer.workbook = wb
            writer.workbook.sheets = dict((ws.title, ws) for ws in wb.worksheets)
            res.to_excel(writer, sheet_name=raceSheetName,index=False)

            # 'MeetIndex'
            botRow = writer.sheets['MeetIndex'].max_row
            isEmpty = botRow < 1.5
            if isEmpty:
                raceIndexEntry.to_excel(writer, sheet_name='MeetIndex', index=False, header=True)
            else:
                raceIndexEntry.to_excel(writer, sheet_name='MeetIndex', index=False, header=False, startrow=botRow)

            writer.workbook.save(fName)

        


if __name__ == "__main__":
    from datetime import datetime

    allMeetInfo = pd.read_csv('meetInfo2025.csv')
    postedMeetInfo = allMeetInfo[allMeetInfo.Formatted].reset_index()
    boysRes = 'meetResultsBoys2025.xlsx'
    girlsRes = 'meetResultsGirls2025.xlsx'
    recordedMeets = []
    if os.path.exists(boysRes):
        index = pd.read_excel(boysRes, sheet_name="MeetIndex")
        recordedMeets = list(set(index.MeetTitle))
    
    for m in range(postedMeetInfo.shape[0]):
        meetDate = datetime.strptime(postedMeetInfo.Date[m],"%Y-%m-%d").date()
        meetURL = postedMeetInfo.url[m]
        meetTitle = getMeetTitle(meetURL)
        meetBoysRecord = postedMeetInfo.BoysRecord[m]
        meetGirlsRecord = postedMeetInfo.GirlsRecord[m]
        if meetTitle not in recordedMeets:
            writeMeetToDatabase(meetURL, meetDate, meetBoysRecord, meetGirlsRecord)
    




