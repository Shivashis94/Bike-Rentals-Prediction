#!/usr/bin/env python
# coding: utf-8

# ## Data Set Information

# Bike sharing systems are new generation of traditional bike rentals where whole process from membership, rental and return back has become automatic. Through these systems, user is able to easily rent a bike from a particular position and return back at another position. Currently, there are about over 500 bike-sharing programs around the world which is composed of over 500 thousands bicycles. Today, there exists great interest in these systems due to their important role in traffic, environmental and health issues.
# 
# Apart from interesting real world applications of bike sharing systems, the characteristics of data being generated by these systems make them attractive for the research. Opposed to other transport services such as bus or subway, the duration of travel, departure and arrival position is explicitly recorded in these systems. This feature turns bike sharing system into a virtual sensor network that can be used for sensing mobility in the city. Hence, it is expected that most of important events in the city could be detected via monitoring these data. 
# 
# 

# ### Problem Statement: Predicting total Number of Bike rentals per hour.

# ## Attribute Information:

# Both hour.csv and day.csv have the following fields, except hr which is not available in day.csv
# 
# 1.instant: record index
# 
# 2.dteday : date
# 
# 3.season : season (1:winter, 2:spring, 3:summer, 4:fall)
# 
# 4.yr : year (0: 2011, 1:2012)
# 
# 5.mnth : month ( 1 to 12)
# 
# 6.hr : hour (0 to 23)
# 
# 7.holiday : weather day is holiday or not
# 
# 8.weekday : day of the week
# 
# 9.workingday : if day is neither weekend nor holiday is 1, otherwise is 0.
# 
# 10.weathersit:
#  *1: Clear, Few clouds, Partly cloudy, Partly cloudy
#  *2: Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist
#  *3: Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds
#  *4: Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog
#  
# 11.temp : Normalized temperature in Celsius. The values are derived via (t-t_min)/(t_max-t_min), t_min=-8, t_max=*+39 (only in hourly scale)
# 
# 12.atemp: Normalized feeling temperature in Celsius. The values are derived via (t-t_min)/(t_max-t_min), t_min=-16, *t_max=+50 (only in hourly scale)
# 
# 13.hum: Normalized humidity. The values are divided to 100 (max)
# 
# 14.windspeed: Normalized wind speed. The values are divided to 67 (max)
# 
# 15.casual: count of casual users
# 
# 16.registered: count of registered users
# 
# 17.cnt: count of total rental bikes including both casual and registered
# 
# 

# ### 1. Data Import and Data manupulation

# ### Import Libraries

# In[141]:


import os
import numpy as np
import statistics as stat
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sn

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from scipy import stats
from numpy import median
from statsmodels.graphics.gofplots import qqplot

from sklearn import model_selection
from sklearn.metrics import mean_squared_log_error, r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, HuberRegressor, ElasticNetCV
from sklearn.ensemble import BaggingRegressor, ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor,AdaBoostRegressor


# In[132]:


os.getcwd()


# ### 2. Reading Datasets

# In[3]:


os.chdir("E:\\JupyterCodes\\Bike-Sharing-Dataset")


# In[5]:


df_daily = pd.read_csv("day.csv")
df_daily.head()


# In[6]:


df_hourly = pd.read_csv("hour.csv")
df_hourly.head()


# ##### We use the columns attribute of "df_hourly" and see it has the same columns as df_daily plus the hour of the day ('hr')
# 

# In[7]:


df_hourly.columns


# ### 3. Data Discovery ( Descriptive Statistics )

# ### Finiding Missing values 

# In[8]:


df_daily.isnull().sum()


# In[9]:


df_hourly.isnull().sum()


# In[10]:


# Changing column name for a nice precise reading

df_hourly.rename(columns={'weathersit':'weather',
                     'mnth':'month',
                     'hr':'hour',
                     'yr':'year',
                     'hum': 'humidity',
                     'cnt':'count'},inplace=True)
df_hourly.head()


# In[11]:


# Checking data type for each column

df_daily.dtypes


# In[12]:


# Checking data type for each column

df_hourly.dtypes


# In[13]:


# Some of the columns need to be deleted because they are ambiguous and they  carry no-importance to the analysis

df_hourly = df_hourly.drop(['instant','dteday'], axis=1)

# Some data types need to be changed from numerical to categorical. Otherwise the prediction model can interpret wrongly

df_hourly['year'] = df_hourly.year.astype('category')
df_hourly['season'] = df_hourly.season.astype('category')
df_hourly['month'] = df_hourly.month.astype('category')
df_hourly['hour'] = df_hourly.hour.astype('category')
df_hourly['holiday'] = df_hourly.holiday.astype('category')
df_hourly['weekday'] = df_hourly.weekday.astype('category')
df_hourly['workingday'] = df_hourly.workingday.astype('category')
df_hourly['weather'] = df_hourly.weather.astype('category')


# ### 4. Exploratory Data Analysis through Visualization

# In[129]:


# Analyzing the change in bike sharing pattern('count' variable in dataset) with categorical variables

fig,[ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8] = plt.subplots(nrows=8, figsize=(15,25))
sn.barplot(x = df_hourly['weekday'], y = df_hourly['count'],ax = ax1)
sn.barplot(x = df_hourly['season'], y = df_hourly['count'],ax = ax2)
sn.barplot(x = df_hourly['month'], y = df_hourly['count'],ax = ax3)
sn.barplot(x = df_hourly['holiday'], y = df_hourly['count'],ax = ax4)
sn.barplot(x = df_hourly['hour'], y = df_hourly['count'],ax = ax5)
sn.barplot(x = df_hourly['weather'], y = df_hourly['count'],ax = ax6)
sn.barplot(x = df_hourly['workingday'], y = df_hourly['count'],ax = ax7)
sn.barplot(x = df_hourly['year'], y = df_hourly['count'],ax = ax8)


# #### It clearly shows that each of the above categorical variable has impacts on 'count' variable 

#  NOTE: It is clearly evident that, if we take count on hourly basis, at 8am which is preferably time for working people
#  commute from home to office that is why the frequency is more on barplot and also at 5pm , assuming working people and
#  businessman return timming. 

# #### Total bike users(count) is sum of registered and casual users. Need to analyze how they vary individually with hour.
# 
# #### The variation is observed in different circumstances to check how those impact the bike users.
# 
# 

# In[24]:


fig,axes = plt.subplots(nrows = 3,ncols = 3, figsize=(25,30))

sn.pointplot(x = 'hour', y = 'registered', hue = 'month',data  = df_hourly,ax = axes[0][0])
sn.pointplot(x = 'hour', y = 'casual', hue = 'month', data  = df_hourly,ax = axes[0][1])
sn.pointplot(x = 'hour', y = 'count', hue = 'month', size = 7, data   = df_hourly,ax = axes[0][2])

sn.pointplot(x = 'hour', y = 'registered', hue = 'season',data   = df_hourly,ax = axes[1][0])
sn.pointplot(x = 'hour', y = 'casual', hue = 'season', data   = df_hourly,ax = axes[1][1])
sn.pointplot(x = 'hour', y = 'count', hue = 'season', size = 7, data  = df_hourly,ax = axes[1][2])

sn.pointplot(x = 'hour', y = 'registered', hue = 'weather',data   = df_hourly,ax = axes[2][0])
sn.pointplot(x = 'hour', y = 'casual', hue = 'weather', data  = df_hourly,ax = axes[2][1])
sn.pointplot(x = 'hour', y = 'count', hue = 'weather', size = 7, data = df_hourly,ax = axes[2][2])


# In[20]:


# To see how variables are connected with each other, data correlation can be checked 

df_hourly_corr = df_hourly[['temp', 'atemp', 'casual', 'registered', 'humidity', 'windspeed', 'count']].corr()
mask = np.array(df_hourly_corr)
mask[np.tril_indices_from(mask)] = False
fig = plt.subplots(figsize=(15,10))
sn.heatmap(df_hourly_corr, mask=mask, vmax=1, square=True, annot=True,cmap="YlGnBu")


# #### 1. It is evident that temp and atemp variables are highly correlated
# #### 2.Temp has positive correlation and humidity has negative correlation with 'count'
# #### 3. Again it can be observed that windspeed has little correlation with count

# ### 5. Finding the Outliers

# In[23]:


# Checking the outliers with boxplot

fig, axes = plt.subplots(nrows=2,ncols=2,figsize=(17,15))
plt.rc('xtick', labelsize=10) 
plt.rc('ytick', labelsize=10) 

sn.boxplot(data=df_hourly,y="count",ax=axes[0][0])
sn.boxplot(data=df_hourly,y="count",x="season",hue = "workingday",ax=axes[0][1])
sn.boxplot(data=df_hourly,y="count",x="month",hue = "workingday",ax=axes[1][0])
sn.boxplot(data=df_hourly,y="count",x="hour",ax=axes[1][1])


# ### 6. Dropping irrelavant coloumns

# In[26]:


# 'count' variable is the decomposition of 'casual' and 'registered variable'. These 2 variables can be deleted
# 'atemp' and 'temp' variables are similar almost. Can get rid of these
# 'windspeed' has not much correlation with 'count'. Can skip it too

df_hourly = df_hourly.drop(['atemp', 'casual', 'registered', 'windspeed'], axis=1)


# ### 7. Dummification

# In[27]:


# Numbers in the categorical variable are non-binary which can impact wrongly the prediction model
# One hot encoding is used to convert those variables in binary by creating dummy data
# To avoid multicolinearity, the first variable in the dummydata is dropped

data_dummy = df_hourly

def dummify_dataset(dataframe, col):
    dummy_column = pd.get_dummies(dataframe[col], prefix = col, drop_first = True)
    new_data = pd.concat([dataframe,dummy_column],axis = 1)
    new_data = new_data.drop([col], axis=1)
    return new_data

dcol = ['season', 'month', 'hour', 'holiday', 'weekday', 'workingday', 'weather','year']

for i in range(0,8):
    data_dummy = dummify_dataset(data_dummy,dcol[i])


# ### 8. Train- Test Spilt

# In[115]:


# Training and test data is created by splitting the main data. 33% of test data is considered

y = data_dummy['count']
X = data_dummy.drop(['count'], axis=1)

X_train, X_test, y_train, y_test = train_test_split(X,y,
                                                   test_size=0.33,
                                                   random_state=42)


# ### 9. Building Machine Learning model

# In[29]:


# Comparing performance of the regression models

models = [LinearRegression(),
          AdaBoostRegressor(),
          Ridge(),
          HuberRegressor(),
          ElasticNetCV(),
          DecisionTreeRegressor(), 
          ExtraTreesRegressor(),
          GradientBoostingRegressor(),
          RandomForestRegressor(),
          BaggingRegressor()]


# ### 10.  Error Metrics

# In[142]:


# A function is wrtten to find out the cross validation score based on mean absolute error

def test_algorithms(model):
    kfold = model_selection.KFold(n_splits=10, random_state=0)
    mean_dev_scores = model_selection.cross_val_score(model, X_train, y_train, cv=kfold, scoring='neg_mean_absolute_error')
    r2_scores = model_selection.cross_val_score(model, X_train, y_train, cv=kfold, scoring='r2')
    Scores= pd.DataFrame({'Mean deviation':[np.mean(mean_dev_scores)],'R Square':[np.mean(r2_scores)]})
    print(Scores)
    
for model in models:
    test_algorithms(model)


# In[31]:


# It is evident that the ExtraTreeRegressor() has the lowest error rating
# To find out the best parameters from a list, a function 'GridSearchCV' from Scikit library is used 

parameters={'n_estimators': (50,100,500),
        'max_features': (20,40,50),
        'min_samples_leaf': (1,5,10),
        'min_samples_split': (5,10,20)}

clf = GridSearchCV(ExtraTreesRegressor(), parameters,scoring = 'r2')
clf.fit(X_train,y_train)

print(clf.best_score_)
print(clf.best_params_)
print(clf.best_estimator_)


# ### 11. Performance of the prediction model

# In[140]:


# 'count' variables for test data is predicted with the chosen model and parameters

clf = ExtraTreesRegressor(max_features= 40, min_samples_leaf= 1, min_samples_split= 5, n_estimators= 500)
clf.fit(X_train,y_train)
y_pred = clf.predict(X_test)


# In[143]:


print(y_pred)


# In[32]:


# A regression plot can be drawn between actual and predicted data to understand the performance of the model
# Bins are used to make the pattern more meaningful

ax = sn.regplot(y_test,y_pred,x_bins = 200)
ax.set(title = "Comparison between the actual vs prediction")


# In[33]:


# Another regression plot to understand the error residuals from actual test data

y_res = y_test - y_pred
ax = sn.regplot(y_test,y_res)
ax.set(title = "Comparison between the actual vs residual")


# In[ ]:


#From the plot it is visible that the deviations from actual test data are not very high and restricted in a limit. 
#It is another proof for the preciseness of the prediction model


# ### 12. Conclusion :

# #### Before I conclude, we have to be aware that we haven't tested our hypothesis. We have just theories no facts and we were just looking at two years.
# 
# We found out that registered and casual users behaved differently, so it's likely that they are to completely different groups. It's probable that the registered users use the bike mainly for transportation (e.g. go to work) and the casual users use it for leisure (making tours or sightseeing).This theory would explain a lot we had observed. As we have seen that the increasing trend is mostly caused by the registered user? Our new theory could explain that. The registered users need time to increasing, since they must change their habits. 

# ### 13. Suggestion:

# They first have to register, then perhaps sell their car or own bike. It could also be that they have monthly or yearly tickets for public transportation and just want to wait till those expire. Make a long story short the casual users can be more spontaneous. Tourists planning to go to Washington Monument or lovers wanting to cycle through Rock Creek Park just take a bike and start their trip. We can also assume that spontaneous trips are made on holidays or during vacation so the weather has a greater impact on their behaviour. During a hurricane, your partner really must be Right, when you go cycling in the park (please have a look on the casual column at 2012-10-29 an congratulate them💕), also think of day tourists here, they come perhaps for a weekend and decide what they want to do, depending on the weather. On the other side the poor registered users have to go to work no matter if it's raining or not. We also wondered why the impact of the weather on weekends is less than on holidays. An explanation could be that the registered users, also have fixed dates on the weekend (sports, brunch, church etc.). Hence, we need more data to do forecasting 
