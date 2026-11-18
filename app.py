from flask import Flask, render_template
import data_handler

app = Flask(__name__)

@app.route('/')
def dashboard():
    try:
        # Load data and get metrics
        df = data_handler.load_and_clean_data()
        kpis = data_handler.get_kpis(df)
        charts = data_handler.get_charts(df)
        forecast = data_handler.get_sales_forecast(df)
        
        return render_template('index.html', kpis=kpis, charts=charts, forecast=forecast)
    
    except Exception as e:
        
        return f"<h3>An error occurred:</h3> <p>{str(e)}</p>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)