import requests
import re
from lxml import etree
import pandas as pd
import time


StockPriceUrl = "http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/#code.phtml?year=#year&jidu=#jd"
StockListUrl = "http://quote.eastmoney.com/stocklist.html"
StockInfoUrl = 'https://gupiao.baidu.com/stock/'
StockListDataFile = "StockList.dat"
StockDictDataFile = "StockDict.dat"
StockDataFile = "StockInfo.dat"
StockGDData = "StockGD.dat"
StockGDUrl = "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CirculateStockHolder/stockid/#code.phtml"
GDDataFile = "GDData.dat"
stockdict={}
StockList=[]

df = pd.DataFrame(columns=  ['date', 'code', 'name', 'no.',"price", 'cop', 'total', 'change', 'type'])

debug = False

def debugout(str):
    if debug:
        print(str)

#取得HTML数据
def GetHTMLText(url):
    try:
        debugout("Starting get url" + url)
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""

#取得股票列表——东方财富
def GetStockList():
    html = GetHTMLText(StockListUrl)
    s = html.lower()
    page = etree.HTML(s)
    if page==None:
        return
    href = page.xpath('//a')
    for i in href:
        try:
            s = i.text
            #d = re.findall('"(.*")"(""[630][0]\d[4]")"',s)
            d = re.findall(r"[630][0]\d{4}",s)
            if len(d)>0:
                n = s.find(d[0])
                d1 = s[0:n-1]
                if len(d1)>5:
                    continue
                StockList.append(d[0])
                stockdict.update({d[0]:d1})
        except:
            continue

    '''
    #use beautiful soup
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.find_all('a')
    for i in a:
        try:
            href = i.attrs['href']
            s = href
            StockList.append(re.findall(r"[s][hz][630][0]\d{4}", s)[0])
        except:
            continue
    return StockList
    '''
    return StockList


#取得股票当日价格——百度
def getStockInfo(lst, stockURL, fpath):
    count = 0
    errCount = 0
    for stock in lst:
        #重组URL
        if stock[0]=='6':
            s = 'sh'+stock
        elif stock[0]== 's':
            s = stock
        else:
            s = 'sz' + stock
        url = stockURL + s + ".html"
        html = GetHTMLText(url)
        try:
            if html == "":
                continue
            infoDict = {}
            s=html.lower()

            page = etree.HTML(s)
            if page==None:
                return
            stockInfo = page.xpath('//a[@class="bets-name"]')

            name =  (stockInfo[0].text)
            name = name.split()[0]

            infoDict.update({'股票名称': name})

            keylist = page.xpath('//div[@class="bets-content"]/div/dl/dt')
            valueList = page.xpath('//div[@class="bets-content"]/div/dl/dd')

            for i in range(len(keylist)):
                key = keylist[i].text
                val = valueList[i].text
                infoDict[key] = val

            with open(fpath, 'a', encoding='utf-8') as f:
                f.write(str(infoDict) + '\n')
                count = count + 1
                print("\r当前进度: %.2f%%   %s  Count: %d Error: %d  Name:%s" % (count * 100 / len(lst), stock, count, errCount,name),
                      end="")
        except:
            count = count + 1
            errCount = errCount + 1
            print("\r当前进度: %.2f%%   %s  Count: %d Error: %d  Name:%s" % (
            count * 100 / len(lst), stock, count, errCount, name),
                  end="")
            continue


#取得股票季末价格
def GetJimoPrice(code,ayear,ajd):
    url = StockPriceUrl
    url = url.replace("#year",ayear)
    url = url.replace("#jd",ajd)
    url = url.replace("#code",code)
    HTML = GetHTMLText(url)
    s = HTML.lower()
    page = etree.HTML(s)
    if page == None:
        return ""
    x = page.xpath('//tr/td/div[@align="center"]')
    if len(x)>10:
        return x[10].text
    else:
        return ""


#处理股票代码
def gpCode(code,with_s=False,upper=False):
    code = code.lower()
    if with_s:
        if code[0] != "s":
            if code[0]=="6":
                code = "sh"+code
            else:
                code= "sz"+code
    else:
        if code[0]=="s":
            code = code[2:]
    if upper:
        code = code.upper()
    if len(code)==6 or len(code)==8:
        return code
    else:
        return ""



def main():
    debugout("Starting get stock list...")
    GetStockList()
    with open(StockListDataFile, 'w', encoding='utf-8') as f:
        f.write(str(StockList))
    with open(StockDictDataFile, 'w', encoding='utf-8') as f1:
        f1.write(str(stockdict))
    debugout("Starting get stock info......")
    icount=len(StockList)
    idx = 1

main()