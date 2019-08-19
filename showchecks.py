import json
from wordcloud import WordCloud, STOPWORDS
from flask import Flask, render_template, request,redirect,url_for
import pandas as pd

# addding extra words to stopwords list
custom_stopwords = list(STOPWORDS) + ['state', 'states', 'patient', 'right', 'left', 'or', 'and', 'el']

app = Flask(__name__)

@app.route('/')
def metrics():
    return render_template('landingpage.html')

@app.route('/highcostlitigationapi')
def litigation():
    """Function to create API for Donut chart."""
    data = get_data()
    high_cost = data[data['High Cost'] == 1]
    high_lit = high_cost[high_cost['Litigation'] == 'yes']
    sector_wise = high_lit.groupby('Sector/Industry').size().reset_index()
    sector_wise.columns = ['name', 'value']
    litigation = sector_wise.to_json(orient='records')
    return litigation

@app.route('/topcostclaims')
def claims_cost():
    data = get_data()
    high_cost = data[data['High Cost'] == 1]
    high_lit = high_cost[high_cost['Litigation'] == 'yes']
    sector_group = high_lit.groupby(['Sector/Industry','Occupation'], sort=True).sum().reset_index()
    claim_cost = sector_group.sort_values(by=['Sector/Industry', 'Claim Cost'],ascending=[True,False])
    claim_cost = claim_cost[['Sector/Industry','Occupation','Claim Cost']]
    return claim_cost.to_json(orient='records')
    

@app.route("/wordcloud/", defaults={'sector': 'Industrials'})
@app.route("/wordcloud/<sector>")
def word_cloud(sector):
    data = get_data()
    data = data[data['Sector/Industry'] == sector.lower()]
    high_cost = data[data['High Cost'] == 1]
    high_lit = high_cost[high_cost['Litigation'] == 'yes']
    high_lit = high_lit[high_lit['Cause Description'].notnull()]

    high_lit['Cause Description'] = high_lit['Cause Description'].apply(
        lambda x: ' '.join([word for word in x.split() if word not in (custom_stopwords)]))

    cause = ' '.join(map(str, high_lit['Cause Description']))
    # chart_data = json.dumps(chart_data, indent=2)
    word_data = {'chart_data': json.dumps(cause), 'sector_name': json.dumps(sector)}
    return render_template("wordcloud.html", data=word_data)


@app.route("/wordcloudapi/", defaults={'sector': 'Industrials'})
@app.route("/wordcloudapi/<sector>")
def word_cloud_api(sector):
    """Function to create the word cloud API."""
    data = get_data()
    print sector
    data = data[data['Sector/Industry'] == sector.lower()]
    high_cost = data[data['High Cost'] == 1]
    high_lit = high_cost[high_cost['Litigation'] == 'yes']
    high_lit = high_lit[high_lit['Cause Description'].notnull()]

    high_lit['Cause Description'] = high_lit['Cause Description'].apply(
        lambda x: ' '.join([word for word in x.split() if word not in (custom_stopwords)]))

    cause = ' '.join(map(str, high_lit['Cause Description']))
    # chart_data = json.dumps(chart_data, indent=2)
    return json.dumps(cause)


def get_data():
    """Function to read the data file."""
    df = pd.read_csv('data.csv')
    df['Claim Cost'] = pd.to_numeric(df['Claim Cost'], errors='coerce')
    df['Sector/Industry'] = df['Sector/Industry'].str.lower()
    df['Litigation'] = df['Litigation '].str.lower()
    df['Cause Description'] = df['Cause Description'].str.replace('[^a-zA-Z \n\.]', '')
    return df

if __name__ == "__main__":
    app.run(debug=True)
