# システムモジュール

## 概要
システムモジュールは、取引システム全体の設定、構成、統合を管理する中心的なコンポーネントです。各モジュール間の連携を調整し、システム全体の一貫性と安定性を確保します。

## 主要コンポーネント

### 1. 設定管理
- **グローバル設定**: システム全体の設定パラメータ
- **モジュール設定**: 各モジュール固有の設定
- **環境設定**: 開発、テスト、本番環境の設定
- **ユーザー設定**: ユーザー固有の設定とプリファレンス

### 2. ロギングとモニタリング
- **ログシステム**: 詳細なシステムログの記録
- **パフォーマンスモニタリング**: システムリソースの使用状況追跡
- **エラー処理**: 例外とエラーの捕捉と処理
- **ヘルスチェック**: システムコンポーネントの健全性確認

### 3. データ管理
- **データフロー**: モジュール間のデータ転送の管理
- **データ整合性**: 一貫したデータ形式と品質の確保
- **キャッシュ管理**: 効率的なデータアクセスのためのキャッシュ
- **ストレージ最適化**: データストレージの効率化

### 4. セキュリティ
- **認証**: ユーザーとAPIの認証
- **認可**: 機能とデータへのアクセス制御
- **機密情報管理**: APIキーなどの安全な保存
- **監査**: セキュリティイベントの記録と監視

### 5. 統合とオーケストレーション
- **モジュール連携**: 各モジュール間の連携調整
- **ワークフロー管理**: 複雑なプロセスの自動化
- **スケジューリング**: 定期的なタスクの管理
- **イベント処理**: システムイベントの処理と伝播

## 使用方法

### 基本的な設定管理
```python
from src.system import config

# グローバル設定を読み込む
system_config = config.load_config()

# 特定のモジュールの設定を取得
market_info_config = config.get_module_config('market_information')
strategy_config = config.get_module_config('strategy')

# 設定値を取得
api_key = config.get_value('api_keys.alpha_vantage')
risk_limit = config.get_value('trading.risk_limits.max_drawdown', default=0.05)

# 設定を更新
config.update_value('trading.commission', 0.0015)
config.save_config()
```

### 環境変数と機密情報
```python
from src.system import config

# 環境変数から設定を読み込む
config.load_env_vars()

# 機密情報を安全に取得
api_credentials = config.get_credentials('broker_api')

# 一時的な設定オーバーライド
with config.override_config({"trading.mode": "paper"}):
    # このブロック内では設定が一時的に変更される
    trading_system.execute()
```

### ロギングの設定
```python
from src.system import logging

# ロガーを初期化
logger = logging.get_logger('strategy')

# 様々なレベルでログを記録
logger.debug("詳細なデバッグ情報")
logger.info("一般的な情報メッセージ")
logger.warning("警告メッセージ")
logger.error("エラーメッセージ")
logger.critical("致命的なエラー")

# ログレベルを変更
logging.set_level('strategy', 'DEBUG')

# ファイルへのログ出力を設定
logging.add_file_handler('strategy', 'logs/strategy.log', level='INFO')
```

### システム統合
```python
from src.system import integration

# モジュール間の連携を設定
integration.connect_modules(
    source='strategy',
    target='trading',
    data_type='signals',
    transformation=lambda x: x  # 必要に応じてデータ変換
)

# イベントハンドラを登録
integration.register_event_handler(
    event_type='new_data',
    handler=lambda data: strategy.update(data)
)

# ワークフローを定義
workflow = integration.create_workflow([
    {'module': 'market_information', 'function': 'fetch_data'},
    {'module': 'strategy', 'function': 'generate_signals'},
    {'module': 'trading', 'function': 'execute_trades'},
    {'module': 'report', 'function': 'generate_report'}
])

# ワークフローを実行
integration.execute_workflow(workflow)
```

### スケジューリング
```python
from src.system import scheduler

# 定期的なタスクをスケジュール
scheduler.schedule_task(
    task=market_info.update_data,
    schedule='daily',
    time='18:00',
    timezone='Asia/Tokyo'
)

# 複雑なスケジュールを設定
scheduler.schedule_task(
    task=strategy.optimize,
    schedule='cron',
    day_of_week='sat',
    hour=2,
    minute=30
)

# 条件付きタスクをスケジュール
scheduler.schedule_conditional_task(
    task=risk_manager.rebalance,
    condition=lambda: portfolio.drawdown > 0.05,
    check_interval='hourly'
)
```

## 設定ファイル構造

### config.py
システム全体の設定を管理する中心的なモジュールです。

```python
# 設定の例
CONFIG = {
    "system": {
        "name": "Online Learning Trading System",
        "version": "1.0.0",
        "environment": "development",  # development, testing, production
        "log_level": "INFO"
    },
    "market_information": {
        "data_sources": ["yahoo", "alpha_vantage", "japan_exchange"],
        "update_frequency": "daily",
        "cache_expiry": 86400  # 24時間（秒）
    },
    "strategy": {
        "default_parameters": {
            "lookback_period": 20,
            "optimization_interval": "weekly"
        },
        "model_save_path": "data/strategy/models/"
    },
    "evaluation": {
        "metrics": ["return", "sharpe", "sortino", "max_drawdown", "win_rate"],
        "benchmark": "SPY",
        "risk_free_rate": 0.02
    },
    "trading": {
        "mode": "paper",  # paper, real
        "commission": 0.001,
        "slippage": 0.0005,
        "risk_limits": {
            "max_position_size": 0.1,
            "max_drawdown": 0.15,
            "max_daily_loss": 0.03
        }
    },
    "report": {
        "default_formats": ["pdf", "html"],
        "email_notifications": True,
        "recipients": ["user@example.com"]
    }
}
```

### .env ファイル
機密情報や環境固有の設定を管理します。

```
# API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
YAHOO_FINANCE_API_KEY=your_yahoo_finance_api_key
JAPAN_EXCHANGE_API_KEY=your_japan_exchange_api_key

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_db
DB_USER=user
DB_PASSWORD=password

# Trading Configuration
PAPER_TRADING=True
REAL_TRADING=False

# Email Configuration
EMAIL_SMTP_SERVER=smtp.example.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_password
```

## システムアーキテクチャ

### モジュール間の関係
```
Market Information ──→ Strategy ──→ Evaluation
       │                  │             │
       │                  ↓             │
       └───────────→ Trading ←──────────┘
                        │
                        ↓
                      Report
```

### データフロー
1. **市場情報** モジュールが生データを収集・処理
2. **戦略** モジュールがデータを分析し、シグナルを生成
3. **評価** モジュールが戦略のパフォーマンスを分析
4. **取引** モジュールがシグナルに基づいて注文を実行
5. **レポート** モジュールが結果を集計・可視化

### コンポーネント間の通信
- ファイルベース: 処理済みデータの保存と共有
- メモリベース: リアルタイム処理のための直接データ転送
- イベントベース: 非同期通信とイベント駆動アーキテクチャ
- APIベース: モジュール間の標準化されたインターフェース

## 依存関係
- python-dotenv
- pyyaml
- logging
- apscheduler
- pytest (テスト用)

## 将来の拡張
- マイクロサービスアーキテクチャへの移行
- コンテナ化とオーケストレーション
- 分散システムサポート
- ウェブインターフェースとAPI
- リアルタイムモニタリングダッシュボード