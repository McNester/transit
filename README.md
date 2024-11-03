# Transit Time Prediction Tool

This tool predicts bus arrival times based on historical transit data. It analyzes patterns in bus movements to provide estimated arrival times with confidence intervals.

## Features
- Predicts arrival times for specific trips and stops
- Calculates confidence intervals for predictions
- Considers time-of-day and day-of-week patterns
- Handles historical transit data in CSV format
- Provides comprehensive error handling and data validation
- Lists all available trips with their details
- Shows stops information for specific trips
- Uses default data file from project directory

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/McNester/transit.git
cd transit
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

The script can be used in several ways:

### Basic Prediction
```bash
# Using default CSV file (dwell_sorted.csv in project directory)
python estimator.py --trip "1" --stop "114"

# Using a specific CSV file
python estimator.py --csv "path/to/your/data.csv" --trip "1" --stop "114"
```

### View Available Data
```bash
# Show all available trip IDs with their details
python estimator.py --showTrips

# Show all stops and their statistics
python estimator.py --showStops

# Show stops for a specific trip
python estimator.py --showStops --trip "1"
```

### Additional Options
```bash
# Save prediction results to a file
python estimator.py --trip "1" --stop "114" --output "results.txt"

# Show debug information
python estimator.py --trip "1" --stop "114" --debug
```

### Command Line Arguments
- `--csv`: Path to the CSV file (default: dwell_sorted.csv in project directory)
- `--trip`: Specific trip ID to predict
- `--stop`: Specific stop to predict
- `--output`: Path to save results (optional)
- `--debug`: Show debug information
- `--showTrips`: Display all available trip IDs with details
- `--showStops`: Show all stops or stops for specific trip (use with --trip)

## Input Data Format

The CSV file should have the following columns:
- `trip_id`: Unique identifier for each trip
- `deviceid`: Identifier for the transit vehicle
- `direction`: Direction of travel
- `bus_stop`: Stop identifier
- `date`: Date of the trip (YYYY-MM-DD)
- `arrival_time`: Time of arrival (HH:MM:SS)
- `departure_time`: Time of departure (HH:MM:SS)
- `dwell_time_in_seconds`: Time spent at stop

Example CSV format:
```csv
trip_id,deviceid,direction,bus_stop,date,arrival_time,departure_time,dwell_time_in_seconds
1,262,1,101,2021-10-01,06:40:58,06:42:12,74.0
```

## Output Format

### Trip List Output
```
Available Trip IDs:
--------------------------------------------------------------------------------
Trip ID         Direction  First Stop Last Stop  Date      
--------------------------------------------------------------------------------
1               1          101        114        2021-10-01
```

### Stop List Output
```
Stops for Trip ID: 1
Direction: 1
------------------------------------------------------------
Stop ID    Arrival Time           Dwell Time (s)
------------------------------------------------------------
101        2021-10-01 06:40:58   74.0
```

### Prediction Output
```
Prediction Results:
------------------
Trip ID: 1
Stop: 114
Predicted arrival: 2021-10-01 07:15:30
Confidence interval: ±2.5 minutes
Time window: 2021-10-01 07:13:00 to 2021-10-01 07:18:00
```

## Project Structure
```
transit/
│
├── data/                  # Data directory (gitignored)
├── output/               # Output directory (gitignored)
├── venv/                 # Virtual environment (gitignored)
├── .gitignore           # Git ignore file
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
├── LICENSE             # License file
├── dwell_sorted.csv    # Default data file
└── estimator.py        # Main script
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

Common issues and solutions:

1. **CSV file not found**
   - Ensure dwell_sorted.csv is in the project directory or
   - Provide the correct path using --csv option

2. **Module not found error**
   - Ensure you've activated the virtual environment
   - Run `pip install -r requirements.txt`

3. **Invalid trip or stop ID**
   - Use --showTrips to see available trip IDs
   - Use --showStops to see available stops

4. **Permission denied**
   - Ensure you have read/write permissions in the project directory
   - Use sudo or run as administrator if necessary
