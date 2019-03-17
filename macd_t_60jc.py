import macd_base as mb



if __name__ == "__main__":
    # 60 即将金叉
    # macd_w = mb.MACD_INDEX( 'w' )
    # macd_w.save_golden( 'all' )

    macd_60 = mb.MACD_INDEX('60')
    macd_60.save_bottom('D:\\0_stock_macd\\_周K线金叉.xls',False)
