import macd_base as mb
# from  stock_base import ReturnError


if __name__ == "__main__":
	# macd_w = mb.MACD_INDEX('w')
	# macd_w.save_golden('all')
	#
	# macd_d = mb.MACD_INDEX('d')
	# macd_d.save_day_golden('D:\\0_stock_macd\\_周K线金叉.xls', False)

	macd_60 = mb.MACD_INDEX('60')
	# 底背离
	# macd_60.save_bottom('D:\\0_stock_macd\\_日K线(即将)金叉.xls', False)
	# 将要金叉
	macd_60.save_bing_golden('D:\\0_stock_macd\\_日K线(即将)金叉.xls')