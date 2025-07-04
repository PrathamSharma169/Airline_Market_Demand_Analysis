# ✈️ Airline Market Demand Analysis Tool

A comprehensive web application that provides flight data analysis and insights using the AviationStack API. This tool helps users analyze flight routes, pricing trends, and market demand patterns between different countries and airports.

## 🌟 Features

- **Dynamic Country Selection**: Choose from a comprehensive list of countries for both origin and destination
- **Airport Filtering**: Automatically populate airports based on selected countries
- **Flight Data Analysis**: Get detailed insights including:
  - Average flight prices
  - Popular routes analysis
  - Price trend visualization
  - Available flights with schedules
- **Interactive Dashboard**: Modern, responsive UI with charts and tables
- **Mock Data Support**: Fallback to mock data for testing when API limits are reached
- **Error Handling**: Robust error handling with user-friendly messages

## 🚀 Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Processing**: Pandas for data analysis
- **Visualization**: Chart.js for interactive charts
- **API Integration**: AviationStack API for flight data
- **Environment Management**: python-dotenv for configuration

## 📋 Prerequisites

- Python 3.7 or higher
- AviationStack API key (free tier available)
- Internet connection for API calls

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   API_KEY=your_aviationstack_api_key_here
   ```

5. **Get your AviationStack API key**
   - Visit [AviationStack](https://aviationstack.com/)
   - Sign up for a free account
   - Copy your API key to the `.env` file

## 🎯 Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

3. **Use the application**
   - Select origin country and airport
   - Select destination country and airport
   - Click "Analyze Flight Data"
   - View comprehensive flight analysis results

## 📊 Features Explained

### Country and Airport Selection
- Dynamic dropdown menus that populate based on available data
- Fallback airports for major countries to ensure functionality
- Real-time airport loading based on country selection

### Flight Analysis
- **Average Price Calculation**: Computes mean prices across all available flights
- **Popular Routes**: Identifies the most frequently available routes
- **Price Trends**: Visualizes price variations over different dates
- **Flight Listings**: Shows detailed flight information including airlines, schedules, and prices

### Data Visualization
- Interactive line charts showing price trends over time
- Statistical cards displaying key metrics
- Responsive tables for route and flight data
- Modern, gradient-based UI design

## 🔧 Configuration

### API Configuration
The application uses the AviationStack API with the following endpoints:
- `countries`: Fetches available countries
- `airports`: Gets airports for specific countries
- `schedules`: Retrieves flight schedule data

### Fallback Data
The application includes hardcoded fallback data for:
- Major countries (US, UK, Australia, etc.)
- Popular airports in each country
- Mock flight data for testing

### Environment Variables
- `API_KEY`: Your AviationStack API key
- `DEBUG`: Set to `True` for development mode

## 📁 Project Structure

```
airline-market-demand-analysis/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend template
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── README.md            # Project documentation
└── .gitignore           # Git ignore file
```

## 🎨 UI/UX Features

- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern Gradient Design**: Beautiful purple-blue gradient theme
- **Interactive Elements**: Hover effects, smooth transitions, and loading states
- **Error Handling**: User-friendly error messages and fallback options
- **Loading States**: Visual feedback during data fetching

## 🔄 Data Flow

1. User selects origin country → Airports are fetched and populated
2. User selects destination country → Airports are fetched and populated
3. User clicks analyze → Multiple API calls are made for different dates
4. Data is processed using Pandas for insights
5. Results are displayed with charts and tables

## 📈 Analytics Capabilities

- **Price Analysis**: Calculate average prices, identify trends
- **Route Popularity**: Determine most common flight routes
- **Temporal Analysis**: Track price changes over time
- **Market Insights**: Comprehensive overview of flight availability

## 🛡️ Error Handling

- API rate limit management
- Fallback to mock data when API fails
- User-friendly error messages
- Graceful degradation of features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

For support and questions:
- Check the AviationStack API documentation
- Review the error messages in the browser console
- Ensure your API key is valid and has remaining quota

## 🔮 Future Enhancements

- Integration with multiple flight APIs
- Advanced filtering options
- Export functionality for reports
- Historical data tracking
- Price prediction models
- Email alerts for price changes

## 📞 Contact

For any questions or suggestions, please open an issue on the repository.