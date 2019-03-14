import baostock as bs
import pandas as pd
import numpy as np
import macd_base as mb


if __name__ == '__main__':
    macd_60 = mb.MACD_INDEX('60')
    # macd_60.set_time('2018-06-01','2018-12-11')

    macd_60.save_bottom('D:\\0_stock_macd\\_周K线金叉.xls', False)