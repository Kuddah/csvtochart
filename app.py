import pandas as pd
import numpy as np
import json
import plotly.express as px
import sys
import plotly
from flask import Flask, render_template_string, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_charts(filepath, chart_type):
    # Load data
    df = pd.read_csv(filepath)

    # Combine 'date' and 'time' columns into a single 'date_time' column
    df['date_time'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

    # Drop the original 'date' and 'time' columns
    df.drop(columns=['Date', 'Time'], inplace=True)

    # Columns to create charts for
    columns = df.columns.drop(['date_time'])

    chart_ids = []
    charts = {}

    for col in columns:
        if chart_type == 'line':
            fig = px.line(df, x='date_time', y=col)
        else:
            fig = px.scatter(df, x='date_time', y=col)

        # Set hover format for y-axis labels to display decimal values correctly
        fig.update_yaxes(hoverformat='.2f')

        chart_id = f"chart_{col}"
        chart_ids.append(chart_id)
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        charts[chart_id] = chart_json
        print(f"Chart for {col}: {chart_json}")

    return chart_ids, charts

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['csv_file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            chart_type = request.form['chart_type']
            chart_ids, charts = create_charts(file_path, chart_type)

            chart_template = '''
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="utf-8">
                <title>Charts</title>
              </head>
              <body>
                {% for chart_id in chart_ids %}
                <div id="{{chart_id}}" style="width:100%;height:500px;"></div>
                {% endfor %}
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <script>
                  var chart_ids = {{chart_ids|tojson}};
                  var charts = {{charts|tojson}};
                  for (var i = 0; i < chart_ids.length; i++) {
                    var chart_id = chart_ids[i];
                    var chart = document.getElementById(chart_id);
                    var chart_data = JSON.parse(charts[chart_id]);
                    Plotly.newPlot(chart, chart_data.data, chart_data.layout);
                  }
                </script>
              </body>
            </html>
            '''

            return render_template_string(chart_template, chart_ids=chart_ids, charts=charts)

    return '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Upload CSV</title>
      </head>
      <body>
        <h1>Upload a CSV file</h1>
        <form method="POST" enctype="multipart/form-data">
          <input type="file" name="csv_file" accept=".csv">
          <input type="radio" name="chart_type" value="line" checked> Line Chart
          <input type="radio" name="chart_type"
          <input type="radio" name="chart_type" value="scatter"> Scatter Chart
          <input type="submit" value="Upload">
        </form>
      </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
