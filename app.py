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

def inject_location_script():
    """Inject JavaScript to get location and store in session state"""
    location_js = f"""
    <script>
    function getLocationData() {{
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(
                function(position) {{
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const accuracy = position.coords.accuracy;
                    
                    // Store in localStorage temporarily
                    localStorage.setItem('streamlit_location_data', JSON.stringify({{
                        lat: lat,
                        lon: lon,
                        accuracy: accuracy,
                        timestamp: Date.now()
                    }}));
                    
                    // Trigger a page refresh to update Streamlit
                    window.location.reload();
                }},
                function(error) {{
                    let errorMessage = 'Error getting location: ';
                    switch(error.code) {{
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
                    }}
                    
                    localStorage.setItem('streamlit_location_error', errorMessage);
                    window.location.reload();
                }},
                {{
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                }}
            );
        }} else {{
            localStorage.setItem('streamlit_location_error', 'Geolocation is not supported by this browser.');
            window.location.reload();
        }}
    }}
    
    // Auto-run if we're in detection mode
    if (localStorage.getItem('streamlit_detecting_location') === 'true') {{
        localStorage.removeItem('streamlit_detecting_location');
        getLocationData();
    }}
    </script>
    """
    return location_js

def check_for_location_data():
    """Check if location data is available from JavaScript"""
    check_js = """
    <script>
    // Check for location data
    const locationData = localStorage.getItem('streamlit_location_data');
    const locationError = localStorage.getItem('streamlit_location_error');
    
    if (locationData) {
        // Clear the data after reading
        localStorage.removeItem('streamlit_location_data');
        
        // Send data to Streamlit via a form
        const data = JSON.parse(locationData);
        const form = document.createElement('form');
        form.method = 'POST';
        form.style.display = 'none';
        
        const latInput = document.createElement('input');
        latInput.name = 'lat';
        latInput.value = data.lat;
        form.appendChild(latInput);
        
        const lonInput = document.createElement('input');
        lonInput.name = 'lon';
        lonInput.value = data.lon;
        form.appendChild(lonInput);
        
        const accInput = document.createElement('input');
        accInput.name = 'accuracy';
        accInput.value = data.accuracy;
        form.appendChild(accInput);
        
        document.body.appendChild(form);
        
        // Update URL with parameters
        const params = new URLSearchParams(window.location.search);
        params.set('lat', data.lat);
        params.set('lon', data.lon);
        params.set('accuracy', data.accuracy);
        window.history.replaceState({}, '', `${window.location.pathname}?${params}`);
        
        // Trigger rerun
        window.location.reload();
    } else if (locationError) {
        localStorage.removeItem('streamlit_location_error');
        
        // Update URL with error
        const params = new URLSearchParams(window.location.search);
        params.set('error', encodeURIComponent(locationError));
        window.history.replaceState({}, '', `${window.location.pathname}?${params}`);
        
        // Trigger rerun
        window.location.reload();
    }
    </script>
    """
    html(check_js, height=0)

def main():
    st.set_page_config(
        page_title="Precise Location Detector",
        page_icon="📍",
        layout="centered"
    )
    
    st.title("📍 Precise Location Detector")
    st.write("This app detects your current location using your browser's geolocation capabilities.")
    
    # Inject the location detection script
    html(inject_location_script(), height=0)
    
    # Check for location data from URL parameters
    query_params = st.query_params
    lat = query_params.get('lat')
    lon = query_params.get('lon')
    accuracy = query_params.get('accuracy')
    error = query_params.get('error')
    
    if lat and lon:
        try:
            lat = float(lat)
            lon = float(lon)
            accuracy = float(accuracy) if accuracy else 'N/A'
            
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
                <p>📡 Accuracy: Within {int(accuracy)} meters</p>
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
            
            # Clear button
            if st.button("🔄 Detect Location Again"):
                # Clear query params and reload
                st.query_params.clear()
                st.rerun()
                
        except (ValueError, TypeError) as e:
            st.error(f"Invalid location data received: {e}")
            
    elif error:
        st.error(error)
        st.markdown("""
        ### 🛠️ Troubleshooting Tips:
        
        1. **Check browser permissions**: Make sure location access is enabled for this website
        2. **Enable location services**: Ensure your device's location services are turned on
        3. **Try a different browser**: Some browsers have stricter location policies
        4. **Use HTTPS**: Location services work better on secure connections
        5. **Check network connection**: Make sure you have a stable internet connection
        """)
        
        # Clear error and try again button
        if st.button("🔄 Try Again"):
            st.query_params.clear()
            st.rerun()
    
    else:
        # Main location detection interface
        st.markdown("""
        <div style='text-align: center; margin: 30px 0;'>
            <p style='font-size: 18px; color: #666; margin-bottom: 20px;'>
                Click the button below to detect your precise location
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Location detection button
        if st.button("🌍 Detect My Precise Location", type="primary"):
            # Set flag for JavaScript to detect location
            detect_js = """
            <script>
            localStorage.setItem('streamlit_detecting_location', 'true');
            window.location.reload();
            </script>
            """
            html(detect_js, height=0)
            st.info("🔄 Initializing location detection...")
    
    # Check for any pending location data
    check_for_location_data()
    
    # Add styling
    st.markdown("""
    <style>
        .stButton > button {
            width: 100%;
            background-color: #1E88E5;
            color: white;
            font-weight: bold;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 18px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
        }
        .stButton > button:hover {
            background-color: #1565C0;
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
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
    </style>
    """, unsafe_allow_html=True)
    
    # Add instructions
    st.markdown("---")
    st.markdown("### ℹ️ How it works:")
    st.markdown("""
    1. Click the "Detect My Precise Location" button
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