# レポートモジュール

## 概要
レポートモジュールは、取引システムのパフォーマンス、リスク、取引活動に関する包括的なレポートとアラートを生成します。データを視覚化し、重要な指標を追跡して、意思決定をサポートするインサイトを提供します。

## 主要コンポーネント

### 1. レポート生成
- **定期レポート**: 日次、週次、月次、四半期、年次レポート
- **パフォーマンスレポート**: リターン、リスク、取引統計の詳細分析
- **ポートフォリオレポート**: 資産配分、セクターエクスポージャー、相関分析
- **カスタムレポート**: ユーザー定義の指標とフォーマット

### 2. 可視化
- **インタラクティブチャート**: ズーム、フィルタリング機能付きのグラフ
- **ダッシュボード**: 主要指標のリアルタイム表示
- **ヒートマップ**: 相関、パフォーマンス、リスクの視覚化
- **分布プロット**: リターン分布、取引結果の統計的表示

### 3. アラートシステム
- **パフォーマンスアラート**: 閾値に基づくパフォーマンス通知
- **リスクアラート**: リスク指標が閾値を超えた場合の警告
- **システムアラート**: 技術的問題や異常の通知
- **市場アラート**: 重要な市場イベントや条件の通知

### 4. 配信メカニズム
- **メール配信**: レポートとアラートのメール送信
- **ウェブダッシュボード**: オンラインアクセス可能なダッシュボード
- **API統合**: 外部システムとの統合
- **エクスポート機能**: PDF、Excel、CSVなどの形式でのエクスポート

### 5. 監査とコンプライアンス
- **取引ログ**: 完全な取引履歴の記録
- **監査証跡**: システム活動の詳細記録
- **規制レポート**: コンプライアンス要件に合わせたレポート
- **データ保持**: 適切なデータ保持ポリシーの実装

## 使用方法

### 基本的なレポート生成
```python
from src.report import report
from src.report.reporting import reporter

# パフォーマンスレポートを生成
performance_report = reporter.generate_performance_report(
    strategy_results=results,
    period='monthly',
    start_date='2022-01-01',
    end_date='2022-12-31',
    benchmark='SPY'  # S&P 500をベンチマークとして使用
)

# レポートを保存
report.save_report(
    report=performance_report,
    format='pdf',
    path='data/report/generated_reports/performance_monthly_202212.pdf'
)

# レポートをメールで送信
report.send_report(
    report=performance_report,
    recipients=['user@example.com'],
    subject='Monthly Performance Report - December 2022'
)
```

### カスタムダッシュボードの作成
```python
from src.report.reporting import reporter

# カスタムダッシュボードを作成
dashboard = reporter.create_dashboard(
    title='Strategy Performance Dashboard',
    components=[
        {
            'type': 'equity_curve',
            'data': equity_data,
            'title': 'Equity Curve',
            'width': 12
        },
        {
            'type': 'drawdown_chart',
            'data': drawdown_data,
            'title': 'Drawdown Analysis',
            'width': 6
        },
        {
            'type': 'metrics_table',
            'data': metrics_data,
            'title': 'Key Performance Indicators',
            'width': 6
        },
        {
            'type': 'trade_distribution',
            'data': trade_data,
            'title': 'Trade P&L Distribution',
            'width': 12
        }
    ]
)

# ダッシュボードを表示または保存
dashboard.display()  # インタラクティブ表示
dashboard.save('data/report/generated_reports/dashboard.html')
```

### アラートの設定
```python
from src.report.reporting import reporter

# アラートを設定
alerts = reporter.setup_alerts([
    {
        'type': 'performance',
        'metric': 'drawdown',
        'threshold': -0.1,  # 10%以上のドローダウンでアラート
        'condition': 'less_than',
        'notification': ['email', 'dashboard']
    },
    {
        'type': 'risk',
        'metric': 'volatility',
        'threshold': 0.2,  # ボラティリティが20%を超えるとアラート
        'condition': 'greater_than',
        'notification': ['email']
    },
    {
        'type': 'system',
        'metric': 'api_errors',
        'threshold': 5,  # 5回以上のAPI接続エラーでアラート
        'condition': 'greater_than',
        'notification': ['email', 'sms']
    }
])

# アラートを有効化
reporter.enable_alerts(alerts)
```

### 定期レポートのスケジュール設定
```python
from src.report.reporting import reporter

# 定期レポートをスケジュール
reporter.schedule_reports([
    {
        'type': 'performance',
        'frequency': 'daily',
        'time': '18:00',
        'timezone': 'Asia/Tokyo',
        'recipients': ['trader@example.com'],
        'format': ['pdf', 'email']
    },
    {
        'type': 'risk',
        'frequency': 'weekly',
        'day': 'Friday',
        'time': '17:00',
        'timezone': 'Asia/Tokyo',
        'recipients': ['risk@example.com', 'manager@example.com'],
        'format': ['pdf', 'email']
    },
    {
        'type': 'portfolio',
        'frequency': 'monthly',
        'day': 1,  # 毎月1日
        'time': '09:00',
        'timezone': 'Asia/Tokyo',
        'recipients': ['investor@example.com'],
        'format': ['pdf', 'email', 'excel']
    }
])
```

## レポート種類

### パフォーマンスレポート
- **概要**: 全体的なパフォーマンスサマリー
- **リターン分析**: 期間別、年率、累積リターン
- **リスク指標**: ボラティリティ、シャープレシオ、ソルティノレシオ、最大ドローダウン
- **ベンチマーク比較**: 市場指標との比較
- **月次/年次パフォーマンス**: 期間別のパフォーマンス表

### 取引レポート
- **取引サマリー**: 取引数、勝率、平均利益/損失
- **取引詳細**: 個別取引の詳細リスト
- **取引分布**: 利益/損失の分布分析
- **時間分析**: 時間帯、曜日、月別の取引パフォーマンス
- **戦略別分析**: 複数戦略の比較

### リスクレポート
- **リスク指標**: VaR、CVaR、ストレステスト結果
- **ドローダウン分析**: 深さ、期間、回復時間
- **相関分析**: 他の資産、戦略、市場との相関
- **テールリスク**: 極端なイベントのリスク評価
- **シナリオ分析**: 様々な市場シナリオでのパフォーマンス予測

### ポートフォリオレポート
- **資産配分**: 資産クラス、セクター、地域別の配分
- **ポジションサマリー**: 現在のポジションと評価
- **貢献度分析**: リターンへの貢献度分析
- **リスク配分**: リスクの分解と配分
- **最適化提案**: ポートフォリオ最適化の提案

## 設定
レポート設定は `src/system/config.py` で管理されています。主な設定項目：
- レポートテンプレート
- アラート閾値
- 通知設定
- スケジュール設定
- 出力形式と保存場所

## 依存関係
- pandas
- numpy
- matplotlib
- seaborn
- plotly
- dash (インタラクティブダッシュボード)
- reportlab (PDF生成)
- smtplib (メール送信)

## 将来の拡張
- 機械学習ベースのアノマリー検出
- 自然言語生成によるレポート解説
- モバイルアプリ通知
- 音声アシスタント統合
- 予測分析の強化