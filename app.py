import streamlit as st
import requests
import json
from streamlit.components.v1 import html

def get_client_ip():
    """Get client's IP address from the request headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # Get client's public IP
        response = requests.get('https://api.ipify.org?format=json', headers=headers)
        if response.status_code == 200:
            return response.json().get('ip')
    except:
        pass
    return None

def get_user_city():
    try:
        # Try to get client's IP
        client_ip = get_client_ip()
        if not client_ip:
            return 'Unable to detect your location'
            
        # Get location data based on client's IP
        location_response = requests.get(f'http://ip-api.com/json/{client_ip}?fields=status,message,city,country,regionName')
        location_data = location_response.json()
        
        if location_data.get('status') == 'success':
            city = location_data.get('city', '')
            region = location_data.get('regionName', '')
            country = location_data.get('country', '')
            
            # Return the most specific location available
            if city and region and country:
                return f"{city}, {region}, {country}"
            elif city and country:
                return f"{city}, {country}"
            elif city:
                return city
            
        return 'Location not available'
    except Exception as e:
        return 'Error detecting location'

def main():
    st.set_page_config(
        page_title="City Detector",
        page_icon="🌍",
        layout="centered"
    )
    
    st.title("🌍 Location Detector")
    st.write("This app detects your current location based on your device's IP address.")
    st.warning("For the most accurate results, please allow location access in your browser if prompted.")
    
    if st.button("Detect My City"):
        with st.spinner('Detecting your location...'):
            city = get_user_city()
            # Display the location in a larger, more prominent way
            st.markdown(f"""
            <div style='text-align: center; margin: 30px 0;'>
                <h2>Your current location is:</h2>
                <h1 style='color: #1E88E5; margin: 15px 0;'>{city}</h1>
                <p>ℹ️ This is based on your device's network information</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a map using OpenStreetMap (approximate location)
            try:
                # Get coordinates for the map
                coord_response = requests.get(f'https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1')
                if coord_response.status_code == 200 and coord_response.json():
                    lat = coord_response.json()[0]['lat']
                    lon = coord_response.json()[0]['lon']
                    
                    # Create an iframe with OpenStreetMap
                    map_html = f"""
                    <div style='width: 100%; height: 300px; margin: 20px 0; border-radius: 10px; overflow: hidden;'>
                        <iframe 
                            width="100%" 
                            height="100%" 
                            frameborder="0" 
                            scrolling="no" 
                            marginheight="0" 
                            marginwidth="0" 
                            src="https://www.openstreetmap.org/export/embed.html?bbox={lon-0.05}%2C{lat-0.05}%2C{lon+0.05}%2C{lat+0.05}&amp;layer=mapnik&amp;marker={lat}%2C{lon}"
                            style="border: 1px solid #ccc;">
                        </iframe>
                    </div>
                    <small>
                        <a href="https://www.openstreetmap.org/?mlat={lat}&amp;mlon={lon}#map=12/{lat}/{lon}">View Larger Map</a>
                    </small>
                    """
                    html(map_html, height=320)
            except:
                pass
    
    # Add some styling
    st.markdown("""
    <style>
        .stButton>button {
            background-color: #1E88E5;
            color: white;
            font-weight: bold;
            border: none;
            padding: 10px 24px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #1565C0;
            transform: translateY(-2px);
        }
        .stAlert {
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
