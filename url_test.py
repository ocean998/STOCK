import tushare as ts
import pandas as pd

# 这里注意， tushare版本需大于1.2.10
#
#

# ts.set_token('3a225717090aa813ddf5d75c51b9d97349c8f0a38f8cea52e1a8fcff')
# pro = ts.pro_api()
# 如果上一步骤ts.set_token('your token')无效或不想保存token到本地，也可以在初始化接口里直接设置token:






# 设置token

pro = ts.pro_api('3a225717090aa813ddf5d75c51b9d97349c8f0a38f8cea52e1a8fcff')
#查询当前所有正常上市交易的股票列表
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
code = []
codes = pd.DataFrame(columns=('stock_code', 'stock_name'))
for i in range(1,data.shape[0]):
	code.append(data.iloc[i]['ts_code'][7:10].lower()+'.'+data.iloc[i]['ts_code'][0:6])
	code.append(data.iloc[i]['name'])
	codes.loc[i] = code
	code.clear()
codes.to_excel('股票代码.xls',  sheet_name='金叉清单')

