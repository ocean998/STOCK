

import tushare as ts
d = ts.get_tick_data('000725',date='2019-03-14')
print(d)

e = ts.get_hist_data('601318',start='2019-01-01',end='2019-03-14')
print(e)