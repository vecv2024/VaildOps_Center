from flask import Flask, render_template, request, url_for
from folium.plugins import BeautifyIcon
import pandas as pd
import folium
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing messages

# Excel file path
excel_file_path = 'Vehicle_data01.xlsx'

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





@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dtc')
def dtc():
    return render_template('dtc.html')

@app.route('/protus')
def protus():
    return render_template('protus.html')

@app.route('/Segment')
def Segment():
    return render_template('Segment.html')

@app.route('/State_History')
def State_History():
    return render_template('State_History.html')

@app.route('/dtc_description')
def dtc_description():
    return render_template('dtc_description.html')

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

if __name__ == '__main__':
    # Generate the map before starting the app
    generate_india_map()
    app.run(debug=True)
