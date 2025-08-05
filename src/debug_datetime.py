import pandas as pd
import os

def check_datetime_format():
    """Check the datetime format in existing CSV files"""
    
    data_dir = "data/raw"
    
    if not os.path.exists(data_dir):
        print("data/raw directory not found")
        return
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    for csv_file in csv_files:
        csv_path = os.path.join(data_dir, csv_file)
        
        try:
            df = pd.read_csv(csv_path)
            
            if 'published_at' in df.columns:
                print(f"\n📁 File: {csv_file}")
                print(f"   Sample published_at values:")
                
                # Convert to datetime and check timezone info
                dt_series = pd.to_datetime(df['published_at'])
                
                print(f"   First 3 values: {dt_series.head(3).tolist()}")
                print(f"   Timezone info: {dt_series.dt.tz}")
                print(f"   Data type: {dt_series.dtype}")
                
                # Check current time comparison
                current_time = pd.Timestamp.now()
                print(f"   Current time: {current_time}")
                print(f"   Current time timezone: {current_time.tz}")
                
                break
                
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

if __name__ == "__main__":
    check_datetime_format()