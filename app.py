import os
import io
import datetime
from pathlib import Path
import requests
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv

# Path to .env in the same directory as app.py
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
IPINFO_URL = "https://ipinfo.io/json"


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Atmosphere — Weather & Forecast")
        self.root.geometry("850x700")
        self.root.resizable(False, False)
        
        # Color Palette
        self.bg_color = "#1E1E2E"        # Dark slate
        self.card_bg = "#2B2B3D"         # Card container bg
        self.accent_color = "#89B4FA"    # Soft neon blue
        self.text_primary = "#CDD6F4"    # Bright light text
        self.text_secondary = "#A6ADC8"  # Soft gray text
        self.error_color = "#F38BA8"     # Soft red
        
        self.root.configure(bg=self.bg_color)

        # State Variables
        self.unit = "metric"  # 'metric' = Celsius (°C, m/s), 'imperial' = Fahrenheit (°F, mph)
        self.icon_cache = {}
        
        self._build_ui()
        self._auto_detect_location()

    def _build_ui(self):
        # Header / Search Bar Frame
        search_frame = tk.Frame(self.root, bg=self.bg_color)
        search_frame.pack(fill="x", padx=25, pady=(20, 10))

        self.city_entry = tk.Entry(
            search_frame,
            font=("Helvetica", 14),
            bg=self.card_bg,
            fg=self.text_primary,
            insertbackground=self.text_primary,
            bd=0,
            relief="flat"
        )
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.city_entry.bind("<Return>", lambda event: self.fetch_weather())

        search_btn = tk.Button(
            search_frame,
            text="Get Weather",
            font=("Helvetica", 11, "bold"),
            bg=self.accent_color,
            fg=self.bg_color,
            activebackground="#74C7EC",
            activeforeground=self.bg_color,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.fetch_weather
        )
        search_btn.pack(side="left", ipadx=15, ipady=8, padx=(0, 10))

        self.unit_btn = tk.Button(
            search_frame,
            text="°C / °F",
            font=("Helvetica", 11, "bold"),
            bg=self.card_bg,
            fg=self.accent_color,
            activebackground=self.card_bg,
            activeforeground=self.text_primary,
            bd=1,
            relief="solid",
            cursor="hand2",
            command=self.toggle_unit
        )
        self.unit_btn.pack(side="left", ipadx=10, ipady=8)

        # Error Banner Label
        self.error_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.error_color
        )
        self.error_label.pack(fill="x", padx=25, pady=(2, 5))

        # Main Current Weather Panel
        self.current_frame = tk.Frame(self.root, bg=self.card_bg, bd=0)
        self.current_frame.pack(fill="x", padx=25, pady=10)

        # Left Column: Location & Main Temp
        left_box = tk.Frame(self.current_frame, bg=self.card_bg)
        left_box.pack(side="left", padx=20, pady=20)

        self.location_lbl = tk.Label(
            left_box,
            text="---",
            font=("Helvetica", 22, "bold"),
            bg=self.card_bg,
            fg=self.text_primary
        )
        self.location_lbl.pack(anchor="w")

        self.temp_lbl = tk.Label(
            left_box,
            text="--°",
            font=("Helvetica", 48, "bold"),
            bg=self.card_bg,
            fg=self.accent_color
        )
        self.temp_lbl.pack(anchor="w")

        self.desc_lbl = tk.Label(
            left_box,
            text="---",
            font=("Helvetica", 13, "italic"),
            bg=self.card_bg,
            fg=self.text_secondary
        )
        self.desc_lbl.pack(anchor="w")

        # Right Column: Weather Icon & Extra Stats
        right_box = tk.Frame(self.current_frame, bg=self.card_bg)
        right_box.pack(side="right", padx=20, pady=20)

        self.current_icon_lbl = tk.Label(right_box, bg=self.card_bg)
        self.current_icon_lbl.pack(anchor="e")

        self.stats_lbl = tk.Label(
            right_box,
            text="Humidity: --%\nWind: --",
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_primary,
            justify="right"
        )
        self.stats_lbl.pack(anchor="e", pady=(5, 0))

        # Hourly Forecast Section (Next 6 Hours)
        hourly_title = tk.Label(
            self.root,
            text="Hourly Forecast (Next 6 Hours)",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            fg=self.text_primary
        )
        hourly_title.pack(anchor="w", padx=25, pady=(15, 5))

        self.hourly_frame = tk.Frame(self.root, bg=self.bg_color)
        self.hourly_frame.pack(fill="x", padx=25)

        # Daily Forecast Section (5 Days)
        daily_title = tk.Label(
            self.root,
            text="5-Day Forecast",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            fg=self.text_primary
        )
        daily_title.pack(anchor="w", padx=25, pady=(15, 5))

        self.daily_frame = tk.Frame(self.root, bg=self.bg_color)
        self.daily_frame.pack(fill="x", padx=25)

    def show_error(self, message):
        """Displays user-friendly inline error messages."""
        self.error_label.config(text=f"⚠️ {message}")

    def clear_error(self):
        """Clears current error display."""
        self.error_label.config(text="")

    def _get_icon(self, icon_code, size=(50, 50)):
        """Fetches and caches weather icon images from OpenWeatherMap."""
        if (icon_code, size) in self.icon_cache:
            return self.icon_cache[(icon_code, size)]
        
        try:
            url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                img_data = Image.open(io.BytesIO(res.content)).resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_data)
                self.icon_cache[(icon_code, size)] = photo
                return photo
        except Exception:
            pass
        return None

    def _auto_detect_location(self):
        """Detects current city automatically using ipinfo.io IP geolocation API."""
        try:
            res = requests.get(IPINFO_URL, timeout=4)
            if res.status_code == 200:
                data = res.json()
                city = data.get("city")
                if city:
                    self.city_entry.insert(0, city)
                    self.fetch_weather()
                    return
        except Exception:
            pass
        self.show_error("Could not auto-detect location. Please enter a city manually.")

    def toggle_unit(self):
        """Switches between metric (°C) and imperial (°F) units."""
        self.unit = "imperial" if self.unit == "metric" else "metric"
        if self.city_entry.get().strip():
            self.fetch_weather()

    def fetch_weather(self):
        """Retrieves and processes current weather and forecast data."""
        self.clear_error()
        city = self.city_entry.get().strip()

        # Load environment variable explicitly from .env
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if api_key:
            api_key = api_key.strip().strip("'\"")

        # Input validation
        if not city:
            self.show_error("Please enter a valid city name or ZIP code.")
            return

        if not api_key or api_key == "your_actual_api_key_here":
            self.show_error("Invalid or missing OpenWeatherMap API Key in .env file.")
            return

        # Fetch Current Weather Data
        try:
            curr_params = {"q": city, "appid": api_key, "units": self.unit}
            curr_res = requests.get(CURRENT_WEATHER_URL, params=curr_params, timeout=8)
            
            if curr_res.status_code == 404:
                self.show_error("City not found. Please check spelling.")
                return
            elif curr_res.status_code == 401:
                self.show_error("Invalid API key provided.")
                return
            elif curr_res.status_code != 200:
                self.show_error(f"API Error ({curr_res.status_code}). Please try again.")
                return

            curr_data = curr_res.json()

            # Fetch Forecast Data
            fc_params = {"q": city, "appid": api_key, "units": self.unit}
            fc_res = requests.get(FORECAST_URL, params=fc_params, timeout=8)
            fc_data = fc_res.json() if fc_res.status_code == 200 else None

            # Render Data to UI
            self._update_current_ui(curr_data)
            if fc_data:
                self._update_hourly_ui(fc_data)
                self._update_daily_ui(fc_data)

        except requests.exceptions.Timeout:
            self.show_error("Network timeout. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            self.show_error(f"Network error occurred: {e}")

    def _update_current_ui(self, data):
        """Updates the main current weather section."""
        city_name = data.get("name", "")
        country = data.get("sys", {}).get("country", "")
        temp = round(data["main"]["temp"])
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        desc = data["weather"][0]["description"].title()
        icon_code = data["weather"][0]["icon"]

        unit_symbol = "°C" if self.unit == "metric" else "°F"
        speed_symbol = "m/s" if self.unit == "metric" else "mph"

        self.location_lbl.config(text=f"{city_name}, {country}")
        self.temp_lbl.config(text=f"{temp}{unit_symbol}")
        self.desc_lbl.config(text=desc)
        self.stats_lbl.config(text=f"Humidity: {humidity}%\nWind: {wind_speed} {speed_symbol}")

        icon = self._get_icon(icon_code, size=(80, 80))
        if icon:
            self.current_icon_lbl.config(image=icon)
            self.current_icon_lbl.image = icon

    def _update_hourly_ui(self, data):
        """Populates the next 6-hour forecast timeline."""
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()

        unit_symbol = "°C" if self.unit == "metric" else "°F"
        hourly_items = data.get("list", [])[:2]  # OpenWeatherMap returns 3-hr increments (2 items = 6 hrs)

        for item in hourly_items:
            dt = datetime.datetime.fromtimestamp(item["dt"])
            time_str = dt.strftime("%I:%M %p")
            temp = round(item["main"]["temp"])
            icon_code = item["weather"][0]["icon"]

            card = tk.Frame(self.hourly_frame, bg=self.card_bg, width=380, height=70)
            card.pack(side="left", expand=True, fill="both", padx=5)

            tk.Label(card, text=time_str, font=("Helvetica", 10, "bold"), bg=self.card_bg, fg=self.text_secondary).pack(side="left", padx=10)
            
            icon = self._get_icon(icon_code, size=(40, 40))
            if icon:
                lbl = tk.Label(card, image=icon, bg=self.card_bg)
                lbl.image = icon
                lbl.pack(side="left", padx=5)

            tk.Label(card, text=f"{temp}{unit_symbol}", font=("Helvetica", 12, "bold"), bg=self.card_bg, fg=self.accent_color).pack(side="right", padx=15)

    def _update_daily_ui(self, data):
        """Populates the 5-day forecast cards."""
        for widget in self.daily_frame.winfo_children():
            widget.destroy()

        unit_symbol = "°C" if self.unit == "metric" else "°F"
        daily_entries = {}

        # Filter forecast data targeting ~12:00 PM for each upcoming day
        for item in data.get("list", []):
            dt = datetime.datetime.fromtimestamp(item["dt"])
            date_str = dt.strftime("%Y-%m-%d")
            
            if date_str not in daily_entries or dt.hour == 12:
                daily_entries[date_str] = item

        # Select up to 5 days
        forecast_items = list(daily_entries.values())[:5]

        for item in forecast_items:
            dt = datetime.datetime.fromtimestamp(item["dt"])
            day_name = dt.strftime("%a")
            temp = round(item["main"]["temp"])
            icon_code = item["weather"][0]["icon"]

            card = tk.Frame(self.daily_frame, bg=self.card_bg, width=140, height=120)
            card.pack(side="left", expand=True, fill="both", padx=4)

            tk.Label(card, text=day_name, font=("Helvetica", 11, "bold"), bg=self.card_bg, fg=self.text_primary).pack(pady=(10, 2))
            
            icon = self._get_icon(icon_code, size=(40, 40))
            if icon:
                lbl = tk.Label(card, image=icon, bg=self.card_bg)
                lbl.image = icon
                lbl.pack()

            tk.Label(card, text=f"{temp}{unit_symbol}", font=("Helvetica", 12, "bold"), bg=self.card_bg, fg=self.accent_color).pack(pady=(2, 10))


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()