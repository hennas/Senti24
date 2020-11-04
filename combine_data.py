import pandas as pd

filenames = ["s24_csv\s24_20{:02}.csv".format(i+1) for i in range(8,17)]

data = pd.DataFrame()
for fn in filenames:
    year_data = pd.read_csv(fn) 
    data = pd.concat([data, year_data], ignore_index=True)
    
data.to_csv("data_combined.csv", index=False)