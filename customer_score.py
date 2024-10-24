import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")
pd.options.display.max_rows = 155000
pd.options.display.max_columns = 500
pd.options.display.float_format = '{:20,.2f}'.format
seed = np.random.seed(66)


def calculate_customer_score(data):
    # data = pd.read_excel("customer_data.xlsx",names=["Client_ID", "Age_Category", "State", "Annual_Income", "Source_of_Income","Investment_Amount","Dependents", "Expected_ROI"])
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

# CALCULATING THE PERMISSIBLE AMOUNT TO INVEST
    data['Max_Investment'] = np.select(
        [
            data['AGE_BUCKET'] == 1,
            data['AGE_BUCKET'] == 2,
            data['AGE_BUCKET'] == 3,
            data['AGE_BUCKET'] == 4,
            data['AGE_BUCKET'] == 5
        ],
        [
            0.6 * data['Annual_Income'].astype(int),
            0.5 * data['Annual_Income'].astype(int),
            0.3 * data['Annual_Income'].astype(int),
            0.2 * data['Annual_Income'].astype(int),
            0.1 * data['Annual_Income'].astype(int)
        ]
    )


    # #CALCULATING THE PERMISSIBLE AMOUNT TO INVEST
    # for i in data['AGE_BUCKET']:
    #     if i==1:
    #             data['Max_Investment'] = 0.6 * data['Annual_Income']
    #     elif i==2:
    #             data['Max_Investment'] = 0.5 * data['Annual_Income']
    #     elif i==3:
    #             data['Max_Investment'] = 0.3 * data['Annual_Income']
    #     elif i==4:
    #             data['Max_Investment'] = 0.2 * data['Annual_Income']
    #     else:
    #             data['Max_Investment'] = 0.1 * data['Annual_Income']

    #CALCULATING THE INVESTMENT RATIO AND RISK SCORE
    data['Inv_Ratio'] = data['Max_Investment']/data['Investment_Amount'].astype(int)
    data['Risk_Score_N'] = 1 - ((data['Dependents'].astype(int)*3 + data['Inv_Ratio']*4
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
    data['Investment_Amount'] = data['Investment_Amount'].astype(int)
    data['Amt_Investment'] = data[['Investment_Amount','Max_Investment']].min(axis=1)

    # GETTING THE MATCHING COMPANIES
    def get_company_list(dat1, dat2, col1, col2):
        # Select the most recent customer (last row)
        recent_customer = dat1.iloc[-1]
        risk_profile = recent_customer[col2]
        # Print the risk profile for debugging
        print(f"Processing Client_ID: {recent_customer[col1]} with Risk Profile: {risk_profile}")
        # print(f"Company Risk Profile is :{dat2[dat2[col2] == risk_profile]}")
        # Find the matching companies based on the risk profile
        matching_companies = dat2[dat2[col2] == risk_profile][['Name', 'BSE Code', 'NSE Code', 'Industry', 'Current Price', 'Risk Profile', 'Company_Rank']]
        
        # Sort companies by rank and select the top 10
        matching_companies = matching_companies.sort_values("Company_Rank").head(5)
        
        print("Matching Companies are :",matching_companies)  # Debug output
        return matching_companies
     
    #LOADING THE COMPANY DATA
    data_comp = pd.read_csv('Data_Companies.csv')

    # COMPANIES MATCHING THE INVESTOR'S RISK APPETITE
    result = get_company_list(data, data_comp, 'Client_ID', 'Risk Profile').sort_values("Company_Rank").head(10)
        
    return result