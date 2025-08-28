## Big Carolina Conference Cross Country summaries
This repository takes results from [MileSplit.com](https://nc.milesplit.com/) and collects the Cross Country Results for the teams in the Big Carolina Conference 6A/7A within NCHSAA. These are:

- J.H. Rose (6A)
- Jacksonville (6A)
- White Oak (6A)
- D.H. Conley (7A)
- New Bern (7A)
- South Central (7A)

## Work flow:
1. Update `meetInfo2025.csv` with results that have been posted
2. Run `python writeMeetToDataBase.py` to update the `meetResults[Gender]2025.xlsx` files.
3. Build the weekly reports.

## To Do:
- Create tools for pulling the meets that occur during a given week.
- Aggregate BCC team results across multiple meets. Report PB/SBs and high performers.