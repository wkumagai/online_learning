import pandas as pd

# Excelファイルを読み込む
file_path = 'data/data_tosho.xls'
print(f"{file_path}を読み込んでいます...")

try:
    # Excelファイルを読み込む
    df = pd.read_excel(file_path)
    
    # 基本情報を表示
    print(f"\n基本情報:")
    print(f"行数: {len(df)}")
    print(f"列数: {len(df.columns)}")
    print(f"列名: {df.columns.tolist()}")
    
    # 最初の5行を表示
    print(f"\n最初の5行:")
    print(df.head())
    
    # 銘柄コード列の特定
    code_columns = ['コード', '証券コード', '銘柄コード', 'コード番号', 'Code']
    code_column = None
    
    for col in code_columns:
        if col in df.columns:
            code_column = col
            break
    
    if code_column is None:
        print(f"\n警告: 銘柄コード列が見つかりませんでした。")
        # 最初の列を使用
        code_column = df.columns[0]
        print(f"最初の列 '{code_column}' を銘柄コードとして使用します。")
    
    # 銘柄コードの例を表示
    print(f"\n銘柄コード列: {code_column}")
    codes = df[code_column].astype(str).tolist()[:10]
    print(f"銘柄コードの例: {codes}")
    
    # yfinance形式のティッカーシンボルに変換
    tickers = []
    for code in codes:
        # 数字のみを抽出
        code = ''.join(filter(str.isdigit, code))
        
        # 空でない場合のみ追加
        if code:
            # 4桁未満の場合は0埋め
            if len(code) < 4:
                code = code.zfill(4)
            
            # yfinance形式のティッカーシンボルに変換（日本株は末尾に.Tを付ける）
            ticker = f"{code}.T"
            tickers.append(ticker)
    
    print(f"\nyfinance形式のティッカーシンボル例: {tickers}")
    
except Exception as e:
    print(f"ファイルの読み込み中にエラーが発生しました: {e}")