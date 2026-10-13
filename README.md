# Atmosphere — Weather & Forecast Application

A modern desktop weather application built with Python and Tkinter, powered by the OpenWeatherMap API and IP geolocation.

---

## Features

- **Automatic Location Detection**: Automatically detects and loads the weather for your current city on startup via IP geolocation.
- **Search Any City**: Search current weather and forecast for any city or ZIP code worldwide.
- **Current Weather Conditions**: Displays real-time temperature, condition description, weather icon, humidity percentage, and wind speed.
- **Hourly Forecast**: Timeline view of the forecast for the next 6 hours (in 3-hour intervals).
- **5-Day Daily Forecast**: Clean card view showing expected weather and temperatures across the next 5 days.
- **Unit Switching**: Easily toggle between Metric (°C, m/s) and Imperial (°F, mph) with a single click.
- **Dark Theme UI**: Clean, slate-themed modern interface.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/mohammadalihaji/Weather_app.git
cd Weather_app
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key
1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api).
2. Copy the `.env.example` file to create `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and paste your API key:
   ```env
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
   ```

---

## Running the Application

Execute the Python script:
```bash
python app.py
```

---

## Project Structure

```text
├── app.py              # Main Tkinter desktop application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore configuration
└── README.md           # Project documentation
```

---

## License
This project is open-source and available under the MIT License.
