import baostock as bs
import pandas as pd
import stock_base


class ReturnError(Exception):
    """"各函数返回异常结果时抛出的异常"""

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg


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

    def set_time(self, begin='2019', end='2019'):
        '''重新设置开始时间和结束时间'''
        if begin != '2019':
            self.begin = begin
        if end != '2019':
            self.end = end
        print('k线级别:', self.jb, '\t新设置的开始时间:', self.begin, '\t结束时间:', self.end)

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
            raise ReturnError(code + ':k线指标获取失败！' + rs.error_msg)

        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            # data_list[-1].append(float(data_list[-1][-1])/float(data_list[-1][-2]))
            data_list.append(rs.get_row_data())

        result = pd.DataFrame(data_list, columns=rs.fields)
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

    def get_MACD(self, data, sema=12, lema=26, m_ema=9):
        '''
            根据股票代码计算macd结果，设置macd属性
            data是包含高开低收成交量的标准dataframe
            sema,lema,m_ema分别是macd的三个参数
        '''
        if data.shape[0] < 30:
            raise ReturnError('K线数据少于30个周期，不计算MACD')
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

    def analyze_dead(self, macd, isprt=False):
        ''' macd最后一次交叉是死叉，才有返回值，返回包括 死叉日期，死叉后红柱数量，绿柱高度，快线高度
            save_golden方法计算完macd后调用，后续应继续调用判断 是否即将金叉的方法 analyze_bing_golden
        '''
        rst = pd.DataFrame(columns=[macd.columns.values])
        cnt_lv = 0
        cnt = macd.shape[0]
        if cnt < 30:
            raise ReturnError(self.code + '，macd数据少于30周期,不判断死叉！')
        # isprt是否打印输入的macd数组，用于调试
        # if isprt:
        #     print(macd)
        # 如果当前macd红柱表示已经金叉，不判断直接返回
        if macd.iloc[-1]['macd'] > 0:
            raise ReturnError(self.code + '，已经金叉！')
        for i in range(1, cnt - 1):
            # macd>0 为红柱，计数并向前找小于0的时间为金叉点
            if macd.iloc[-i]['macd'] < 0:
                cnt_lv += 1  # 绿柱计数
                continue
            else:
                rst = macd.iloc[-i + 1:].reset_index(drop=True)
                return rst
        raise ReturnError(self.code + '，没有找到死叉！')

    def analyze_bing_golden(self, macd, isprt=False):
        ''' 用于判断是否将要金叉macd已经死叉还未金叉，如果快线斜率在3个周期内发生金叉则返回
            macd死叉后的macd指标，pandas.DataFrame类型 save_golden方法计算完macd发生死叉后调用，
            零轴下死叉适用 frame.iloc[frame['test2'].idxmin()]['test3']
        '''

        rst = []
        try:
            dead_macd = self.analyze_dead(macd, isprt)
        except ReturnError:
            raise ReturnError(self.code + ', 不用判断即将金叉')
        dead_len = dead_macd.shape[0]

        # 死叉macd为负值 所以取最小值
        idx_min = dead_macd['macd'].idxmin()
        # 绿线最低值发生在当前
        if dead_len == idx_min + 1:
            raise ReturnError(self.code + ', 死叉后开口正在放大！')
        # 取最低点后的数据
        macd_jc = dead_macd.iloc[idx_min:].reset_index(drop=True)
        dead_len = macd_jc.shape[0]
        if isprt:
            print('\nMACD最低点后的数据是：\n')
            print(macd_jc)
        if dead_len > 3:
            x = []
            # 最低点后如果有3根以上的柱子再判断趋势，缩短y，加长n
            for idx in range(0, dead_len - 1):
                if macd_jc.iloc[idx]['macd'] - \
                        macd_jc.iloc[(idx + 1)]['macd'] >= 0:
                    x.append('n')
                else:
                    if isprt:
                        print(idx, ':', macd_jc.iloc[idx]['macd'],
                              '-', macd_jc.iloc[(idx + 1)]['macd'])
                    x.append('y')
            if x[-1] == 'y':
                rst.append('即将金叉')
            if isprt:
                print('\nMACD最低点后的 趋势\n', x)
        else:
            # 不足4跟，最后一根比前面一根短
            if dead_macd.iloc[-1]['macd'] <= dead_macd.iloc[-2]['macd']:
                rst.append('即将金叉')

        if len(rst) == 1:
            rst.append(self.code.split('.')[1])
            rst.append(dead_macd.iloc[0]['time'])
            rst.append(dead_macd.iloc[-1]['macd'])
            rst.append(dead_macd.iloc[-2]['macd'])
            rst.append(self.code)
            return rst
        else:
            raise ReturnError(self.code + ', 不是即将金叉！')

    def analyze_golden(self, macd, isprt=False):
        ''' macd最后一次交叉是金叉才有返回值，否则返回空列表，
            返回包括金叉日期，金叉后红柱数量，红柱高度，快线高度
            save_golden方法计算完macd后调用
        '''
        cnt_hz = 0
        rst = []
        cnt = int(macd.shape[0])
        if cnt < 30:
            raise ReturnError(self.code + '，macd数据少于30周期,不判断金叉！')

        if isprt:
            print(macd)
        # 如果当前macd绿柱不判断直接返回
        if macd.iloc[-1]['macd'] < 0:
            raise ReturnError(self.code + '，绿柱不是金叉！')
        for i in range(1, cnt - 1):
            # macd>0 为红柱，计数并向前找小于0的时间为金叉点
            if macd.iloc[-i]['macd'] > 0:
                cnt_hz += 1  # 红柱计数
                continue
            else:
                # MACD 金叉
                if macd.iloc[-1]['macd'] < macd.iloc[-2]['macd'] < macd.iloc[-3]['macd']:
                    raise ReturnError( self.code+'，金叉后开口方向没有向上！' )
                rst.append('golden')
                rst.append(self.code.split('.')[1])
                rst.append(macd.iloc[-i + 1]['time'])
                if macd.iloc[-i]['dif'] >= 0.001:
                    rst.append('up0')
                else:
                    rst.append('down0')
                # 第一个金叉判断完成退出
                rst.append(cnt_hz)
                rst.append(self.code)
                return rst

        raise ReturnError( self.code+'，不是金叉！' )

    def analyze_top(self, macd, isptt=False):
        ''' 分析macd 顶背离
        '''
        rst = []
        rst2 = []
        cnt = int(macd.shape[0])
        if cnt < 40:
            raise ReturnError( self.code+'，macd数据少于40周期,不判断顶背离！' )

        # 绿柱结束直接退出
        if macd.iloc[-1]['macd'] < 0:
            raise ReturnError( self.code+'，macd最后为绿柱！' )

        rst.append(macd.iloc[-1]['time'])
        rst2.append(macd.iloc[-1]['macd'])
        for idx in range(1, cnt - 1):
            if len(rst2) == 1:
                # 从右向左第一次为死叉,macd应从红转绿,记录最后的红线时间
                if macd.iloc[-idx]['macd'] >= 0:
                    rst.append(macd.iloc[-1]['time'])
                    rst2.append(macd.iloc[-idx]['macd'])
            if len(rst2) == 2:
                # 从右向左第二次为金叉,macd应从绿转红,记录最后的绿线时间
                if macd.iloc[-idx]['macd'] < 0:
                    rst.append(macd.iloc[-1]['time'])
                    rst2.append(macd.iloc[-idx]['macd'])
            if len(rst2) == 3:
                # 从右向左第三次为死叉,macd应从红转绿,记录最后的红线时间
                if macd.iloc[-idx]['macd'] >= 0:
                    rst.append(macd.iloc[-1]['time'])
                    rst2.append(macd.iloc[-idx]['macd'])

        if len(rst) == 4:
            if isptt:
                print(rst)
                print(rst2)
            return rst2
        else:
            raise ReturnError( self.code+'，不是顶背离！' )

    def analyze_bottom(self, macd, isptt=False):
        ''' 分析macd 底背离 从右向左 先有死叉再有金叉，再判断将要金叉，及其与左边金叉高度
        '''
        rst = ['time']
        rst2 = []
        cnt = int(macd.shape[0])
        if cnt < 40:
            raise ReturnError( self.code+'，MACD少于40周期，不判断底背离！' )

        # 红柱结束直接退出
        if macd.iloc[-1]['macd'] > 0:
            raise ReturnError( self.code+'，以红柱结束，已过底背离！' )

        rst.clear()
        rst.append(macd.iloc[-1]['time'])
        rst2.append(macd.iloc[-1]['dif'])

        for idx in range(1, cnt - 1):
            if len(rst2) == 1:
                # 从右向左先死叉,macd应从红转绿,记录最后的红线时间
                if macd.iloc[-idx]['macd'] >= 0:
                    rst.append(macd.iloc[-idx]['time'])
                    rst2.append(macd.iloc[-idx]['dif'])
            if len(rst2) == 2:
                # 从右向左死叉后又金叉,macd应从绿转红,记录最后的绿线时间
                if macd.iloc[-idx]['macd'] < 0:
                    rst.append(macd.iloc[-idx]['time'])
                    rst2.append(macd.iloc[-idx]['dif'])

        if len(rst2) == 3:
            # rst2[0]：dif将要金叉的高度 ， rst2[2]：第一次金叉的高度,  都要在0轴下
            if 0 > rst2[0] > rst2[2]:
                # 符合底背离条件，需要再判断是否即将金叉
                try:
                    bing_golden = self.analyze_bing_golden(macd, isptt)
                except ReturnError:
                    raise ReturnError( self.code+'，不是底背离，没有将要金叉！' )

                # 将要金叉，符合背离，本只股票，将要底背离
                if isptt:
                    print('\n 股票代码：', self.code)
                    print(rst)
                    print(rst2)
                dbl = []
                dbl.append('即将底背离')
                dbl.append(self.code.split('.')[1])
                dbl.append(rst[0])
                dbl.append(rst2[0])
                dbl.append(rst[2])
                dbl.append(rst2[2])
                return dbl

            else:
                raise ReturnError( self.code+'，不是底背离，三次交叉不符合条件！' )
        else:
            raise ReturnError( self.code+'，不是底背离，不是三次交叉！' )

    def save_golden(self, market='all'):
        df_rst = pd.DataFrame(
            columns=(
                '类别',
                '股票代码',
                '日期',
                '快线强弱',
                '红柱数量',
                '大陆代码'))
        # print('\r', str(10 - i).ljust(10), end='')

        stock_code = stock_base.get_stock_code(market)

        if self.jb == 'm':
            pre = '月K线金叉'
        if self.jb == 'd':
            pre = '日K线金叉'
        if self.jb == 'w':
            pre = '周K线金叉'
        if self.jb == '60':
            pre = '60分钟K线金叉'
        if self.jb == '15':
            pre = '15分钟K线金叉'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.xls'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):
            pre2 = '剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')
            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except ReturnError:
                continue

            try:
                df2 = self.get_MACD(df)
            except ReturnError:
                continue

            try:
                df3 = self.analyze_golden(df2)
            except ReturnError:
                continue
            else:
                line += 1
                df_rst.loc[line] = df3

        print('\n\t\t', '完成！\n')
        df_rst.to_excel(self.save_name, sheet_name='金叉清单')

    def save_bing_golden(self, market='all'):
        """周线选股时，日线即将金叉，或者已经金叉的日线级别增强判断"""
        df_rst = pd.DataFrame(
            columns=(
                '类别',
                '股票代码',
                '日期',
                '快线强弱',
                '红柱数量',
                '大陆代码'))
        # print('\r', str(10 - i).ljust(10), end='')

        stock_code = stock_base.get_stock_code(market)

        if self.jb == 'm':
            pre = '月K线金叉'
        if self.jb == 'd':
            pre = '日K线金叉'
        if self.jb == 'w':
            pre = '周K线金叉'
        if self.jb == '60':
            pre = '60分钟K线金叉'
        if self.jb == '15':
            pre = '15分钟K线金叉'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.xls'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):
            pre2 = '剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')
            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except ReturnError:
                continue

            try:
                df2 = self.get_MACD(df)
            except ReturnError:
                continue

            try:
                df3 = self.analyze_golden(df2)
            except ReturnError:
                continue
            else:
                line += 1
                df_rst.loc[line] = df3

        print('\n\t\t', '完成！\n')
        df_rst.to_excel(self.save_name, sheet_name='金叉清单')


    def save_day_golden(self, market='all', isprt=False):
        df_rst = pd.DataFrame(
            columns=(
                '类别',
                '股票代码',
                '日期',
                '快线强弱',
                '将要金叉周期',
                '大陆代码'))
        try:
            stock_code = stock_base.get_stock_code(market)
        except sb.ReturnError:
            print(sb.ReturnError)
            return
        if self.jb == 'm':
            pre = '月K线(即将)金叉'
        if self.jb == 'd':
            pre = '日K线(即将)金叉'
        if self.jb == 'w':
            pre = '周K线(即将)金叉'
        if self.jb == '60':
            pre = '60分钟K线(即将)金叉'
        if self.jb == '15':
            pre = '15分钟K线(即将)金叉'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.xls'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):
            pre2 = '剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')

            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except ReturnError:
                continue

            try:
                df2 = self.get_MACD(df)
            except ReturnError:
                continue

            try:
                df3 = self.analyze_bing_golden(df2, isprt)
            except ReturnError:
                pass
            else:
                line += 1
                df_rst.loc[line] = df3
                continue

            try:
                df3 = self.analyze_golden(df2, isprt)
            except ReturnError:
                continue
            else:
                line += 1
                df_rst.loc[line] = df3

        print('\n \t\t', '完成！\n')
        df_rst.to_excel(self.save_name, sheet_name='将要金叉清单')

    def save_bottom(self, market='all', isprt=False):
        df_rst = pd.DataFrame(
            columns=(
                '指标类别',
                '股票代码',
                '日期',
                '快线强弱',
                '首次金叉时间',
                '大陆代码'))
        # market不是'all'，从传入的文件取代码
        try:
            stock_code = stock_base.get_stock_code(market)
        except stock_base.ReturnError:
            print(stock_base.ReturnError)

        if self.jb == 'm':
            pre = '月K线 即将底背离'
        if self.jb == 'd':
            pre = '日K线 即将底背离'
        if self.jb == 'w':
            pre = '周K线 即将底背离'
        if self.jb == '60':
            pre = '60分钟K线 即将底背离'
        if self.jb == '15':
            pre = '15分钟K线 即将底背离'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.xls'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):
            pre2 = '剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')
            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except ReturnError:
                continue

            try:
                df2 = self.get_MACD(df)
            except ReturnError:
                continue
            try:
                dbl_rst = self.analyze_bottom(df2, isprt)
            except ReturnError:
                continue
            else:
                line += 1
                df_rst.loc[line] = dbl_rst

        print('\n \t\t', '完成！\n')
        df_rst.to_excel(self.save_name, sheet_name='将要底背离')

    def save_top(self, market='all', isprt=False):
        df_rst = pd.DataFrame(
            columns=(
                '类别',
                '股票代码',
                '日期',
                '快线强弱',
                '将要金叉周期',
                '大陆代码'))
        # market不是'all'，从传入的文件取代码
        stock_code = stock_base.get_stock_code(market)

        if self.jb == 'm':
            pre = '月K线 顶背离'
        if self.jb == 'd':
            pre = '日K线 顶背离'
        if self.jb == 'w':
            pre = '周K线 顶背离'
        if self.jb == '60':
            pre = '60分钟K线 顶背离'
        if self.jb == '15':
            pre = '15分钟K线 顶背离'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.xls'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):
            pre2 = '剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')
            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except ReturnError:
                continue

            try:
                df2 = self.get_MACD(df)
            except ReturnError:
                continue
            df3 = self.analyze_top(df2, isprt)


if __name__ == "__main__":
    macd_60 = MACD_INDEX('60')
    macd_60.save_golden('D:\\0_stock_macd\\_日K线金叉.xls')

    # macd_15 = MACD_INDEX('15')
    # macd_15.save_golden('D:\\0_stock_macd\\_60分钟K线金叉.xls')

    # # 日线已经金叉，算60分钟即将金叉
    # macd_60 = MACD_INDEX('60')
    # # macd_60.save_bing_golden('D:\\0_stock_macd\\_周K线金叉.xls')
    # macd_60.save_bing_golden('D:\\0_stock_macd\\_日K线金叉.xls', False)

    macd_60 = MACD_INDEX('60')
    macd_60.set_time('2018-06-01', '2018-12-11')

    macd_60.save_bottom('all', False)

    # 周K线已经金叉，算日线即将金叉  # macd_d = MACD_INDEX('d')  #  #
    # macd_d.save_bing_golden('D:\\0_stock_macd\\_周K线金叉.xls')

    # stock_code = stock_base.get_stock_code('D:\\0_stock_macd\\_周K线金叉.xls')
    # # # cnt = stock_code.shape[0]

# 单只股票调试
