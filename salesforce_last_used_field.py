# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 09:18:50 2021

@author: Sebastian Undurraga, sebastian.undurraga@gmail.com
"""

from simple_salesforce import Salesforce
import pandas as pd
import datetime

# Connection to Salesforce
sf = Salesforce(password='password',
                username='username',
                organizationId='organizationId')


# Change the name to the object that you want to evaluate. If is a custom object remember to end it with __c
object_to_evaluate = "object"

# Get all the fields from the Object
object_fields = getattr(sf, object_to_evaluate).describe()

# Define an empty list to append the information
data = []

# Create a date variable to define from when we want to get the data
last_year = (datetime.datetime.now() + datetime.timedelta(days=-365)).strftime("%Y-%m-%d"+"T"+"%H:%M:%S"+"Z")

# Iterate over the fields and bring the last record created Date where the field wasn't empty
# If the record is not found, store it in the CSV/Excel file as not found
for field in object_fields['fields']:
    print(field['name'])
    try:
        field_detail = pd.DataFrame(
            sf.query("SELECT Id, createddate, SystemModStamp \
                      FROM {} \
                      WHERE createddate > {} \
                        AND {} != null \
                      ORDER BY Id DESC \
                      LIMIT 1".format(object_to_evaluate, last_year , field['name'])
                      )['records'])
                                      
        field_detail['Field Name'] = field['name']
        field_detail['Field Label'] = field['label']
        field_detail['Found?'] = 'Yes'
        
        field_quantity = pd.DataFrame(
            sf.query("SELECT count(Id) \
                    FROM {} \
                    WHERE createddate > {} \
                    AND {} != null".format(object_to_evaluate, last_year , field['name'])
                    ))['records'][0]['expr0']
        
        field_detail['Quantity'] = field_quantity                        
        data.append(field_detail)
        
        if field_detail.empty:
            error_data = {'Field Name': [field['name']],
                          'Field Label': [field['label']] , 
                          'Found?': ['Yes, no data']}
            data.append(pd.DataFrame(error_data))
    except:
        error_data = {'Field Name': [field['name']],
                      'Field Label': [field['label']] , 
                      'Found?': ['No']}
        data.append(pd.DataFrame(error_data))

# Concatenate the list of result into one dataframe
data_to_csv = pd.concat(data, ignore_index=True)

# Format the CSV/Excel report
data_to_csv.rename(columns={'CreatedDate': 'Created Date', 'SystemModstamp': 'Modified Date'}, inplace=True)
data_to_csv['Created Date'] = pd.to_datetime(data_to_csv['Created Date']).dt.date
data_to_csv['Modified Date'] = pd.to_datetime(data_to_csv['Modified Date']).dt.date
data_to_csv = data_to_csv.drop('attributes', axis=1)
max_value = data_to_csv['Quantity'].max()
data_to_csv['% of use'] = data_to_csv['Quantity'] / max_value

# Export the data to a CSV/Excel file
data_to_csv.to_csv('last Field Usage Date.csv')
data_to_csv.to_excel('last Field Usage Date.xlsx', float_format="%.3f")
