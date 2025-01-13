# Real-Time Agri-Monitor

Real-time agriculture monitoring dashboard for NMC System (Netafim), designed to track and visualize temperature and humidity data across multiple agricultural zones.

## Features

- Real-time data monitoring from NMC-Pro Climate system
- Multi-zone tracking (4 zones)
- Interactive graphs with temperature and humidity data
- Customizable time frames (day/week/month/year)
- Dynamic base directory configuration
- Auto-refresh every 5 minutes
- Hebrew support for zone names

## Installation

1. Clone the repository:

2. Install required dependencies:

3. Run the application:

2. Access the dashboard through your web browser at `http://127.0.0.1:8050`

3. Configure the dashboard:
   - Set the base directory path to your NMC System data folder
   - Select desired timeframe from the dropdown
   - Click "Update Path" to refresh the data source

## Data Structure

The application expects data files in the following structure:

## Zones

1. חממת טיפוח (Breeding Greenhouse)
2. חממת משתלה (Nursery Greenhouse)
3. חדר סבתות (Grandmothers Room)
4. חדר השרשה משתלה (Nursery Rooting Room)

## Developer

Developed by Jecki Shoef (2024)

## Requirements

- Python 3.x
- Dash
- Pandas
- Plotly
- OpenPyXL
