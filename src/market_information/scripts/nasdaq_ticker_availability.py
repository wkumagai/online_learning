import pandas as pd
import yfinance as yf
import requests
import io
import time
import random

def get_nasdaq_tickers_from_ftp():
    """
    Get NASDAQ tickers from NASDAQ's FTP server
    """
    print("Fetching NASDAQ tickers from NASDAQ's FTP server...")
    
    try:
        # URL for NASDAQ-listed companies
        url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt"
        
        # Try to download the file
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse the file
            data = pd.read_csv(io.StringIO(response.text), delimiter='|')
            
            # Filter for NASDAQ-listed stocks (Exchange = 'Q')
            nasdaq_stocks = data[data['Exchange'] == 'Q']
            
            # Get the ticker symbols
            tickers = nasdaq_stocks['Symbol'].tolist()
            
            print(f"Successfully fetched {len(tickers)} NASDAQ tickers.")
            return tickers
        else:
            print(f"Failed to download from FTP server. Status code: {response.status_code}")
            return get_nasdaq_tickers_fallback()
    
    except Exception as e:
        print(f"Error fetching NASDAQ tickers from FTP: {e}")
        return get_nasdaq_tickers_fallback()

def get_nasdaq_tickers_fallback():
    """
    Fallback method to get NASDAQ tickers
    """
    print("Using fallback method to get NASDAQ tickers...")
    
    try:
        # Try to download from a different source
        url = "https://www.nasdaq.com/market-activity/stocks/screener"
        print(f"Attempting to download from {url}")
        print("Note: This requires web scraping which might not work reliably.")
        
        # Fallback to a predefined list of major NASDAQ tickers
        print("Using a predefined list of major NASDAQ tickers as a fallback.")
        
        major_nasdaq_tickers = [
            'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA', 'PYPL', 'INTC', 'CMCSA',
            'CSCO', 'PEP', 'ADBE', 'NFLX', 'AVGO', 'TXN', 'COST', 'QCOM', 'TMUS', 'AMGN',
            'SBUX', 'INTU', 'CHTR', 'MDLZ', 'ISRG', 'GILD', 'BKNG', 'ADP', 'AMAT', 'ADI',
            'REGN', 'ILMN', 'ATVI', 'CSX', 'MU', 'BIIB', 'LRCX', 'VRTX', 'FISV', 'ADSK',
            'NXPI', 'MELI', 'KLAC', 'MNST', 'ALGN', 'IDXX', 'WDAY', 'EXC', 'PAYX', 'CTAS'
        ]
        
        print(f"Using a list of {len(major_nasdaq_tickers)} major NASDAQ tickers as a sample.")
        return major_nasdaq_tickers
        
    except Exception as e:
        print(f"Error in fallback method: {e}")
        
        # Return a minimal list as a last resort
        minimal_tickers = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
        print(f"Using a minimal list of {len(minimal_tickers)} tickers.")
        return minimal_tickers

def check_ticker_availability(tickers, sample_size=50):
    """
    Check if tickers are available in yfinance
    
    Parameters:
    -----------
    tickers : list
        List of ticker symbols to check
    sample_size : int
        Size of the random sample to check
    
    Returns:
    --------
    tuple
        (available_tickers, unavailable_tickers, availability_percentage)
    """
    print(f"Checking availability of a random sample of {sample_size} tickers in yfinance...")
    
    # Take a random sample to avoid bias
    if len(tickers) > sample_size:
        sample_tickers = random.sample(tickers, sample_size)
    else:
        sample_tickers = tickers
    
    available_tickers = []
    unavailable_tickers = []
    
    for i, ticker in enumerate(sample_tickers):
        try:
            print(f"[{i+1}/{len(sample_tickers)}] Checking {ticker}...", end="")
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
    
    # Calculate availability percentage
    availability_percentage = (len(available_tickers) / len(sample_tickers)) * 100
    
    return available_tickers, unavailable_tickers, availability_percentage

def main():
    print("NASDAQ Ticker Availability in yfinance")
    print("======================================")
    
    # Get NASDAQ tickers
    nasdaq_tickers = get_nasdaq_tickers_from_ftp()
    
    # Print some statistics
    print(f"\nTotal NASDAQ tickers found: {len(nasdaq_tickers)}")
    print(f"First 10 tickers: {nasdaq_tickers[:10]}")
    
    # Check availability of a sample of tickers
    sample_size = 20  # Adjust this number as needed
    available, unavailable, percentage = check_ticker_availability(nasdaq_tickers, sample_size)
    
    # Print results
    print("\nResults:")
    print(f"Sample size: {len(available) + len(unavailable)} tickers")
    print(f"Available tickers: {len(available)} ({', '.join(available[:5])}{'...' if len(available) > 5 else ''})")
    print(f"Unavailable tickers: {len(unavailable)} ({', '.join(unavailable[:5])}{'...' if len(unavailable) > 5 else ''})")
    print(f"Availability percentage: {percentage:.2f}%")
    
    # Estimate total available tickers
    estimated_available = int(len(nasdaq_tickers) * percentage / 100)
    
    print(f"\nEstimated available NASDAQ tickers in yfinance: ~{estimated_available} out of {len(nasdaq_tickers)}")
    
    print("\nNote:")
    print("1. This is based on a random sample and actual availability may vary.")
    print("2. Availability can change over time due to API changes, rate limiting, etc.")
    print("3. Some tickers might be available but return incomplete data.")
    print("4. yfinance is an unofficial API and has no guarantees of data availability.")

if __name__ == "__main__":
    main()