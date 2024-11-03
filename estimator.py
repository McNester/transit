#!/usr/bin/env python3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import sys
import os
from pathlib import Path

def get_default_csv_path():
    """Get the default CSV path from the project directory"""
    project_dir = Path(__file__).parent
    default_path = project_dir / "dwell_sorted.csv"
    return str(default_path)

def load_and_preprocess_csv(csv_path):
    try:
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"Error: File not found at {csv_path}")
            return None
            
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Convert date and time columns to datetime
        df['date'] = pd.to_datetime(df['date'])
        df['arrival_time'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['arrival_time'])
        df['departure_time'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['departure_time'])
        
        # Ensure numeric type for dwell time
        df['dwell_time_in_seconds'] = pd.to_numeric(df['dwell_time_in_seconds'], errors='coerce')
        
        # Convert trip_id and bus_stop to string to ensure matching works correctly
        df['trip_id'] = df['trip_id'].astype(str)
        df['bus_stop'] = df['bus_stop'].astype(str)
        
        # Sort by trip and time
        df = df.sort_values(['trip_id', 'arrival_time'])
        
        return df
        
    except Exception as e:
        print(f"Error loading CSV file: {str(e)}")
        return None

def show_available_trips(df):
    """Display all available trip IDs with additional information"""
    print("\nAvailable Trip IDs:")
    print("-" * 80)
    print(f"{'Trip ID':<15} {'Direction':<10} {'First Stop':<10} {'Last Stop':<10} {'Date':<12}")
    print("-" * 80)
    
    for trip_id in sorted(df['trip_id'].unique()):
        trip_data = df[df['trip_id'] == trip_id].sort_values('arrival_time')
        if not trip_data.empty:
            first_record = trip_data.iloc[0]
            last_record = trip_data.iloc[-1]
            print(f"{trip_id:<15} {str(first_record['direction']):<10} "
                  f"{str(first_record['bus_stop']):<10} {str(last_record['bus_stop']):<10} "
                  f"{first_record['date'].strftime('%Y-%m-%d'):<12}")
    print("-" * 80)
    print(f"Total number of unique trips: {df['trip_id'].nunique()}")

def show_stops_for_trip(df, trip_id=None):
    """Display all stops with their details, optionally filtered by trip_id"""
    if trip_id:
        trip_data = df[df['trip_id'] == trip_id].sort_values('arrival_time')
        if trip_data.empty:
            print(f"\nNo data found for trip ID: {trip_id}")
            return
        
        print(f"\nStops for Trip ID: {trip_id}")
        print(f"Direction: {trip_data.iloc[0]['direction']}")
        print("-" * 60)
        print(f"{'Stop ID':<10} {'Arrival Time':<20} {'Dwell Time (s)':<15}")
        print("-" * 60)
        
        for _, row in trip_data.iterrows():
            print(f"{str(row['bus_stop']):<10} "
                  f"{row['arrival_time'].strftime('%Y-%m-%d %H:%M:%S'):<20} "
                  f"{row['dwell_time_in_seconds']:<15.1f}")
    else:
        print("\nAll Available Stops:")
        print("-" * 50)
        print(f"{'Stop ID':<10} {'Times Used':<12} {'Avg Dwell Time (s)':<20}")
        print("-" * 50)
        
        stop_stats = df.groupby('bus_stop').agg({
            'trip_id': 'count',
            'dwell_time_in_seconds': 'mean'
        }).reset_index()
        
        for _, row in stop_stats.sort_values('bus_stop').iterrows():
            print(f"{str(row['bus_stop']):<10} "
                  f"{row['trip_id']:<12} "
                  f"{row['dwell_time_in_seconds']:<20.1f}")

def calculate_estimates(group_data):
    data = group_data.copy()
    
    # Check if we have enough data
    if len(data) < 2 or data['travel_time'].isna().all():
        return pd.Series({
            'mean_travel_time': np.nan,
            'std_travel_time': np.nan,
            'mean_dwell_time': np.nan,
            'hourly_factors': {},
            'daily_factors': {}
        })
    
    # Remove NaN values
    data = data.dropna(subset=['travel_time'])
    
    # Basic statistics
    mean_travel = data['travel_time'].mean()
    std_travel = data['travel_time'].std()
    mean_dwell = data['dwell_time_in_seconds'].mean()
    
    # Time of day effects
    data['hour'] = data['arrival_time'].dt.hour
    hourly_factors = data.groupby('hour')['travel_time'].mean()
    if not hourly_factors.empty:
        hourly_factors = hourly_factors / hourly_factors.mean()
    
    # Day of week effects
    data['day_of_week'] = data['arrival_time'].dt.dayofweek
    daily_factors = data.groupby('day_of_week')['travel_time'].mean()
    if not daily_factors.empty:
        daily_factors = daily_factors / daily_factors.mean()
    
    return pd.Series({
        'mean_travel_time': mean_travel,
        'std_travel_time': std_travel,
        'mean_dwell_time': mean_dwell,
        'hourly_factors': hourly_factors.to_dict() if not hourly_factors.empty else {},
        'daily_factors': daily_factors.to_dict() if not daily_factors.empty else {}
    })


def estimate_arrival_time(df, target_trip_id=None, target_stop=None):
    # Calculate travel time between consecutive stops
    df = df.sort_values(['trip_id', 'arrival_time'])
    df['next_stop_arrival'] = df.groupby('trip_id')['arrival_time'].shift(-1)
    df['travel_time'] = (df['next_stop_arrival'] - df['departure_time']).dt.total_seconds()
    
    # Calculate estimates for each direction and stop combination
    # Using agg instead of apply to avoid the deprecation warning
    grouped = df.groupby(['direction', 'bus_stop'])
    estimates = grouped.apply(lambda x: calculate_estimates(x))
    
    if target_trip_id and target_stop:
        # Validate that trip_id exists
        if target_trip_id not in df['trip_id'].unique():
            print(f"Error: Trip ID '{target_trip_id}' not found in dataset")
            print("Available trip IDs (first 5):", ', '.join(sorted(df['trip_id'].unique())[:5]), "...")
            return None
            
        # Validate that stop exists
        if target_stop not in df['bus_stop'].unique():
            print(f"Error: Stop '{target_stop}' not found in dataset")
            print("Available stops:", ', '.join(sorted(df['bus_stop'].unique())))
            return None
            
        # Get last known position for target trip
        trip_data = df[df['trip_id'] == target_trip_id].sort_values('arrival_time')
        
        if trip_data.empty:
            print(f"No data found for trip {target_trip_id}")
            return None
            
        last_known = trip_data.iloc[-1]
        
        # Get direction and current time
        direction = last_known['direction']
        current_time = last_known['departure_time']
        
        # Check if we have estimates for this direction and stop
        if (direction, target_stop) not in estimates.index:
            print(f"No historical data for direction {direction} and stop {target_stop}")
            print("\nAvailable direction-stop combinations:")
            for idx in estimates.index[:5]:
                print(f"Direction: {idx[0]}, Stop: {idx[1]}")
            return None
            
        stats = estimates.loc[(direction, target_stop)]
        
        if pd.isna(stats['mean_travel_time']):
            print(f"Insufficient data to make prediction for direction {direction} and stop {target_stop}")
            return None
            
        # Calculate prediction
        base_prediction = float(stats['mean_travel_time'])  # Convert to float explicitly
        
        # Apply time-based factors
        hour = current_time.hour
        day_of_week = current_time.dayofweek
        
        hourly_factors = stats['hourly_factors']
        daily_factors = stats['daily_factors']
        
        if hour in hourly_factors:
            base_prediction *= hourly_factors[hour]
        if day_of_week in daily_factors:
            base_prediction *= daily_factors[day_of_week]
            
        # Ensure we have valid numbers
        if pd.isna(base_prediction) or base_prediction <= 0:
            print(f"Cannot make reliable prediction for stop {target_stop} due to insufficient data")
            return None
            
        # Calculate confidence interval
        confidence_interval = float(1.96 * stats['std_travel_time']) if pd.notna(stats['std_travel_time']) else base_prediction * 0.2
        
        return {
            'predicted_travel_time': base_prediction,
            'confidence_interval': confidence_interval,
            'predicted_arrival': current_time + timedelta(seconds=int(base_prediction)),
            'lower_bound': current_time + timedelta(seconds=int(base_prediction - confidence_interval)),
            'upper_bound': current_time + timedelta(seconds=int(base_prediction + confidence_interval))
        }
    
    return estimates

def main():
    parser = argparse.ArgumentParser(description='Transit Arrival Time Prediction Tool')
    parser.add_argument('--csv', default=get_default_csv_path(),
                       help='Path to the CSV file (default: dwell_sorted.csv in project directory)')
    parser.add_argument('--trip', help='Specific trip ID to predict')
    parser.add_argument('--stop', help='Specific stop to predict')
    parser.add_argument('--output', help='Path to save results (optional)')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    parser.add_argument('--showTrips', action='store_true', help='Show all available trip IDs')
    parser.add_argument('--showStops', action='store_true', help='Show all stops or stops for specific trip (use with --trip)')
    
    args = parser.parse_args()
    
    print(f"Loading data from: {args.csv}")
    transit_data = load_and_preprocess_csv(args.csv)
    
    if transit_data is None:
        print("Failed to load data. Exiting.")
        sys.exit(1)
    
    print("\nDataset Overview:")
    print(f"Total number of records: {len(transit_data)}")
    print(f"Number of unique trips: {transit_data['trip_id'].nunique()}")
    print(f"Number of unique stops: {transit_data['bus_stop'].nunique()}")
    print(f"Date range: {transit_data['date'].min()} to {transit_data['date'].max()}")
    
    # Handle information display flags
    if args.showTrips:
        show_available_trips(transit_data)
        return
        
    if args.showStops:
        show_stops_for_trip(transit_data, args.trip)
        return
    
    # Continue with prediction if no display flags are set
    try:
        if args.trip and args.stop:
            prediction = estimate_arrival_time(transit_data, 
                                            target_trip_id=args.trip,
                                            target_stop=args.stop)
            
            if prediction:
                results = f"""
Prediction Results:
------------------
Trip ID: {args.trip}
Stop: {args.stop}
Predicted arrival: {prediction['predicted_arrival']}
Confidence interval: ±{prediction['confidence_interval']/60:.1f} minutes
Time window: {prediction['lower_bound']} to {prediction['upper_bound']}
"""
                print(results)
                
                if args.output:
                    with open(args.output, 'w') as f:
                        f.write(results)
                    print(f"\nResults saved to: {args.output}")
        else:
            if not (args.showTrips or args.showStops):
                print("\nPlease specify either:")
                print("1. --trip and --stop for predictions")
                print("2. --showTrips to see available trips")
                print("3. --showStops [--trip TRIP_ID] to see stops")
                print("\nExample usage:")
                print("python estimator.py --trip 1 --stop 114")
                print("python estimator.py --showTrips")
                print("python estimator.py --showStops --trip 1")
    
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
