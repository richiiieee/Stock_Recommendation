from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Render your main page

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Retrieve form data
        age_category = request.form['age-category']
        state = request.form['state']
        income = request.form['income']
        source_income = request.form['source-income']
        dependents = request.form['dependents']
        roi = request.form['roi']

        # Here you can process the data (store it, analyze it, etc.)
        print(f"Received data: {age_category}, {state}, {income}, {source_income}, {dependents}, {roi}")

        # Redirect to a thank you page or back to the form
        return redirect(url_for('thank_you'))

    return render_template('form.html')  # Render your form page

@app.route('/thank_you')
def thank_you():
    return "<h1>Thank you for submitting the form!</h1>"

if __name__ == '__main__':
    app.run(debug=True)

*******************************************************************************************************************

from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Define the path for the Excel file
EXCEL_FILE = 'customer_data.xlsx'

@app.route('/')
def home():
    return render_template('index.html')  # Render your main page

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

        # Create a DataFrame for the form data with column names without spaces
        form_data = {
            'Age_Category': [age_category],
            'State': [state],
            'Annual_Income': [income],
            'Source_of_Income': [source_income],
            'Investment_Amount':[investment],
            'Dependents': [dependents],
            'Expected_ROI': [roi]
        }

        df = pd.DataFrame(form_data)

        # Check if the Excel file exists; if not, create it with headers
        if not os.path.exists(EXCEL_FILE):
            df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        else:
            # Append the new data to the existing Excel file
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)

        print(f"Data saved: {age_category}, {state}, {income}, {source_income},{investment},{dependents}, {roi}")

        return redirect(url_for('thank_you'))

    return render_template('form.html')  # Render your form page

@app.route('/thank_you')
def thank_you():
    return "<h1>Thank you for submitting the form!</h1>"

if __name__ == '__main__':
    app.run(debug=True)
