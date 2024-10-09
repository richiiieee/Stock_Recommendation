import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")
pd.options.display.max_rows = 155000
pd.options.display.max_columns = 500
pd.options.display.float_format = '{:20,.2f}'.format
seed = np.random.seed(66)


def calculate_customer_score(data):
    data = pd.read_excel("C:\D Drive\Richa\S3\cloud\customer_data.xlsx")
    data['Age_Category'] = data['Age_Category'].astype(str)

    #  AGE MAPPING
    def map_age_category(age_str):
        if age_str == '<30':
            return 1
        elif age_str == '30-40':
            return 2
        elif age_str == '40-50':
            return 3
        elif age_str == '50-60':
            return 4
        elif age_str == '>60':
            return 5
        else:
            return None  # Handle unexpected values

    # Apply the mapping function to the Age_Category column
    data['AGE_BUCKET'] = data['Age_Category'].apply(map_age_category)
   
    #TARGET BUCKET
    list = []
    for i in data['Expected_ROI']:
        if i == '<10%':
            list.append(4)
        elif i == '10-15%':
            list.append(3)  
        elif i == '15-25%':
            list.append(2)   
        else:
            list.append(1)    
          
    data['TARGET_BUCKET'] = list     

    #CALCULATING THE PERMISSIBLE AMOUNT TO INVEST
    for i in data['AGE_BUCKET']:
        if i==1:
                data['Max_Investment'] = 0.6 * data['Annual_Income']
        elif i==2:
                data['Max_Investment'] = 0.5 * data['Annual_Income']
        elif i==3:
                data['Max_Investment'] = 0.3 * data['Annual_Income']
        elif i==4:
                data['Max_Investment'] = 0.2 * data['Annual_Income']
        else:
                data['Max_Investment'] = 0.1 * data['Annual_Income']

    #CALCULATING THE INVESTMENT RATIO AND RISK SCORE
    data['Inv_Ratio'] = data['Max_Investment']/data['Investment_Amount']
    data['Risk_Score_N'] = 1 - ((data['Dependents']*3 + data['Inv_Ratio']*4
                             + data['AGE_BUCKET']*3)*data['TARGET_BUCKET'])/100
    
    #CATEGORISING CUSTOMERS
    list = []
    for i in abs(data['Risk_Score_N']):
        if i <= 0.2:
            list.append('Conservative')
        elif i <= 0.4:
            list.append('Moderatively Conservative')  
        elif i <= 0.6:
            list.append('Moderatively Aggresive')    
        elif i <= 0.8:
            list.append('Aggresive')   
        else:
            list.append('Very Aggresive')    
          
    data['Risk Profile'] = list 

    #PERMISSBLE AMOUNT TO INVEST
    data['Amt_Investment'] = data[['Investment_Amount','Max_Investment']].min(axis=1)

    #GETTING THE MATCHING COMPANIES
    def get_company_list(dat1,dat2,col1,col2):
        for i in dat1[col1]:
            print(i)
            dat_1 = dat1[dat1[col1] == i]
            print(dat_1['Client_ID'])
            for j in dat_1[col2]:
                dat_2 = dat2[dat2[col2] == j][[ 'Name','BSE Code', 'NSE Code', 'Industry', 'Current Price','Risk Profile','Company_Rank']].sort_values("Company_Rank").head(10)
                dat_2 = dat_2.sample(frac = 0.5).reset_index(drop = True)           
            return dat_2 
        
        #LOADING THE COMPANY DATA
        data_comp = pd.read_csv('C:\D Drive\Richa\S3\cloud\Data_Companies.csv')

        # COMPANIES MATCHING THE INVESTOR'S RISK APPETITE
        result = get_company_list(data,data_comp,'Client_ID','Risk Profile').sort_values("Company_Rank").head(10)
        
        return result