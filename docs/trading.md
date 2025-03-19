# トレード実行方法に関する説明

## 1. 証券API連携とダミートレードの違い

取引システムを実装する際、実際の市場で取引を行う「実取引」と、仮想的に取引をシミュレーションする「ダミートレード（ペーパートレード）」の2つの方法があります。それぞれの特徴と違いを理解することが重要です。

### 証券API連携（実取引）

実取引では、証券会社や取引所が提供するAPIを使用して、実際の市場で注文を発注し、実際の資金で取引を行います。

**特徴:**
- 実際の資金を使用して取引が行われる
- 実際の市場流動性、スリッページ、手数料が発生する
- 注文の約定は市場状況に依存する
- 取引結果が実際の損益として反映される

**主な証券API:**
- Interactive Brokers API
- Alpaca API
- TD Ameritrade API
- 楽天証券API
- SBI証券API

**実装例（Interactive Brokers API）:**
```python
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

class IBTrader(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        
    def place_market_order(self, symbol, quantity, action):
        """
        市場注文を発注する
        
        Parameters:
        -----------
        symbol : str
            銘柄シンボル
        quantity : int
            数量
        action : str
            'BUY' または 'SELL'
        """
        # 注文IDの生成
        order_id = self.next_order_id()
        
        # 銘柄情報の設定
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        
        # 注文情報の設定
        order = Order()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity
        
        # 注文の発注
        self.placeOrder(order_id, contract, order)
        print(f"Market order placed: {action} {quantity} {symbol}")
```

### ダミートレード（ペーパートレード）

ダミートレードは、実際の資金を使わずに仮想的に取引をシミュレーションする方法です。戦略のテストや練習に適しています。

**特徴:**
- 仮想資金を使用するため、実際の損失リスクがない
- 取引結果は仮想的な損益として記録される
- 市場の流動性やスリッページを完全に再現することは難しい
- システムの安定性や戦略の有効性を検証できる

**実装方法:**
- 証券会社が提供するペーパートレード環境を利用する
- 独自のペーパートレードシステムを実装する
- バックテストシステムをリアルタイムデータで動作させる

**実装例（独自ペーパートレードシステム）:**
```python
class PaperTrader:
    def __init__(self, initial_capital=100000):
        self.capital = initial_capital
        self.positions = {}  # シンボル -> 数量のマッピング
        self.trades = []  # 取引履歴
        
    def place_order(self, symbol, quantity, price, action, order_type="MARKET"):
        """
        ペーパートレード注文を実行
        
        Parameters:
        -----------
        symbol : str
            銘柄シンボル
        quantity : int
            数量
        price : float
            価格（指値注文の場合）
        action : str
            'BUY' または 'SELL'
        order_type : str
            'MARKET' または 'LIMIT'
        """
        # 手数料の計算（例: 取引額の0.1%）
        commission = price * quantity * 0.001
        
        # 取引額の計算
        trade_value = price * quantity + commission
        
        # 買い注文の処理
        if action == "BUY":
            # 資金チェック
            if trade_value > self.capital:
                print(f"Insufficient funds: Required {trade_value}, Available {self.capital}")
                return False
            
            # 資金の減少
            self.capital -= trade_value
            
            # ポジションの更新
            if symbol in self.positions:
                self.positions[symbol] += quantity
            else:
                self.positions[symbol] = quantity
                
        # 売り注文の処理
        elif action == "SELL":
            # ポジションチェック
            if symbol not in self.positions or self.positions[symbol] < quantity:
                print(f"Insufficient position: Required {quantity}, Available {self.positions.get(symbol, 0)}")
                return False
            
            # 資金の増加
            self.capital += trade_value - 2 * commission  # 手数料を2回引く
            
            # ポジションの更新
            self.positions[symbol] -= quantity
            if self.positions[symbol] == 0:
                del self.positions[symbol]
        
        # 取引の記録
        trade = {
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "commission": commission,
            "timestamp": datetime.now(),
            "order_type": order_type
        }
        self.trades.append(trade)
        
        print(f"Paper trade executed: {action} {quantity} {symbol} @ {price}")
        return True
```

### 主な違い

| 項目 | 証券API連携（実取引） | ダミートレード（ペーパートレード） |
|------|----------------------|--------------------------------|
| 資金 | 実際の資金を使用 | 仮想資金を使用 |
| リスク | 実際の損失リスクあり | 損失リスクなし |
| 約定 | 実際の市場状況に依存 | シミュレーションによる仮想約定 |
| 流動性 | 実際の市場流動性に制限される | 理想的な流動性を仮定可能 |
| 心理的要因 | 実際の損益による心理的影響あり | 心理的影響が少ない |
| 目的 | 実際の利益獲得 | 戦略検証、トレーニング |

## 2. 注文タイプの基本

取引を行う際には、様々な注文タイプを使い分けることで、取引の効率性やリスク管理を向上させることができます。

### 主な注文タイプ

#### 成行注文（Market Order）
- **概要**: 現在の市場価格で即時に約定させる注文
- **メリット**: 確実に約定する（流動性がある限り）
- **デメリット**: 約定価格が不明確、スリッページのリスクが高い
- **適した状況**: 即時の取引執行が必要な場合、高流動性銘柄の取引

```python
def place_market_order(api, symbol, quantity, side):
    """
    成行注文を発注する
    
    Parameters:
    -----------
    api : TradingAPI
        取引APIインスタンス
    symbol : str
        銘柄シンボル
    quantity : int
        数量
    side : str
        'buy' または 'sell'
    """
    order = {
        "symbol": symbol,
        "quantity": quantity,
        "side": side,
        "type": "market",
        "time_in_force": "day"
    }
    return api.submit_order(order)
```

#### 指値注文（Limit Order）
- **概要**: 指定した価格以下（買い）または以上（売り）でのみ約定する注文
- **メリット**: 約定価格が明確、スリッページがない
- **デメリット**: 指定価格に到達しない場合は約定しない
- **適した状況**: 特定価格での取引を希望する場合、低流動性銘柄の取引

```python
def place_limit_order(api, symbol, quantity, side, limit_price):
    """
    指値注文を発注する
    
    Parameters:
    -----------
    api : TradingAPI
        取引APIインスタンス
    symbol : str
        銘柄シンボル
    quantity : int
        数量
    side : str
        'buy' または 'sell'
    limit_price : float
        指値価格
    """
    order = {
        "symbol": symbol,
        "quantity": quantity,
        "side": side,
        "type": "limit",
        "limit_price": limit_price,
        "time_in_force": "day"
    }
    return api.submit_order(order)
```

#### 逆指値注文（Stop Order）
- **概要**: 指定した価格に到達した時点で成行注文として発注される注文
- **メリット**: 価格トリガーによる自動執行、損失制限に有効
- **デメリット**: トリガー後は成行注文となるためスリッページのリスクあり
- **適した状況**: 損切り（ストップロス）の設定

```python
def place_stop_order(api, symbol, quantity, side, stop_price):
    """
    逆指値注文を発注する
    
    Parameters:
    -----------
    api : TradingAPI
        取引APIインスタンス
    symbol : str
        銘柄シンボル
    quantity : int
        数量
    side : str
        'buy' または 'sell'
    stop_price : float
        逆指値価格
    """
    order = {
        "symbol": symbol,
        "quantity": quantity,
        "side": side,
        "type": "stop",
        "stop_price": stop_price,
        "time_in_force": "day"
    }
    return api.submit_order(order)
```

#### 逆指値指値注文（Stop Limit Order）
- **概要**: 指定した価格に到達した時点で指値注文として発注される注文
- **メリット**: 価格トリガーと約定価格の両方を制御できる
- **デメリット**: トリガー後も指値価格に到達しないと約定しない
- **適した状況**: スリッページを抑えつつ損切りを行いたい場合

```python
def place_stop_limit_order(api, symbol, quantity, side, stop_price, limit_price):
    """
    逆指値指値注文を発注する
    
    Parameters:
    -----------
    api : TradingAPI
        取引APIインスタンス
    symbol : str
        銘柄シンボル
    quantity : int
        数量
    side : str
        'buy' または 'sell'
    stop_price : float
        逆指値価格
    limit_price : float
        指値価格
    """
    order = {
        "symbol": symbol,
        "quantity": quantity,
        "side": side,
        "type": "stop_limit",
        "stop_price": stop_price,
        "limit_price": limit_price,
        "time_in_force": "day"
    }
    return api.submit_order(order)
```

### 有効期限の設定

注文の有効期限（Time in Force）は、注文がどれだけの期間有効であるかを指定します。

- **当日中（Day）**: 取引日の終了まで有効
- **即時執行・取消（IOC: Immediate or Cancel）**: 即時に一部または全部を約定し、残りはキャンセル
- **全数執行・取消（FOK: Fill or Kill）**: 全数量が即時に約定するか、全てキャンセル
- **取消まで有効（GTC: Good Till Canceled）**: 明示的にキャンセルされるまで有効
- **日時指定（GTD: Good Till Date）**: 指定した日時まで有効

```python
def place_order_with_tif(api, symbol, quantity, side, order_type, tif, **params):
    """
    有効期限を指定して注文を発注する
    
    Parameters:
    -----------
    api : TradingAPI
        取引APIインスタンス
    symbol : str
        銘柄シンボル
    quantity : int
        数量
    side : str
        'buy' または 'sell'
    order_type : str
        注文タイプ ('market', 'limit', 'stop', 'stop_limit')
    tif : str
        有効期限 ('day', 'ioc', 'fok', 'gtc', 'gtd')
    params : dict
        その他のパラメータ（limit_price, stop_price, expire_dateなど）
    """
    order = {
        "symbol": symbol,
        "quantity": quantity,
        "side": side,
        "type": order_type,
        "time_in_force": tif,
        **params
    }
    return api.submit_order(order)
```

## 3. 注文失敗時の処理やリトライ方針

取引システムでは、様々な理由で注文が失敗することがあります。これらの失敗に適切に対応するための処理とリトライ方針が重要です。

### 注文失敗の主な原因

1. **接続エラー**: API接続の切断やタイムアウト
2. **認証エラー**: APIキーの無効化や権限不足
3. **バリデーションエラー**: 注文パラメータの不備（数量不足、価格制限など）
4. **資金不足**: 注文に必要な資金が不足
5. **市場状況**: 取引停止、サーキットブレーカー発動
6. **レート制限**: APIのリクエスト制限超過

### エラーハンドリングの基本方針

1. **エラーの分類**: 一時的なエラーと永続的なエラーを区別する
2. **ログ記録**: すべてのエラーを詳細にログに記録する
3. **通知**: 重大なエラーは管理者に通知する
4. **リトライ**: 一時的なエラーに対しては適切なリトライ戦略を実装する
5. **フォールバック**: 代替手段がある場合は切り替える

### リトライ戦略

#### 指数バックオフ
失敗するたびに待機時間を指数関数的に増加させる方法です。

```python
import time
import random

def exponential_backoff_retry(func, max_retries=5, initial_delay=1, max_delay=60):
    """
    指数バックオフを使用した関数実行のリトライ
    
    Parameters:
    -----------
    func : callable
        実行する関数
    max_retries : int
        最大リトライ回数
    initial_delay : float
        初期待機時間（秒）
    max_delay : float
        最大待機時間（秒）
    
    Returns:
    --------
    結果またはNone（全リトライ失敗時）
    """
    delay = initial_delay
    
    for retry in range(max_retries):
        try:
            return func()
        except Exception as e:
            # 永続的なエラーの場合はすぐに失敗
            if is_permanent_error(e):
                logger.error(f"Permanent error: {str(e)}")
                return None
            
            # 最後のリトライでも失敗した場合
            if retry == max_retries - 1:
                logger.error(f"All retries failed: {str(e)}")
                return None
            
            # 待機時間にランダム性を加える（ジッター）
            jitter = random.uniform(0, 0.1 * delay)
            wait_time = delay + jitter
            
            logger.warning(f"Retry {retry+1}/{max_retries} after {wait_time:.2f}s: {str(e)}")
            time.sleep(wait_time)
            
            # 次の待機時間を計算（最大値を超えないように）
            delay = min(delay * 2, max_delay)
    
    return None
```

#### 条件付きリトライ
エラーの種類や状況に応じてリトライ戦略を変える方法です。

```python
def conditional_retry(order_func, symbol, quantity, side, **params):
    """
    条件に応じたリトライ戦略
    
    Parameters:
    -----------
    order_func : callable
        注文関数
    symbol : str
        銘柄シンボル
    quantity : int
        数量
    side : str
        'buy' または 'sell'
    params : dict
        その他のパラメータ
    """
    max_retries = 5
    
    for retry in range(max_retries):
        try:
            return order_func(symbol, quantity, side, **params)
        except ConnectionError as e:
            # 接続エラーは短い間隔でリトライ
            if retry < max_retries - 1:
                logger.warning(f"Connection error, retrying in 2s: {str(e)}")
                time.sleep(2)
            else:
                logger.error(f"Connection error, all retries failed: {str(e)}")
                return None
        except RateLimitError as e:
            # レート制限エラーは長めの間隔でリトライ
            wait_time = 30 * (retry + 1)
            logger.warning(f"Rate limit error, retrying in {wait_time}s: {str(e)}")
            time.sleep(wait_time)
        except InsufficientFundsError as e:
            # 資金不足は即時失敗
            logger.error(f"Insufficient funds: {str(e)}")
            return None
        except ValidationError as e:
            # バリデーションエラーは注文パラメータを調整してリトライ
            logger.warning(f"Validation error: {str(e)}")
            # パラメータ調整ロジック（例: 数量を調整）
            if "quantity" in str(e).lower():
                new_quantity = adjust_quantity(quantity, retry)
                if new_quantity != quantity:
                    logger.info(f"Adjusting quantity from {quantity} to {new_quantity}")
                    quantity = new_quantity
                    continue
            return None
        except Exception as e:
            # その他のエラーは一定間隔でリトライ
            logger.error(f"Unexpected error: {str(e)}")
            if retry < max_retries - 1:
                time.sleep(5)
            else:
                return None
    
    return None
```

### 注文状態の監視と確認

注文を発注した後は、その状態を監視して適切に対応することが重要です。

```python
def monitor_order_status(api, order_id, timeout=60):
    """
    注文状態を監視する
    
    Parameters:
    -----------
    api : TradingAPI
        取引APIインスタンス
    order_id : str
        注文ID
    timeout : int
        タイムアウト時間（秒）
    
    Returns:
    --------
    最終的な注文状態
    """
    start_time = time.time()
    check_interval = 2  # 2秒ごとにチェック
    
    while time.time() - start_time < timeout:
        try:
            order = api.get_order(order_id)
            status = order["status"]
            
            logger.info(f"Order {order_id} status: {status}")
            
            # 終了状態の場合
            if status in ["filled", "canceled", "rejected", "expired"]:
                if status == "filled":
                    logger.info(f"Order filled: {order}")
                elif status == "rejected":
                    logger.warning(f"Order rejected: {order}")
                return status
            
            # まだ処理中の場合は待機
            time.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"Error checking order status: {str(e)}")
            time.sleep(check_interval)
    
    # タイムアウト
    logger.warning(f"Order status check timed out after {timeout}s")
    return "timeout"
```

## 4. リスク管理（発注制限など）

取引システムにおけるリスク管理は、予期せぬ損失から資産を守るために不可欠です。適切なリスク管理メカニズムを実装することで、システムの安全性と信頼性を高めることができます。

### ポジションサイズの制限

資金に対する適切なポジションサイズを設定することで、1つの取引による損失を制限します。

```python
def calculate_position_size(account_value, risk_per_trade, stop_loss_pct):
    """
    リスクに基づいたポジションサイズを計算
    
    Parameters:
    -----------
    account_value : float
        口座の資産価値
    risk_per_trade : float
        1取引あたりのリスク比率（例: 0.01 = 1%）
    stop_loss_pct : float
        ストップロスの比率（例: 0.05 = 5%）
    
    Returns:
    --------
    float
        適切なポジションサイズ（金額）
    """
    # リスク金額の計算
    risk_amount = account_value * risk_per_trade
    
    # ポジションサイズの計算
    position_size = risk_amount / stop_loss_pct
    
    return position_size
```

### 注文数量の制限

1回の注文で発注できる最大数量を制限します。

```python
def limit_order_quantity(symbol, requested_quantity, max_quantity_per_order, max_notional_value=None, current_price=None):
    """
    注文数量を制限する
    
    Parameters:
    -----------
    symbol : str
        銘柄シンボル
    requested_quantity : int
        要求された注文数量
    max_quantity_per_order : int
        1注文あたりの最大数量
    max_notional_value : float, optional
        1注文あたりの最大金額
    current_price : float, optional
        現在の価格（max_notional_valueが指定された場合に必要）
    
    Returns:
    --------
    int
        制限された注文数量
    """
    limited_quantity = min(requested_quantity, max_quantity_per_order)
    
    # 金額ベースの制限がある場合
    if max_notional_value is not None and current_price is not None:
        max_quantity_by_value = int(max_notional_value / current_price)
        limited_quantity = min(limited_quantity, max_quantity_by_value)
    
    if limited_quantity < requested_quantity:
        logger.warning(f"Order quantity limited: {requested_quantity} -> {limited_quantity} for {symbol}")
    
    return limited_quantity
```

### 注文頻度の制限

短時間に多数の注文を発注することを防ぎます。

```python
class OrderRateLimiter:
    def __init__(self, max_orders_per_minute=10, max_orders_per_hour=100):
        self.max_orders_per_minute = max_orders_per_minute
        self.max_orders_per_hour = max_orders_per_hour
        self.order_timestamps = []
    
    def can_place_order(self):
        """
        注文を発注できるかどうかをチェック
        
        Returns:
        --------
        bool
            注文を発注できる場合はTrue
        """
        current_time = time.time()
        
        # 古い注文履歴を削除
        self.order_timestamps = [ts for ts in self.order_timestamps if current_time - ts < 3600]
        
        # 直近1時間の注文数をチェック
        if len(self.order_timestamps) >= self.max_orders_per_hour:
            logger.warning(f"Hourly order limit reached: {self.max_orders_per_hour}")
            return False
        
        # 直近1分間の注文数をチェック
        minute_orders = sum(1 for ts in self.order_timestamps if current_time - ts < 60)
        if minute_orders >= self.max_orders_per_minute:
            logger.warning(f"Minute order limit reached: {self.max_orders_per_minute}")
            return False
        
        return True
    
    def record_order(self):
        """注文を記録"""
        self.order_timestamps.append(time.time())
```

### 損失制限（ストップロス）

ポジションごとに損失制限を設定します。

```python
def set_stop_loss(api, position, stop_loss_pct, trailing=False):
    """
    ストップロス注文を設定
    
    Parameters:
    -----------
    api : TradingAPI
        取引APIインスタンス
    position : dict
        ポジション情報
    stop_loss_pct : float
        ストップロスの比率（例: 0.05 = 5%）
    trailing : bool
        トレーリングストップロスを使用するかどうか
    
    Returns:
    --------
    str
        注文ID
    """
    symbol = position["symbol"]
    quantity = position["quantity"]
    entry_price = position["entry_price"]
    
    # 買いポジションの場合
    if quantity > 0:
        stop_price = entry_price * (1 - stop_loss_pct)
        side = "sell"
    # 売りポジションの場合
    else:
        stop_price = entry_price * (1 + stop_loss_pct)
        side = "buy"
        quantity = abs(quantity)
    
    # トレーリングストップロスの場合
    if trailing:
        trail_percent = stop_loss_pct * 100
        order = {
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "type": "trailing_stop",
            "trail_percent": trail_percent,
            "time_in_force": "gtc"
        }
    # 通常のストップロスの場合
    else:
        order = {
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "type": "stop",
            "stop_price": stop_price,
            "time_in_force": "gtc"
        }
    
    return api.submit_order(order)
```

### 総合的なリスク管理システム

上記の各要素を組み合わせた総合的なリスク管理システムの例です。

```python
class RiskManager:
    def __init__(self, api, account_value, risk_per_trade=0.01, max_open_positions=5,
                 max_position_size_pct=0.2, max_orders_per_minute=10):
        self.api = api
        self.account_value = account_value
        self.risk_per_trade = risk_per_trade
        self.max_open_positions = max_open_positions
        self.max_position_size_pct = max_position_size_pct
        self.rate_limiter = OrderRateLimiter(max_orders_per_minute=max_orders_per_minute)
    
    def check_pre_order(self, symbol, quantity, side, price):
        """
        注文前のリスクチェック
        
        Returns:
        --------
        (bool, str)
            (許可されるかどうか, 拒否理由)
        """
        # 注文頻度チェック
        if not self.rate_limiter.can_place_order():
            return False, "Order rate limit exceeded"
        
        # ポジション数チェック
        positions = self.api.get_positions()
        if len(positions) >= self.max_open_positions and side == "buy":
            return False, f"Maximum open positions ({self.max_open_positions}) reached"
        
        # 注文金額チェック
        order_value = quantity * price
        max_order_value = self.account_value * self.max_position_size_pct
        if order_value > max_order_value:
            return False, f"Order value ({order_value}) exceeds maximum ({max_order_value})"
        
        # すべてのチェックをパス
        return True, ""
    
    def execute_order_with_risk_management(self, symbol, quantity, side, order_type="market", **params):
        """
        リスク管理付きの注文実行
        
        Returns:
        --------
        dict
            注文結果
        """
        # 現在価格の取得
        current_price = self.api.get_latest_price(symbol)
        
        # リスクチェック
        allowed, reason = self.check_pre_order(symbol, quantity, side, current_price)
        if not allowed:
            logger.warning(f"Order rejected: {reason}")
            return {"status": "rejected", "reason": reason}
        
        # 注文数量の制限
        limited_quantity = limit_order_quantity(
            symbol, 
            quantity, 
            max_quantity_per_order=1000,
            max_notional_value=self.account_value * 0.1,
            current_price=current_price
        )
        
        # 注文の実行
        try:
            order_result = self.api.submit_order({
                "symbol": symbol,
                "quantity": limited_quantity,
                "side": side,
                "type": order_type,
                **params
            })
            
            # 注文記録
            self.rate_limiter.record_order()
            
            # 買い注文の場合、自動的にストップロスを設定
            if side == "buy" and order_result["status"] == "filled":
                self.set_stop_loss_for_position(symbol, self.risk_per_trade)
            
            return order_result
            
        except Exception as e:
            logger.error(f"Order execution error: {str(e)}")
            return {"status": "error", "reason": str(e)}
    
    def set_stop_loss_for_position(self, symbol, stop_loss_pct):
        """ポジションにストップロスを設定"""
        position = self.api.get_position(symbol)
        if position:
            return set_stop_loss(self.api, position, stop_loss_pct)
        return None
```

適切なリスク管理を実装することで、取引システムの安全性と持続可能性を大幅に向上させることができます。特に自動取引システムでは、予期せぬ状況に対する防御メカニズムが不可欠です。