from flask import Flask, render_template
import pandas as pd

# creates a flask instance
app = Flask(__name__)

# Load the CSV file using pandas and rounds the indoor temp to the nearest decimal place
data = pd.read_csv('temperature_log_api.csv', dtype={'indoor_temp': 'float'})
data['indoor_temp'] = data['indoor_temp'].round(1)

# renders the data and displays the csv file onto a table based on the html
# code found in templates/display_data.html
@app.route('/')
def display_data():
    # Pass the loaded data to the HTML template
    return render_template('display_data.html', data=data)

# run the web app
if __name__ == '__main__':
    app.run(debug=True)