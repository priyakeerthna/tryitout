#!/usr/bin/env python
# coding: utf-8

# In[110]:


import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import csv
import re
import plotly.express as px
#import chart_studio.plotly as py
import plotly.offline as py
#import plotly.figure_factory as ff
#import plotly.graph_objects as go
#import plotly.plotly as py
#from plotly import __version__ 
#from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#from plotly.offline import init_notebook_mode, iplot
#init_notebook_mode()
#import cufflinks as cf
#init_notebook_mode(connected=True)
#cf.go_offline()


# In[111]:


invoice_data=pd.read_csv('sample.csv')
#invoice_data.reset_index(drop=True,inplace=True)


# In[112]:


invoice_data.head()


# # Data description/Understanding:

# In[113]:


invoice_data.shape


# In[114]:


invoice_data.columns


# In[115]:


invoice_data.info()


# In[116]:


invoice_data.isnull().sum()


# ### area_business attribute is always NULL and could be discarded
# ### clear_date column is of importance later, uncleared invoice in place which is of use while testing model
# 

# In[117]:


invoice_data.describe()


# In[118]:


# to summarize unique values across columns or attributes
count  = invoice_data.nunique().to_frame(name = 'Counts')
count


# In[119]:


count.dtypes


# In[120]:


fig=px.bar(count,x=count.index,y='Counts',title='Unique values across atributes',labels={'Counts':'Total unique values across attributes',
            'index':'Attributes in i/p dataset'},text=count.Counts)
fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
fig.show()


# #### Describing entire dataset either by Mean,Median or Mode is not accurate, since the dataset is a mix of Continous and Ordinal attributes
# ##### Mean of Continous attribute (total_open_amount)

# In[121]:


invoice_data['total_open_amount'].agg(['mean','std']).to_frame()


# ##### Median of Ordinal variables (business_year, invoice_id, is_Open, doc_id)

# In[122]:


invoice_data[['invoice_id','isOpen']].agg(np.median).to_frame('Values') 


# ##### Mode of categorical attributes ('business_code','buisness_year','invoice_currency','document type','cust_payment_terms') 

# In[123]:


invoice_data[['business_code','buisness_year','invoice_currency','document type','cust_payment_terms','isOpen']].agg(pd.Series.mode) 


# ##  Data cleaning/Data pre-processing:

# ### Handling NULL values 

# In[124]:


invoice_data.isnull().sum()


# ### drop area_business attribute since it's NULL for all rows

# In[125]:


invoice_data.drop(['area_business'],axis=1,inplace=True)
invoice_data.head()


# In[126]:


invoice_data.shape


# #### Date attributes like posting_date', 'document_create_date','document_create_date.1','clear_date',
# #### 'due_in_date', 'baseline_create_date' data type has to be converted as date since it's as Object or Int

# In[127]:


def string_to_date(time_s,dt):
    dt=''
    for i in range(len(time_s)+3):
        if(i<4):
            dt+=time_s[i]
        if(i==4):
            dt+='-'
        if(i==5 or i==6):
            dt+= time_s[i-1]
        if(i==7):
            dt+='-'
        if(i==8 or i==9):
            dt+=time_s[i-2]
    return dt  


# In[128]:


date_list = ['baseline_create_date','due_in_date','document_create_date.1','document_create_date']

dt = ''
invoice_data['baseline_create_date'] = pd.Series(invoice_data['baseline_create_date']).map(lambda x: string_to_date(str(x),dt))
invoice_data['due_in_date'] = pd.Series(invoice_data['due_in_date']).map(lambda x: string_to_date(str(int(x)),dt))
invoice_data['document_create_date.1'] = pd.Series(invoice_data['document_create_date.1']).map(lambda x: string_to_date(str(int(x)),dt))
invoice_data['document_create_date'] = pd.Series(invoice_data['document_create_date']).map(lambda x: string_to_date(str(int(x)),dt))
#invoice_data['clear_date'] = pd.Series(invoice_data['clear_date']).map(lambda x: string_to_date(str(int(x)),st))
#invoice_data['posting_date'] = pd.Series(invoice_data['posting_date']).map(lambda x: string_to_date(str(int(x)),st))


# In[129]:


date_list = ['baseline_create_date','due_in_date','document_create_date.1','document_create_date','posting_date','clear_date']

for col in date_list:
    invoice_data[col] = pd.to_datetime(invoice_data[col],format='%Y-%m-%d')
invoice_data.shape


# In[130]:


#invoice_data['clear_date']=pd.to_datetime(invoice_data['clear_date'],format='%Y-%m-%d %H:%M:%S')
#invoice_data['clear_date'].head()


# In[131]:


#invoice_data['posting_date']=pd.to_datetime(invoice_data['posting_date'],format='%Y-%m-%d')
#invoice_data['posting_date'].head()


# In[132]:


# Dtype of date attribues were converted to datetime64[ns] type
invoice_data.info()


# In[133]:


#convert business_year to int dtype
invoice_data['buisness_year']=invoice_data['buisness_year'].astype(int)
invoice_data['buisness_year'].head()


# In[134]:


invoice_data.info()


# In[135]:


#table = ff.create_table(invoice_data)
#py.iplot(table, filename='jupyter-table1')


# In[136]:


invoice_data.isnull().sum()
#6 null Invoice ID's


# In[137]:


#NUll values handling in invoice_id attribute
invoice_data['document type'].value_counts()


# In[138]:


invoice_data.loc[invoice_data['document type'] == 'X2']
# invoice_id is NULL where document type == 'X2', so this could be discarded further.
#Also posting_date is different from document_create _date.1


# In[139]:


#discrading rows where invoice_id is NULL
invoice_data.dropna(axis=0,subset=['invoice_id'],inplace=True)
invoice_data.reset_index(drop=True,inplace=True) # resets the index number post deletion
invoice_data.shape


# In[140]:


invoice_data


# In[141]:


invoice_data.isnull().any()  
#NULL values in Columns is completely handled now


# ###### Handling Unique data columns - (Columns with unique data values is of not much use in model designing, hence those were discarded)

# In[142]:


unique_cols =  [x for x in invoice_data.columns if invoice_data[x].nunique()==1] 
print(unique_cols)


# In[143]:


invoice_data.drop(unique_cols,axis=1,inplace=True)
invoice_data.columns


# In[144]:


invoice_data.shape


# In[145]:


invoice_data.isnull().any()


# In[146]:


invoice_data.rename(columns = {'name_customer':'customer_name'}, inplace = True)
invoice_data.columns


# ### Handling Duplicate columns - Duplicate columns has to be removed during pre processing as this redundant data is of no use during model designing

# In[147]:


#invoice_data['doc_id'].duplicated(keep= 'first') # to drop duplicate column document_create_date.1 which has same data as 
# posting_date
#invoice_data=invoice_data.T.drop_duplicates().T
#invoice_data.shape


# In[148]:


#function to find duplicate columns
def DuplicateColumns(df1):
    duplicate_columns=set()
    for x in range(df1.shape[1]):
        col1=df1.iloc[:,x]
       # print(col1)
        for y in range(x+1,df1.shape[1]):
            col2=df1.iloc[:,y]
            if col1.equals(col2):
                print(col1)
                print(col2)
                duplicate_columns.add(df1.columns.values[x])
    return list(duplicate_columns)


# In[149]:


dup_cols = DuplicateColumns(invoice_data) 
dup_cols
#posting_date and document_create_date.1 are similar


# In[150]:


invoice_data.drop(columns=['document_create_date.1','posting_date'],inplace=True)


# In[151]:


invoice_data.shape  #document_create_date.1 is dropped


# In[152]:


invoice_data.info()


# In[153]:


#invoice_data['customer_name']=invoice_data['customer_name'].apply(lambda name: for x in name if  )
#invoice_data['customer_name'] = invoice_data['customer_name'].str.extract(r"[^A-Z]*([A-Z]*)[^A-Z]*")
#invoice_data.head()
#invoice_data.shape
#invoice_data.info()
#df1.shape
#for i in range(df1.shape[1]):
#    for ele in df1[i]:
#        if bool(re.match(r'\w*[A-Z]\w*', str(ele))):
#            print(ele)


# ### Dropping not significant columns

# In[154]:


#Since doc_id and invoice_id, all are unique here, both the columns could be dropped
invoice_data.drop(columns=['invoice_id','doc_id','customer_name','isOpen'],inplace=True)


# In[155]:


print(invoice_data.columns)
invoice_data.shape


# In[156]:


invoice_data.info()


# In[157]:


invoice_data.to_csv('cleaned_data.csv',index=False)
print('Clean Data created successfully')


# In[158]:


print("Percentage of data lost after cleaning of dataset:",((50000-invoice_data.shape[0])/50000)*100 ,"%")


# In[159]:


invoice_data.value_counts(invoice_data.cust_number)


# In[ ]:




