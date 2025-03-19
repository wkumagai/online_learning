import xlrd

# Excelファイルを読み込む
file_path = 'data/data_tosho.xls'
print(f"{file_path}を読み込んでいます...")

try:
    # Excelファイルを開く
    workbook = xlrd.open_workbook(file_path)
    
    # シート名を表示
    print(f"\nシート名: {workbook.sheet_names()}")
    
    # 最初のシートを取得
    sheet = workbook.sheet_by_index(0)
    
    # 基本情報を表示
    print(f"\n基本情報:")
    print(f"行数: {sheet.nrows}")
    print(f"列数: {sheet.ncols}")
    
    # ヘッダー行を表示
    if sheet.nrows > 0:
        header = [sheet.cell_value(0, i) for i in range(sheet.ncols)]
        print(f"\nヘッダー行: {header}")
    
    # 最初の5行を表示
    print(f"\n最初の5行:")
    for row_idx in range(1, min(6, sheet.nrows)):
        row = [sheet.cell_value(row_idx, i) for i in range(sheet.ncols)]
        print(f"行 {row_idx}: {row}")
    
except Exception as e:
    print(f"ファイルの読み込み中にエラーが発生しました: {e}")