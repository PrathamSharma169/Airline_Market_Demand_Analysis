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

# Load environment variables
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
        ('BLR', 'Bangalore Kempegowda'),
        ('MAA', 'Chennai International'),
        ('CCU', 'Kolkata Netaji Subhas Chandra Bose'),
        ('HYD', 'Hyderabad Rajiv Gandhi')
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

# Fallback countries (including India)
FALLBACK_COUNTRIES = [
    ('AU', 'Australia'),
    ('US', 'United States'),
    ('GB', 'United Kingdom'),
    ('DE', 'Germany'),
    ('FR', 'France'),
    ('IN', 'India'),
    ('SG', 'Singapore'),
    ('CA', 'Canada'),
    ('NZ', 'New Zealand'),
    ('JP', 'Japan'),
    ('CN', 'China'),
    ('BR', 'Brazil'),
    ('IT', 'Italy'),
    ('ES', 'Spain'),
    ('NL', 'Netherlands')
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
            
            # Ensure India is included
            india_included = any(country[0] == 'IN' for country in countries)
            if not india_included:
                countries.append(('IN', 'India'))
            
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
    airlines = ['Qantas', 'Virgin Australia', 'American Airlines', 'Delta', 'United', 'Emirates', 'British Airways', 'Air India', 'IndiGo', 'SpiceJet']
    flights = []
    
    # Generate 3-7 flights per day
    num_flights = random.randint(3, 7)
    for i in range(num_flights):
        flight_num = f"{random.choice(['QF', 'VA', 'AA', 'DL', 'UA', 'EK', 'BA', 'AI', '6E', 'SG'])}{random.randint(100, 999)}"
        base_price = random.randint(200, 800)
        
        # Add some price variation based on date
        date_obj = datetime.strptime(depart_date, '%Y-%m-%d')
        days_from_today = (date_obj - datetime.now()).days
        
        # Prices tend to be higher closer to departure and on weekends
        if days_from_today < 3:
            price_modifier = 1.3
        elif days_from_today < 7:
            price_modifier = 1.1
        else:
            price_modifier = 1.0
            
        if date_obj.weekday() >= 5:  # Weekend
            price_modifier *= 1.2
            
        price = int(base_price * price_modifier)
        
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
        logger.info(f"Using mock data for {origin} to {destination} on {depart_date}")
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

def get_date_range(selected_date):
    """Get a 10-day date range: 5 days before and 5 days after the selected date."""
    try:
        center_date = datetime.strptime(selected_date, '%Y-%m-%d')
    except ValueError:
        # If invalid date, use today
        center_date = datetime.now()
    
    dates = []
    for i in range(-5, 6):  # -5 to +5 days
        date = center_date + timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    
    return dates

def process_flight_data_multi_date(origin, destination, selected_date, use_mock=True):
    """Process flight data for multiple dates around the selected date."""
    dates = get_date_range(selected_date)
    all_flights = []
    price_trends = []
    
    for date in dates:
        logger.info(f"Fetching data for {date}")
        data = fetch_flight_data(origin, destination, date, use_mock)
        
        if "error" in data:
            continue
            
        if not data or 'data' not in data or not data['data']:
            continue
            
        flights = data['data']
        daily_prices = []
        
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
            
            price = flight.get('price', random.randint(150, 500))
            daily_prices.append(price)
            
            flight_info = {
                'price': price,
                'origin': flight['departure']['iata'],
                'destination': flight['arrival']['iata'],
                'depart_date': flight['flight_date'],
                'depart_time': depart_time,
                'flight_number': flight['flight']['iata'],
                'airline': flight['airline']['name']
            }
            
            all_flights.append(flight_info)
        
        # Calculate average price for this date
        if daily_prices:
            avg_price = sum(daily_prices) / len(daily_prices)
            price_trends.append({
                'depart_date': date,
                'price': round(avg_price, 2)
            })

    if not all_flights:
        return {"error": "No flight data found for the selected date range"}

    df = pd.DataFrame(all_flights)

    # Calculate insights
    avg_price = df['price'].mean() if 'price' in df.columns else 0
    popular_routes = df.groupby(['origin', 'destination']).size().reset_index(name='count').sort_values('count', ascending=False)
    
    # Get flights for the selected date specifically
    selected_date_flights = df[df['depart_date'] == selected_date]
    if selected_date_flights.empty:
        # If no flights for selected date, show flights from the closest available date
        selected_date_flights = df.head(10)

    return {
        'avg_price': round(avg_price, 2),
        'popular_routes': popular_routes.head(5).to_dict(orient='records'),
        'price_trends': price_trends,
        'flights': selected_date_flights.head(10).to_dict(orient='records'),
        'selected_date': selected_date,
        'date_range': dates
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
    selected_date = request.form.get('departure_date')
    
    if not origin or not destination:
        return jsonify({'error': 'Please select both origin and destination airports'})
    
    if not selected_date:
        selected_date = datetime.now().strftime('%Y-%m-%d')
    
    logger.info(f"Analyzing flights from {origin} to {destination} around {selected_date}")
    
    insights = process_flight_data_multi_date(origin, destination, selected_date, use_mock=True)
    
    if insights and "error" not in insights:
        return jsonify(insights)
    else:
        error_msg = insights.get('error', 'No data available for the selected route and date range')
        logger.error(error_msg)
        return jsonify({'error': error_msg})

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Bind to 0.0.0.0 to make it accessible externally on Render
    app.run(host='0.0.0.0', port=port, debug=False)