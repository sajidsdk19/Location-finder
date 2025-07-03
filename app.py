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
        st.error(f"Error getting location from coords: {e}")
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
    if state and (not city or state != city):
        components.append(state)
    
    # Add country
    country = address.get('country')
    if country and (not state or country != state):
        components.append(country)
    
    return ', '.join(components) if components else 'Unknown location'

def create_location_component():
    """Create a custom component that handles geolocation"""
    location_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/streamlit-component-lib@1.3.0/dist/streamlit-component-lib.js"></script>
    </head>
    <body>
        <div id="location-container">
            <button id="get-location-btn" onclick="getLocation()" style="
                background-color: #1E88E5;
                color: white;
                font-weight: bold;
                border: none;
                padding: 12px 28px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 10px 0;
                width: 100%;
            ">
                🌍 Detect My Precise Location
            </button>
            <div id="status" style="margin-top: 10px; text-align: center;"></div>
        </div>

        <script>
            function setStatus(message, isError = false) {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = message;
                statusDiv.style.color = isError ? 'red' : 'green';
            }

            function getLocation() {
                const button = document.getElementById('get-location-btn');
                button.disabled = true;
                button.innerHTML = '🔍 Getting location...';
                
                setStatus('Requesting location access... Please allow location access in your browser.');
                
                if (!navigator.geolocation) {
                    setStatus('❌ Geolocation is not supported by this browser.', true);
                    button.disabled = false;
                    button.innerHTML = '🌍 Detect My Precise Location';
                    Streamlit.setComponentValue({error: 'Geolocation not supported'});
                    return;
                }

                const options = {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                };

                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const accuracy = position.coords.accuracy;
                        
                        setStatus('✅ Location detected successfully!');
                        
                        // Send data back to Streamlit
                        Streamlit.setComponentValue({
                            lat: lat,
                            lon: lon,
                            accuracy: accuracy,
                            success: true
                        });
                        
                        button.disabled = false;
                        button.innerHTML = '🌍 Detect My Precise Location';
                    },
                    function(error) {
                        let errorMessage = 'Error getting location: ';
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                errorMessage += 'User denied the request for geolocation. Please enable location access and try again.';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMessage += 'Location information is unavailable. Please check your device settings.';
                                break;
                            case error.TIMEOUT:
                                errorMessage += 'The request to get user location timed out. Please try again.';
                                break;
                            default:
                                errorMessage += 'An unknown error occurred.';
                        }
                        
                        setStatus('❌ ' + errorMessage, true);
                        
                        Streamlit.setComponentValue({
                            error: errorMessage,
                            success: false
                        });
                        
                        button.disabled = false;
                        button.innerHTML = '🌍 Detect My Precise Location';
                    },
                    options
                );
            }

            // Initialize Streamlit component
            Streamlit.setComponentReady();
        </script>
    </body>
    </html>
    """
    
    return html(location_html, height=120)

def main():
    st.set_page_config(
        page_title="Precise Location Detector",
        page_icon="📍",
        layout="centered"
    )
    
    st.title("📍 Precise Location Detector")
    st.write("This app detects your current location using your browser's geolocation capabilities.")
    
    # Initialize session state
    if 'location_detected' not in st.session_state:
        st.session_state.location_detected = False
    
    # Create the location detection component
    location_result = create_location_component()
    
    # Process the location result
    if location_result:
        if location_result.get('success'):
            lat = location_result.get('lat')
            lon = location_result.get('lon')
            accuracy = location_result.get('accuracy', 'N/A')
            
            if lat is not None and lon is not None:
                st.session_state.location_detected = True
                st.session_state.lat = lat
                st.session_state.lon = lon
                st.session_state.accuracy = accuracy
                
                # Get location details using reverse geocoding
                with st.spinner('Getting location details...'):
                    address = get_location_from_coords(lat, lon)
                    location_name = get_formatted_location(address)
                
                # Display the location
                st.success("Location detected successfully!")
                st.markdown(f"""
                <div style='text-align: center; margin: 20px 0;'>
                    <h2>Your current location is:</h2>
                    <h1 style='color: #1E88E5; margin: 15px 0;'>{location_name}</h1>
                    <p>📡 Accuracy: Within {int(float(accuracy))} meters</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show coordinates
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Latitude", f"{lat:.6f}")
                with col2:
                    st.metric("Longitude", f"{lon:.6f}")
                
                # Show the map
                st.subheader("📍 Location on Map")
                map_html = f"""
                <div style='width: 100%; height: 400px; margin: 20px 0; border-radius: 10px; overflow: hidden; border: 1px solid #ddd;'>
                    <iframe 
                        width="100%" 
                        height="100%" 
                        frameborder="0" 
                        scrolling="no" 
                        marginheight="0" 
                        marginwidth="0" 
                        src="https://www.openstreetmap.org/export/embed.html?bbox={lon-0.01}%2C{lat-0.01}%2C{lon+0.01}%2C{lat+0.01}&amp;layer=mapnik&amp;marker={lat}%2C{lon}"
                        style="border: 0;">
                    </iframe>
                </div>
                <div style='text-align: center; margin-bottom: 20px;'>
                    <a href="https://www.openstreetmap.org/?mlat={lat}&amp;mlon={lon}#map=16/{lat}/{lon}" target="_blank" style='color: #1E88E5; text-decoration: none;'>
                        🗺️ View Larger Map (OpenStreetMap)
                    </a>
                </div>
                """
                st.markdown(map_html, unsafe_allow_html=True)
                
                # Show raw address data
                with st.expander("🔍 View detailed location information"):
                    st.json(address)
                
                # Show raw coordinates
                with st.expander("📊 Raw coordinate data"):
                    st.json({
                        "latitude": lat,
                        "longitude": lon,
                        "accuracy_meters": accuracy
                    })
        
        elif location_result.get('error'):
            st.error(location_result.get('error'))
            st.markdown("""
            ### 🛠️ Troubleshooting Tips:
            
            1. **Check browser permissions**: Make sure location access is enabled for this website
            2. **Enable location services**: Ensure your device's location services are turned on
            3. **Try a different browser**: Some browsers have stricter location policies
            4. **Use HTTPS**: Location services work better on secure connections
            5. **Check network connection**: Make sure you have a stable internet connection
            """)
    
    # Add styling
    st.markdown("""
    <style>
        .stAlert {
            border-radius: 10px;
        }
        .stMetric {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }
        .stExpander {
            border: 1px solid #ddd;
            border-radius: 10px;
            margin: 10px 0;
        }
        .stExpander > div {
            padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Add instructions
    st.markdown("---")
    st.markdown("### ℹ️ How it works:")
    st.markdown("""
    1. Click the "Detect My Precise Location" button above
    2. Allow location access when prompted by your browser
    3. Your precise location will be shown with coordinates and map
    
    **🔒 Privacy Note:** Your location data is processed entirely in your browser and 
    never stored on any server. The app only uses your location to show you where you are.
    """)
    
    # Add browser compatibility info
    with st.expander("🌐 Browser Compatibility"):
        st.markdown("""
        **Supported Browsers:**
        - ✅ Chrome/Chromium (recommended)
        - ✅ Firefox
        - ✅ Safari
        - ✅ Edge
        - ⚠️ Internet Explorer (limited support)
        
        **Requirements:**
        - HTTPS connection (for security)
        - Location services enabled on device
        - JavaScript enabled in browser
        """)

if __name__ == "__main__":
    main()