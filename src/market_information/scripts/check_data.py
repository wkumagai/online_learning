import pandas as pd

def main():
    # Load data from Pickle file
    data_path = 'data/stock_data.pkl'
    stock_data = pd.read_pickle(data_path)
    
    # Display basic information about the data
    print("Data Information:")
    print(f"Data shape: {stock_data.shape}")
    print(f"Index: {stock_data.index.name}")
    
    # Check MultiIndex structure
    print("\nColumn MultiIndex Structure:")
    print(f"Number of levels: {stock_data.columns.nlevels}")
    print(f"Level names: {stock_data.columns.names}")
    
    # Display values at each level
    for i in range(stock_data.columns.nlevels):
        print(f"Values at level {i}: {stock_data.columns.get_level_values(i).unique()}")
    
    # Display the first few rows of data
    print("\nData Sample:")
    print(stock_data.head())
    
    # Examples of extracting specific data
    print("\nData Extraction Examples:")
    print("NVDA Close prices:")
    print(stock_data['NVDA']['Close'].head())
    
    print("\nTSM Volume:")
    print(stock_data['TSM']['Volume'].head())
    
    # Example of extracting the same item for multiple tickers
    print("\nClose prices for both tickers:")
    print(stock_data.xs('Close', level=1, axis=1).head())

if __name__ == "__main__":
    main()