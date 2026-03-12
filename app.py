
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Airline Delay Analytics Dashboard")
st.write("Interactive analysis of airline delays")

df = pd.read_csv("airline_clean.csv")
#Deleting(droping) the unnamed column
#df = df.drop(columns=["Unnamed: 0"], errors="ignore")

st.subheader("Dataset Preview")
st.dataframe(df.head())


airlines = df['UniqueCarrier'].unique()

selected_airline = st.selectbox(
    "Select Airline",
    airlines
)

filtered_df = df[df['UniqueCarrier'] == selected_airline]

fig, ax = plt.subplots()

sns.histplot(filtered_df['ArrDelay'], bins=50, ax=ax)

ax.set_title("Arrival Delay Distribution")

st.pyplot(fig)

total_flights = len(df)
avg_arr_delay = df["ArrDelay"].mean()
avg_dep_delay = df["DepDelay"].mean()

col1, col2, col3 = st.columns(3)

col1.metric("Total Flights", f"{total_flights:,}")
col2.metric("Avg Arrival Delay", f"{avg_arr_delay:.2f} min")
col3.metric("Avg Departure Delay", f"{avg_dep_delay:.2f} min")

airline = st.sidebar.selectbox(
    "Select Airline",
    df["UniqueCarrier"].unique()
)

filtered_df = df[df["UniqueCarrier"] == airline]

weekly_delay = df.groupby("Week")["ArrDelay"].mean()
fig, ax = plt.subplots()
weekly_delay.plot(ax=ax, marker='o')
ax.set_title("Average Arrival Delay by Week")
ax.set_xlabel("Week Number")
ax.set_ylabel("Delay (minutes)")
st.pyplot(fig)





import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')





#df = pd.read_csv("DelayedFlights.csv")
#df.head()
print(f"\n Shape of the Dataset is : {df.shape}")





print(f"\n Info of the dataset is : {df.info()}")


# In[6]:


df.describe()


# In[7]:


print(f"\n Columns : {df.columns.to_list()}")


# In[8]:


print(f"\n Data Types : {df.dtypes}")


# In[9]:


#checking null values
df.isnull().sum()


# #Data Cleaning

# In[10]:


# Drop rows where critical columns are missing
df.dropna(subset=['Origin','Dest','Distance','DepTime','ArrTime'])

#Fill delay related null values with 0
delay_cols = ['ArrDelay','DepDelay','CarrierDelay','WeatherDelay','NASDelay','SecurityDelay','LateAircraftDelay'
               ,'TaxiIn','TaxiOut','ActualElapsedTime','AirTime']

for col in delay_cols:
  df[col] = df[col].fillna(0)

#Fill CRSElapsedTime null values with median
df['CRSElapsedTime'].fillna(df['CRSElapsedTime'].median(),inplace=True)
df['ArrTime'].fillna(df['ArrTime'].median(),inplace=True)


#fill categorical columns
df['TailNum'].fillna('Unknown',inplace=True)
df['CancellationCode'].fillna('Not Cancelled',inplace=True)


# In[11]:


#========Create New Useful Columns===========
#Delay Flag
df['Is_Delayed']= (df['ArrDelay']>15).astype(int)

#Delay Category

df['Delay_Category'] = pd.cut(df['ArrDelay'],bins=[-float('inf'),0,15,60,float('inf')],
                              labels=['Early/On Time','Minor Delay','Major Delay','Severe Delay'])

#Cancellation flag
df['Is_Cancelled'] = (df['Cancelled'] == 1).astype(int)

#total delay from all causes

df['Total_delay'] = (df['CarrierDelay']+df['LateAircraftDelay']+df['NASDelay']+df['SecurityDelay']+df['WeatherDelay'])


# Fill any remaining NaN values in CRSDepTime before calculating Dep_hour
df['CRSDepTime'].fillna(df['CRSDepTime'].median(), inplace=True)
#Extract departure hour
df['Dep_hour'] = (df['CRSDepTime'] // 100).astype(int)
df['Dep_hour']=df['Dep_hour'].clip(0,23)

#Peak Hour flag

df['Is_Peak_Hour'] = (df['Dep_hour'].isin([7,8,9,16,17,18,19])).astype(int)

#Day Type

df['Day_Type']=df['DayOfWeek'].apply(lambda x: 'Weekend' if x in [6,7] else 'WeekDay')

#Route Columns

df['Route'] = df['Origin'] + 'to(->)' + df['Dest']

#Day Name Mapping

day_names = {1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat',7:'Sun'}
df['Day_Name'] = df['DayOfWeek'].map(day_names)


# In[12]:


print(" Cleaned Shape:", df.shape)
print("\n Missing Values After Cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])

print("\n Delay Category Distribution:")
print(df['Delay_Category'].value_counts())

print(f"\n  Total Flights  : {len(df):,}")
print(f"  Delayed Flights : {df['Is_Delayed'].sum():,}")
print(f" Cancelled Flights: {df['Is_Cancelled'].sum():,}")
print(f"\n Data Cleaning Complete!")


# In[13]:


#Now we can Drop null values from our dataset as they are very minimal
df.dropna(inplace=True)
df.isnull().sum()


# #**EDA Part 1 (Delay Overview)**

# In[14]:


fig,axes=plt.subplots(2,2,figsize=(16,12))
plt.suptitle('Ailine Delay Analysis-Overview',fontsize=18,fontweight='bold',y=1.02)

#Plot1 - Delay category Distribution
delay_counts=df['Delay_Category'].value_counts()
colors= ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
axes[0,0].bar(delay_counts.index,delay_counts.values,color=colors,edgecolor='white')
axes[0,0].set_title('Flight Delay Category',fontweight='bold')
axes[0,0].set_xlabel('Delay Category')
axes[0,0].set_ylabel('Number of Flights')
for i,v in enumerate(delay_counts.values):
  axes[0,0].text(i,v+100,f'{v:,}',ha='center',fontweight='bold')

#Plot2 - Delay By day of week
day_delay = df.groupby('DayOfWeek')['ArrDelay'].mean()
day_labels= [day_names[d] for d in day_delay.index]
axes[0,1].bar(day_labels,day_delay.values,color='steelblue',edgecolor='white')
axes[0,1].set_title('Average Delay by Day of Week ',fontweight='bold')
axes[0,1].set_xlabel('Day of week')
axes[0,1].set_ylabel('Average Delay(Minutes)')
axes[0,1].axhline(y=day_delay.mean(),color='red',linestyle='--',label='Average')
axes[0,1].legend()

#Plot-3 Hourly delay Pattern
hourly_delay=df.groupby('Dep_hour')['ArrDelay'].mean()
axes[1,0].plot(hourly_delay.index,hourly_delay.values,marker='o',color='coral',linewidth=2.5)
axes[1,0].set_title('Average Delay By Dep hour',fontweight='bold')
axes[1,0].set_xlabel('Hour of day')
axes[1,0].set_ylabel('Average Delay(Minutes)')
axes[1,0].axvspan(7,9,alpha=0.2,color='red',label='Morning Peak')
axes[1,0].axvspan(16,19,alpha=0.2,color='orange',label='Evening Peak')
axes[1,0].legend()
axes[1,0].grid(True,alpha=0.3)

#Plot-4 Delay Causes Breakdown

delay_causes={'Carrie':df['CarrierDelay'].sum(),
              'NSA':df['NASDelay'].sum(),
              'Weather':df['WeatherDelay'].sum(),
              'Security':df['SecurityDelay'].sum(),
              'Late':df['LateAircraftDelay'].sum()}
cause_Series = pd.Series(delay_causes).sort_values(ascending=False)
colors=['#3498db','#e74c3c','#2ecc71','#f39c12','#9b59b6']
axes[1,1].bar(cause_Series.index,cause_Series.values,color=colors,edgecolor='white')
axes[1,1].set_title("Total Delay Minutes By Cause",fontweight='bold')
axes[1,1].set_xlabel('Delay Cause')
axes[1,1].set_ylabel('Total Delay(Minutes)')


plt.tight_layout()
st.pyplot(fig)


# #**EDA Part 2 (Airline And Route Analysis)**

# In[15]:


fig,axes=plt.subplots(2,2,figsize=(16,12))
fig.suptitle("Airline And Route Performance Analysis",fontweight='bold',fontsize=18)

#Plot 1 -Worst Airlines by Delay
airline_delay=df.groupby('UniqueCarrier')['ArrDelay'].mean()
airline_delay=airline_delay.sort_values(ascending=False)
colors=['#e74c3c' if x>airline_delay.mean() else '#2ecc71' for x in airline_delay.values]
axes[0,0].bar(airline_delay.index,airline_delay.values,color=colors,edgecolor='white')
axes[0,0].set_title('Average Delay by Airline',fontweight='bold')
axes[0,0].set_xlabel('Airlines Code')
axes[0,0].set_ylabel('Average Delay (Minutes)')
axes[0,0].axhline(y=airline_delay.mean(),color='black',linestyle='--',label='Industry Average')
axes[0,0].legend()

#Plot 2 --Weekly Delay Trend
weekly_delay = df.groupby("Week")["ArrDelay"].mean()

axes[0,1].plot(weekly_delay.index, weekly_delay.values, marker='o', linewidth=2.5, color='steelblue')
axes[0,1].set_title('Weekly Delay Trend', fontweight='bold')
axes[0,1].set_xlabel('Week Number')
axes[0,1].set_ylabel('Avg Delay (mins)')
axes[0,1].set_xticks(weekly_delay.index)
axes[0,1].grid(True, alpha=0.3)

#plot 3 -Top 10 Most Delayed Routes
route_delay=df.groupby('Route')['ArrDelay'].mean()
top_routes = route_delay.sort_values(ascending=False).head(10)
axes[1,0].barh(top_routes.index,top_routes.values,color='coral',edgecolor='white')
axes[1,0].set_title('Top 10 Most Delayed Routes',fontweight='bold')
axes[1,0].set_xlabel('Avg Delay (min)')
axes[1,0].axvline(x=0,color='black',linestyle='--')

#Plot 4 --Distance Vs Delay
sample=df.sample(5000,random_state=42)
axes[1,1].scatter(sample['Distance'],sample['ArrDelay'],alpha=0.3,color='steelblue',s=10)
axes[1,1].set_title('Distance vs Arrival Delay ',fontweight='bold')
axes[1,1].set_xlabel('Flight Distance(miles)')
axes[1,1].set_ylabel('Arrival Delay (minutes)')
axes[1,1].axhline(y=0,color='red',linestyle='--')

plt.tight_layout()
st.pyplot(fig)


# # **KEY BUSINESS INSIGHTS**




print("=" * 60)
print("      AIRLINE DELAY — KEY BUSINESS INSIGHTS")
print("=" * 60)

total = len(df)
delayed = df['Is_Delayed'].sum()
cancelled = df['Is_Cancelled'].sum()

print(f"\n OVERVIEW:")
print(f"   Total Flights Analyzed : {total:,}")
print(f"   Delayed Flights (>15m) : {delayed:,} ({delayed/total*100:.1f}%)")
print(f"   Cancelled Flights      : {cancelled:,} ({cancelled/total*100:.1f}%)")

print(f"\n  AIRLINE PERFORMANCE:")
worst = airline_delay.idxmax()
best = airline_delay.idxmin()
print(f"   Worst Airline : {worst} ({airline_delay.max():.1f} mins avg delay)")
print(f"   Best Airline  : {best} ({airline_delay.min():.1f} mins avg delay)")

print(f"\n TIME PATTERNS:")
worst_hour = hourly_delay.idxmax()
best_hour = hourly_delay.idxmin()
print(f"   Worst Departure Hour : {worst_hour}:00 ({hourly_delay.max():.1f} mins)")
print(f"   Best Departure Hour  : {best_hour}:00 ({hourly_delay.min():.1f} mins)")

print(f"\n  DELAY CAUSES:")
for cause, mins in cause_Series.items():
    pct = mins / cause_Series.sum() * 100
    print(f"   {cause:15} : {mins:>12,.0f} mins ({pct:.1f}%)")

print(f"\n TOP BUSINESS RECOMMENDATIONS:")
print(f"   1. Avoid booking flights after 3 PM —")
print(f"      evening flights have highest delay risk")
print(f"   2. {worst} airline has worst punctuality —")
print(f"      switch to {best} for time-sensitive travel")
print(f"   3. Late Aircraft is biggest delay cause —")
print(f"      better turnaround management needed")
print("=" * 60)


# #**SQL Setup**




import sqlite3

# Load dataframe into SQL database
conn = sqlite3.connect(':memory:')
df.to_sql('flights', conn, index=False, if_exists='replace')

print(" SQL Database Created Successfully!")
print(f"   Table Name : flights")
print(f"   Total Rows : {len(df):,}")

# Helper function to run SQL queries
def run_sql(query):
  return pd.read_sql_query(query,conn)


# Test connection
test = run_sql("SELECT COUNT(*) as total_flights FROM flights")
print(f"\n SQL Connection Working!")
print(test)


# **SQL Query 1 (Basic Airline Performance)**




q1= run_sql("""SELECT
        UniqueCarrier as Airline,
        COUNT(*) as Total_Flights,
        ROUND(AVG(ArrDelay), 2) as Avg_Arrival_Delay,
        ROUND(AVG(DepDelay), 2) as Avg_Departure_Delay,
        SUM(CASE WHEN Is_Delayed = 1
            THEN 1 ELSE 0 END) as Delayed_Flights,
        ROUND(AVG(CASE WHEN Is_Delayed = 1
            THEN 100.0 ELSE 0 END), 1) as Delay_Rate_Pct,
        SUM(Is_Cancelled) as Cancelled_Flights,
        MAX(ArrDelay) as Worst_Delay_Mins
    FROM flights
    GROUP BY UniqueCarrier
    ORDER BY Avg_Arrival_Delay DESC""")

print("Airline Performance Scorecard : ")
print('='*70)
print(q1.to_string(index=False))


# **SQL Query-2 Intermediate -Time Analysis**

# In[19]:


q2=run_sql("""
        SELECT
              Dep_Hour AS Departure_Hour,
              COUNT(*) AS Total_Flights,
              ROUND(AVG(ArrDelay),2) AS Average_Delay,
              SUM(CASE WHEN ArrDelay >60
                   THEN 1 ELSE 0 END) AS Severe_Delays,
              ROUND(AVG(CASE WHEN Is_Delayed =1 THEN 100.0 ELSE 0 END),1) AS Delay_rate_PCT,
              CASE
                  WHEN Dep_Hour BETWEEN 5 AND 11
                   THEN "MORNING"
                  WHEN Dep_Hour BETWEEN 12 AND 16
                   THEN "AFTERNOON"
                  WHEN Dep_Hour BETWEEN 17 AND 20
                    THEN "EVENING"
                  ELSE "NIGHT"
                END AS Time_Slot

            FROM flights
            GROUP BY Dep_Hour
            ORDER BY Average_Delay DESC
""")


print("🕐 DELAY BY DEPARTURE HOUR:")
print("="*70)
print(q2.to_string(index=False))


# **SQL Query 3**

# In[20]:


q3 = run_sql("""
    SELECT
        UniqueCarrier as Airline,
        ROUND(AVG(CarrierDelay), 2) as Avg_Carrier_Delay,
        ROUND(AVG(WeatherDelay), 2) as Avg_Weather_Delay,
        ROUND(AVG(NASDelay), 2) as Avg_NAS_Delay,
        ROUND(AVG(SecurityDelay), 2) as Avg_Security_Delay,
        ROUND(AVG(LateAircraftDelay), 2) as Avg_LateAircraft_Delay,
        ROUND(AVG(CarrierDelay) + AVG(WeatherDelay) +
              AVG(NASDelay) + AVG(SecurityDelay) +
              AVG(LateAircraftDelay), 2) as Total_Avg_Delay
    FROM flights
    WHERE CarrierDelay > 0
       OR WeatherDelay > 0
    GROUP BY UniqueCarrier
    ORDER BY Total_Avg_Delay DESC
""")

print(" DELAY CAUSES BY AIRLINE:")
print("="*70)
print(q3.to_string(index=False))


# **SQL Query 4**

# In[21]:


q4 = run_sql("""
    SELECT
        UniqueCarrier as Airline,
        Route,
        ROUND(AVG(ArrDelay), 2) as Avg_Delay,
        COUNT(*) as Flight_Count,
        ROUND(AVG(ArrDelay) OVER (
            PARTITION BY UniqueCarrier), 2) as Airline_Avg_Delay,
        RANK() OVER (
            PARTITION BY UniqueCarrier
            ORDER BY AVG(ArrDelay) DESC) as Delay_Rank,
        ROUND(AVG(ArrDelay) - AVG(ArrDelay) OVER (
            PARTITION BY UniqueCarrier), 2) as Deviation_From_Airline_Avg
    FROM flights
    GROUP BY UniqueCarrier, Route
    HAVING Flight_Count >= 10
    ORDER BY UniqueCarrier, Delay_Rank
    LIMIT 30
""")

print("ADVANCED WINDOW FUNCTION — ROUTE RANKING:")
print("="*70)
print(q4.to_string(index=False))


# **SQL Query 5**

# In[22]:


q5 = run_sql("""
    SELECT 'Total Flights' as KPI,
        CAST(COUNT(*) as TEXT) as Value
        FROM flights
    UNION ALL
    SELECT 'On Time Flights',
        CAST(SUM(CASE WHEN Is_Delayed=0
            THEN 1 ELSE 0 END) as TEXT)
        FROM flights
    UNION ALL
    SELECT 'Delayed Flights',
        CAST(SUM(Is_Delayed) as TEXT)
        FROM flights
    UNION ALL
    SELECT 'Cancelled Flights',
        CAST(SUM(Is_Cancelled) as TEXT)
        FROM flights
    UNION ALL
    SELECT 'On Time Rate %',
        CAST(ROUND(AVG(CASE WHEN Is_Delayed=0
            THEN 100.0 ELSE 0 END), 1) as TEXT)
        FROM flights
    UNION ALL
    SELECT 'Avg Arrival Delay (mins)',
        CAST(ROUND(AVG(ArrDelay), 1) as TEXT)
        FROM flights
    UNION ALL
    SELECT 'Worst Single Delay (mins)',
        CAST(MAX(ArrDelay) as TEXT)
        FROM flights
    UNION ALL
    SELECT 'Most Common Delay Cause',
        CASE
            WHEN AVG(CarrierDelay) > AVG(WeatherDelay)
             AND AVG(CarrierDelay) > AVG(NASDelay)
             AND AVG(CarrierDelay) > AVG(LateAircraftDelay)
                THEN 'Carrier Delay'
            WHEN AVG(LateAircraftDelay) > AVG(WeatherDelay)
             AND AVG(LateAircraftDelay) > AVG(NASDelay)
                THEN 'Late Aircraft'
            WHEN AVG(WeatherDelay) > AVG(NASDelay)
                THEN 'Weather'
            ELSE 'NAS (Air Traffic Control)'
        END
        FROM flights
""")

print(" COMPLETE BUSINESS KPI DASHBOARD:")
print("="*50)
print(q5.to_string(index=False))


# # **Visualization of SQL Analysis**

# In[23]:


fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('SQL Analysis — Visual Summary',
             fontsize=16, fontweight='bold')

# Plot 1 - Airline Delay Rate from SQL
axes[0].bar(q1['Airline'], q1['Delay_Rate_Pct'],
            color=['#e74c3c' if x > q1['Delay_Rate_Pct'].mean()
                   else '#2ecc71'
                   for x in q1['Delay_Rate_Pct']],
            edgecolor='white')
axes[0].set_title('Delay Rate % by Airline',
                   fontweight='bold')
axes[0].set_xlabel('Airline')
axes[0].set_ylabel('Delay Rate %')
axes[0].axhline(y=q1['Delay_Rate_Pct'].mean(),
                color='black', linestyle='--',
                label='Industry Average')
axes[0].legend()

# Plot 2 - Time Slot Delay Comparison
time_slot = q2.groupby('Time_Slot')['Average_Delay'].mean()
colors_slot = ['#3498db','#e74c3c','#f39c12','#2ecc71']
axes[1].bar(time_slot.index, time_slot.values,
            color=colors_slot, edgecolor='white')
axes[1].set_title('Average Delay by Time Slot',
                   fontweight='bold')
axes[1].set_xlabel('Time of Day')
axes[1].set_ylabel('Avg Delay (mins)')

plt.tight_layout()
st.pyplot(fig)
print("\nSQL Analysis Complete!")


# In[24]:


df.columns


# #**Building ML Model**

# In[25]:


from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.metrics import classification_report,confusion_matrix,roc_auc_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

#Create a copy of df
df_ml=df.copy()

#Encode categorical Column
le=LabelEncoder()
cat_cols=['UniqueCarrier','Dest','Origin','Day_Type']
for col in cat_cols:
  df_ml[col] = le.fit_transform(df_ml[col].astype(str))

#Define Features

features = [
    'Month','DayOfWeek','Dep_hour',
    'Is_Peak_Hour', 'Distance','UniqueCarrier',
    'Origin', 'Dest','Day_Type',
    'CRSElapsedTime','TaxiOut'
]

X=df_ml[features]
y=df_ml['Is_Delayed']

#Train Test Split

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)

print("Features Ready")
print(f"Training Samples : {len(X_train)}")
print(f"Testing samples : {len(X_test)}")
print(f" Features Used : {len(features)}")
print(f"\n Features : {features}")
print(f"\n Delayed Flights : {y.sum():,}({y.mean()*100:.1f}%)")
print(f" On Time flights : {(y==0).sum():,}({(y==0).mean()*100:.1f}%)")


# **Train And Compare Models**

# In[26]:


#Train Both Models
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100,random_state=42,n_jobs=-1),
    'Gradient Boosting':GradientBoostingClassifier(n_estimators=100,random_state=42)
}

results={}

print("Training Models...")
print("="*50)

for name,model in models.items():
  print(f"\n Training {name}...")
  model.fit(X_train,y_train)
  y_pred = model.predict(X_test)
  y_prob = model.predict_proba(X_test)[:,1]
  accuracy = (y_pred==y_test).mean()*100
  roc_score = roc_auc_score(y_test,y_prob)*100

  results[name] = {
      'accuracy':accuracy,
      'roc_score':roc_score,
      'Predictions':y_pred
  }


  print(f"\n{'='*40}")
  print(f"  {name} Results:")
  print(f"{'='*40}")
  print(f"  Accuracy  : {accuracy:.1f}%")
  print(f"  ROC AUC   : {roc_score:.1f}%")
  print(f"\n{classification_report(y_test, y_pred)}")

#pick the best Model

best_model_name=max(results,key=lambda x:results[x]['accuracy'])
best_model = models[best_model_name]
print(f"\n Best Model :{best_model_name}")
print(f"Accuracy : {results[best_model_name]['accuracy']:.1f}%")


# **Confusion Matrix**

# In[27]:


fig,axes=plt.subplots(1,2,figsize=(14,5))
fig.suptitle("Model Performance - Confusion Matrix",fontsize=16,fontweight='bold')

for idx,(name,result) in enumerate(results.items()):
  cm = confusion_matrix(y_test,result['Predictions'])
  sns.heatmap(cm,annot=True,fmt='d',cmap='Blues',
              xticklabels=['On Time','Delayed'],
              yticklabels=['On Time','Delayed'],
              ax=axes[idx])
  axes[idx].set_title(f"{name}\nAccuracy:{result['accuracy']:.1f}%",fontweight='bold')
  axes[idx].set_ylabel('Actual')
  axes[idx].set_xlabel("Predicted")

plt.tight_layout()
st.pyplot(fig)


# **Feature Importance**

# In[28]:


plt.figure(figsize=(10, 6))

importance = pd.Series(
    best_model.feature_importances_,
    index=features
).sort_values(ascending=True)

colors = ['#e74c3c' if x >= importance.nlargest(3).min()
          else '#3498db'
          for x in importance.values]

importance.plot(kind='barh', color=colors)
plt.title(f'What Causes Flight Delays?\n'
          f'Feature Importance — {best_model_name}',
          fontsize=14, fontweight='bold')
plt.xlabel('Importance Score')
plt.axvline(x=importance.mean(), color='black',
            linestyle='--', label='Average Importance')
plt.legend()
plt.tight_layout()
st.pyplot(fig)

print("\n TOP FACTORS CAUSING DELAYS:")
print("="*45)
for feat, imp in importance.sort_values(
        ascending=False).items():
    bar = '*' * int(imp * 200)
    print(f"  {feat:20} : {imp:.4f} {bar}")


# #**Sales Forecasting**

# In[29]:


# Check what years are in dataset first
print("Years in dataset:", df['Year'].unique())
print("Months in dataset:", sorted(df['Month'].unique()))
print("Total rows:", len(df))

# Prepare data differently
df['Date'] = pd.to_datetime(
    df['Year'].astype(str) + '-' +
    df['Month'].astype(str) + '-01'
)

# Group by date
monthly = df.groupby('Date').agg(
    y=('ArrDelay', 'mean')
).reset_index()
monthly.columns = ['ds', 'y']

# Remove any NaN rows
monthly = monthly.dropna()
monthly = monthly.sort_values('ds').reset_index(drop=True)

print("\nMonthly Data prepared:")
print(monthly)
print(f"\nTotal months available: {len(monthly)}")


# In[30]:


from sklearn.linear_model import LinearRegression
import numpy as np

# Create weekly aggregation
df['Week'] = df['DayofMonth'].apply(
    lambda x: 1 if x<=7 else 2 if x<=14
    else 3 if x<=21 else 4)

weekly = df.groupby('Week').agg(
    Avg_Delay=('ArrDelay', 'mean'),
    Total_Flights=('FlightNum', 'count'),
    Delayed_Flights=('Is_Delayed', 'sum')
).reset_index()

weekly['Delay_Rate'] = (
    weekly['Delayed_Flights'] /
    weekly['Total_Flights'] * 100
).round(2)

print("Weekly Summary:")
print(weekly)

# Simple Linear Regression Forecast
X_week = weekly['Week'].values.reshape(-1,1)
y_week = weekly['Avg_Delay'].values

model_lr = LinearRegression()
model_lr.fit(X_week, y_week)

# Predict next 4 weeks
future_weeks = np.array([5,6,7,8]).reshape(-1,1)
predictions = model_lr.predict(future_weeks)

# Plot
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Flight Delay Forecast Analysis',
             fontsize=16, fontweight='bold')

# Plot 1 - Weekly trend + forecast
all_weeks = np.append(weekly['Week'].values, [5,6,7,8])
all_delays = np.append(weekly['Avg_Delay'].values,
                        predictions)
colors = (['#3498db'] * len(weekly)) + (['#e74c3c'] * 4)

axes[0].bar(all_weeks, all_delays, color=colors,
            edgecolor='white', width=0.6)
axes[0].axvline(x=4.5, color='black',
                linestyle='--', linewidth=2,
                label='Forecast Starts')
axes[0].set_title('Weekly Delay Trend + 4 Week Forecast',
                   fontweight='bold')
axes[0].set_xlabel('Week Number')
axes[0].set_ylabel('Average Delay (mins)')
axes[0].legend(['Forecast Start', 'Actual', 'Predicted'])
axes[0].set_xticks(range(1,9))
axes[0].set_xticklabels([f'Week {i}' for i in range(1,9)],
                         rotation=45)

# Add value labels on bars
for i, v in enumerate(all_delays):
    axes[0].text(all_weeks[i], v + 0.3,
                f'{v:.1f}', ha='center',
                fontsize=9, fontweight='bold')

# Plot 2 - Daily delay pattern
daily = df.groupby('DayofMonth').agg(
    Avg_Delay=('ArrDelay', 'mean'),
    Total_Flights=('FlightNum', 'count')
).reset_index()

axes[1].plot(daily['DayofMonth'],
             daily['Avg_Delay'],
             marker='o', color='coral',
             linewidth=2.5, markersize=6)
axes[1].fill_between(daily['DayofMonth'],
                      daily['Avg_Delay'],
                      alpha=0.3, color='coral')
axes[1].set_title('Daily Delay Pattern — January 2008',
                   fontweight='bold')
axes[1].set_xlabel('Day of Month')
axes[1].set_ylabel('Average Delay (mins)')
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=daily['Avg_Delay'].mean(),
                color='blue', linestyle='--',
                label=f'Monthly Avg: {daily["Avg_Delay"].mean():.1f} mins')
axes[1].legend()

plt.tight_layout()
st.pyplot(fig)

# Print forecast summary
print("\n" + "="*50)
print("   DELAY FORECAST SUMMARY")
print("="*50)
print("\nActual Weekly Delays:")
for _, row in weekly.iterrows():
    print(f"  Week {int(row['Week'])}: "
          f"{row['Avg_Delay']:.1f} mins avg delay "
          f"({row['Delay_Rate']}% delayed)")

print("\nForecasted Weekly Delays:")
for week, pred in zip([5,6,7,8], predictions):
    print(f"  Week {week}: {pred:.1f} mins avg delay (predicted)")

trend = "INCREASING " if predictions[-1] > predictions[0] \
        else "DECREASING "
print(f"\nDelay Trend: {trend}")
print("="*50)


# **Imp Note - Why we choose linear Regression for forecasting instead of Prophet ?**
# 
# The dataset contained only one month of data
# which was insufficient for Prophet's seasonal
# forecasting. I adapted my approach and used
# weekly aggregation with Linear Regression to
# still demonstrate forecasting capability within
# the available data constraints.

# #**ML Models Summary**

# In[31]:


print("="*60)
print('ML Model - complete Summary')
print("="*60)

for name,result in results.items():
  print(f"\n {name} : ")
  print(f"\n Accuracy : {result['accuracy']:.1f}%")
  print(f"  ROC AUC   : {result['roc_score']:.1f}%")

print(f"\n Best Model : {best_model_name}")
print(f"\n Top 3 Delay Factors:")

top3 = importance.sort_values(ascending=False).head(3)
for i,(feat,imp) in enumerate(top3.items(),1):
  print(f"{i} .{feat} ({imp:.4f})")

print(f"""
       KEY ML INSIGHTS:
       1.{top3.index[0]} is the strongest Predictor of flight delays

       2. Peak hour Flights significantly more likely to be delayed

       3.Gradient Boosting Vs Random Forest shows
         {abs(results['Gradient Boosting']['accuracy']-results['Random Forest']['accuracy']):.1f}% accuracy difference

       4. weekly Forecast shows delay trend is
          {'increasing' if predictions[-1]>predictions[0] else 'Decreasing'} over coming Weeks


       5. Model predicts delays BEFORE flight departs — saving passengers time and airlines money


""")


print('='*60)
print("ML Model Summary completed")


# **Exporting clean data from colab to local computer**

# In[32]:


# Export all files needed for Power BI
# Main cleaned dataset
"""df.to_csv('airline_clean.csv', index=False)

# Weekly summary for forecast chart
weekly_summary = df.groupby('Week').agg(
    Total_Flights=('FlightNum', 'count'),
    Avg_Delay=('ArrDelay', 'mean'),
    Delayed_Flights=('Is_Delayed', 'sum'),
    Cancelled_Flights=('Is_Cancelled', 'sum'),
    Avg_Distance=('Distance', 'mean')
).reset_index()
weekly_summary['Delay_Rate'] = (
    weekly_summary['Delayed_Flights'] /
    weekly_summary['Total_Flights'] * 100
).round(2)
weekly_summary.to_csv('weekly_summary.csv', index=False)

# Airline performance summary
airline_summary = df.groupby('UniqueCarrier').agg(
    Total_Flights=('FlightNum', 'count'),
    Avg_Delay=('ArrDelay', 'mean'),
    Delayed_Flights=('Is_Delayed', 'sum'),
    Cancelled_Flights=('Is_Cancelled', 'sum'),
    Carrier_Delay=('CarrierDelay', 'mean'),
    Weather_Delay=('WeatherDelay', 'mean'),
    NAS_Delay=('NASDelay', 'mean'),
    LateAircraft_Delay=('LateAircraftDelay', 'mean')
).reset_index()
airline_summary['Delay_Rate'] = (
    airline_summary['Delayed_Flights'] /
    airline_summary['Total_Flights'] * 100
).round(2)
airline_summary['On_Time_Rate'] = (
    100 - airline_summary['Delay_Rate']
).round(2)
airline_summary.to_csv('airline_summary.csv', index=False)

# Route performance
route_summary = df.groupby(['Origin','Dest','Route']).agg(
    Total_Flights=('FlightNum', 'count'),
    Avg_Delay=('ArrDelay', 'mean'),
    Avg_Distance=('Distance', 'mean')
).reset_index()
route_summary = route_summary[
    route_summary['Total_Flights'] >= 10
].sort_values('Avg_Delay', ascending=False)
route_summary.to_csv('route_summary.csv', index=False)

# Hourly summary
hourly_summary = df.groupby('Dep_hour').agg(
    Total_Flights=('FlightNum', 'count'),
    Avg_Delay=('ArrDelay', 'mean'),
    Delay_Rate=('Is_Delayed', 'mean')
).reset_index()
hourly_summary['Delay_Rate'] = (
    hourly_summary['Delay_Rate'] * 100
).round(2)
hourly_summary.to_csv('hourly_summary.csv', index=False)

# Download all files
from google.colab import files
files.download('airline_clean.csv')
files.download('weekly_summary.csv')
files.download('airline_summary.csv')
files.download('route_summary.csv')
files.download('hourly_summary.csv')"""

print(" All 5 files downloaded!")
print("""
Files Ready:
1. airline_clean.csv      → Main dataset
2. weekly_summary.csv     → Forecast page
3. airline_summary.csv    → Airline analysis
4. route_summary.csv      → Route analysis
5. hourly_summary.csv     → Time analysis
""")


# In[33]:


total = len(df)
delayed = df['Is_Delayed'].sum()
cancelled = df['Is_Cancelled'].sum()
ontime = total - delayed

print("="*50)
print("   YOUR PAGE 5 NUMBERS")
print("="*50)
print(f"\nTotal Flights    : {total:,}")
print(f"\nDelayed Flights  : {delayed:,} "
      f"({delayed/total*100:.1f}%)")
print(f"\nCancelled Flights: {cancelled:,} "
      f"({cancelled/total*100:.1f}%)")
print(f"\nOn Time Flights  : {ontime:,} "
      f"({ontime/total*100:.1f}%)")

print("\n" + "="*50)
print("   AIRLINE PERFORMANCE")
print("="*50)
airline = df.groupby('UniqueCarrier').agg(
    Total=('FlightNum','count'),
    Delayed=('Is_Delayed','sum')
).reset_index()
airline['On_Time_Rate'] = (
    (airline['Total'] - airline['Delayed']) /
    airline['Total'] * 100
).round(1)
airline['Delay_Rate'] = (
    airline['Delayed'] /
    airline['Total'] * 100
).round(1)
airline = airline.sort_values(
    'On_Time_Rate', ascending=False)

print(f"\n🏆 Best Airline : "
      f"{airline.iloc[0]['UniqueCarrier']} "
      f"({airline.iloc[0]['On_Time_Rate']}% on time)")
print(f"⚠️  Worst Airline: "
      f"{airline.iloc[-1]['UniqueCarrier']} "
      f"({airline.iloc[-1]['Delay_Rate']}% delayed)")

print("\n" + "="*50)
print("   DELAY CAUSES")
print("="*50)
causes = {
    'Late Aircraft': df['LateAircraftDelay'].sum(),
    'Carrier'      : df['CarrierDelay'].sum(),
    'NAS/ATC'      : df['NASDelay'].sum(),
    'Weather'      : df['WeatherDelay'].sum(),
    'Security'     : df['SecurityDelay'].sum()
}
total_cause = sum(causes.values())
for cause, mins in sorted(causes.items(),
    key=lambda x: x[1], reverse=True):
    print(f"  {cause:15}: "
          f"{mins/total_cause*100:.1f}%")

print("\n" + "="*50)
print("   TIME PATTERNS")
print("="*50)
hourly = df.groupby('Dep_hour')['ArrDelay'].mean()
print(f"\n  Worst Hour: {hourly.idxmax()}:00 "
      f"({hourly.max():.1f} mins avg delay)")
print(f"  Best Hour : {hourly.idxmin()}:00 "
      f"({hourly.min():.1f} mins avg delay)")

day_map = {1:'Monday', 2:'Tuesday', 3:'Wednesday',
           4:'Thursday', 5:'Friday',
           6:'Saturday', 7:'Sunday'}
daily = df.groupby('DayOfWeek')['ArrDelay'].mean()
print(f"\n  Worst Day : {day_map[daily.idxmax()]} "
      f"({daily.max():.1f} mins)")
print(f"  Best Day  : {day_map[daily.idxmin()]} "
      f"({daily.min():.1f} mins)")
print("="*50)









