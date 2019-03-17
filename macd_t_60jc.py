import macd_base as mb



if __name__ == "__main__":
    # 60 即将金叉
    macd_w = mb.MACD_INDEX( 'w' )
    macd_w.save_golden( 'D:\\0_stock_macd\\_月K线金叉.xls' )

    macd_60 = mb.MACD_INDEX('60')
    macd_60.save_bing_golden('D:\\0_stock_macd\\_周K线金叉.xls'  False)
