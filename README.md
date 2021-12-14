# Understanding the field usage of any object in Salesforce

One of the biggest problems that I have addressed while working with Salesforce is to understand and evaluate the field usage of a custom object. This application does the work for you, generating a CSV/Excel file with the date of the last record that used each field, and the percentage of use across all of them.
<br />
<br />
>To make this app work, you will need a System Administrator credential to log into Salesforce <br />
>This app is currently working with the Spyder IDE, which is part of Anaconda
<br />

**Let's understand how it works!**

## Dependencies
First, we need our dependencies. We will use Pandas, datetime and [Simple Salesforce](https://github.com/simple-salesforce/simple-salesforce.git)

    from simple_salesforce import Salesforce
    import pandas as pd
    import datetime

## Credentials
Next, we are going to connect to Salesforce with Simple Salesforce

      sf = Salesforce(password='password',
                username='username',
                organizationId='organizationId')
                 
Your `organizationId` should look like this, *00JH0000000tYml*. <br />
To find it, just follow the next steps (Lightning experience):
* Log into Salesforce with your System Administrator credentials
* Press the gear button
* Press Setup, *(setup for current app)*
* In the quick search bar (the one in the left) type *Company Information*
* Click *Company Information*
* Finally, look for `Salesforce.com Organization ID.` The ID will look like *00JH0000000tYml*

## The Object
Now you will need to plug the object name. The object name is the *API Name* of the object. Normally, if it is a custom object, it will finish like this, __c <br />
To find the *API NAME* just follow these instructions:
* Log into Salesforce with your System Administrator credentials
* Press the gear button
* Press Setup, *(setup for current app)*
* Click on *Object Manager* in the header of the page
* Find your object using the name and copy the *API NAME* which is next to the name of the object
<br />
This part of the code if going to use the name of the object to bring all the fields

      object_to_evaluate = "object"
      object_fields = getattr(sf, object_to_evaluate).describe()

## The Date
This part is important and will make you think. The default code is going to bring the data from the last year. Is important to understand what happened during that period. If you release a new field a week ago, it will show that it was use a couple of days ago, but the usage will be really low, around a 2% *(7/365).* You can change the days to evaluate simple change the `365` for the number of days that you want.

    last_year = (datetime.datetime.now() + datetime.timedelta(days=-365)).strftime("%Y-%m-%d"+"T"+"%H:%M:%S"+"Z")

## The Result
Now we are going to iterate all the fields and get the created date from the last record that used the field, and the number of records that use that field during the period (one year).

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

## Some Formatting
Formatting is a nice to have to understand the result, especially if you are going to share the insights. We are going to rename some columns, format the dates column in a way that CSV/Excel can understand, and we are adding a `% of use column`.

    data_to_csv.rename(columns={'CreatedDate': 'Created Date', 'SystemModstamp': 'Modified Date'}, inplace=True)
    data_to_csv['Created Date'] = pd.to_datetime(data_to_csv['Created Date']).dt.date
    data_to_csv['Modified Date'] = pd.to_datetime(data_to_csv['Modified Date']).dt.date
    data_to_csv = data_to_csv.drop('attributes', axis=1)
    max_value = data_to_csv['Quantity'].max()
    data_to_csv['% of use'] = data_to_csv['Quantity'] / max_value

### The Files
Finally, we are going to export the files to CSV and Excel, so you can choose which one you prefer to use. The files will be stored in the same folder as the app. So, if you are running this app in your Desktop folder, the CSV and Excel files will be store in the same folder.

    data_to_csv.to_csv('last Field Usage Date.csv')
    data_to_csv.to_excel('last Field Usage Date.xlsx', float_format="%.3f")

---------------------
**If you like it, remember to <br />**
<a href="https://www.buymeacoffee.com/unduslabs" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

------------------------------
### The final code will look like this:
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

HOPE IT HELPS!
----------------------------
**If you like it, remember to <br />**
<a href="https://www.buymeacoffee.com/unduslabs" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>
