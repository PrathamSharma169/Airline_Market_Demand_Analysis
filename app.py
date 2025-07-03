from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
import json
import random
from dotenv import load_dotenv
import os
load_dotenv()


app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration for AviationStack API
API_KEY = os.environ.get("API_KEY") # Replace with your AviationStack API key
BASE_URL = "http://api.aviationstack.com/v1/"

# Cache for countries and airports to reduce API calls
COUNTRY_CACHE = {}
AIRPORT_CACHE = {}

# Fallback airports for multiple countries
FALLBACK_AIRPORTS = {
    'AU': [
        ('SYD', 'Sydney Kingsford Smith'),
        ('MEL', 'Melbourne Tullamarine'),
        ('BNE', 'Brisbane'),
        ('PER', 'Perth'),
        ('ADL', 'Adelaide')
    ],
    'NZ': [
        ('AKL', 'Auckland'),
        ('CHC', 'Christchurch'),
        ('WLG', 'Wellington')
    ],
    'US': [
        ('LAX', 'Los Angeles International'),
        ('JFK', 'John F. Kennedy International'),
        ('ORD', 'Chicago O\'Hare'),
        ('DFW', 'Dallas Fort Worth'),
        ('ATL', 'Atlanta Hartsfield-Jackson')
    ],
    'GB': [
        ('LHR', 'London Heathrow'),
        ('LGW', 'London Gatwick'),
        ('MAN', 'Manchester')
    ],
    'DE': [
        ('FRA', 'Frankfurt'),
        ('MUC', 'Munich'),
        ('BER', 'Berlin Brandenburg')
    ],
    'FR': [
        ('CDG', 'Paris Charles de Gaulle'),
        ('ORY', 'Paris Orly'),
        ('NCE', 'Nice')
    ],
    'IN': [
        ('DEL', 'Delhi Indira Gandhi'),
        ('BOM', 'Mumbai Chhatrapati Shivaji'),
        ('BLR', 'Bangalore')
    ],
    'SG': [
        ('SIN', 'Singapore Changi')
    ],
    'CA': [
        ('YYZ', 'Toronto Pearson'),
        ('YVR', 'Vancouver'),
        ('YUL', 'Montreal')
    ]
}

# Fallback countries
FALLBACK_COUNTRIES = [
    ('AU', 'Australia'),
    ('US', 'United States'),
    ('GB', 'United Kingdom'),
    ('DE', 'Germany'),
    ('FR', 'France'),
    ('IN', 'India'),
    ('SG', 'Singapore'),
    ('CA', 'Canada'),
    ('NZ', 'New Zealand')
]

def fetch_countries():
    """Fetch all countries from AviationStack API with caching."""
    if COUNTRY_CACHE:
        logger.info("Using cached countries")
        return COUNTRY_CACHE['countries']
    
    endpoint = "countries"
    url = f"{BASE_URL}{endpoint}"
    params = {'access_key': API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        logger.debug(f"Countries API Request URL: {response.url}")
        logger.debug(f"Countries API Response Status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and data['data']:
            countries = [(country['country_iso2'], country['country_name']) 
                        for country in data['data'] 
                        if country.get('country_iso2') and country.get('country_name')]
            COUNTRY_CACHE['countries'] = sorted(countries, key=lambda x: x[1])
            return COUNTRY_CACHE['countries']
        else:
            logger.warning("No countries data in API response, using fallback")
            COUNTRY_CACHE['countries'] = FALLBACK_COUNTRIES
            return COUNTRY_CACHE['countries']
            
    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        logger.info("Using fallback countries")
        COUNTRY_CACHE['countries'] = FALLBACK_COUNTRIES
        return COUNTRY_CACHE['countries']

def fetch_airports(country_iso2):
    """Fetch airports for a given country ISO2 code from AviationStack API with caching."""
    if country_iso2 in AIRPORT_CACHE:
        logger.info(f"Using cached airports for {country_iso2}")
        return AIRPORT_CACHE[country_iso2]
    
    # First check if we have fallback airports for this country
    if country_iso2 in FALLBACK_AIRPORTS:
        AIRPORT_CACHE[country_iso2] = FALLBACK_AIRPORTS[country_iso2]
        return AIRPORT_CACHE[country_iso2]
    
    endpoint = "airports"
    url = f"{BASE_URL}{endpoint}"
    params = {
        'access_key': API_KEY,
        'country_iso2': country_iso2
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        logger.debug(f"Airports API Request URL: {response.url}")
        logger.debug(f"Airports API Response Status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and data['data']:
            airports = [(airport['iata_code'], airport['airport_name']) 
                       for airport in data['data'] 
                       if airport.get('iata_code')]
            AIRPORT_CACHE[country_iso2] = airports if airports else FALLBACK_AIRPORTS.get(country_iso2, [])
        else:
            AIRPORT_CACHE[country_iso2] = FALLBACK_AIRPORTS.get(country_iso2, [])
            
        return AIRPORT_CACHE[country_iso2]
        
    except Exception as e:
        logger.error(f"Error fetching airports for {country_iso2}: {e}")
        AIRPORT_CACHE[country_iso2] = FALLBACK_AIRPORTS.get(country_iso2, [])
        return AIRPORT_CACHE[country_iso2]

def generate_mock_flight_data(origin, destination, depart_date):
    """Generate mock flight data for testing."""
    airlines = ['Qantas', 'Virgin Australia', 'American Airlines', 'Delta', 'United', 'Emirates', 'British Airways', 'Air India']
    flights = []
    
    for i in range(5):
        flight_num = f"{random.choice(['QF', 'VA', 'AA', 'DL', 'UA', 'EK', 'BA', 'AI'])}{random.randint(100, 999)}"
        price = random.randint(150, 800)
        time_hour = random.randint(6, 22)
        time_min = random.choice([0, 15, 30, 45])
        
        flights.append({
            "flight_date": depart_date,
            "flight": {"iata": flight_num},
            "airline": {"name": random.choice(airlines)},
            "departure": {
                "iata": origin,
                "scheduled": f"{depart_date}T{time_hour:02d}:{time_min:02d}:00+00:00"
            },
            "arrival": {"iata": destination},
            "price": price
        })
    
    return {"data": flights}

def fetch_flight_data(origin, destination, depart_date, use_mock=True):
    """Fetch flight data from AviationStack API or use mock data."""
    if use_mock:
        logger.info("Using mock data for testing")
        return generate_mock_flight_data(origin, destination, depart_date)

    endpoint = "schedules"
    url = f"{BASE_URL}{endpoint}"
    params = {
        'access_key': API_KEY,
        'dep_iata': origin,
        'arr_iata': destination,
        'flight_date': depart_date
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        logger.debug(f"Flights API Request URL: {response.url}")
        logger.debug(f"Flights API Response Status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and data['data']:
            return data
        else:
            logger.warning("No flight data from API, using mock data")
            return generate_mock_flight_data(origin, destination, depart_date)
            
    except Exception as e:
        logger.error(f"Error fetching flight data: {e}")
        logger.info("Using mock data due to API error")
        return generate_mock_flight_data(origin, destination, depart_date)

def process_flight_data(data):
    """Process flight data to extract insights."""
    if "error" in data:
        return {"error": data["error"]}
    
    if not data or 'data' not in data or not data['data']:
        logger.warning("No flight data available in API response")
        return {"error": "No flight data available"}

    flights = data['data']
    processed_flights = []
    
    for flight in flights:
        if not flight.get('flight'):
            continue
            
        scheduled_time = flight['departure'].get('scheduled', '')
        depart_time = 'N/A'
        if scheduled_time:
            try:
                depart_time = scheduled_time.split('T')[1][:5]
            except:
                depart_time = 'N/A'
        
        processed_flights.append({
            'price': flight.get('price', random.randint(150, 500)),
            'origin': flight['departure']['iata'],
            'destination': flight['arrival']['iata'],
            'depart_date': flight['flight_date'],
            'depart_time': depart_time,
            'flight_number': flight['flight']['iata'],
            'airline': flight['airline']['name']
        })

    if not processed_flights:
        logger.warning("No processed flights available")
        return {"error": "No valid flight data found"}

    df = pd.DataFrame(processed_flights)

    # Calculate insights
    avg_price = df['price'].mean() if 'price' in df.columns else 0
    popular_routes = df.groupby(['origin', 'destination']).size().reset_index(name='count').sort_values('count', ascending=False)
    price_trends = df.groupby('depart_date')['price'].mean().reset_index() if 'price' in df.columns else pd.DataFrame({'depart_date': [], 'price': []})

    return {
        'avg_price': round(avg_price, 2),
        'popular_routes': popular_routes.head(5).to_dict(orient='records'),
        'price_trends': price_trends.to_dict(orient='records'),
        'flights': df[['flight_number', 'airline', 'depart_date', 'depart_time', 'price']].head(10).to_dict(orient='records')
    }

@app.route('/')
def index():
    """Render the main page with input form."""
    countries = fetch_countries()
    return render_template('index.html', countries=countries)

@app.route('/get_airports/<country_iso2>')
def get_airports(country_iso2):
    """Return airports for the selected country ISO2 code."""
    airports = fetch_airports(country_iso2)
    return jsonify(airports)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle form submission and display results."""
    origin = request.form.get('origin')
    destination = request.form.get('destination')
    
    if not origin or not destination:
        return jsonify({'error': 'Please select both origin and destination airports'})
    
    # Try multiple dates to increase chances of data
    dates = [(datetime.now() + timedelta(days=d)).strftime('%Y-%m-%d') for d in [0, 1, 7, 14]]
    insights = None
    errors = []

    for date in dates:
        logger.info(f"Trying date: {date} for {origin} to {destination}")
        data = fetch_flight_data(origin, destination, date, use_mock=True)  # Using mock data for demo
        if "error" in data:
            errors.append(f"Date {date}: {data['error']}")
            continue
        insights = process_flight_data(data)
        if insights and "error" not in insights:
            break

    if not insights or "error" in insights:
        error_msg = insights.get('error', 'No data available for the selected route')
        logger.error(error_msg)
        return jsonify({'error': error_msg})

    return jsonify(insights)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    app.run(debug=True)