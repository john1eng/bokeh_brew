import pandas as pd
from brewasisdb import add_brew2018

brew2018 = pd.read_excel('brew2018.xlsx', index_col=None, header=0)
brew2018.columns=['state', 'produced', 'population', 'num_co', 'rank', 'by_adults', 'capita']
brew2018['by_adults'] = brew2018['by_adults'].apply(lambda x: round(x, 2))
print(brew2018.head())



for index, row in brew2018.iterrows():
    add_brew2018(row['state'], row['produced'], row['population'], row['num_co'], row['rank'], row['by_adults'], row['capita'])
