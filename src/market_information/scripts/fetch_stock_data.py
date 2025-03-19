import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(tickers, start_date, end_date, interval='1d'):
    """
    Fetch stock price data for multiple tickers using yfinance and return as a MultiIndex DataFrame
    
    Parameters:
    -----------
    tickers : list
        List of ticker symbols to fetch
    start_date : str
        Start date for data retrieval (YYYY-MM-DD)
    end_date : str
        End date for data retrieval (YYYY-MM-DD)
    interval : str, default '1d'
        Data interval ('1d'=daily, '1wk'=weekly, '1mo'=monthly)
        
    Returns:
    --------
    pandas.DataFrame
        MultiIndex DataFrame
    """
    # Dictionary to store data for each ticker
    data_dict = {}
    
    # Fetch data for each ticker
    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date, interval=interval)
        data_dict[ticker] = data
    
    # Create MultiIndex DataFrame
    multi_index_df = pd.concat(data_dict, axis=1)
    
    return multi_index_df

def main():
    # Settings
    tickers = ['NVDA', 'TSM']  # Nvidia and TSMC
    start_date = '2020-01-01'
    end_date = '2025-03-14'  # Current date
    
    # Fetch data
    stock_data = fetch_stock_data(tickers, start_date, end_date)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save as CSV file
    csv_path = 'data/stock_data.csv'
    stock_data.to_csv(csv_path)
    print(f"Data saved to {csv_path}")
    
    # Also save as Pickle file (preserves MultiIndex structure completely)
    pickle_path = 'data/stock_data.pkl'
    stock_data.to_pickle(pickle_path)
    print(f"Data saved to {pickle_path}")
    
    # Display basic information about the data
    print("\nData Information:")
    print(f"Period: {start_date} to {end_date}")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Data shape: {stock_data.shape}")
    print(f"Columns: {stock_data.columns.names}")
    print(f"Index: {stock_data.index.name}")
    
    # Display the first few rows of data
    print("\nData Sample:")
    print(stock_data.head())

if __name__ == "__main__":
    main()