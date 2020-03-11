import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import SGDRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def calculate_room_number(text):
    r = re.findall('\d+', text)
    if 'fél' in text:
        if len(r) == 2:
            return float(r[0]) + 0.5*float(r[1])
        else:
            return float(r[0])
    else:
        return float(r[0])

def construction_classes(text):
    r = re.findall('\d+', text)
    # import pdb
    # pdb.set_trace()
    if len(r) == 1:
        xx=float(r[0])
        if xx < 1950:
            return '1950 előtt'
        elif xx>=1950 and xx<1980:
            return '1950-1980 között'
        elif xx>=1980 and xx<2000:
            return '1981-2000 között'
        elif xx>=2000 and xx<2010:
            return '2001-2010 között'
        else:
            return '2010-2020 között'
    else:
        return text

def get_coordinates(text, north=True):
    if text is np.nan:
        return np.nan
    else:
        r = re.findall('north=(\d+\.\d+), east=(\d+\.\d+)',text)
        if north:
            north = np.zeros(2)
            for i,x in enumerate(r):
                north[i] = x[0]
            return north.mean()
        else:
            east = np.zeros(2)
            for i,x in enumerate(r):
                east[i]  = x[1]
            return east.mean()
                
         

def print_stats(y_true, y_pred):
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    print(f'R2: {r2}')
    print(f'MAE: {mae}')
    print(f'sqrt(MSE): {np.sqrt(mse)}')

file_name = '20200309_result.xlsx'
full_name = os.path.join('Data', file_name)

df = pd.read_excel(full_name, header=0)

prop_type = 'House'
df_sel = df.loc[df['type'] == prop_type, ['city', 'size', 'price', 'land_size', 'room_number', 'condition', 'construction_year']]
# df_sel = df_sel[df_sel.city=='Algyo']
df_sel = df_sel.dropna()
df_sel = df_sel[df_sel.condition!='nincs megadva']

df_sel.room_number = df_sel.room_number.apply(calculate_room_number)
df_sel.construction_year = df_sel.construction_year.apply(construction_classes)
city_dummy = pd.get_dummies(df_sel.city)
condition_dummy = pd.get_dummies(df_sel.condition)
year_dummy = pd.get_dummies(df_sel.construction_year)

data_input = df_sel.merge(city_dummy, left_index=True, right_index=True)
data_input = data_input.merge(condition_dummy, left_index=True, right_index=True)
data_input = data_input.merge(year_dummy, left_index=True, right_index=True)
# data_input = data_input[data_input.price < 200e6]
# take out one input
final_target = data_input[(data_input.city == 'Algyo') & (data_input['size'] == 170)]
data_input = data_input[~((data_input.city == 'Algyo') & (data_input['size'] == 170))]



# combined_features = ['size', 'land_size', 'room_number', 'Algyo', 'Morahalom', 'Szeged', 'befejezetlen', 'felújítandó',
#        'felújított', 'jó állapotú', 'közepes állapotú', 'új építésű', 'újszerű']
combined_features = [x for x in data_input.columns if x not in ['city', 'condition', 'price', 'construction_year']]
target = 'price'

X_train, X_test, y_train, y_test = train_test_split(data_input[combined_features], data_input[target], 
                                                    test_size=0.20, random_state=42)

#################################
regressor = DecisionTreeRegressor(random_state=42)
# Fit the model
regressor.fit(X_train, y_train)

prediction = regressor.predict(X_test)
print('Decision tree results')
print_stats(y_test, prediction)

#######################################

regressor = GradientBoostingRegressor(n_estimators=500, learning_rate=0.01, max_depth=5, random_state=0, loss='ls', max_features='log2')
# Fit the model
regressor.fit(X_train, y_train)

prediction = regressor.predict(X_test)
print('Gradient boost regression results')
print_stats(y_test, prediction)

##############################################

params = {'legend.fontsize': '15',
          'figure.figsize': (15, 8),
         'axes.labelsize': '15',
         'axes.titlesize':'15',
         'xtick.labelsize':'15',
         'ytick.labelsize':'15'}
plt.rcParams.update(params)

plt.plot(y_test/1e6, prediction/1e6, 'o', markersize=6, label='Prediction')
plt.plot(y_test/1e6, y_test/1e6, linewidth=3, label='Advertised price')
plt.xlabel('Price on Ingatlan.com (million Ft)')#, fontsize=18)
plt.ylabel('Predicted price (million Ft)')#, fontsize=18)
plt.legend()
plt.show()
