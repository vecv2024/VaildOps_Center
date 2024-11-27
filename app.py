from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/filter-data')
def filter_data():
    start = request.args.get('start')
    end = request.args.get('end')

    # Replace with actual logic to fetch and process vehicle data
    data = {
        "message": "Data filtered successfully.",
        "start": start,
        "end": end
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=False) 
