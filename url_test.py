import requests
import urllib
# 取得HTML数据


url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000725&scale=60&ma=no&datalen=5'
# r = urllib.open(url).read()
r = requests.get(url)
# r.raise_for_status() requests.get(url).content
# r.encoding = r.apparent_encoding

print(r.text)