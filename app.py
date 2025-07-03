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
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('address', {})
    except Exception as e:
        st.error(f"Error getting location details: {e}")
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

def create_location_detector():
    """Create a simple HTML page that handles geolocation"""
    location_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Location Detector</title>
        <style>
            body {
                font-family: 'Source Sans Pro', sans-serif;
                margin: 20px;
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                max-width: 500px;
                width: 90%;
            }
            button {
                background: linear-gradient(45deg, #1E88E5, #1565C0);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                margin: 10px;
                min-width: 200px;
            }
            button:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .result {
                margin-top: 20px;
                padding: 20px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                display: none;
            }
            .error {
                background: rgba(244, 67, 54, 0.8);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                display: none;
            }
            .loading {
                margin: 20px 0;
                display: none;
            }
            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top: 3px solid white;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .coordinates {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📍 Location Detector</h1>
            <p>Click the button below to detect your precise location</p>
            
            <button id="detectBtn" onclick="getLocation()">
                🌍 Detect My Location
            </button>
            
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Getting your location...</p>
            </div>
            
            <div id="result" class="result">
                <h2>📍 Your Location:</h2>
                <div id="locationName"></div>
                <div id="coordinates" class="coordinates"></div>
                <p id="accuracy"></p>
                <button onclick="copyCoordinates()">📋 Copy Coordinates</button>
                <button onclick="openInMaps()">🗺️ Open in Maps</button>
            </div>
            
            <div id="error" class="error"></div>
        </div>

        <script>
            let currentLat, currentLon, currentAccuracy;

            function showLoading() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('detectBtn').disabled = true;
                document.getElementById('result').style.display = 'none';
                document.getElementById('error').style.display = 'none';
            }

            function hideLoading() {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('detectBtn').disabled = false;
            }

            function showError(message) {
                hideLoading();
                document.getElementById('error').textContent = message;
                document.getElementById('error').style.display = 'block';
                document.getElementById('result').style.display = 'none';
            }

            function showResult(lat, lon, accuracy) {
                hideLoading();
                currentLat = lat;
                currentLon = lon;
                currentAccuracy = accuracy;
                
                document.getElementById('coordinates').innerHTML = 
                    `Latitude: ${lat.toFixed(6)}<br>Longitude: ${lon.toFixed(6)}`;
                document.getElementById('accuracy').textContent = 
                    `📡 Accuracy: Within ${Math.round(accuracy)} meters`;
                
                // Get location name
                getLocationName(lat, lon);
                
                document.getElementById('result').style.display = 'block';
                document.getElementById('error').style.display = 'none';
            }

            async function getLocationName(lat, lon) {
                try {
                    const response = await fetch(
                        `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&accept-language=en`,
                        {
                            headers: {
                                'User-Agent': 'LocationDetector/1.0'
                            }
                        }
                    );
                    
                    if (response.ok) {
                        const data = await response.json();
                        const address = data.address || {};
                        
                        const city = address.city || address.town || address.village || address.hamlet;
                        const state = address.state || address.region;
                        const country = address.country;
                        
                        let locationParts = [];
                        if (city) locationParts.push(city);
                        if (state && state !== city) locationParts.push(state);
                        if (country && country !== state) locationParts.push(country);
                        
                        const locationName = locationParts.length > 0 ? locationParts.join(', ') : 'Unknown location';
                        document.getElementById('locationName').innerHTML = `<h3>${locationName}</h3>`;
                    } else {
                        document.getElementById('locationName').innerHTML = '<h3>Location detected</h3>';
                    }
                } catch (error) {
                    document.getElementById('locationName').innerHTML = '<h3>Location detected</h3>';
                }
            }

            function getLocation() {
                if (!navigator.geolocation) {
                    showError('Geolocation is not supported by this browser.');
                    return;
                }

                showLoading();

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
                        showResult(lat, lon, accuracy);
                    },
                    function(error) {
                        let errorMessage = 'Error getting location: ';
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                errorMessage += 'Permission denied. Please enable location access and try again.';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMessage += 'Location information is unavailable. Please check your device settings.';
                                break;
                            case error.TIMEOUT:
                                errorMessage += 'Request timed out. Please try again.';
                                break;
                            default:
                                errorMessage += 'An unknown error occurred.';
                        }
                        showError(errorMessage);
                    },
                    options
                );
            }

            function copyCoordinates() {
                if (currentLat && currentLon) {
                    const text = `${currentLat}, ${currentLon}`;
                    navigator.clipboard.writeText(text).then(() => {
                        alert('Coordinates copied to clipboard!');
                    }).catch(() => {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = text;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        alert('Coordinates copied to clipboard!');
                    });
                }
            }

            function openInMaps() {
                if (currentLat && currentLon) {
                    window.open(`https://www.openstreetmap.org/?mlat=${currentLat}&mlon=${currentLon}#map=16/${currentLat}/${currentLon}`, '_blank');
                }
            }
        </script>
    </body>
    </html>
    """
    return location_html

def main():
    st.set_page_config(
        page_title="Precise Location Detector",
        page_icon="📍",
        layout="wide"
    )
    
    st.title("📍 Precise Location Detector")
    
    # Create tabs for different approaches
    st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre;
            background-color: #f0f2f6;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding: 0 16px;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e1e4e8;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: white;
            border-bottom: 2px solid #1E88E5;
        }
    </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌐 Web Detector", 
        "📊 Manual Input", 
        "ℹ️ Instructions", 
        "🔌 WordPress Plugin"
    ])
    
    with tab1:
        st.markdown("""
        ### Browser-Based Location Detection
        This detector works entirely in your browser and provides the most accurate results.
        """)
        
        # Display the location detector in an iframe
        html(create_location_detector(), height=600)
        
        st.markdown("""
        ---
        **🔒 Privacy:** Your location is processed entirely in your browser. No data is sent to servers except for the optional address lookup.
        """)
    
    with tab2:
        st.markdown("""
        ### Manual Coordinate Input
        If the browser detection doesn't work, you can manually enter coordinates.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            manual_lat = st.number_input("Latitude", value=0.0, format="%.6f", help="Enter latitude (-90 to 90)")
        with col2:
            manual_lon = st.number_input("Longitude", value=0.0, format="%.6f", help="Enter longitude (-180 to 180)")
        
        if st.button("🔍 Look Up Location", type="primary"):
            if manual_lat != 0.0 or manual_lon != 0.0:
                with st.spinner('Getting location details...'):
                    address = get_location_from_coords(manual_lat, manual_lon)
                    location_name = get_formatted_location(address)
                
                st.success("Location found!")
                st.markdown(f"""
                <div style='text-align: center; margin: 20px 0;'>
                    <h2>Location:</h2>
                    <h1 style='color: #1E88E5; margin: 15px 0;'>{location_name}</h1>
                </div>
                """, unsafe_allow_html=True)
                
                # Show coordinates
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Latitude", f"{manual_lat:.6f}")
                with col2:
                    st.metric("Longitude", f"{manual_lon:.6f}")
                
                # Show map
                map_html = f"""
                <div style='width: 100%; height: 400px; margin: 20px 0; border-radius: 10px; overflow: hidden; border: 1px solid #ddd;'>
                    <iframe 
                        width="100%" 
                        height="100%" 
                        frameborder="0" 
                        scrolling="no" 
                        marginheight="0" 
                        marginwidth="0" 
                        src="https://www.openstreetmap.org/export/embed.html?bbox={manual_lon-0.01}%2C{manual_lat-0.01}%2C{manual_lon+0.01}%2C{manual_lat+0.01}&amp;layer=mapnik&amp;marker={manual_lat}%2C{manual_lon}"
                        style="border: 0;">
                    </iframe>
                </div>
                """
                st.markdown(map_html, unsafe_allow_html=True)
                
                # Show address details
                with st.expander("🔍 Detailed location information"):
                    st.json(address)
            else:
                st.warning("Please enter valid coordinates")
    
    with tab3:
        st.markdown("""
        ### 📱 How to Use This App
        
        #### Browser Detection (Recommended)
        1. Go to the **Web Detector** tab
        2. Click "Detect My Location" 
        3. Allow location access when prompted
        4. View your precise location with map
        
        #### Manual Input (Backup)
        1. Go to the **Manual Input** tab
        2. Enter your latitude and longitude coordinates
        3. Click "Look Up Location" to see details
        
        ### 🛠️ Troubleshooting
        
        **If location detection fails:**
        - ✅ Enable location services on your device
        - ✅ Allow location access for your browser
        - ✅ Use HTTPS (secure connection)
        - ✅ Try a different browser (Chrome recommended)
        - ✅ Check if JavaScript is enabled
        
        **Getting your coordinates manually:**
        - Use your phone's GPS app
        - Check Google Maps (right-click → "What's here?")
        - Use any GPS device or app
        
        ### 🌐 Browser Compatibility
        
        | Browser | Support | Notes |
        |---------|---------|-------|
        | Chrome | ✅ Excellent | Recommended |
        | Firefox | ✅ Excellent | Works great |
        | Safari | ✅ Good | May need permission |
        | Edge | ✅ Good | Works well |
        | Mobile | ✅ Excellent | Usually most accurate |
        
        ### 🔒 Privacy & Security
        
        - **No data storage**: Your location is never saved
        - **Browser-only**: Processing happens in your browser
        - **Optional lookup**: Address lookup uses OpenStreetMap
        - **No tracking**: No cookies or user tracking
        - **Open source**: Code is transparent and auditable
        
        ### 📍 Accuracy Information
        
        - **GPS devices**: Usually 3-5 meters
        - **Smartphones**: Usually 5-10 meters  
        - **WiFi/Cell**: Usually 10-100+ meters
        - **Desktop**: Varies widely (IP-based fallback)
        
        For best accuracy, use a smartphone with GPS enabled.
        """)
    
    with tab4:
        st.markdown("# 🌍 WordPress Location Detector Plugin")
        st.markdown("""
        Enhance your WordPress website with our easy-to-use location detection plugin. 
        This plugin allows you to show location-based content to your visitors.
        """)
        
        st.markdown("### 🚀 Features")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            - ✅ Simple installation and setup
            - ✅ Automatic location detection
            - ✅ Mobile-friendly design
            - ✅ Lightweight and fast
            - ✅ Compatible with all modern themes
            """)
        
        st.markdown("### 📋 Requirements")
        st.markdown("""
        - WordPress 5.0 or higher
        - PHP 7.4 or higher
        - JavaScript enabled in visitor's browser
        """)
        
        st.markdown("### 📥 Installation")
        st.markdown("""
        1. Download the plugin zip file below
        2. Go to WordPress Admin > Plugins > Add New
        3. Click "Upload Plugin" and select the downloaded zip file
        4. Activate the plugin
        5. Configure the settings in WordPress admin
        """)
        
        # Add download button for the plugin with error handling
        try:
            with open("geocity.zip", "rb") as file:
                btn = st.download_button(
                    label="⬇️ Download WordPress Plugin",
                    data=file,
                    file_name="geocity-location-detector.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"Error loading plugin file: {e}")
            st.info("Please make sure 'geocity.zip' exists in the project directory.")
        
        st.markdown("### 📝 Support")
        st.markdown("""
        Need help with the plugin? Contact our support team at support@example.com
        
        ### 🔄 Version
        Current version: 1.0.0  
        Last updated: July 2024
        """)

if __name__ == "__main__":
    main()