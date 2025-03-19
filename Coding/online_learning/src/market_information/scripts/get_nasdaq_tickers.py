import pandas as pd
import requests
import io
import os
import yfinance as yf
import time
import csv

def get_nasdaq_tickers_from_ftp():
    """
    Get NASDAQ tickers from NASDAQ's website
    """
    print("Fetching NASDAQ tickers from NASDAQ's website...")
    
    try:
        # URL for NASDAQ-listed companies (old NASDAQ website)
        url = "https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download"
        
        # Try to download the file
        response = requests.get(url)
        
        if response.status_code == 200:
            # Save the CSV file
            with open('data/nasdaq_tickers_raw.csv', 'wb') as f:
                f.write(response.content)
            
            # Parse the CSV file
            tickers = []
            with open('data/nasdaq_tickers_raw.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) > 0:
                        tickers.append(row[0])  # First column is the ticker symbol
            
            print(f"Successfully fetched {len(tickers)} NASDAQ tickers.")
            
            # Save the tickers to a CSV file
            nasdaq_df = pd.DataFrame(tickers, columns=['Symbol'])
            nasdaq_df.to_csv('data/nasdaq_tickers.csv', index=False)
            print(f"Saved {len(tickers)} NASDAQ tickers to data/nasdaq_tickers.csv")
            
            return tickers
        else:
            print(f"Failed to download from NASDAQ website. Status code: {response.status_code}")
            return get_nasdaq_tickers_alternative()
    
    except Exception as e:
        print(f"Error fetching NASDAQ tickers from website: {e}")
        return get_nasdaq_tickers_alternative()

def get_nasdaq_tickers_alternative():
    """
    Alternative method to get NASDAQ tickers using a different URL
    """
    print("Trying alternative method to fetch NASDAQ tickers...")
    
    try:
        # Alternative URL for NASDAQ-listed companies
        url = "https://www.nasdaq.com/market-activity/stocks/screener?exchange=NASDAQ&render=download"
        
        # Try to download the file
        response = requests.get(url)
        
        if response.status_code == 200:
            # Save the CSV file
            with open('data/nasdaq_tickers_raw.csv', 'wb') as f:
                f.write(response.content)
            
            # Parse the CSV file
            data = pd.read_csv('data/nasdaq_tickers_raw.csv')
            
            # Extract ticker symbols
            tickers = data['Symbol'].tolist()
            
            print(f"Successfully fetched {len(tickers)} NASDAQ tickers.")
            
            # Save the tickers to a CSV file
            nasdaq_df = pd.DataFrame(tickers, columns=['Symbol'])
            nasdaq_df.to_csv('data/nasdaq_tickers.csv', index=False)
            print(f"Saved {len(tickers)} NASDAQ tickers to data/nasdaq_tickers.csv")
            
            return tickers
        else:
            print(f"Failed to download from alternative URL. Status code: {response.status_code}")
            return get_nasdaq_tickers_fallback()
        
    except Exception as e:
        print(f"Error fetching NASDAQ tickers from alternative URL: {e}")
        return get_nasdaq_tickers_fallback()

def get_nasdaq_tickers_fallback():
    """
    Fallback method to get NASDAQ tickers using a predefined list
    """
    print("Using fallback method with predefined list of major NASDAQ tickers...")
    
    # List of major NASDAQ tickers
    major_nasdaq_tickers = [
        'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA', 'PYPL', 'INTC', 'CMCSA',
        'CSCO', 'PEP', 'ADBE', 'NFLX', 'AVGO', 'TXN', 'COST', 'QCOM', 'TMUS', 'AMGN',
        'SBUX', 'INTU', 'CHTR', 'MDLZ', 'ISRG', 'GILD', 'BKNG', 'ADP', 'AMAT', 'ADI',
        'REGN', 'ILMN', 'ATVI', 'CSX', 'MU', 'BIIB', 'LRCX', 'VRTX', 'FISV', 'ADSK',
        'NXPI', 'MELI', 'KLAC', 'MNST', 'ALGN', 'IDXX', 'WDAY', 'EXC', 'PAYX', 'CTAS'
    ]
    
    print(f"Using a list of {len(major_nasdaq_tickers)} major NASDAQ tickers.")
    
    # Save the tickers to a CSV file
    nasdaq_df = pd.DataFrame(major_nasdaq_tickers, columns=['Symbol'])
    nasdaq_df.to_csv('data/nasdaq_tickers.csv', index=False)
    print(f"Saved {len(major_nasdaq_tickers)} NASDAQ tickers to data/nasdaq_tickers.csv")
    
    return major_nasdaq_tickers

def check_ticker_availability(tickers, max_tickers=None):
    """
    Check if tickers are available in yfinance
    
    Parameters:
    -----------
    tickers : list
        List of ticker symbols to check
    max_tickers : int, optional
        Maximum number of tickers to check
    
    Returns:
    --------
    tuple
        (available_tickers, unavailable_tickers)
    """
    if tickers is None or len(tickers) == 0:
        print("No tickers to check.")
        return [], []
    
    # Determine how many tickers to check
    if max_tickers is not None and max_tickers < len(tickers):
        check_tickers = tickers[:max_tickers]
        print(f"Checking availability of the first {max_tickers} tickers in yfinance...")
    else:
        check_tickers = tickers
        print(f"Checking availability of all {len(tickers)} tickers in yfinance...")
    
    available_tickers = []
    unavailable_tickers = []
    
    for i, ticker in enumerate(check_tickers):
        try:
            print(f"[{i+1}/{len(check_tickers)}] Checking {ticker}...", end="")
            stock = yf.Ticker(ticker)
            
            # Try to get some basic info
            info = stock.info
            
            # Check if we got valid data
            if 'symbol' in info and info['symbol'] == ticker:
                print(" Available")
                available_tickers.append(ticker)
            else:
                print(" Unavailable (No valid data)")
                unavailable_tickers.append(ticker)
                
        except Exception as e:
            print(f" Unavailable (Error: {str(e)[:50]}...)")
            unavailable_tickers.append(ticker)
        
        # Sleep to avoid rate limiting
        time.sleep(0.5)
    
    return available_tickers, unavailable_tickers

def create_available_tickers_dataset(available_tickers, output_file='data/available_nasdaq_tickers.csv'):
    """
    Create a dataset of available tickers
    
    Parameters:
    -----------
    available_tickers : list
        List of available ticker symbols
    output_file : str, default 'data/available_nasdaq_tickers.csv'
        Output file path
    """
    if not available_tickers:
        print("No available tickers to save.")
        return
    
    # Create a DataFrame with the available tickers
    df = pd.DataFrame(available_tickers, columns=['Symbol'])
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Saved {len(available_tickers)} available tickers to {output_file}")

def main():
    print("NASDAQ Ticker Availability in yfinance")
    print("======================================")
    
    # Get NASDAQ tickers from website
    nasdaq_tickers = get_nasdaq_tickers_from_ftp()
    
    if nasdaq_tickers:
        # Print some statistics
        print(f"\nTotal NASDAQ tickers found: {len(nasdaq_tickers)}")
        print(f"First 10 tickers: {nasdaq_tickers[:10]}")
        
        # Check availability of tickers
        # For demonstration, we'll check a small sample
        # In a real scenario, you might want to check all tickers
        max_tickers = 10  # Adjust this number as needed
        available, unavailable = check_ticker_availability(nasdaq_tickers, max_tickers)
        
        # Print results
        print("\nResults:")
        print(f"Sample size: {len(available) + len(unavailable)} tickers")
        print(f"Available tickers: {len(available)} ({', '.join(available[:5])}{'...' if len(available) > 5 else ''})")
        print(f"Unavailable tickers: {len(unavailable)} ({', '.join(unavailable[:5])}{'...' if len(unavailable) > 5 else ''})")
        
        # Calculate availability percentage
        availability_percentage = (len(available) / len(available + unavailable)) * 100
        print(f"Availability percentage: {availability_percentage:.2f}%")
        
        # Create dataset of available tickers
        create_available_tickers_dataset(available)
        
        print("\nNote:")
        print("1. This is based on a sample and actual availability may vary.")
        print("2. To check all tickers, adjust the max_tickers parameter.")
        print("3. The full list of NASDAQ tickers is saved in data/nasdaq_tickers.csv")
        print("4. The available tickers are saved in data/available_nasdaq_tickers.csv")
    else:
        print("Failed to retrieve NASDAQ tickers. Please try again later.")

if __name__ == "__main__":
    main()