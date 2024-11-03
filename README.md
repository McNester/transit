# Transit Time Prediction Tool

This tool predicts bus arrival times based on historical transit data. It analyzes patterns in bus movements to provide estimated arrival times with confidence intervals.

## Features
- Predicts arrival times for specific trips and stops
- Calculates confidence intervals for predictions
- Considers time-of-day and day-of-week patterns
- Handles historical transit data in CSV format
- Provides comprehensive error handling and data validation

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

Basic usage:
```bash
python estimator.py your_data.csv --trip "trip_id" --stop "stop_id"
```

Options:
- `--trip`: Specific trip ID to predict
- `--stop`: Specific stop to predict
- `--output`: Path to save results (optional)
- `--debug`: Show debug information

Example:
```bash
python estimator.py dwell_sorted.csv --trip "1" --stop "114" --debug
```

## Input Data Format

The CSV file should have the following columns:
- trip_id: Unique identifier for each trip
- deviceid: Identifier for the transit vehicle
- direction: Direction of travel
- bus_stop: Stop identifier
- date: Date of the trip (YYYY-MM-DD)
- arrival_time: Time of arrival (HH:MM:SS)
- departure_time: Time of departure (HH:MM:SS)
- dwell_time_in_seconds: Time spent at stop

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
