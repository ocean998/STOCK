import macd_base as mb
# from  stock_base import ReturnError


if __name__ == "__main__":
    # macd_w = mb.MACD_INDEX( 'w' )
    # macd_w.save_golden( 'all' )

    macd_60 = mb.MACD_INDEX('15')
    # 保存底背离
    macd_60.save_bottom('D:\\0_stock_macd\\_日K线金叉.xls',False)


    # macd_60 = mb.MACD_INDEX('60')
    # try:
    #     df = macd_60.get_index('sh.600021')
    # except mb.ReturnError:
    #     print(mb.ReturnError)
    #
    # try:
    #     df2 = macd_60.get_MACD(df)
    # except mb.ReturnError:
    #     print(mb.ReturnError)
    # print('*'*20, 'macd  结果')
    # print(df2)
    # try:
    #     dbl_rst = macd_60.analyze_bottom(df2, True)
    # except mb.ReturnError:
    #     print(mb.ReturnError)
    # else:
    #     print( dbl_rst )