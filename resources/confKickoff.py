import pandas as pd

############################################################
## Boys Championship Results
with open('raw/conf-kickoff-boys.txt', 'r') as file:
    rawRes = file.readlines()

# Remove header row
rawRes = rawRes[1:]
Athlete = []
Mark = []
Team = []
Time = []
for res in rawRes:
    line = res.strip().split(' ')  
    Athlete.append(line[1] + " " + line[2])
    last = []
    while len(last) < 6:
        last = line[-1]
        line = line[:-1]
        thisMark = last
    lineLen = len(line)
    Mark.append(thisMark)
    Team.append(' '.join(line[3:(lineLen)]))
    mins, secs = thisMark.split(":")
    Time.append(60*float(mins) + float(secs))
    
results = pd.DataFrame({
    "Athlete": Athlete,
    "Team": Team,
    "Mark": Mark,
    "Time": Time
})

## Add place column and move to front
results["Place"] = results.index + 1
Place = results.pop("Place")
results.insert(0, "Place", Place)

boysRes = results

############################################################
## Boys Championship Results
with open('raw/conf-kickoff-girls.txt', 'r') as file:
    rawRes = file.readlines()

# Remove header row
rawRes = rawRes[1:]
Athlete = []
Mark = []
Team = []
Time = []
for res in rawRes:
    line = res.strip().split(' ')  
    Athlete.append(line[1] + " " + line[2])
    last = []
    while len(last) < 6:
        last = line[-1]
        line = line[:-1]
        thisMark = last
    lineLen = len(line)
    Mark.append(thisMark)
    Team.append(' '.join(line[3:(lineLen)]))
    mins, secs = thisMark.split(":")
    Time.append(60*float(mins) + float(secs))
    
results = pd.DataFrame({
    "Athlete": Athlete,
    "Team": Team,
    "Mark": Mark,
    "Time": Time
})

## Add place column and move to front
results["Place"] = results.index + 1
Place = results.pop("Place")
results.insert(0, "Place", Place)

girlsRes = results



file_path = 'conference-kickoff.xlsx'

with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    # Write each DataFrame to a different sheet
    boysRes.to_excel(writer, sheet_name='Boys', index=False)
    girlsRes.to_excel(writer, sheet_name='Girls', index=False)