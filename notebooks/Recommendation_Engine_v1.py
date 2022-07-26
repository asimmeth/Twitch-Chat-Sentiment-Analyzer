import os 
import pandas as pd
import copy

files = []  
file_name = []
path = r'C:\Users\alebo\Desktop\Berkeley\210\Dummy'
with os.scandir(path) as entries:
    for entry in entries:
        files.append(entry.name)

for i in range(0, len(files)):  
    file_name.append(files[i])
    files[i] = path + "/" + files[i]


#print(f'There are {len(files)} file(s) in the sub-folder.')


pof = files[0]
xlsx = pd.ExcelFile(pof)
sheets = xlsx.sheet_names

data_df = pd.read_excel(xlsx, index_col=None, na_values="NA")  #<---THIS IS THE DATAFRAME WE WANT. CHANGE INPUT PATH TO GET DATAFRAME


#Section to normalize data
def normalizing_followers(row):
    '''
    Function to normalize followers to followers gained over time.
    '''
    return row['Followers Gained'] / float(row['Time'])

def normalizing_subs(row):
    '''
    Function to normalize subs to subs gained over time.
    '''
    return row['Subs Gained'] / float(row['Time'])

#Applying the functions
data_df['Norm_Foll'] = data_df.apply(normalizing_followers, axis = 1)
data_df['Norm_Sub'] = data_df.apply(normalizing_subs, axis = 1)

#Isolating the three columns to normalize
columns = ['Mean Views', 'Norm_Foll', 'Norm_Sub']

for col in columns: #Normalizing them to 0-1 scale through min max
    norm_data = data_df[col].tolist()
    min_val = min(norm_data)
    max_val = max(norm_data)

    for i in range(len(norm_data)):
        norm_data[i] = (norm_data[i] - min_val) / (max_val - min_val)

    data_df[col] = norm_data


#Normalizing Sentiment to  0 - 1 scale
norm_sentiments = data_df['Mean Sentiment'].tolist()
for i in range(len(norm_sentiments)):
    norm_sentiments[i] = (norm_sentiments[i] + 1) / 2.0
data_df['Mean Sentiment'] = norm_sentiments



def recommendation(row):
    '''
    Basic recommendation engine. Each normalized category times the weight. 
    
    Current weight configuration: 
    35% Sentiment Value
    30% Subs Gained
    25% Followers Gained
    10% Views
    '''
    value = (0.1 * (row['Mean Views'])) + (0.25 * (row['Norm_Foll'])) + (.30 * (row['Norm_Sub'])) + (0.35 * (row['Mean Sentiment']))
    return value

data_df['Scores'] = data_df.apply(recommendation, axis = 1)

rec_cat = data_df[data_df['Scores'] == data_df['Scores'].max()]['Categories'].tolist()[0]


print(f'Given the latest stream performance, we recommend continuing to stream the following category: {rec_cat}') #<--- THIS IS THE OUTPUT WE CARE ABOUT, SPECIFICALLY 'REC_CAT'