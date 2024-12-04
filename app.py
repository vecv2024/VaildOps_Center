from flask import Flask, jsonify, render_template, request, url_for, Response
from folium.plugins import BeautifyIcon
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import folium
import os
import io
import random

def read_excel_data(filepath):
    try:
        # Read the Excel file into a DataFrame
        data = pd.read_excel(filepath)
        # Replace NaN values with "Not available" for missing fields
        data = data.fillna("Not available")
        return data.to_dict(orient="records")  # Convert to a list of dictionaries
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

app = Flask(__name__)
# Load data from Excel sheets
ev_data = pd.read_excel('Vehicle_dataEV.xlsx')
lmd_data = pd.read_excel('Vehicle_dataLMD.xlsx')
hd_data = pd.read_excel('Vehicle_dataHD.xlsx')
scv_data = pd.read_excel('Vehicle_dataSCV.xlsx')

# Convert data to dictionaries for easier access
vehicle_data = {
    "EV": {"title": "EV Vehicle", "data": ev_data},
    "LMD": {"title": "LMD Vehicle", "data": lmd_data},
    "HD": {"title": "HD Vehicle", "data": hd_data},
    "SCV": {"title": "SCV Vehicle", "data": scv_data},
}

@app.route('/dtc')
def dtc():
    # Create sections for each vehicle type
    sections = {}
    for key, info in vehicle_data.items():
        data = info["data"]
        dtcs = data.iloc[:, [2, 1]].values.tolist()  # Extract DTCs (column 3) and descriptions (column 2)
        sections[key] = {"title": info["title"], "dtcs": dtcs}
    return render_template('dtc.html', sections=sections)

@app.route('/dtc/dtc_description/<vehicle>/<dtc_code>')
def dtc_description(vehicle, dtc_code):
    # Fetch data for the specified vehicle
    data = vehicle_data[vehicle]["data"]
    
    # Find the row that corresponds to the selected DTC code
    dtc_details = data[data.iloc[:, 2] == dtc_code].iloc[0]
    
    # Depending on the vehicle type, adjust which details are shown
    if vehicle == "LMD":
        details = {
            "fault_name": dtc_details[0],
            "Fault type Description": dtc_details[7],
            "remedy": dtc_details[9],
            "comments": dtc_details[10] if len(dtc_details) > 10 else 'No additional comments'
        }
    elif vehicle == "HD":
        details = {
            "short_name": dtc_details[3],
            "ecu": dtc_details[1],
            "category": dtc_details[13] if len(dtc_details) > 13 else 'No category'
        }
    elif vehicle == "SCV":
        details = {
            "fault_code": dtc_details[1],
            "vehicle_reaction": dtc_details[31] if len(dtc_details) > 31 else 'No reaction data'
        }
    else:  # Default case for EV
        details = {
            "description": dtc_details[1],
            "Fault type Description": dtc_details[7],
            "Cause": dtc_details[8],
            "Remedy": dtc_details[9] if len(dtc_details) > 9 else 'No remedy provided'
        }

    return render_template('dtc_description.html', vehicle=vehicle, dtc_code=dtc_code, details=details)

# Load data from Excel
vehicle_live_data = pd.read_excel('Vehicle_live.xlsx')

# Clean the data for consistency
vehicle_live_data['model_sticker'] = vehicle_live_data.iloc[:, 5].astype(str).str.strip().str.lower()

# Initialize segment-wise totals
segment_totals = vehicle_live_data.groupby(vehicle_live_data.iloc[:, 0]).agg({
    vehicle_live_data.columns[8]: 'sum',  # Column 9 for distance
    vehicle_live_data.columns[9]: 'sum'  # Column 10 for engine hours
}).rename(columns={vehicle_live_data.columns[8]: 'total_kms', vehicle_live_data.columns[9]: 'total_engine_hours'}).to_dict(orient='index')

@app.route('/')
def home():
    # Get segment names and stats
    segments = vehicle_live_data.iloc[:, 0].unique()
    stats = {seg: len(vehicle_live_data[vehicle_live_data.iloc[:, 0] == seg]) for seg in segments}

    # Prepare segment totals for rendering
    totals = {seg: {
        "total_kms": round(segment_totals[seg]['total_kms'], 2),
        "total_engine_hours": round(segment_totals[seg]['total_engine_hours'], 2)
    } for seg in segment_totals}

    return render_template('home.html', stats=stats, totals=totals)

@app.route('/update_segment_totals', methods=['GET'])
def update_segment_totals():
    # Simulate real-time updates
    for segment in segment_totals:
        segment_totals[segment]['total_kms'] += random.uniform(0.0, 0.0)  # Increment kilometers
        segment_totals[segment]['total_engine_hours'] += random.uniform(0.000, 0.00)  # Increment engine hours

    updated_totals = {seg: {
        "total_kms": round(segment_totals[seg]['total_kms'], 2),
        "total_engine_hours": round(segment_totals[seg]['total_engine_hours'], 2)
    } for seg in segment_totals}

    return jsonify(updated_totals)

@app.route('/segment/<segment>')
def segment(segment):
    # Filter data for the given segment
    segment_data = vehicle_live_data[vehicle_live_data.iloc[:, 0] == segment]
    vehicles = []

    for _, row in segment_data.iterrows():
        vehicles.append({
            "model_sticker": row[5],  # Column 6
            "speed": row[7],          # Column 8
            "distance": row[8],       # Column 9
            "engine_hours": row[9],   # Column 10
            "location": row[6]        # Column 5
        })
    
    return render_template('segment.html', segment=segment, vehicles=vehicles)

@app.route('/vehicle_detail/<model_sticker>')
def vehicle_detail(model_sticker):
    model_sticker = str(model_sticker).strip().lower()
    vehicle_data = vehicle_live_data[vehicle_live_data['model_sticker'] == model_sticker]

    if vehicle_data.empty:
        return render_template('error.html', message=f"No vehicle found with Model Sticker: {model_sticker}")
    
    vehicle_data = vehicle_data.iloc[0]
    vehicle = {
        "model_sticker": vehicle_data[5],
        "speed": vehicle_data[7],
        "distance": vehicle_data[8],
        "engine_hours": vehicle_data[9],
        "location": vehicle_data[6],
        "Engine_Temp": vehicle_data[13],
        "Fuel_Level": vehicle_data[10]
    }
    segment = vehicle_data[0]
    
    return render_template('vehicle_detail.html', vehicle=vehicle, segment=segment)



# <..................................................................>
# Function to generate the India cities map
def generate_india_map():
    # Create a map centered on India
    india_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    # List of popular cities in India with their coordinates
    LMD_cities = [
        {"name": "Delhi", "coords": [28.6139, 77.2090]},
        {"name": "Mumbai", "coords": [19.0760, 72.8777]},
        {"name": "Bengaluru", "coords": [12.9716, 77.5946]},
        {"name": "Chennai", "coords": [13.0827, 80.2707]},
        {"name": "Kolkata", "coords": [22.5726, 88.3639]},
        {"name": "Hyderabad", "coords": [17.385044, 78.486671]},
        {"name": "Ahmedabad", "coords": [23.0225, 72.5714]},
        {"name": "Jaipur", "coords": [26.9124, 75.7873]},
    ]

    HD_cities = [
        {"name": "Lucknow", "coords": [26.8467, 80.9462]},    # North
        {"name": "Pune", "coords": [18.5204, 73.8567]},       # West
        {"name": "Surat", "coords": [21.1702, 72.8311]},      # West
        {"name": "Patna", "coords": [25.5941, 85.1376]},      # East
        {"name": "Bhopal", "coords": [23.2599, 77.4126]},     # Central
        {"name": "Kanpur", "coords": [26.4499, 80.3319]},     # North
        {"name": "Nagpur", "coords": [21.1458, 79.0882]},     # Central
        {"name": "Indore", "coords": [22.7196, 75.8577]},     # Central
        {"name": "Thiruvananthapuram", "coords": [8.5241, 76.9366]}, # South
        {"name": "Ranchi", "coords": [23.3441, 85.3096]},     # East
        {"name": "Guwahati", "coords": [26.1445, 91.7362]},   # North-East
    ]

    BUS_cities = [
        {"name": "Chandigarh", "coords": [30.7333, 76.7794]}, # North
        {"name": "Kochi", "coords": [9.9312, 76.2673]},       # South
        {"name": "Coimbatore", "coords": [11.0168, 76.9558]}, # South
        {"name": "Vishakhapatnam", "coords": [17.6868, 83.2185]}, # South-East
        {"name": "Varanasi", "coords": [25.3176, 82.9739]},   # North
        {"name": "Madurai", "coords": [9.9252, 78.1198]},     # South
    ]


    EV_cities = [
        {"name": "Jodhpur", "coords": [26.2389, 73.0243]},    # North-West
        {"name": "Agra", "coords": [27.1767, 78.0081]},       # North
        {"name": "Amritsar", "coords": [31.6340, 74.8723]},   # North
        {"name": "Dehradun", "coords": [30.3165, 78.0322]},   # North
        {"name": "Shimla", "coords": [31.1048, 77.1734]},     # North
        {"name": "Raipur", "coords": [21.2514, 81.6296]},     # Central-East
        {"name": "Panaji", "coords": [15.4909, 73.8278]},     # West (Goa)
    ]

    SCV_cities = [
        {"name": "Shillong", "coords": [25.5788, 91.8933]},   # North-East
        {"name": "Imphal", "coords": [24.8170, 93.9368]},     # North-East
        {"name": "Itanagar", "coords": [27.0844, 93.6053]},   # North-East
        {"name": "Gangtok", "coords": [27.3314, 88.6138]},    # North-East
        {"name": "Aizawl", "coords": [23.7271, 92.7176]},     # North-East
    ]

    # Add markers for each city
    for city in LMD_cities:
        folium.Marker(
            location=city["coords"],
            popup=city["name"],
            tooltip="LMD",
            icon=BeautifyIcon(
            icon='fas fa-truck km-icon',  # Font Awesome truck icon
            icon_shape='marker',  # Marker shape
            background_color='transparent',  # Transparent background
            border_width=0,  # Remove the border
            text_color='red'  # Set the truck icon color to red
        )
    ).add_to(india_map)
        

    # Add markers for each city
    for city in HD_cities:
        folium.Marker(
            location=city["coords"],
            popup=city["name"],
            tooltip="HD",
            icon=BeautifyIcon(
            icon='fas fa-truck-monster km-icon',  # Font Awesome truck icon
            icon_shape='marker',  # Marker shape
            background_color='transparent',  # Transparent background
            border_width=0,  # Remove the border
            text_color='red'  # Set the truck icon color to red
        )
    ).add_to(india_map)
        
    
    # Add markers for each city
    for city in BUS_cities:
        folium.Marker(
            location=city["coords"],
            popup=city["name"],
            tooltip="BUS",
            icon=BeautifyIcon(
            icon='fas fa-bus km-icon',  # Font Awesome truck icon
            icon_shape='marker',  # Marker shape
            background_color='transparent',  # Transparent background
            border_width=0,  # Remove the border
            text_color='red'  # Set the truck icon color to red
        )
    ).add_to(india_map)
        

     # Add markers for each city
    for city in EV_cities:
        folium.Marker(
            location=city["coords"],
            popup=city["name"],
            tooltip="EV",
            icon=BeautifyIcon(
            icon='fas fa-bolt km-icon',  # Font Awesome truck icon
            icon_shape='marker',  # Marker shape
            background_color='transparent',  # Transparent background
            border_width=0,  # Remove the border
            text_color='red'  # Set the truck icon color to red
        )
    ).add_to(india_map)
        
    # Add markers for each city
    for city in SCV_cities:
        folium.Marker(
            location=city["coords"],
            popup=city["name"],
            tooltip="SCV",
            icon=BeautifyIcon(
            icon='fas fa-tractor km-icon',  # Font Awesome truck icon
            icon_shape='marker',  # Marker shape
            background_color='transparent',  # Transparent background
            border_width=0,  # Remove the border
            text_color='red'  # Set the truck icon color to red
        )
    ).add_to(india_map)

    # Save the map to the `static` folder
    map_path = os.path.join('static', 'india_cities_map.html')
    india_map.save(map_path)





    # Function to generate the India map
def generate_india_map1():
    # Create a map centered on India
    india_map1 = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    # Save the map to the `static` folder
    map_path = os.path.join('static', 'india_map.html')
    india_map1.save(map_path)

# <.........................................................>



# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/dtc')
# def dtc():
#     return render_template('dtc.html')

@app.route('/protus')
def protus():
    return render_template('protus.html')

@app.route('/Segment')
def Segment():
    return render_template('Segment.html')

@app.route('/State_History')
def State_History():
    return render_template('State_History.html')

# @app.route('/dtc_description')
# def dtc_description():
#     return render_template('dtc_description.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/Segment2')
def Segment2():
    return render_template('Segment2.html')



@app.route('/Segment3')
def Segment3():
    return render_template('Segment3.html')

@app.route('/Segment4')
def Segment4():
    return render_template('Segment4.html')

@app.route('/Segment5')
def Segment5():
    return render_template('Segment5.html')

@app.route('/Profile')
def Profile():
    return render_template('Profile.html')

@app.route('/map')
def map_view():
    return render_template('map.html')

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

# <......................................................>
# analytics

@app.route('/analytics-data')
def analytics_data():
    analytics_data = pd.read_excel('fan_dtc.xlsx')
    selected_column = ["utc", "FanSpeed"]
    req_data = analytics_data[selected_column]
    return jsonify(req_data.to_json(orient='records'))

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(req_data["utc"], req_data["FanSpeed"], label="Fan Speed")
    plt.title("Fan Speed vs UTC")
    plt.xlabel("UTC")
    plt.ylabel("Fan Speed")
    plt.legend()
    plt.grid(True)

    # Save the plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Return the plot as a response
    return Response(buf, mimetype='image/png')

    # Protus

@app.route('/protus-data')
def protus_data():
    # pdata = pd.read_excel('DTC_new_data.xlsx')
    # Read DTC tickets
    
    dtc_tickets = read_excel_data("vehicle_dataDTC.xlsx")
    # Read Protus Tracking data
    protus_data = read_excel_data("DTC_new_data.xlsx")

    return render_template("index.html", dtc_tickets=dtc_tickets, protus_data=protus_data)


if __name__ == '__main__':
    # Generate the map before starting the app
    generate_india_map()
    app.run(debug=True)
