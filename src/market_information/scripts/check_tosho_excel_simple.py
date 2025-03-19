import pandas as pd

# Excelファイルを読み込む
file_path = 'data/data_tosho.xls'
print(f"{file_path}を読み込んでいます...")

try:
    # Excelファイルを読み込む（最初の5行のみ）
    df = pd.read_excel(file_path, nrows=5)
    
    # 基本情報を表示
    print(f"\n基本情報:")
    print(f"列数: {len(df.columns)}")
    print(f"列名: {df.columns.tolist()}")
    
    # 最初の5行を表示
    print(f"\n最初の5行:")
    print(df)
    
except Exception as e:
    print(f"ファイルの読み込み中にエラーが発生しました: {e}")