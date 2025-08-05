class DataStorage:
    def save_to_csv(self, dataframe, filename):
        dataframe.to_csv(filename, index=False)

    def load_from_csv(self, filename):
        import pandas as pd
        return pd.read_csv(filename)