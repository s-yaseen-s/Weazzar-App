# Weazzar App

A comprehensive weather application built with both web and mobile platforms, providing real-time weather information with an intuitive user interface.

## 📋 Description

Weazzar is a full-stack weather application offering seamless weather tracking across web and mobile platforms. Get accurate, real-time weather data with a modern, responsive design that works on desktop, tablet, and mobile devices.

### Features

- **Real-time Weather Data**: Current conditions, forecasts, and detailed metrics
- **Multi-platform Support**: Web and mobile applications
- **Temperature Unit Toggle**: Switch between Celsius and Fahrenheit
- **Responsive Design**: Glass-morphism UI with smooth animations
- **Search Functionality**: Find weather for any location
- **Cross-platform Compatibility**: Desktop web app and React Native mobile app

## 📂 Project Structure

```
Weather/
├── WeatherAPP/          # Web Application (Python Flask)
│   ├── App.py          # Main Flask application
│   ├── launcher.py     # Application launcher
│   ├── requirements.txt # Python dependencies
│   ├── static/         # CSS, icons, and service worker
│   └── templates/      # HTML templates
└── WeatherMobileApp/   # Mobile Application (React Native/Expo)
    ├── app/            # TypeScript components and pages
    ├── components/     # Reusable UI components
    ├── hooks/          # Custom React hooks
    ├── utils/          # Utility functions
    └── assets/         # App assets
```

## 🛠️ Tech Stack

### Web Application
- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **PWA**: Service Worker support

### Mobile Application
- **Framework**: React Native (Expo)
- **Language**: TypeScript
- **State Management**: React Hooks
- **Build Tool**: EAS Build

## 🚀 Quick Start

### Web Application
```bash
cd Weather/WeatherAPP
pip install -r requirements.txt
python launcher.py
```

### Mobile Application
```bash
cd Weather/WeatherMobileApp
npm install
npm start
```

## 📱 Components

### Web App
- **App.py**: Main Flask server
- **index.html**: Home page
- **weather.html**: Weather details page
- **about.html**: About page
- **contact.html**: Contact page
- **privacy.html**: Privacy policy

### Mobile App
- **WeatherHero**: Main weather display
- **SearchBar**: Location search component
- **ForecastCard**: Weather forecast cards
- **MetricCard**: Individual weather metrics
- **GlassCard**: Reusable glass-morphism component
- **UnitToggle**: Temperature unit selector

## 🔧 Configuration

- **Mobile App Config**: [app.json](Weather/WeatherMobileApp/app.json)
- **EAS Build Config**: [eas.json](Weather/WeatherMobileApp/eas.json)
- **TypeScript Config**: [tsconfig.json](Weather/WeatherMobileApp/tsconfig.json)

## 📄 License

This project is part of the Summer Innovations 2026 initiative.

## 👥 Contributors

- Development Team

---

**Status**: Active Development
