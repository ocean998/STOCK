import baostock as bs
import pandas as pd
import stock_base
import matplotlib.pyplot as plt


class MACD_INDEX:
    '''
            计算macd指标，需要初始化周期级别
    '''

    def __init__(self, jb='d'):
        '''
                根据周期初始化 开始时间，结束时间，股票列表
        '''
        #### 登陆系统 ####
        lg = bs.login()
        # 显示登陆返回信息
        if int(lg.error_code) == 0:
            self.status = '远程登录成功'
        else:
            self.status = '远程登录失败'
            print('baostock 远程登录失败:', lg.error_msg)
            return
        # df = stock_base.get_stock_code('sz')
        self.jb = jb
        date = stock_base.get_start_time(jb)
        self.begin = date[0]
        self.end = date[1]

        print('k线级别:', self.jb, '\t开始时间:', self.begin, '\t结束时间:', self.end)

    def get_index(self, code):
        '''
                根据周期初始化 开始时间，结束时间，获取远程指标数据
        '''
        # 要获取的指标数据列表
        # d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据
        self.code = code
        if self.jb in ['d', 'w', 'm']:
            indexs = 'date,close,volume,amount,turn'
        else:
            indexs = 'time,close,volume,amount'
        rs = bs.query_history_k_data_plus(
            code,
            indexs,
            start_date=self.begin,
            end_date=self.end,
            frequency=self.jb,
            adjustflag="2")
        # 复权状态(1：后复权， 2：前复权，3：不复权）
        if rs.error_code != '0':
            print('周期指标数据获取失败！:' + rs.error_msg)
            return None

        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            # data_list[-1].append(float(data_list[-1][-1])/float(data_list[-1][-2]))
            data_list.append(rs.get_row_data())

        result = pd.DataFrame(
            data_list,
            columns=rs.fields)
        # 修改列名 date-->time
        if self.jb in ['d', 'w', 'm']:
            result.rename(columns={'date': 'time'}, inplace=True)

        for x in range(0, result.shape[0]):
            # print(str(xx.loc[x][0])[:12])
            if self.jb in ['60', '15']:
                result.iloc[x,
                            0] = result.iloc[x,
                                             0][4:6] + '-' + result.iloc[x,
                                                                         0][6:8] + ' ' + result.iloc[x,
                                                                                                     0][8:10] + ':' + result.iloc[x,
                                                                                                                                  0][10:12]
        return result

    def set_time(self, begin='2019', end='2019'):
        '''重新设置开始时间和结束时间'''
        if begin != '2019':
            self.begin = begin
        if end != '2019':
            self.end = end

        print('k线级别:', self.jb, '\t新设置的开始时间:', self.begin, '\t结束时间:', self.end)

    def get_MACD(self, data, sema=12, lema=26, m_ema=9):
        '''
            根据股票代码计算macd结果，设置macd属性
            data是包含高开低收成交量的标准dataframe
            sema,lema,m_ema分别是macd的三个参数
        '''
        # a.rename( columns={'A': 'a', 'B': 'b', 'C': 'c'}, inplace=True )
        xx = pd.DataFrame()

        xx['time'] = data['time']
        xx['dif'] = data['close'].ewm(adjust=False,
                                      alpha=2 / (sema + 1),
                                      ignore_na=True).mean() - data['close'].ewm(adjust=False,
                                                                                 alpha=2 / (lema + 1),
                                                                                 ignore_na=True).mean()

        xx['dea'] = xx['dif'].ewm(
            adjust=False, alpha=2 / (m_ema + 1), ignore_na=True).mean()

        xx['macd'] = 2 * (xx['dif'] - xx['dea'])

        return xx


if __name__ == "__main__":
    # 60 即将金叉
    macd_60 = MACD_INDEX('60')
    data = macd_60.get_index('sz.000725')
    macd = macd_60.get_MACD(data)
    macd.set_index('time')
    print(macd)
    print('macd 图形')

    # macd.plot(x='time',y='macd',y='dif',color='black', y='dea', color='yello')
    # macd.plot(x='time', y='macd',color='blue', y='dif', color='black')
    macd.plot(x='time',y = ['dif','macd','dea'], color=['blue','green','yellow'])
    plt.show()
# pip install matplotlib
