import pandas as pd
import yfinance as yf
import time
import os
import datetime
import argparse
import random
import math
import xlrd
import traceback
import sys

def read_tosho_excel(file_path='data/data_tosho.xls'):
    """
    東証上場銘柄リストのExcelファイルからティッカーシンボルを読み込む
    
    Parameters:
    -----------
    file_path : str
        Excelファイルのパス
    
    Returns:
    --------
    list
        ティッカーシンボルのリスト
    """
    print(f"{file_path}から東証上場銘柄を読み込んでいます...")
    
    try:
        # xlrdを使用してExcelファイルを読み込む
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)
        
        # ヘッダー行を取得
        headers = [sheet.cell_value(0, i) for i in range(sheet.ncols)]
        print(f"ヘッダー行: {headers}")
        
        # 銘柄コード列のインデックスを特定
        code_column_idx = headers.index('コード')
        market_column_idx = headers.index('市場・商品区分')
        
        print(f"銘柄コード列のインデックス: {code_column_idx}")
        print(f"市場・商品区分列のインデックス: {market_column_idx}")
        
        # 銘柄コードを取得
        tickers = []
        etf_count = 0
        stock_count = 0
        
        for row_idx in range(1, min(10, sheet.nrows)):  # 最初の10行だけ表示（デバッグ用）
            code = sheet.cell_value(row_idx, code_column_idx)
            market = sheet.cell_value(row_idx, market_column_idx)
            print(f"行 {row_idx}: コード={code}, 市場={market}")
        
        for row_idx in range(1, sheet.nrows):
            code = sheet.cell_value(row_idx, code_column_idx)
            market = sheet.cell_value(row_idx, market_column_idx)
            
            # 数値を文字列に変換
            if isinstance(code, float):
                code = str(int(code))
            else:
                code = str(code)
            
            # 空でない場合のみ追加
            if code and code != '-':
                # 4桁未満の場合は0埋め
                if len(code) < 4:
                    code = code.zfill(4)
                
                # ETF・ETNはスキップするオプション（現在は含める）
                if 'ETF' in market:
                    etf_count += 1
                else:
                    stock_count += 1
                
                # yfinance形式のティッカーシンボルに変換（日本株は末尾に.Tを付ける）
                ticker = f"{code}.T"
                tickers.append(ticker)
        
        print(f"合計 {len(tickers)} 個の東証上場銘柄を読み込みました（株式: {stock_count}、ETF/ETN: {etf_count}）。")
        return tickers
    
    except Exception as e:
        print(f"ファイルの読み込み中にエラーが発生しました: {e}")
        traceback.print_exc()
        return []

def main():
    try:
        # コマンドライン引数の解析
        parser = argparse.ArgumentParser(description='東証上場銘柄の過去10年間の株価データを取得')
        parser.add_argument('--input', type=str, default='data/data_tosho.xls', help='入力ファイルのパス')
        parser.add_argument('--limit', type=int, default=5, help='処理する銘柄数の上限')
        args = parser.parse_args()
        
        print("東証上場銘柄の過去株価データ取得（デバッグモード）")
        print("========================================")
        
        # 東証上場銘柄リストを読み込む
        tickers = read_tosho_excel(args.input)
        
        if not tickers:
            print("ティッカーを読み込めませんでした。終了します。")
            return
        
        # 処理する銘柄数を制限
        if args.limit > 0 and args.limit < len(tickers):
            print(f"処理する銘柄数を {args.limit} に制限します。")
            tickers_to_process = tickers[:args.limit]
        else:
            tickers_to_process = tickers
        
        print(f"\n処理対象の銘柄: {tickers_to_process}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()