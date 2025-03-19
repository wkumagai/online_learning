# システム管理全般（環境変数・バージョン管理等）のガイド

## 1. 全体設定の仕組み

取引システムの設定は、複数のレイヤーと方法で管理されています。これにより、環境ごとの設定変更や機密情報の安全な管理が可能になります。

### 設定の階層構造

設定は以下の階層構造で管理され、下位の設定が上位の設定を上書きします：

1. **デフォルト設定**: コードにハードコードされたデフォルト値
2. **設定ファイル**: 環境ごとの設定ファイル
3. **環境変数**: システム環境変数や.envファイル
4. **コマンドライン引数**: 実行時に指定される引数

この階層構造により、開発環境、テスト環境、本番環境など、異なる環境での実行が容易になります。

### 設定ファイル（config.py）

基本的な設定は`src/system/config/config.py`で管理されています。

```python
"""
Decision Making System Configuration File
"""

import os
from datetime import datetime, timedelta

# Environment Variables
US_STOCK_API_KEY = os.getenv('US_STOCK_API_KEY')
JP_STOCK_API_KEY = os.getenv('JP_STOCK_API_KEY')
LLM_API_KEY = os.getenv('LLM_API_KEY')
IB_ACCOUNT = os.getenv('IB_ACCOUNT')
IB_PORT = int(os.getenv('IB_PORT', '7497'))
IB_HOST = os.getenv('IB_HOST', '127.0.0.1')
ENV_MODE = os.getenv('ENV_MODE', 'development')

# Trading Settings
STOCK_MARKET = 'US'  # 'US' or 'JP'
PAPER_TRADING = True  # True: paper trading, False: live trading
INITIAL_CAPITAL = 1000000  # Initial capital (USD)

# Target Symbols
US_SYMBOLS = ['NVDA', 'AAPL', 'MSFT', 'GOOGL']
JP_SYMBOLS = ['7203.T', '9984.T', '6758.T', '7974.T']  # Toyota, SoftBank G, Sony, Nintendo

# Risk Management
RISK_PER_TRADE = 0.02      # Risk per trade (proportion of capital)
MAX_POSITION_SIZE = 0.1    # Maximum position size (proportion of capital)
STOP_LOSS_PCT = 0.03      # Stop loss (3%)
TAKE_PROFIT_PCT = 0.06    # Take profit (6%)

# Data Settings
DATA_INTERVAL = '1min'
START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # From 1 year ago

# Alert Thresholds
ALERT_THRESHOLDS = {
    'drawdown': -0.03,     # Alert on 3% drawdown
    'profit': 0.05,        # Alert on 5% profit
    'volume_spike': 2.5    # Alert on 2.5x average volume
}

# Strategy Parameters
STRATEGY_PARAMS = {
    'moving_average': {
        'short_window': 10,
        'long_window': 30
    },
    'momentum': {
        'rsi_period': 14,
        'overbought': 70,
        'oversold': 30
    },
    'lstm': {
        'sequence_length': 20,
        'epochs': 50,
        'batch_size': 32
    }
}

# Feature Settings
FEATURE_COLUMNS = [
    'Close',
    'Volume',
    'RSI',
    'MACD',
    'Signal_Line',
    'BB_Upper',
    'BB_Lower',
    'Momentum'
]

# Directory Settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
MODEL_SAVE_DIR = os.path.join(BASE_DIR, 'models')

# Logging Settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'

def create_directories():
    """Create necessary directories"""
    directories = [
        REPORT_DIR,
        LOG_DIR,
        MODEL_SAVE_DIR
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

# Create directories on startup
create_directories()
```

### 環境変数（.env）

機密情報や環境固有の設定は`.env`ファイルで管理します。このファイルはバージョン管理システムにコミットせず、各環境で個別に管理します。

```
# API Keys
US_STOCK_API_KEY=your_us_stock_api_key_here
JP_STOCK_API_KEY=your_jp_stock_api_key_here
LLM_API_KEY=your_llm_api_key_here

# Interactive Brokers Settings
IB_ACCOUNT=your_ib_account_here
IB_PORT=7497
IB_HOST=127.0.0.1

# Environment Mode
ENV_MODE=development  # development, testing, production

# Email Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
ALERT_SENDER=trading-alerts@example.com

# Slack Settings
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
```

### 環境変数の読み込み

アプリケーション起動時に`.env`ファイルから環境変数を読み込むには、`python-dotenv`ライブラリを使用します。

```python
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数の値を取得
api_key = os.getenv('US_STOCK_API_KEY')
```

### 環境別の設定ファイル

異なる環境（開発、テスト、本番）ごとに設定ファイルを分けることもできます。

```python
import os

# 環境の取得
env = os.getenv('ENV_MODE', 'development')

# 環境に応じた設定ファイルの読み込み
if env == 'production':
    from .config_prod import *
elif env == 'testing':
    from .config_test import *
else:  # development
    from .config_dev import *

# 共通設定の読み込み
from .config_common import *
```

## 2. バージョン管理

効果的なバージョン管理は、コードの変更履歴の追跡、複数の開発者による協業、安定したリリースの管理に不可欠です。

### Gitを使用したバージョン管理

#### リポジトリ構造

```
online_learning/
  ├── .git/                  # Gitリポジトリ
  ├── .gitignore             # バージョン管理から除外するファイル
  ├── docs/                  # ドキュメント
  ├── src/                   # ソースコード
  ├── data/                  # データディレクトリ（大部分はgitignore）
  ├── tests/                 # テストコード
  ├── requirements.txt       # 依存パッケージ
  └── README.md              # プロジェクト概要
```

#### .gitignoreファイル

バージョン管理から除外すべきファイルを指定します。

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project Specific
.env
*.log
logs/
data/market_infomation/raw/
data/market_infomation/processed/
data/market_infomation/news/
data/strategy/models/
data/strategy/logs/
data/evaluation/backtest_results/
data/evaluation/realtime_results/
data/trading/order_logs/
data/report/generated_reports/
data/report/alerts/
```

#### ブランチ戦略

効果的な開発とリリースのためのブランチ戦略（Git Flow）：

1. **main**: 本番環境のコード（安定版）
2. **develop**: 開発版のコード（次回リリース候補）
3. **feature/\***: 新機能の開発
4. **bugfix/\***: バグ修正
5. **release/\***: リリース準備
6. **hotfix/\***: 本番環境の緊急修正

#### コミットメッセージの規約

明確で一貫性のあるコミットメッセージの形式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type**: feat（新機能）、fix（バグ修正）、docs（ドキュメント）、style（フォーマット）、refactor（リファクタリング）、test（テスト）、chore（雑務）
- **scope**: 変更の範囲（market_infomation、strategy、evaluation、tradingなど）
- **subject**: 変更内容の簡潔な説明
- **body**: 詳細な説明（省略可）
- **footer**: 関連するIssueやBreaking Changesの情報（省略可）

例：
```
feat(strategy): add LSTM model for price prediction

- Implement LSTM architecture with configurable layers
- Add data preprocessing for time series
- Include model training and evaluation functions

Closes #123
```

### セマンティックバージョニング

リリースバージョンの命名規則：

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: 互換性のない変更
- **MINOR**: 後方互換性のある機能追加
- **PATCH**: 後方互換性のあるバグ修正

例：`1.2.3`

### タグとリリース

重要なマイルストーンやリリースにはGitタグを使用します：

```bash
# バージョン1.0.0のタグを作成
git tag -a v1.0.0 -m "Version 1.0.0"

# タグをリモートリポジトリにプッシュ
git push origin v1.0.0
```

## 3. リリースフロー

安定したソフトウェアをリリースするための体系的なプロセスです。

### リリースプロセス

1. **リリース準備**
   - developブランチからrelease/vX.Y.Zブランチを作成
   - バージョン番号の更新
   - ドキュメントの更新
   - 最終テストの実行

2. **リリース承認**
   - コードレビュー
   - テスト結果の確認
   - リリースノートの作成

3. **本番環境へのデプロイ**
   - release/vX.Y.Zブランチをmainブランチにマージ
   - mainブランチにバージョンタグを付与
   - デプロイスクリプトの実行

4. **リリース後の作業**
   - リリースブランチをdevelopブランチにマージ
   - リリース完了の通知
   - モニタリングと問題対応

### リリースノート

各リリースの変更内容を記録するリリースノートの例：

```markdown
# Release Notes - v1.2.0

## New Features
- Added LSTM model for price prediction
- Implemented real-time market data streaming
- Added Slack notification for trading alerts

## Improvements
- Optimized backtest performance by 30%
- Enhanced risk management with dynamic position sizing
- Improved error handling in API connections

## Bug Fixes
- Fixed incorrect calculation of Sharpe ratio
- Resolved issue with order execution retry logic
- Fixed data inconsistency in performance reports

## Breaking Changes
- Changed configuration format for strategy parameters
- Updated API authentication method

## Dependencies
- Updated TensorFlow to v2.8.0
- Added pandas-ta v0.3.14b0
```

### デプロイスクリプト

リリースを本番環境にデプロイするスクリプトの例：

```bash
#!/bin/bash

# デプロイスクリプト

# 変数の設定
VERSION=$1
DEPLOY_DIR="/opt/trading-system"
BACKUP_DIR="/opt/backups/trading-system"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 引数のチェック
if [ -z "$VERSION" ]; then
    echo "Error: Version number is required"
    echo "Usage: $0 <version>"
    exit 1
fi

# バックアップの作成
echo "Creating backup of current version..."
mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" $DEPLOY_DIR

# 新バージョンのクローン
echo "Cloning version $VERSION..."
git clone --branch "v$VERSION" --depth 1 https://github.com/your-org/trading-system.git /tmp/trading-system-$VERSION

# 依存パッケージのインストール
echo "Installing dependencies..."
cd /tmp/trading-system-$VERSION
python -m pip install -r requirements.txt

# 設定ファイルの更新
echo "Updating configuration..."
cp $DEPLOY_DIR/.env /tmp/trading-system-$VERSION/

# デプロイディレクトリの更新
echo "Updating deployment directory..."
rm -rf $DEPLOY_DIR
mv /tmp/trading-system-$VERSION $DEPLOY_DIR

# サービスの再起動
echo "Restarting services..."
systemctl restart trading-system

# デプロイ結果の確認
echo "Checking deployment status..."
sleep 5
if systemctl is-active --quiet trading-system; then
    echo "Deployment successful!"
else
    echo "Deployment failed! Rolling back..."
    rm -rf $DEPLOY_DIR
    mkdir -p $DEPLOY_DIR
    tar -xzf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" -C /
    systemctl restart trading-system
    exit 1
fi

echo "Deployment of version $VERSION completed successfully."
```

## 4. 開発フロー（CI/CDの簡易例）

継続的インテグレーション（CI）と継続的デリバリー（CD）のパイプラインにより、コード品質の維持と効率的なデプロイが可能になります。

### GitHub Actionsを使用したCI/CD

`.github/workflows/ci-cd.yml`ファイルの例：

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop, release/* ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8
      
      - name: Lint with flake8
        run: |
          flake8 src tests
      
      - name: Test with pytest
        run: |
          pytest --cov=src tests/
      
      - name: Upload coverage report
        uses: codecov/codecov-action@v1

  build:
    needs: test
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release/'))
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install build
      
      - name: Build package
        run: |
          python -m build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v2
        with:
          name: dist
          path: dist/

  deploy-staging:
    needs: build
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/heads/release/')
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v2
        with:
          name: dist
          path: dist/
      
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment..."
          # ステージング環境へのデプロイスクリプト
          # 例: scp, rsync, または専用のデプロイツールを使用
      
      - name: Run integration tests
        run: |
          echo "Running integration tests..."
          # ステージング環境でのインテグレーションテスト

  deploy-production:
    needs: deploy-staging
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v2
        with:
          name: dist
          path: dist/
      
      - name: Deploy to production
        run: |
          echo "Deploying to production environment..."
          # 本番環境へのデプロイスクリプト
      
      - name: Verify deployment
        run: |
          echo "Verifying production deployment..."
          # デプロイ後の検証
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: dist/*
          body_path: CHANGELOG.md
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### CI/CDパイプラインの各ステージ

1. **テスト（CI）**
   - コードの静的解析（linting）
   - ユニットテストの実行
   - コードカバレッジの計測
   - 依存パッケージの脆弱性スキャン

2. **ビルド**
   - パッケージのビルド
   - ドキュメントの生成
   - ビルド成果物のアーカイブ

3. **ステージング環境へのデプロイ（CD）**
   - ステージング環境の準備
   - ビルド成果物のデプロイ
   - インテグレーションテストの実行
   - パフォーマンステストの実行

4. **本番環境へのデプロイ（CD）**
   - 本番環境へのデプロイ
   - スモークテストの実行
   - モニタリングの設定
   - リリースの公開

### 開発環境のセットアップ

新しい開発者が環境をセットアップするための手順：

```bash
# リポジトリのクローン
git clone https://github.com/your-org/trading-system.git
cd trading-system

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開発用の追加パッケージ

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して必要な値を設定

# テストの実行
pytest

# 開発サーバーの起動
python src/main.py --mode=development
```

## 5. 依存パッケージの管理

プロジェクトの依存パッケージを適切に管理することで、再現性のある環境構築と安定した動作を確保します。

### requirements.txtによる依存管理

基本的な依存パッケージリスト：

```
# Core Dependencies
numpy==1.22.3
pandas==1.4.2
scikit-learn==1.0.2
tensorflow==2.8.0
matplotlib==3.5.1
seaborn==0.11.2

# API Clients
yfinance==0.1.70
alpaca-trade-api==2.3.0
ibapi==9.76.1

# Web & Networking
requests==2.27.1
websockets==10.3
aiohttp==3.8.1

# Data Processing
ta-lib==0.4.24
pandas-ta==0.3.14b0

# Utilities
python-dotenv==0.20.0
schedule==1.1.0
tqdm==4.64.0

# Reporting & Visualization
plotly==5.7.0
dash==2.3.1
jinja2==3.1.1
weasyprint==54.3

# Logging & Monitoring
structlog==21.5.0
prometheus-client==0.14.1
```

### 開発用の追加依存パッケージ

開発時のみ必要な依存パッケージ（`requirements-dev.txt`）：

```
# Testing
pytest==7.1.1
pytest-cov==3.0.0
pytest-mock==3.7.0
pytest-asyncio==0.18.3

# Linting & Formatting
flake8==4.0.1
black==22.3.0
isort==5.10.1
mypy==0.942

# Documentation
sphinx==4.5.0
sphinx-rtd-theme==1.0.0

# Development Tools
jupyter==1.0.0
ipython==8.2.0
pre-commit==2.18.1
```

### 仮想環境の使用

プロジェクト固有の依存関係を分離するための仮想環境：

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Linuxの場合:
source venv/bin/activate
# Windowsの場合:
# venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 現在の環境の依存パッケージを書き出し
pip freeze > requirements-freeze.txt
```

### Dockerによる環境の標準化

`Dockerfile`の例：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# 環境変数の設定
ENV PYTHONUNBUFFERED=1
ENV ENV_MODE=production

# ポートの公開
EXPOSE 8000

# アプリケーションの実行
CMD ["python", "src/main.py"]
```

`docker-compose.yml`の例：

```yaml
version: '3.8'

services:
  trading-system:
    build: .
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    env_file:
      - .env
    ports:
      - "8000:8000"
    restart: unless-stopped
    depends_on:
      - redis
      - elasticsearch

  redis:
    image: redis:6-alpine
    volumes:
      - redis-data:/data
    restart: unless-stopped

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    restart: unless-stopped

volumes:
  redis-data:
  elasticsearch-data:
```

## 6. セキュリティ対策

取引システムでは、資金や機密情報を扱うため、セキュリティ対策が特に重要です。

### 機密情報の管理

1. **環境変数の使用**
   - APIキーやパスワードなどの機密情報は環境変数で管理
   - `.env`ファイルはバージョン管理から除外（`.gitignore`に追加）
   - 本番環境では環境変数を安全に設定（CI/CDシステムの機密変数機能など）

2. **シークレット管理サービスの利用**
   - AWS Secrets Manager、HashiCorp Vault、Google Secret Managerなどの専用サービスの利用
   - アプリケーション起動時にシークレットを取得

```python
def get_secrets():
    """シークレット管理サービスからシークレットを取得"""
    import boto3
    
    # AWS Secrets Managerの例
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='trading-system/api-keys')
    
    import json
    secrets = json.loads(response['SecretString'])
    
    return secrets
```

### アクセス制御

1. **最小権限の原則**
   - 各コンポーネントに必要最小限の権限のみを付与
   - 読み取り専用アクセス、書き込みアクセスを明確に分離

2. **API認証と認可**
   - 強力な認証メカニズムの使用（OAuth、APIキー、JWTなど）
   - レート制限の実装
   - IPアドレス制限の設定

```python
def authenticate_request(api_key):
    """APIリクエストの認証"""
    # APIキーの検証
    if not is_valid_api_key(api_key):
        raise AuthenticationError("Invalid API key")
    
    # レート制限のチェック
    if is_rate_limited(api_key):
        raise RateLimitError("Rate limit exceeded")
    
    # IPアドレスの検証
    client_ip = get_client_ip()
    if not is_allowed_ip(client_ip):
        raise AuthorizationError("IP address not allowed")
    
    return True
```

### データ保護

1. **データ暗号化**
   - 保存データの暗号化（データベース、ファイル）
   - 通信の暗号化（HTTPS、TLS）

2. **データバックアップ**
   - 定期的なバックアップの実施
   - バックアップの暗号化
   - 復元テストの実施

```python
def encrypt_sensitive_data(data, key):
    """機密データの暗号化"""
    from cryptography.fernet import Fernet
    
    # 暗号化キーの生成または取得
    if key is None:
        key = Fernet.generate_key()
    
    # 暗号化
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    
    return encrypted_data, key

def decrypt_sensitive_data(encrypted_data, key):
    """暗号化されたデータの復号"""
    from cryptography.fernet import Fernet
    
    # 復号
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    
    return decrypted_data
```

### 監査とログ記録

1. **セキュリティログの記録**
   - 認証試行（成功と失敗）
   - 重要な操作（取引、設定変更など）
   - システム異常

2. **ログの保護**
   - ログの改ざん防止
   - ログの長期保存
   - ログの定期的な分析

```python
def log_security_event(event_type, user_id, details, success=True):
    """セキュリティイベントのログ記録"""
    import logging
    import json
    
    # 構造化ログの作成
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "success": success,
        "details": details,
        "ip_address": get_client_ip(),
        "user_agent": get_user_agent()
    }
    
    # セキュリティログの記録
    security_logger = logging.getLogger("security")
    security_logger.info(json.dumps(log_data))
    
    # 重大なイベントの場合はアラートを送信
    if event_type in ["login_failure", "unauthorized_access", "api_key_change"]:
        send_security_alert(log_data)
```

適切なシステム管理と開発プロセスを実装することで、取引システムの安定性、セキュリティ、保守性を向上させることができます。これにより、開発チームは効率的に協業し、高品質なソフトウェアを継続的にリリースすることが可能になります。