import streamlit as st
import requests
from streamlit.components.v1 import html

def get_user_city():
    try:
        # Get user's IP address
        ip_response = requests.get('https://api.ipify.org?format=json')
        ip = ip_response.json().get('ip')
        
        # Get location data based on IP
        location_response = requests.get(f'http://ip-api.com/json/{ip}?fields=status,message,city')
        location_data = location_response.json()
        
        if location_data.get('status') == 'success':
            return location_data.get('city', 'Your City')
        return 'Your City'
    except:
        return 'Your City'

def main():
    st.set_page_config(
        page_title="City Detector",
        page_icon="🌍",
        layout="centered"
    )
    
    st.title("🌍 City Detector")
    st.write("This app detects your current city based on your IP address.")
    
    if st.button("Detect My City"):
        with st.spinner('Detecting your location...'):
            city = get_user_city()
            st.success(f"Your detected city is: **{city}**")
            
            # Display the city in a larger, more prominent way
            st.markdown(f"""
            <div style='text-align: center; margin: 20px 0;'>
                <h2>Welcome to <span style='color: #1E88E5;'>{city}</span>!</h2>
            </div>
            """, unsafe_allow_html=True)
    
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
