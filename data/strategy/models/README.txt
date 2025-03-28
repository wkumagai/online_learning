# 戦略モデルディレクトリ

このディレクトリには、取引戦略のモデルとアルゴリズムが保存されます。

## ディレクトリ構造
- Base/: 基本戦略クラスと共通インターフェース
- Technical/: テクニカル分析ベースの戦略
- ML/: 機械学習ベースの戦略
- core/: コアアルゴリズムとユーティリティ
- utils/: ヘルパー関数とツール

## モデルタイプ
1. テクニカル分析モデル
   - 移動平均
   - RSI、MACD、ボリンジャーバンド
   - モメンタム指標
   - パターン認識

2. 機械学習モデル
   - 回帰モデル
   - 分類モデル
   - 時系列予測
   - 強化学習

3. ハイブリッドモデル
   - テクニカル指標を特徴量とした機械学習
   - アンサンブル手法

## ファイル形式
- .py: Pythonソースコード
- .pkl/.joblib: シリアライズされたモデル
- .h5/.keras: 深層学習モデル
- .json/.yaml: モデル設定

## 使用方法
モデルは共通インターフェースを実装し、以下の主要メソッドを提供します：
- initialize(): モデルの初期化
- predict(): 次の行動の予測
- update(): 新しいデータでモデルを更新
- evaluate(): モデルのパフォーマンス評価