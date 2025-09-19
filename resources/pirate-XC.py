import pandas as pd

############################################################
## Boys Championship Results
with open('raw/pirate-XC-champ-boys.txt', 'r') as file:
    rawRes = file.readlines()

# Remove header row
rawRes = rawRes[4:]
Athlete = []
Mark = []
Team = []
Time = []
for res in rawRes:
    line = res.strip().split(' ')  
    lineLen = len(line)
    Athlete.append(line[1] + " " + line[2])
    thisMark = line[-1]
    Mark.append(thisMark)
    Team.append(' '.join(line[3:(lineLen-1)]))
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

boysChamp = results

############################################################
## Boys Open Results
with open('raw/pirate-XC-invite-boys.txt', 'r') as file:
    rawRes = file.readlines()

# Remove header row
rawRes = rawRes[2:]
Athlete = []
Mark = []
Team = []
Time = []
for res in rawRes:
    line = res.strip().split(' ')  
    lineLen = len(line)
    Athlete.append(line[1] + " " + line[2])
    thisMark = line[-1]
    Mark.append(thisMark)
    Team.append(' '.join(line[3:(lineLen-1)]))
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

boysOpen = results

############################################################
## Girls Championship Results
with open('raw/pirate-XC-champ-girls.txt', 'r') as file:
    rawRes = file.readlines()

# Remove header row
rawRes = rawRes[2:]
Athlete = []
Mark = []
Team = []
Time = []
for res in rawRes:
    line = res.strip().split(' ')  
    lineLen = len(line)
    Athlete.append(line[1] + " " + line[2])
    thisMark = line[-1]
    Mark.append(thisMark)
    Team.append(' '.join(line[3:(lineLen-1)]))
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

girlsChamp = results

file_path = 'pirate-XC-invite.xlsx'

with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    # Write each DataFrame to a different sheet
    boysChamp.to_excel(writer, sheet_name='Boys Championship', index=False)
    girlsChamp.to_excel(writer, sheet_name='Girls Championship', index=False)
    boysOpen.to_excel(writer, sheet_name="Boys Invitational", index = False)