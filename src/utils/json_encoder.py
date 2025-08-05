import json
import numpy as np
import pandas as pd
from datetime import datetime, date

class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy and pandas types"""
    
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        elif hasattr(obj, 'item'):  # Handle scalar numpy types
            return obj.item()
        
        return super().default(obj)