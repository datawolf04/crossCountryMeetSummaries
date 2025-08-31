import pandas as pd

############################################################
## Boys Results
with open('raw/jh-rose-invite-boys.txt', 'r') as file:
    boysRawRes = file.readlines()

# Remove header row
boysRawRes = boysRawRes[1:]
Athlete = []
Mark = []
Team = []
for res in boysRawRes:
    line = res.strip().split(' ')  
    Athlete.append(line[0].upper())
    Mark.append(line[1].replace("'",":"))
    Team.append(' '.join(line[2:]).upper())

boysResults = pd.DataFrame({
    "Athlete": Athlete,
    "Team": Team,
    "Mark": Mark
})

boysResults.loc[boysResults.Team == "NORHTERN NASH", "Team"] = "NORTHERN NASH"
boysResults.loc[boysResults.Team == "MARTIN CO", "Team"] = "MARTIN COUNTY"
boysResults.loc[boysResults.Team == "MARTIN CO.", "Team"] = "MARTIN COUNTY"

############################################################
## Girls Results
with open('raw/jh-rose-invite-girls.txt', 'r') as file:
    girlsRawRes = file.readlines()

Athlete = []
Mark = []
Team = []
for res in girlsRawRes:
    line = res.strip().split(' ')  
    Athlete.append(line[0].upper())
    Mark.append(line[1])
    Team.append(' '.join(line[2:]).upper())

girlsResults = pd.DataFrame({
    "Athlete": Athlete,
    "Team": Team,
    "Mark": Mark
})

girlsResults.loc[girlsResults.Team == "MC", "Team"] = "MARTIN COUNTY"
girlsResults.loc[girlsResults.Team == "NORHTERN NASH", "Team"] = "NORTHERN NASH"
girlsResults.loc[girlsResults.Team == "NOTRTHERN NASH", "Team"] = "NORTHERN NASH"
girlsResults.loc[girlsResults.Team == "SC", "Team"] = "SOUTH CENTRAL"
girlsResults.loc[girlsResults.Team == "WO", "Team"] = "WHITE OAK"
girlsResults.loc[girlsResults.Team == "WHITE", "Team"] = "WHITE OAK"

file_path = 'jh-rose-invite.xlsx'

with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    # Write each DataFrame to a different sheet
    boysResults.to_excel(writer, sheet_name='Boys', index=False)
    girlsResults.to_excel(writer, sheet_name='Girls', index=False)