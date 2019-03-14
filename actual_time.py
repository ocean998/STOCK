import tushare as ts


d = ts.get_tick_data('000725',date='2019-03-14')
print(d)

# df = ts.get_tick_data('600848',date='2018-12-12',src='tt')
# e = ts.get_hist_data('000725',start='2019-01-01',end='2019-03-14')
e = ts.get_tick_data('000725',date='2019-03-14')
print(e)


df = ts.get_realtime_quotes('000725')
print(df)