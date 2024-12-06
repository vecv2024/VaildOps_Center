from flask import Flask, render_template, request,  jsonify,  url_for
from flask import Flask, jsonify, redirect, render_template, request, url_for, Response
from flask_cors import CORS
from folium.plugins import BeautifyIcon
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import folium
import os
import io
import random

# File paths
DTC_LIST_FILE = "DTC_List.xlsx"
PROTUS_DATA_FILE = "Protus_data.xlsx"

# Helper function to read Excel data
def read_excel_safe(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()  # Return an empty DataFrame if the file does not exist
    return pd.read_excel(file_path).fillna("Not available")

# Helper function to save data to Excel
def save_excel_safe(file_path, data):
    data.to_excel(file_path, index=False)

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

CSV_DIR = "./csv_files"  # Directory containing CSV files


def get_csv_files():
    """Retrieve a list of CSV files in the directory."""
    files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
    return files


def read_csv_keys(file_path):
    """Read the keys (columns) from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df.columns.tolist(), df
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return [], None


app = Flask(__name__)
CORS(app)


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
    # Convert the segment status counts into a list of dictionaries for rendering in HTML
    segment_data = segment_status_counts.to_dict(orient="records")
    # return render_template("dtc.html",)
    # Create sections for each vehicle type
    sections = {}
    for key, info in vehicle_data.items():
        data = info["data"]
        dtcs = data.iloc[:, [2, 1]].values.tolist()  # Extract DTCs (column 3) and descriptions (column 2)
        sections[key] = {"title": info["title"], "dtcs": dtcs}
    return render_template('dtc.html', sections=sections,  segments=segment_data)

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

# Calculate overall totals for Open and Closed DTCs
    total_open = segment_status_counts["Open"].sum()
    total_closed = segment_status_counts["Closed"].sum()
    total_progress = segment_status_counts["InProcess"].sum()

    # Get segment names and stats
    segments = vehicle_live_data.iloc[:, 0].unique()
    stats = {seg: len(vehicle_live_data[vehicle_live_data.iloc[:, 0] == seg]) for seg in segments}

    # Prepare segment totals for rendering
    totals = {seg: {
        "total_kms": round(segment_totals[seg]['total_kms'], 2),
        "total_engine_hours": round(segment_totals[seg]['total_engine_hours'], 2)
    } for seg in segment_totals}

    return render_template('home.html', stats=stats, totals=totals,
        total_open=total_open,
        total_closed=total_closed,
        total_progress=total_progress,)

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
            "location": row[6],        # Column 5
            "segment": row[0],
            "chassis": row[3]
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

#<.......................................................>

# Load and process the updated Excel file
file_path = "DTC_data.xlsx"
dtc_data = pd.read_excel(file_path)

# Ensure the correct column is used for the 'Status' field (Column 5)
dtc_data["Status"] = dtc_data.iloc[:, 4].str.upper().str.strip()  # Assuming Status is in the 5th column (index 4)

# Filter the data to include only 'O' (Open), 'C' (Closed), and 'P' (InProcess) statuses
dtc_data = dtc_data[dtc_data["Status"].isin(["O", "C", "P"])]

# Group the data by 'Segment/section' and 'Status', then count occurrences
segment_status_counts = (
    dtc_data.groupby(["Segment/section", "Status"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

# Add missing columns with default values if necessary
for status in ["C", "O", "P"]:
    if status not in segment_status_counts.columns:
        segment_status_counts[status] = 0

# Rename columns for clarity
segment_status_counts.rename(
    columns={"C": "Closed", "O": "Open", "P": "InProcess"}, inplace=True
)

# Ensure the DataFrame has the correct column order
segment_status_counts = segment_status_counts[["Segment/section", "Closed", "Open", "InProcess"]]




# Ensure the DataFrame has the correct number of columns
# if segment_status_counts.shape[1] == 3:
#     segment_status_counts.columns = ["Segment/section", "Closed", "Open"]
# else:
#     raise ValueError(
#         f"Unexpected data format: The DataFrame has {segment_status_counts.shape[1]} columns instead of 3."
#     )

@app.route("/fetch_data", methods=["POST"])
def fetch_data():
    segment = request.json.get("segment")
    if not segment:
        return jsonify({"error": "No segment provided"}), 400

    # Filter the DTC data for the selected segment
    filtered_data = dtc_data[dtc_data["Segment/section"] == segment]
    if filtered_data.empty:
        return jsonify([])  # Return an empty array if no data is found

    # Extract the relevant columns and replace NaN values
    data_to_display = filtered_data.iloc[:, [0, 2, 9, 10, 3, 7, 11]].rename(
        columns={
            filtered_data.columns[0]: "Segment",
            filtered_data.columns[2]: "DTC",
            filtered_data.columns[9]: "Description",
            filtered_data.columns[10]: "Ageing",
            filtered_data.columns[3]: "Protus Name",
            filtered_data.columns[7]: "Responsible",
            filtered_data.columns[11]: "Status",
        }
    ).fillna("N/A")  # Replace NaN values with "N/A"

    return jsonify(data_to_display.to_dict(orient="records"))





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
# Protus Dtc Handler

@app.route('/protus')
def protus():
    # Load data from both files
    dtc_data = read_excel_safe(DTC_LIST_FILE)
    protus_data = read_excel_safe(PROTUS_DATA_FILE)
    return render_template(
        "protus.html",
        dtc_data=dtc_data.to_dict(orient="records"),
        protus_data=protus_data.to_dict(orient="records"),
        enumerate=enumerate,  # Pass enumerate explicitly
    )

@app.route("/raise/<int:row_index>", methods=["POST"])
def raise_issue(row_index):
    dtc_data = read_excel_safe(DTC_LIST_FILE)
    protus_data = read_excel_safe(PROTUS_DATA_FILE)

    if row_index < len(dtc_data):
        row_to_move = dtc_data.iloc[row_index]

        protus_data = pd.concat([protus_data, pd.DataFrame([row_to_move])], ignore_index=True)

        # Remove the row from DTC_List.xlsx
        dtc_data = dtc_data.drop(index=row_index).reset_index(drop=True)

        # Save updated data
        save_excel_safe(DTC_LIST_FILE, dtc_data)
        save_excel_safe(PROTUS_DATA_FILE, protus_data)

    return redirect(url_for("protus"))

@app.route("/delete/<int:row_index>", methods=["POST"])
def delete_issue(row_index):
    dtc_data = read_excel_safe(DTC_LIST_FILE)

    if row_index < len(dtc_data):
        # Remove the row
        dtc_data = dtc_data.drop(index=row_index).reset_index(drop=True)

        # Save updated data
        save_excel_safe(DTC_LIST_FILE, dtc_data)

    return redirect(url_for("protus"))

@app.route("/delete-protus/<int:row_index>", methods=["POST"])
def delete_protus(row_index):
    protus_data = read_excel_safe(PROTUS_DATA_FILE)

    if row_index < len(protus_data):
        # Remove the row
        protus_data = protus_data.drop(index=row_index).reset_index(drop=True)

        # Save updated data
        save_excel_safe(PROTUS_DATA_FILE, protus_data)

    return redirect(url_for("protus"))

# Protus DTC handler end
@app.route('/Segment')
def Segment():
    return render_template('Segment.html')

@app.route('/State_History')
def State_History():
    return render_template('State_History.html')

# start of analytics

@app.route("/analytics")
def analytics():
    csv_files = get_csv_files()
    return render_template("analytics.html", files=csv_files)


@app.route("/get_keys", methods=["POST"])
def get_keys():
    """Return column keys and data range for a selected CSV file."""
    filename = request.json.get("filename")
    file_path = os.path.join(CSV_DIR, filename)
    
    columns, df = read_csv_keys(file_path)
    
    if df is not None:
        # Check for IST_DateTime column for date/time range
        if 'IST_DateTime' in df.columns:
            df['IST_DateTime'] = pd.to_datetime(df['IST_DateTime'], errors='coerce')
            min_date = df['IST_DateTime'].min()
            max_date = df['IST_DateTime'].max()
            date_range = {"min": min_date.isoformat(), "max": max_date.isoformat()}
        else:
            date_range = None
        return jsonify({"columns": columns, "date_range": date_range})
    else:
        return jsonify({"error": "Unable to read file"}), 400


@app.route("/plot", methods=["POST"])
def plot_data():
    """Plot data based on user selection."""
    data = request.json
    filename = data.get("filename")
    x_key = data.get("x_key")
    y_key = data.get("y_key")

    # Extract threshold values if provided
    thresholdx1 = data.get("thresholdx1")
    thresholdx2 = data.get("thresholdx2")
    thresholdy1 = data.get("thresholdy1")
    thresholdy2 = data.get("thresholdy2")

    start_time = pd.to_datetime(data.get("start_time"))
    end_time = pd.to_datetime(data.get("end_time"))
    plot_type = data.get("plot_type", "line")

    file_path = os.path.join(CSV_DIR, filename)
    _, df = read_csv_keys(file_path)

    if df is not None:
        if 'IST_DateTime' in df.columns:
            df['IST_DateTime'] = pd.to_datetime(df['IST_DateTime'], errors='coerce')
            df = df[(df['IST_DateTime'] >= start_time) & (df['IST_DateTime'] <= end_time)]

        plt.figure(figsize=(10, 6))

        # Create plots based on the selected plot type
        if plot_type == "line":
            plt.plot(df[x_key], df[y_key], marker='o', label=f"{y_key} (line)")
        elif plot_type == "scatter":
            plt.scatter(df[x_key], df[y_key], label=f"{y_key} (scatter)")
        elif plot_type == "bar":
            plt.bar(df[x_key], df[y_key], label=f"{y_key} (bar)")
        elif plot_type == "histogram":
            plt.hist(df[x_key], bins=20, label=f"{y_key} (histogram)")
        elif plot_type == "heatmap":
            if x_key and y_key:
                heatmap_data = pd.pivot_table(df, values=y_key, index=x_key, aggfunc='mean')
                sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".1f")
            else:
                return jsonify({"error": "Heatmap requires both x_key and y_key."}), 400
        else:
            return jsonify({"error": "Unsupported plot type."}), 400

        # Plot the threshold line if coordinates are provided
        if thresholdx1 is not None and thresholdx2 is not None and thresholdy1 is not None and thresholdy2 is not None:
            # Convert threshold values to float
            thresholdx1 = float(thresholdx1)
            thresholdx2 = float(thresholdx2)
            thresholdy1 = float(thresholdy1)
            thresholdy2 = float(thresholdy2)

            if thresholdy1 == thresholdy2:  # Horizontal line
                # Generate x values across the data range
                x_vals = np.linspace(df[x_key].min(), df[x_key].max(), 500)
                y_vals = np.full_like(x_vals, thresholdy1)  # Constant y-value for the horizontal line
            else:  # Tilted line
                # Calculate slope (m) and intercept (b) of the line
                m = (thresholdy2 - thresholdy1) / (thresholdx2 - thresholdx1)
                b = thresholdy1 - m * thresholdx1

                # Generate x values for the entire plot range
                x_vals = np.linspace(df[x_key].min(), df[x_key].max(), 500)
                y_vals = m * x_vals + b

            # Plot the threshold line
            plt.plot(x_vals, y_vals, 'r--', label=f'Threshold Line')

            # Highlight points above the threshold
            if thresholdy1 == thresholdy2:  # Horizontal line case
                above_threshold = df[df[y_key] > thresholdy1]  # Compare y-values directly
            else:  # Slanted line case
                # Compute the threshold y-value for each data point's x-value
                df['threshold_y'] = m * df[x_key] + b
                above_threshold = df[df[y_key] > df['threshold_y']]  # Compare y-values with the line

            # Highlight the points above the threshold line
            # if not above_threshold.empty:
                # plt.scatter(above_threshold[x_key], above_threshold[y_key],label="Above Threshold", zorder=5)


        plt.title(f"{y_key} vs {x_key} ({plot_type.capitalize()})")
        plt.xlabel(x_key)
        plt.ylabel(y_key)
        plt.legend()
        plt.grid(True)

        # Convert plot to base64 string
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return jsonify({"plot_url": f"data:image/png;base64,{plot_url}"})
    
    else:
        return jsonify({"error": "Unable to read file"}), 400



@app.route("/empty_plot")
def empty_plot():
    """Serve an empty plot as a placeholder."""
    plt.figure(figsize=(10, 6))
    plt.title("Empty Plot")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.grid(True)

    # Save the empty plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return jsonify({"plot_url": f"data:image/png;base64,{plot_url}"})

# end of analytics

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
@app.route('/efficiency')
def efficiency():
    return render_template('efficiency.html')
@app.route('/aggregate')
def aggregate():
    return render_template('aggregate.html')

@app.route('/enhancement')
def enhancement():
    return render_template('enhancement.html')



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



if __name__ == '__main__':
    # Generate the map before starting the app
    generate_india_map()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)