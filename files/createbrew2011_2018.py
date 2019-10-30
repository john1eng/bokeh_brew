import pandas as pd
from brewasisdb import add_brew2011_2018

brew2011_2018 = pd.read_excel('brew2011-2018.xlsx', index_col=None, header=0)
brew2011_2018.columns=['state', 'prod2011', 'prod2012', 'prod2013', 'prod2014', 'prod2015', 'prod2016', 'prod2017', 'prod2018']
for i in list(brew2011_2018.columns):
    if i != 'state':
        brew2011_2018[i] = brew2011_2018[i].round(0).astype(int)

for index, row in brew2011_2018.iterrows():
    add_brew2011_2018(row['state'], row['prod2011'], row['prod2012'], row['prod2013'], row['prod2014'], row['prod2015'], row['prod2016'], row['prod2017'], row['prod2018'])
