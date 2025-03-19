"""
market_information.py

株価やニュースのデータ取得・簡易的な加工処理を行うモジュール。
"""

import os
import json
import logging
import datetime
import time
import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Optional, Union, Tuple
import yfinance as yf
from bs4 import BeautifulSoup

# ロギングの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ファイルハンドラの設定
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = logging.FileHandler('logs/market_information.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# コンソールハンドラの設定
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


def get_stock_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "1d",
    source: str = "yfinance",
    retry_count: int = 3,
    retry_delay: int = 5
) -> pd.DataFrame:
    """
    株価データを取得する関数
    
    Parameters:
    -----------
    symbol : str
        取得する銘柄のシンボル（例: "AAPL", "7203.T"）
    start_date : str, optional
        取得開始日（YYYY-MM-DD形式）
    end_date : str, optional
        取得終了日（YYYY-MM-DD形式）
    interval : str, optional
        データの間隔（"1m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"）
    source : str, optional
        データソース（"yfinance", "alpha_vantage", "custom_api"）
    retry_count : int, optional
        取得失敗時のリトライ回数
    retry_delay : int, optional
        リトライ間の待機時間（秒）
    
    Returns:
    --------
    pd.DataFrame
        取得した株価データ
    """
    # 日付の設定
    if end_date is None:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        # デフォルトは1年前
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    logger.info(f"株価データ取得開始: {symbol}, 期間: {start_date} から {end_date}, 間隔: {interval}")
    
    # データソースに応じた取得処理
    if source == "yfinance":
        return _get_stock_data_from_yfinance(symbol, start_date, end_date, interval, retry_count, retry_delay)
    elif source == "alpha_vantage":
        return _get_stock_data_from_alpha_vantage(symbol, start_date, end_date, interval, retry_count, retry_delay)
    elif source == "custom_api":
        return _get_stock_data_from_custom_api(symbol, start_date, end_date, interval, retry_count, retry_delay)
    else:
        logger.error(f"未対応のデータソース: {source}")
        raise ValueError(f"未対応のデータソース: {source}")


def _get_stock_data_from_yfinance(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str,
    retry_count: int,
    retry_delay: int
) -> pd.DataFrame:
    """
    yfinanceを使用して株価データを取得する
    """
    for attempt in range(retry_count):
        try:
            # yfinanceでデータ取得
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            # データが空かどうかチェック
            if df.empty:
                logger.warning(f"取得データが空です: {symbol}")
                if attempt < retry_count - 1:
                    logger.info(f"リトライします ({attempt+1}/{retry_count})...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"データ取得失敗: {symbol} - 空のデータセット")
                    return pd.DataFrame()
            
            # カラム名を小文字に統一
            df.columns = [col.lower() for col in df.columns]
            
            # インデックスをリセット
            df = df.reset_index()
            
            # 日付列の名前を統一
            if 'date' not in df.columns and 'datetime' in df.columns:
                df = df.rename(columns={'datetime': 'date'})
            
            logger.info(f"データ取得成功: {symbol}, {len(df)}行")
            return df
            
        except Exception as e:
            logger.error(f"データ取得エラー: {symbol} - {str(e)}")
            if attempt < retry_count - 1:
                logger.info(f"リトライします ({attempt+1}/{retry_count})...")
                time.sleep(retry_delay)
            else:
                logger.error(f"リトライ回数超過: {symbol}")
                return pd.DataFrame()


def _get_stock_data_from_alpha_vantage(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str,
    retry_count: int,
    retry_delay: int
) -> pd.DataFrame:
    """
    Alpha Vantage APIを使用して株価データを取得する
    """
    # Alpha Vantage APIキーの取得
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        logger.error("ALPHA_VANTAGE_API_KEYが設定されていません")
        return pd.DataFrame()
    
    # インターバルの変換
    av_interval = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "60m": "60min",
        "1d": "daily",
        "1wk": "weekly",
        "1mo": "monthly"
    }.get(interval, "daily")
    
    # 関数の選択
    if av_interval in ["1min", "5min", "15min", "30min", "60min"]:
        function = "TIME_SERIES_INTRADAY"
        params = {
            "function": function,
            "symbol": symbol,
            "interval": av_interval,
            "apikey": api_key,
            "outputsize": "full"
        }
    else:
        function = {
            "daily": "TIME_SERIES_DAILY",
            "weekly": "TIME_SERIES_WEEKLY",
            "monthly": "TIME_SERIES_MONTHLY"
        }.get(av_interval)
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": api_key,
            "outputsize": "full"
        }
    
    # APIリクエスト
    for attempt in range(retry_count):
        try:
            response = requests.get("https://www.alphavantage.co/query", params=params)
            response.raise_for_status()
            data = response.json()
            
            # エラーチェック
            if "Error Message" in data:
                logger.error(f"Alpha Vantage APIエラー: {data['Error Message']}")
                return pd.DataFrame()
            
            # データの抽出
            time_series_key = next((k for k in data.keys() if "Time Series" in k), None)
            if not time_series_key:
                logger.error(f"Alpha Vantage APIレスポンス形式エラー: {list(data.keys())}")
                return pd.DataFrame()
            
            # DataFrameに変換
            df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # カラム名の整理
            df.columns = [col.split(". ")[1].lower() for col in df.columns]
            
            # 日付範囲でフィルタリング
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            # インデックスをリセットして日付列を追加
            df = df.reset_index()
            df = df.rename(columns={"index": "date"})
            
            # データ型の変換
            for col in df.columns:
                if col != "date":
                    df[col] = pd.to_numeric(df[col])
            
            logger.info(f"Alpha Vantageからデータ取得成功: {symbol}, {len(df)}行")
            return df
            
        except Exception as e:
            logger.error(f"Alpha Vantageデータ取得エラー: {symbol} - {str(e)}")
            if attempt < retry_count - 1:
                logger.info(f"リトライします ({attempt+1}/{retry_count})...")
                time.sleep(retry_delay)
            else:
                logger.error(f"リトライ回数超過: {symbol}")
                return pd.DataFrame()


def _get_stock_data_from_custom_api(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str,
    retry_count: int,
    retry_delay: int
) -> pd.DataFrame:
    """
    カスタムAPIを使用して株価データを取得する
    """
    # カスタムAPIのエンドポイントとキー
    api_endpoint = os.getenv("CUSTOM_API_ENDPOINT")
    api_key = os.getenv("CUSTOM_API_KEY")
    
    if not api_endpoint or not api_key:
        logger.error("CUSTOM_API_ENDPOINTまたはCUSTOM_API_KEYが設定されていません")
        return pd.DataFrame()
    
    # APIリクエスト
    for attempt in range(retry_count):
        try:
            response = requests.get(
                api_endpoint,
                params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "interval": interval,
                    "api_key": api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # DataFrameに変換
            df = pd.DataFrame(data["data"])
            
            # 日付列の処理
            df["date"] = pd.to_datetime(df["date"])
            
            logger.info(f"カスタムAPIからデータ取得成功: {symbol}, {len(df)}行")
            return df
            
        except Exception as e:
            logger.error(f"カスタムAPIデータ取得エラー: {symbol} - {str(e)}")
            if attempt < retry_count - 1:
                logger.info(f"リトライします ({attempt+1}/{retry_count})...")
                time.sleep(retry_delay)
            else:
                logger.error(f"リトライ回数超過: {symbol}")
                return pd.DataFrame()


def get_news_data(
    query: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: str = "newsapi",
    max_results: int = 100,
    language: str = "ja",
    retry_count: int = 3,
    retry_delay: int = 5
) -> List[Dict]:
    """
    ニュースデータを取得する関数
    
    Parameters:
    -----------
    query : str
        検索クエリ（例: "Apple", "トヨタ"）
    start_date : str, optional
        取得開始日（YYYY-MM-DD形式）
    end_date : str, optional
        取得終了日（YYYY-MM-DD形式）
    source : str, optional
        データソース（"newsapi", "custom_news_api", "web_scraping"）
    max_results : int, optional
        取得する最大記事数
    language : str, optional
        言語コード（"ja", "en"など）
    retry_count : int, optional
        取得失敗時のリトライ回数
    retry_delay : int, optional
        リトライ間の待機時間（秒）
    
    Returns:
    --------
    List[Dict]
        取得したニュースデータのリスト
    """
    # 日付の設定
    if end_date is None:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        # デフォルトは1週間前
        start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    
    logger.info(f"ニュースデータ取得開始: '{query}', 期間: {start_date} から {end_date}")
    
    # データソースに応じた取得処理
    if source == "newsapi":
        return _get_news_from_newsapi(query, start_date, end_date, max_results, language, retry_count, retry_delay)
    elif source == "custom_news_api":
        return _get_news_from_custom_api(query, start_date, end_date, max_results, language, retry_count, retry_delay)
    elif source == "web_scraping":
        return _get_news_from_web_scraping(query, start_date, end_date, max_results, language, retry_count, retry_delay)
    else:
        logger.error(f"未対応のニュースソース: {source}")
        raise ValueError(f"未対応のニュースソース: {source}")


def _get_news_from_newsapi(
    query: str,
    start_date: str,
    end_date: str,
    max_results: int,
    language: str,
    retry_count: int,
    retry_delay: int
) -> List[Dict]:
    """
    News APIを使用してニュースデータを取得する
    """
    # News API キーの取得
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        logger.error("NEWS_API_KEYが設定されていません")
        return []
    
    # APIリクエスト
    for attempt in range(retry_count):
        try:
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "from": start_date,
                    "to": end_date,
                    "language": language,
                    "sortBy": "publishedAt",
                    "pageSize": min(max_results, 100),  # News APIの上限は100
                    "apiKey": api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # エラーチェック
            if data.get("status") != "ok":
                logger.error(f"News APIエラー: {data.get('message', 'Unknown error')}")
                if attempt < retry_count - 1:
                    logger.info(f"リトライします ({attempt+1}/{retry_count})...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return []
            
            # 記事の抽出と整形
            articles = data.get("articles", [])
            
            # 必要なフィールドのみ抽出
            processed_articles = []
            for article in articles:
                processed_articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "published_at": article.get("publishedAt", ""),
                    "author": article.get("author", ""),
                    "query": query
                })
            
            logger.info(f"News APIからニュース取得成功: '{query}', {len(processed_articles)}件")
            return processed_articles
            
        except Exception as e:
            logger.error(f"News APIデータ取得エラー: '{query}' - {str(e)}")
            if attempt < retry_count - 1:
                logger.info(f"リトライします ({attempt+1}/{retry_count})...")
                time.sleep(retry_delay)
            else:
                logger.error(f"リトライ回数超過: '{query}'")
                return []


def _get_news_from_custom_api(
    query: str,
    start_date: str,
    end_date: str,
    max_results: int,
    language: str,
    retry_count: int,
    retry_delay: int
) -> List[Dict]:
    """
    カスタムAPIを使用してニュースデータを取得する
    """
    # カスタムAPIのエンドポイントとキー
    api_endpoint = os.getenv("CUSTOM_NEWS_API_ENDPOINT")
    api_key = os.getenv("CUSTOM_NEWS_API_KEY")
    
    if not api_endpoint or not api_key:
        logger.error("CUSTOM_NEWS_API_ENDPOINTまたはCUSTOM_NEWS_API_KEYが設定されていません")
        return []
    
    # APIリクエスト
    for attempt in range(retry_count):
        try:
            response = requests.get(
                api_endpoint,
                params={
                    "query": query,
                    "start_date": start_date,
                    "end_date": end_date,
                    "max_results": max_results,
                    "language": language,
                    "api_key": api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # 記事の抽出
            articles = data.get("articles", [])
            
            logger.info(f"カスタムAPIからニュース取得成功: '{query}', {len(articles)}件")
            return articles
            
        except Exception as e:
            logger.error(f"カスタムAPIニュース取得エラー: '{query}' - {str(e)}")
            if attempt < retry_count - 1:
                logger.info(f"リトライします ({attempt+1}/{retry_count})...")
                time.sleep(retry_delay)
            else:
                logger.error(f"リトライ回数超過: '{query}'")
                return []


def _get_news_from_web_scraping(
    query: str,
    start_date: str,
    end_date: str,
    max_results: int,
    language: str,
    retry_count: int,
    retry_delay: int
) -> List[Dict]:
    """
    Webスクレイピングを使用してニュースデータを取得する
    """
    # 言語に応じたニュースサイトの選択
    if language == "ja":
        # 日本語ニュースサイトの例
        news_sites = [
            {"url": f"https://news.yahoo.co.jp/search?p={query}", "parser": _parse_yahoo_news},
            {"url": f"https://www.nikkei.com/search?keyword={query}", "parser": _parse_nikkei_news}
        ]
    else:
        # 英語ニュースサイトの例
        news_sites = [
            {"url": f"https://www.reuters.com/search/news?blob={query}", "parser": _parse_reuters_news},
            {"url": f"https://www.bloomberg.com/search?query={query}", "parser": _parse_bloomberg_news}
        ]
    
    all_articles = []
    
    # 各サイトからニュースを取得
    for site in news_sites:
        for attempt in range(retry_count):
            try:
                # ページの取得
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(site["url"], headers=headers)
                response.raise_for_status()
                
                # HTMLの解析
                soup = BeautifulSoup(response.text, "html.parser")
                
                # サイト固有のパーサーでニュース記事を抽出
                articles = site["parser"](soup, query, start_date, end_date)
                
                all_articles.extend(articles)
                
                logger.info(f"Webスクレイピングからニュース取得成功: '{query}', {len(articles)}件")
                break
                
            except Exception as e:
                logger.error(f"Webスクレイピングエラー: '{query}' - {str(e)}")
                if attempt < retry_count - 1:
                    logger.info(f"リトライします ({attempt+1}/{retry_count})...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"リトライ回数超過: '{query}'")
    
    # 最大件数で切り捨て
    return all_articles[:max_results]


def _parse_yahoo_news(soup: BeautifulSoup, query: str, start_date: str, end_date: str) -> List[Dict]:
    """
    Yahoo!ニュースのHTMLを解析してニュース記事を抽出する
    """
    articles = []
    
    # 記事要素の抽出（実際のHTMLに合わせて調整が必要）
    article_elements = soup.select("div.newsFeed_item")
    
    for element in article_elements:
        try:
            # タイトル
            title_element = element.select_one("div.newsFeed_item_title")
            title = title_element.text.strip() if title_element else ""
            
            # リンク
            link_element = element.select_one("a.newsFeed_item_link")
            url = link_element["href"] if link_element and "href" in link_element.attrs else ""
            
            # 説明
            desc_element = element.select_one("div.newsFeed_item_desc")
            description = desc_element.text.strip() if desc_element else ""
            
            # 日付
            date_element = element.select_one("time.newsFeed_item_date")
            published_at = date_element["datetime"] if date_element and "datetime" in date_element.attrs else ""
            
            # 日付のフィルタリング
            if published_at:
                pub_date = datetime.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                start = datetime.datetime.fromisoformat(f"{start_date}T00:00:00+00:00")
                end = datetime.datetime.fromisoformat(f"{end_date}T23:59:59+00:00")
                
                if pub_date < start or pub_date > end:
                    continue
            
            # 記事の追加
            articles.append({
                "title": title,
                "description": description,
                "content": "",  # 本文は記事ページを取得する必要がある
                "url": url,
                "source": "Yahoo!ニュース",
                "published_at": published_at,
                "author": "",
                "query": query
            })
            
        except Exception as e:
            logger.error(f"Yahoo!ニュース記事の解析エラー: {str(e)}")
    
    return articles


def _parse_nikkei_news(soup: BeautifulSoup, query: str, start_date: str, end_date: str) -> List[Dict]:
    """
    日経新聞のHTMLを解析してニュース記事を抽出する
    """
    # 実装は省略（Yahoo!ニュースと同様の方法で実装）
    return []


def _parse_reuters_news(soup: BeautifulSoup, query: str, start_date: str, end_date: str) -> List[Dict]:
    """
    ロイターのHTMLを解析してニュース記事を抽出する
    """
    # 実装は省略
    return []


def _parse_bloomberg_news(soup: BeautifulSoup, query: str, start_date: str, end_date: str) -> List[Dict]:
    """
    ブルームバーグのHTMLを解析してニュース記事を抽出する
    """
    # 実装は省略
    return []


def preprocess_stock_data(df: pd.DataFrame, add_indicators: bool = True) -> pd.DataFrame:
    """
    株価データの前処理を行う関数
    
    Parameters:
    -----------
    df : pd.DataFrame
        前処理する株価データ
    add_indicators : bool, optional
        テクニカル指標を追加するかどうか
    
    Returns:
    --------
    pd.DataFrame
        前処理後の株価データ
    """
    if df.empty:
        logger.warning("前処理対象のデータが空です")
        return df
    
    # カラム名の確認と標準化
    required_columns = ["date", "open", "high", "low", "close", "volume"]
    
    # カラム名を小文字に変換
    df.columns = [col.lower() for col in df.columns]
    
    # 必須カラムの存在確認
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"必須カラムがありません: {missing_columns}")
        return df
    
    # 日付型の確認と変換
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])
    
    # 欠損値の処理
    if df.isnull().any().any():
        logger.warning(f"欠損値があります: {df.isnull().sum()}")
        # 前方補間
        df = df.fillna(method="ffill")
        # 残りの欠損値（先頭など）は後方補間
        df = df.fillna(method="bfill")
    
    # 重複行の削除
    if df.duplicated(subset=["date"]).any():
        logger.warning(f"重複行があります: {df.duplicated(subset=['date']).sum()}行")
        df = df.drop_duplicates(subset=["date"])
    
    # 日付でソート
    df = df.sort_values("date")
    
    # テクニカル指標の追加
    if add_indicators:
        df = add_technical_indicators(df)
    
    # 日次リターンの計算
    df["daily_return"] = df["close"].pct_change()
    
    # 対数リターンの計算
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    
    # 欠損値の削除（最初の行など）
    df = df.dropna()
    
    logger.info(f"データ前処理完了: {len(df)}行, {df.columns.tolist()}")
    return df


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    テクニカル指標を追加する関数
    
    Parameters:
    -----------
    df : pd.DataFrame
        テクニカル指標を追加する株価データ
    
    Returns:
    --------
    pd.DataFrame
        テクニカル指標が追加された株価データ
    """
    # 移動平均
    df["sma_5"] = df["close"].rolling(window=5).mean()
    df["sma_20"] = df["close"].rolling(window=20).mean()
    df["sma_50"] = df["close"].rolling(window=50).mean()
    df["sma_200"] = df["close"].rolling(window=200).mean()
    
    # ボリンジャーバンド
    df["bb_middle"] = df["close"].rolling(window=20).mean()
    df["bb_std"] = df["close"].rolling(window=20).std()
    df["bb_upper"] = df["bb_middle"] + 2 * df["bb_std"]
    df["bb_lower"] = df["bb_middle"] - 2 * df["bb_std"]
    
    # RSI
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df["close"].ewm(span=12, adjust=False).mean()
    exp2 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = exp1 - exp2
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    
    # ATR (Average True Range)
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df["atr"] = true_range.rolling(14).mean()
    
    # ストキャスティクス
    low_14 = df["low"].rolling(window=14).min()
    high_14 = df["high"].rolling(window=14).max()
    df["stoch_k"] = 100 * ((df["close"] - low_14) / (high_14 - low_14))
    df["stoch_d"] = df["stoch_k"].rolling(window=3).mean()
    
    return df


def analyze_news_sentiment(news_data: List[Dict]) -> List[Dict]:
    """
    ニュースデータの感情分析を行う関数
    
    Parameters:
    -----------
    news_data : List[Dict]
        感情分析を行うニュースデータ
    
    Returns:
    --------
    List[Dict]
        感情分析結果が追加されたニュースデータ
    """
    # 感情分析APIのエンドポイントとキー
    api_endpoint = os.getenv("SENTIMENT_API_ENDPOINT")
    api_key = os.getenv("SENTIMENT_API_KEY")
    
    if not api_endpoint or not api_key:
        logger.warning("SENTIMENT_API_ENDPOINTまたはSENTIMENT_API_KEYが設定されていません。ダミーの感情スコアを使用します。")
        # ダミーの感情スコアを生成
        for article in news_data:
            article["sentiment"] = {
                "score": np.random.uniform(-1, 1),  # -1（ネガティブ）から1（ポジティブ）
                "magnitude": np.random.uniform(0, 10),  # 0（中立）から10（強い感情）
                "label": np.random.choice(["positive", "negative", "neutral"])
            }
        return news_data
    
    # 感情分析APIを使用
    analyzed_news = []
    
    for article in news_data:
        try:
            # APIリクエスト
            response = requests.post(
                api_endpoint,
                headers={"Content-Type": "application/json", "X-API-Key": api_key},
                json={
                    "text": article.get("title", "") + " " + article.get("description", "")
                }
            )
            response.raise_for_status()
            sentiment_data = response.json()
            
            # 感情分析結果の追加
            article["sentiment"] = {
                "score": sentiment_data.get("score", 0),
                "magnitude": sentiment_data.get("magnitude", 0),
                "label": sentiment_data.get("label", "neutral")
            }
            
            analyzed_news.append(article)
            
        except Exception as e:
            logger.error(f"感情分析エラー: {str(e)}")
            # エラー時はダミーの感情スコアを使用
            article["sentiment"] = {
                "score": 0,
                "magnitude": 0,
                "label": "neutral"
            }
            analyzed_news.append(article)
    
    return analyzed_news


def save_data(data: Union[pd.DataFrame, List[Dict]], data_type: str, symbol: str = None, date: str = None) -> str:
    """
    データを保存する関数
    
    Parameters:
    -----------
    data : Union[pd.DataFrame, List[Dict]]
        保存するデータ
    data_type : str
        データの種類（"stock", "news"）
    symbol : str, optional
        銘柄シンボル（株価データの場合）
    date : str, optional
        日付（YYYYMMDD形式）
    
    Returns:
    --------
    str
        保存したファイルのパス
    """
    # 日付の設定
    if date is None:
        date = datetime.datetime.now().strftime('%Y%m%d')
    
    # データ種類に応じたディレクトリとファイル名の設定
    if data_type == "stock":
        if symbol is None:
            logger.error("株価データの保存にはsymbolが必要です")
            return ""
        
        directory = f"data/market_information/raw"
        filename = f"{symbol}_{date}.csv"
        
        # DataFrameをCSVに保存
        if isinstance(data, pd.DataFrame):
            os.makedirs(directory, exist_ok=True)
            file_path = os.path.join(directory, filename)
            data.to_csv(file_path, index=False)
            logger.info(f"株価データを保存しました: {file_path}")
            return file_path
        else:
            logger.error("株価データはDataFrame形式である必要があります")
            return ""
            
    elif data_type == "news":
        directory = f"data/market_information/news"
        query = data[0].get("query", "unknown") if data else "unknown"
        filename = f"news_{query}_{date}.json"
        
        # リストをJSONに保存
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"ニュースデータを保存しました: {file_path}")
        return file_path
        
    else:
        logger.error(f"未対応のデータ種類: {data_type}")
        return ""


def load_data(data_type: str, symbol: str = None, date: str = None, query: str = None) -> Union[pd.DataFrame, List[Dict]]:
    """
    保存されたデータを読み込む関数
    
    Parameters:
    -----------
    data_type : str
        データの種類（"stock", "news"）
    symbol : str, optional
        銘柄シンボル（株価データの場合）
    date : str, optional
        日付（YYYYMMDD形式）
    query : str, optional
        検索クエリ（ニュースデータの場合）
    
    Returns:
    --------
    Union[pd.DataFrame, List[Dict]]
        読み込んだデータ
    """
    # 日付の設定
    if date is None:
        date = datetime.datetime.now().strftime('%Y%m%d')
    
    # データ種類に応じたディレクトリとファイル名の設定
    if data_type == "stock":
        if symbol is None:
            logger.error("株価データの読み込みにはsymbolが必要です")
            return pd.DataFrame()
        
        directory = f"data/market_information/raw"
        filename = f"{symbol}_{date}.csv"
        file_path = os.path.join(directory, filename)
        
        # CSVからDataFrameを読み込み
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                logger.info(f"株価データを読み込みました: {file_path}")
                return df
            except Exception as e:
                logger.error(f"株価データの読み込みエラー: {str(e)}")
                return pd.DataFrame()
        else:
            logger.warning(f"株価データファイルが存在しません: {file_path}")
            return pd.DataFrame()
            
    elif data_type == "news":
        directory = f"data/market_information/news"
        
        if query is None:
            logger.error("ニュースデータの読み込みにはqueryが必要です")
            return []
        
        filename = f"news_{query}_{date}.json"
        file_path = os.path.join(directory, filename)
        
        # JSONからリストを読み込み
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.info(f"ニュースデータを読み込みました: {file_path}")
                return data
            except Exception as e:
                logger.error(f"ニュースデータの読み込みエラー: {str(e)}")
                return []
        else:
            logger.warning(f"ニュースデータファイルが存在しません: {file_path}")
            return []
        
    else:
        logger.error(f"未対応のデータ種類: {data_type}")
        return None


if __name__ == "__main__":
    # 動作確認用のコード
    logger.info("market_information.py の動作確認を開始します")
    
    # 株価データの取得
    symbol = "AAPL"
    stock_data = get_stock_data(symbol, start_date="2023-01-01", end_date="2023-01-31")
    
    if not stock_data.empty:
        # データの前処理
        processed_data = preprocess_stock_data(stock_data)
        
        # データの保存
        save_data(processed_data, "stock", symbol)
    
    # ニュースデータの取得
    query = "Apple"
    news_data = get_news_data(query, start_date="2023-01-01", end_date="2023-01-31")
    
    if news_data:
        # 感情分析
        analyzed_news = analyze_news_sentiment(news_data)
        
        # データの保存
        save_data(analyzed_news, "news")
    
    logger.info("market_information.py の動作確認を終了します")