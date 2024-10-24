from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
from customer_score import calculate_customer_score  # Import the function from the other file


app = Flask(__name__, static_folder='static')

# Define the path for the Excel file
EXCEL_FILE = 'customer_data.xlsx'

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')  # Render your main page

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Retrieve form data
        age_category = request.form['age-category']
        state = request.form['state']
        income = request.form['income']
        source_income = request.form['source-income']
        investment = request.form['investment']
        dependents = request.form['dependents']
        roi = request.form['roi']

        # Check if the Excel file exists; if not, create it with headers
        if not os.path.exists(EXCEL_FILE):
            # Create a DataFrame with an initial row for the headers
            df = pd.DataFrame(columns=['Client_ID', 'Age_Category', 'State', 'Annual_Income', 
                                       'Source_of_Income', 'Investment_Amount', 
                                       'Dependents', 'Expected_ROI'])

            df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')

        # Load existing data to determine the next Client_ID
        existing_data = pd.read_excel(EXCEL_FILE)
        next_client_id = existing_data.shape[0] + 1  # Unique Client ID based on existing records

        # Create a DataFrame for the form data with column names without spaces
        form_data = {
            'Client_ID': [next_client_id],
            'Age_Category': [age_category],
            'State': [state],
            'Annual_Income': [income],
            'Source_of_Income': [source_income],
            'Investment_Amount': [investment],
            'Dependents': [dependents],
            'Expected_ROI': [roi]
        }

        df = pd.DataFrame(form_data)

        # Append the new data to the existing Excel file
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)

        print(f"Data saved: {next_client_id}, {age_category}, {state}, {income}, {source_income}, {investment}, {dependents}, {roi}")
        
        # Call the customer score calculation function
        result = calculate_customer_score(df) 
        # print(result)
        result = result.to_dict('records')
        risk_profile = result[0]['Risk Profile']  # Access the 'Risk_Profile' of the first dictionary

        if result is None:
    # Handle case where no companies are found
            return render_template('results.html', error_message="No matching companies found")
        else:
            return render_template('results.html', companies=result,risk_profile = risk_profile )# This will calculate the customer score and get matching companies

          # Assuming you have a results.html to display the companies

    return render_template('form.html')

    # return render_template('form.html')  # Render your form page

@app.route('/thank_you')
def thank_you():
    return "<h1>Thank you for submitting the form!</h1>"

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Bind to all interfaces
