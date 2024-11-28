from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('State_History.html')

@app.route('/get-data', methods=['POST'])
def get_data():
    # Handle form data or parameters (mock response for now)
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    x_param = request.form.get('x_param')
    y_param = request.form.get('y_param')
    return {
        "status": "success",
        "data": {
            "start_date": start_date,
            "end_date": end_date,
            "x_param": x_param,
            "y_param": y_param
        }
    }

if __name__ == '__main__':
    app.run(debug=True)
