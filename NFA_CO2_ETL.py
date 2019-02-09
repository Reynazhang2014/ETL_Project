#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import pycountry
from sqlalchemy import create_engine
import sqlalchemy
import pymysql
import numpy as np
pymysql.install_as_MySQLdb()


# ## World CO2 emissions from consumption of energy from theguardian.com

# In[2]:


co2 = pd.read_excel('World CO2 emissions from consumption of energy.xlsx',sheet_name= 'Total Carbon Dioxide Emissions')
co2.columns = co2.iloc[0,]
co2.reset_index(inplace= True)
co2 = co2.reindex(co2.index.drop(0))
co2.rename(columns = {'level_0':'rank_2009','level_1':'rank_2008','Rank, 2006':'rank_2006',
                     'ISO country code': 'iso_code'},inplace = True)
co2.columns.name = None
clean = co2.loc[~co2['iso_code'].isnull(),]


# In[3]:


# Table!! Create the ISO Code and Country List
iso_country = clean[['iso_code','Country']].drop_duplicates().reset_index(drop = True).rename(columns = {'Country':'country','index':'id'})
iso_country.head()

# remove duplicated isocode and year combinations
iso_country = iso_country.loc[~iso_country.duplicated(subset=['iso_code','country'])]

# UM map to both 'Wake Island' and U.S. Pacific Islands. After research, update UM for U.S. Pacific Islands to UM1
#iso_country[iso_country['country'] == 'U.S. Pacific Islands']['iso_code'] = 'UM1'
iso_country.loc[iso_country['country'] == 'U.S. Pacific Islands','iso_code'] = 'UM1'
#iso_country[iso_country["iso_code"] == "CN"]["country"]="chinaa"


# manually add Micronesia, Federated States of to ISO mapping table after checking with NFA dataset
iso_country = iso_country.append(pd.DataFrame([['FM','Micronesia, Federated States of'],
                                              ['NA','Namibia']],
                                columns = iso_country.columns),ignore_index = True)

iso_country[iso_country['iso_code'] == 'UM']
            


# In[4]:


rank_list = ['rank_2009','rank_2008','rank_2006','% change,  2008 to 2009','% change 2000 to 2009','Change in place, 2008 to 2009']
clean_rank_change = clean[[*rank_list,'iso_code']].set_index('iso_code')
clean_rank_change.head()
#remove the percentage changes
clean_rank_CO2 = clean_rank_change[['rank_2009','rank_2008','rank_2006']].rename(columns = lambda x : x.replace('rank_',''))

clean_rank_CO2 = clean_rank_CO2.stack().reset_index().rename(columns = {'level_1':'year',0:'rank'})

##Table!! iso_code-year-rank
clean_rank_CO2 = clean_rank_CO2[~clean_rank_CO2.duplicated(subset = ['iso_code','year'])]
clean_rank_CO2.head()


# In[5]:


##Table!! Create the Country, Year, and CO2 Emission table
clean_CO2 = clean.drop(rank_list,axis = 1)
clean_CO2 = clean_CO2.set_index('iso_code').drop('Country',axis = 1)
clean_CO2 = clean_CO2.stack().reset_index().rename(columns = {'level_1':'year',0:'co2_emission'})

# remove duplicated isocode and year combinations
clean_CO2 = clean_CO2.loc[~clean_CO2.duplicated(subset=['iso_code','year'])]


# ## National Footprint Accounts 2018 from kaggle.com

# In[6]:


NFA_df1=pd.read_csv("NFA_2018.csv")
co2 = pd.read_excel('World CO2 emissions from consumption of energy.xlsx',sheet_name= 'Total Carbon Dioxide Emissions')
print(NFA_df1.shape)
print(NFA_df1.columns)
NFA_df1.head()
NFA_df1=NFA_df1.rename(columns={'ISO alpha-3 code':'alpha_3'})


# # REYNA ADDED THIS PART TO UPDATE COUNTRY AND ISO MAPPING

# In[7]:


#find not joinable countries for NFA and CO2 datasets
merged_nfa = pd.merge(NFA_df1,iso_country,on = 'country',how = 'left')
unique_country_nfa = sorted(merged_nfa[merged_nfa.iso_code.isnull()]['country'].unique())
merged_co2 = pd.merge(NFA_df1,iso_country,on = 'country',how = 'right')
unique_country_co2 = sorted(merged_co2[merged_co2.alpha_3.isnull()]['country'].unique())

#manually create the mapping for not matching countries in NFA. Will use this mapping to update NFA country names

to_change = {'Brunei Darussalam':'Brunei',
 'Cabo Verde':'Cape Verde',
 'Congo, Democratic Republic of':'Congo, Dem Rep',
 'Czechoslovakia':'',#no longer exists
 "Côte d'Ivoire":'Cote dIvoire (IvoryCoast)',
 'Ethiopia PDR':'', #no longer exists
 'Iran, Islamic Republic of':'Iran',
 "Korea, Democratic People's Republic of":'Korea, North',
 'Korea, Republic of':'Korea, South',
 "Lao People's Democratic Republic":'Laos',
 'Libyan Arab Jamahiriya':'Libya',
 'Macedonia TFYR':'Macedonia',
 #'Micronesia, Federated States of':'', #added in map_iso_country
 'Myanmar':'Burma',
# 'Namibia', #added in map_iso_country
 'Russian Federation':'Russia',
 'Réunion':'Reunion',
 'Serbia and Montenegro':'', #no longer exists
 'South Sudan':'Sudan',
 'Sudan (former)':'', #no longer exists
 'Syrian Arab Republic':'Syria',
 'Tanzania, United Republic of':'Tanzania',
 'Timor-Leste':'Timor-Leste (East Timor)',
 'USSR':'', #Soviet Union no longer exists
 'United States of America':'United States',
 'Venezuela, Bolivarian Republic of':'Venezuela',
 'Viet Nam':'Vietnam',
 'World':'', #world is not a country
 'Yugoslav SFR':'' #no longer exists
            }

#update NFA not matching country names
NFA_df1['country'].replace(to_change,inplace = True)
NFA_df = pd.merge(NFA_df1,iso_country,on = 'country',how = 'left')
#remove not valid countries that was set '' in previously in dictionary
NFA_df = NFA_df[NFA_df['country'] != '']

#sanity check to see if there are still not matched ISO code
NFA_df[NFA_df.iso_code.isnull()]


# In[8]:


# create country/ountry_code table and clean it
countries_df=NFA_df[["alpha_3","country"]].drop_duplicates(keep="first")
print(countries_df.shape)
# find missing values in  column
print(len(countries_df["alpha_3"].unique()) == len(countries_df["country"].unique()))

drop_list=countries_df[countries_df["alpha_3"].isna()]["country"]
print(drop_list)
countries_df=countries_df[~(countries_df["country"].isin(drop_list))]


# In[9]:


countries_df


# In[10]:


#NFA_2_df=NFA_df[~(NFA_df["country"].isin(drop_list))] #delete/modify


# In[11]:


#two tables here
subregions_df=NFA_df[['iso_code','UN_subregion']].drop_duplicates(keep="first").reset_index(drop=True) 
subregions_df

map_region_subregion = NFA_df[['UN_subregion','UN_region']].drop_duplicates(keep="first").reset_index(drop=True) 


# In[61]:


population_df=NFA_df[["iso_code","year","population"]].drop_duplicates(keep="first").reset_index(drop=True)

#remove duplicated records
population_df.drop_duplicates(subset=["iso_code","year"],keep = "first",inplace = True)


# In[13]:


records_list_df=NFA_df["record"].drop_duplicates(keep="first")
records_list_df


# In[72]:


e_footprint_df=NFA_df[["iso_code","year",'record', 'crop_land', 'grazing_land', 'forest_land', 'fishing_ground',
       'built_up_land', 'carbon']].loc[NFA_df["record"].isin(["BiocapTotGHA"," EFConsTotGHA","EFExportsTotGHA","EFImportsTotGHA","EFProdTotGHA"])]

# remove duplicated primary key record
e_footprint_df.drop_duplicates(subset=["iso_code","year",'record'],keep="first",inplace = True)
e_footprint_df.head()


# ## Use pandas to load csv converted DataFrame into database

# In[51]:


url="https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area"
country_area_df=pd.read_html(url)[0]
print(country_area_df.head())
# clean the country_area_df 
columns=list(country_area_df.loc[0])
#print(columns)
columns=['Rank', 'country', 'Total_in_km2_mi2', 'Land_in_km2_mi2', 'Water_in_km2_mi2', '%water', 'Notes']
country_area_df.columns=columns
country_area_df=country_area_df.iloc[2:]
country_area_df=country_area_df.drop(columns="Rank").reset_index(drop=True).sort_values("country")
print(country_area_df.shape)
country_area_df.head()


# ## countries' land area from wikipedia page

# In[52]:


to_change1 = {
'American Samoa (United States)':'American Samoa',
 'Aruba (Netherlands)':'Aruba',
 'Bermuda (United Kingdom)':'Bermuda',
 #'Burma', #can't find
 'Cayman Islands (United Kingdom)':'Cayman Islands',
 'Republic of the Congo':'Congo', 
 #'Congo, Dem Rep', #can't find
 'Cook Islands (New Zealand)':'Cook Islands', 
 #'Cote dIvoire (IvoryCoast)',#can't find
 'Falkland Islands (United Kingdom)':'Falkland Islands (Islas Malvinas)',
 'Faroe Islands (Denmark)':'Faroe Islands',
 #'French Guiana', #can't find
 'French Polynesia (France)':'French Polynesia',
 'The Gambia':'Gambia', 
 'Gibraltar (United Kingdom)':'Gibraltar',
 'Greenland (Kingdom of Denmark)':'Greenland',
 #'Guadeloupe', #can't find
 'Guam (United States)':'Guam',
 'Hong Kong (China)':'Hong Kong',
 'North Korea':'Korea, North',
 'South Korea':'Korea, South',
 'Macau (China)':'Macau',
 #'Martinique',#can't find
 'Federated States of Micronesia':'Micronesia, Federated States of', 
 'Montserrat (United Kingdom)':'Montserrat',
 #'Netherlands Antilles',#can't find
 'New Caledonia (France)':'New Caledonia',
 'Niue (New Zealand)':'Niue',
 'State of Palestine':'Palestine', 
 'Puerto Rico (United States)':'Puerto Rico',
 #'Reunion', #can't find
 'Saint Helena, Ascension and Tristan da Cunha (United Kingdom)':'Saint Helena',
 'Saint Pierre and Miquelon (France)':'Saint Pierre and Miquelon',
 'Saint Vincent and the Grenadines':'Saint Vincent/Grenadines',
 #'Sao Tome and Principe', #can't find
 #'Swaziland', #can't find
 'East Timor':'Timor-Leste (East Timor)',
 'Turks and Caicos Islands (United Kingdom)':'Turks and Caicos Islands',
 #'U.S. Pacific Islands', #can't find
 'U.S. Virgin Islands (United States)':'Virgin Islands,  U.S.',
 'British Virgin Islands (United Kingdom)':'Virgin Islands, British'
 #'Wake Island'#can't find
}

country_area_df['country'].replace(to_change1,inplace = True)


# In[89]:


country_area_df1 = pd.merge(country_area_df,iso_country,on = 'country',how = 'inner')

country_area_df1.drop(columns = ['country'],inplace = True)
country_area_df1.rename(columns={'%water':'water_pct'},inplace = True)
country_area_df1.drop_duplicates(subset=['iso_code'],keep = 'first',inplace = True)


# ## Summarize list of dataframes

# In[90]:


df_names=[clean_rank_CO2,clean_CO2,map_region_subregion,subregions_df,population_df,country_area_df1,e_footprint_df]
table_names=["co2_emission_rank","co2_emission_amt","map_subregion_region","map_iso_subregion",
             "population","area","e_footprint"]
#remove iso_country and map_iso_country


# ## Use pandas to load csv converted DataFrame into database

# In[91]:


rds_connection_string = "root:test123@localhost/national_footprint"
engine = create_engine(f'mysql://{rds_connection_string}')


# In[95]:




for i in range(len(df_names)):
    engine.execute(f'delete from {table_names[i]}')
engine.execute(f'delete from map_iso_country')  
iso_country.to_sql(name = 'map_iso_country',if_exists = 'append', con = engine, index = False)
for i in range(len(df_names)):
    df_names[i].to_sql(name =table_names[i],if_exists = 'append', con = engine, index = False)

### Confirm data has been added by querying the customer_location table
pd.read_sql_query('select * from map_iso_subregion', con=engine).head()


# In[ ]:




