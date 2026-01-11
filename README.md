# Florida Weather Tracker

A full-stack suite of tools to identify cities in Florida predicted to have at least three consecutive days with high temperatures above a specified threshold.

## 🚀 Overview
This project provides two ways to track Florida weather:
1.  **CLI Tool**: A lightweight Python script for quick command-line analysis.
2.  **Web Dashboard**: A premium, mobile-responsive web application with a FastAPI backend and Vite frontend.

---

## 🛠 CLI Usage

### Prerequisites
- Python 3.8+
- `requests` library

### Running the Script
```bash
# Install dependencies
pip install requests

# Usage: python3 weather_tracker.py <threshold_f> <city1> <city2> ...
python3 weather_tracker.py 75 Miami Orlando Tampa
```

**Features:**
- 14-day weather forecasts via Open-Meteo.
- Automatic geocoding for cities in Florida.
- High/Low ranges for each day.
- Match indicator (*) for days meeting the temperature criterion.

---

## 🌐 Web Application

The web app provides a modern, interactive dashboard with a glassmorphism design.

### Local Development

1. **Start the Backend**:
   ```bash
   cd backend
   pip install -r ../requirements.txt
   python3 main.py
   ```
2. **Start the Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 🚢 Remote Deployment

Includes a dedicated script for deploying to a remote Linux server (e.g., a Raspberry Pi) running Nginx.

### How to Deploy
The deployment script automates the build process, rsyncs files, sets up a systemd service, and configures an Nginx catch-all subpath.

```bash
chmod +x deploy.sh
./deploy.sh <remote-hostname>
```

**Post-deployment:**
- Backend runs via **Systemd** (`weather-tracker.service`).
- Nginx serves the app at `http://<hostname>/weather-tracker`.
- Nginx config is placed in `/etc/nginx/conf.d/weather-tracker.conf`.

---

## 📂 Project Structure
- `weather_tracker.py`: Main CLI script.
- `backend/`: FastAPI application logic and weather services.
- `frontend/`: Vite + Vanilla JS project for the UI.
- `deployment/`: Nginx and Systemd configuration files.
- `deploy.sh`: Unified remote deployment automation.
- `requirements.txt`: Python dependencies.
