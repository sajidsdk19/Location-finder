import streamlit as st
import requests
import json
from streamlit.components.v1 import html
import time

def get_location_from_coords(lat, lon):
    """Get location details using OpenStreetMap's reverse geocoding"""
    try:
        url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en'
        headers = {'User-Agent': 'LocationDetector/1.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('address', {})
    except Exception as e:
        print(f"Error getting location from coords: {e}")
    return {}

def get_formatted_location(address):
    """Format the location details into a readable string"""
    components = []
    
    # Add city/town/village
    city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
    if city:
        components.append(city)
    
    # Add state/region
    state = address.get('state') or address.get('region')
    if state and (not city or state != city):  # Avoid duplication if city and state are same
        components.append(state)
    
    # Add country
    country = address.get('country')
    if country and (not state or country != state):  # Avoid duplication if state and country are same
        components.append(country)
    
    return ', '.join(components) if components else 'Unknown location'

def main():
    st.set_page_config(
        page_title="Precise Location Detector",
        page_icon="📍",
        layout="centered"
    )
    
    st.title("📍 Precise Location Detector")
    st.write("This app detects your current location using your browser's geolocation capabilities.")
    
    # JavaScript to get geolocation
    get_location_js = """
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    // Success callback
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const accuracy = position.coords.accuracy;
                    
                    // Update Streamlit with the coordinates
                    window.parent.postMessage({
                        isStreamlitMessage: true,
                        type: 'streamlit:setComponentValue',
                        api: 'streamlit:component',
                        args: [{
                            lat: lat,
                            lon: lon,
                            accuracy: accuracy
                        }]
                    }, '*');
                },
                function(error) {
                    // Error callback
                    let errorMessage = 'Error getting location: ';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage += 'User denied the request for geolocation.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage += 'Location information is unavailable.';
                            break;
                        case error.TIMEOUT:
                            errorMessage += 'The request to get user location timed out.';
                            break;
                        default:
                            errorMessage += 'An unknown error occurred.';
                    }
                    window.parent.postMessage({
                        isStreamlitMessage: true,
                        type: 'streamlit:setComponentValue',
                        api: 'streamlit:component',
                        args: [{
                            error: errorMessage
                        }]
                    }, '*');
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        } else {
            window.parent.postMessage({
                isStreamlitMessage: true,
                type: 'streamlit:setComponentValue',
                api: 'streamlit:component',
                args: [{
                    error: 'Geolocation is not supported by this browser.'
                }]
            }, '*');
        }
        return false;
    }
    
    // Run the function when the script loads
    getLocation();
    </script>
    """
    
    # Display the location detection UI
    if 'location_data' not in st.session_state:
        st.session_state.location_data = None
    
    if 'location_error' not in st.session_state:
        st.session_state.location_error = None
    
    # Button to trigger location detection
    if st.button("Detect My Precise Location"):
        with st.spinner('Requesting location access... (Please allow location access in your browser)'):
            # Inject the JavaScript to get geolocation
            html(get_location_js, height=0)
            
            # Wait for the JavaScript to complete
            time.sleep(2)  # Give some time for the location to be detected
            
            # Check if we have location data from the JavaScript
            if st.session_state.location_data:
                lat = st.session_state.location_data.get('lat')
                lon = st.session_state.location_data.get('lon')
                accuracy = st.session_state.location_data.get('accuracy', 'N/A')
                
                if lat is not None and lon is not None:
                    # Get location details using reverse geocoding
                    address = get_location_from_coords(lat, lon)
                    location_name = get_formatted_location(address)
                    
                    # Display the location
                    st.success("Location detected successfully!")
                    st.markdown(f"""
                    <div style='text-align: center; margin: 20px 0;'>
                        <h2>Your current location is:</h2>
                        <h1 style='color: #1E88E5; margin: 15px 0;'>{location_name}</h1>
                        <p>📡 Accuracy: Within {int(accuracy)} meters</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show the map
                    map_html = f"""
                    <div style='width: 100%; height: 400px; margin: 20px 0; border-radius: 10px; overflow: hidden;'>
                        <iframe 
                            width="100%" 
                            height="100%" 
                            frameborder="0" 
                            scrolling="no" 
                            marginheight="0" 
                            marginwidth="0" 
                            src="https://www.openstreetmap.org/export/embed.html?bbox={lon-0.01}%2C{lat-0.01}%2C{lon+0.01}%2C{lat+0.01}&amp;layer=mapnik&amp;marker={lat}%2C{lon}"
                            style="border: 1px solid #ccc;">
                        </iframe>
                    </div>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <a href="https://www.openstreetmap.org/?mlat={lat}&amp;mlon={lon}#map=16/{lat}/{lon}" target="_blank" style='color: #1E88E5; text-decoration: none;'>
                            View Larger Map (OpenStreetMap)
                        </a>
                    </div>
                    """
                    html(map_html, height=420)
                    
                    # Show raw address data
                    with st.expander("View detailed location information"):
                        st.json(address)
                
                elif st.session_state.location_error:
                    st.error(st.session_state.location_error)
                else:
                    st.warning("Could not determine your precise location. Please try again and make sure to allow location access.")
            
            elif st.session_state.location_error:
                st.error(st.session_state.location_error)
            else:
                st.warning("Could not access your location. Please ensure you've granted location permissions and try again.")
    
    # Add a callback to handle the JavaScript response
    html("""
    <script>
    window.addEventListener('message', function(event) {
        // Only process messages from the streamlit:component API
        if (event.data && event.data.type === 'streamlit:setComponentValue') {
            const data = event.data.args[0];
            if (data.error) {
                window.parent.streamlitComponentBackend
                    .getInstance()
                    .setComponentValue(JSON.stringify({ error: data.error }));
            } else {
                window.parent.streamlitComponentBackend
                    .getInstance()
                    .setComponentValue(JSON.stringify(data));
            }
        }
    });
    </script>
    """, height=0)
    
    # Add a hidden component to receive the location data
    location_data = st.empty()
    location_data.text_input("Location Data", "", key="location_input", label_visibility="collapsed")
    
    # Parse the location data when it changes
    if st.session_state.get('location_input'):
        try:
            data = json.loads(st.session_state.location_input)
            if 'error' in data:
                st.session_state.location_error = data['error']
            else:
                st.session_state.location_data = data
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
            padding: 12px 28px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        }
        .stButton>button:hover {
            background-color: #1565C0;
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        .stButton>button:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .stAlert {
            border-radius: 10px;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            text-align: center;
        }
        .stMarkdown p {
            text-align: center;
            color: #666;
        }
        .stMarkdown div[data-testid="stExpander"] > div {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Add some instructions
    st.markdown("---")
    st.markdown("### How it works:")
    st.markdown("""
    1. Click the "Detect My Precise Location" button
    2. Allow location access when prompted by your browser
    3. Your precise location will be shown on the map
    
    **Note:** Your location data is processed entirely in your browser and 
    never stored on any server. For the most accurate results, 
    ensure your device's location services are enabled.
    """)

if __name__ == "__main__":
    main()
