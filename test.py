import Select as sl
import macd_base as mb
from PyQt5 import QtWidgets
import pandas as pd
import stock_base as stb


class Slt_Stock(QtWidgets.QMainWindow, sl.Ui_MainWindow):
    '''根据界面、逻辑分离原则 初始化界面部分'''

    def __init__(self, parent=None):
        super(Slt_Stock, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.golden_60)
        self.pushButton_3.clicked.connect(self.bottom_60)
        self.pushButton_4.clicked.connect(self.golden_15)

    def golden_60(self):
        self.statusbar.showMessage('正在获取网络数据计算 周线金叉60分钟级别金叉，请稍等！')
        macd_d = mb.MACD_INDEX('60')
        macd_d.save_golden('D:\\0_stock_macd\\_周K线金叉.xls')
        stock_code = stb.get_stock_code(macd_d.save_name)

        cnt = stock_code.shape[0]
        code = '周线金叉60分钟级别金叉共 ' + str(cnt) + ' 只'
        self.textEdit.append(code)
        for x in range(cnt):
            code = stock_code.iloc[x]['stock_code']
            self.textEdit.append(code)

    def golden_15(self):
        self.statusbar.showMessage('正在获取网络数据计算 日线金叉15分钟级别金叉，请稍等！')
        macd_d = mb.MACD_INDEX('15')
        macd_d.save_golden('D:\\0_stock_macd\\_日K线金叉.xls')
        stock_code = stb.get_stock_code(macd_d.save_name)

        cnt = stock_code.shape[0]
        code = '日线金叉15分钟级别金叉共 ' + str(cnt) + ' 只'
        self.textEdit_3.append(code)
        for x in range(cnt):
            code = stock_code.iloc[x]['stock_code']
            self.textEdit_3.append(code)

    def bottom_60(self):
        self.statusbar.showMessage('正在获取网络数据计算 周线金叉60分钟级别底背离，请稍等！')
        macd_d = mb.MACD_INDEX('60')
        macd_d.save_bottom('D:\\0_stock_macd\\_周K线金叉.xls')
        stock_code = stb.get_stock_code(macd_d.save_name)

        cnt = stock_code.shape[0]
        code = '周线金叉60分钟底背离共 ' + str(cnt) + ' 只'
        self.textEdit_2.append(code)
        for x in range(cnt):
            code = stock_code.iloc[x]['stock_code']
            self.textEdit_2.append(code)

    def init_MWD(self):
        '''初始化 月 周 日 分别在上级别基础上金叉'''
        macd_m = mb.MACD_INDEX('m')
        macd_m.save_golden('all')

        macd_w = mb.MACD_INDEX('w')
        macd_w.save_golden('D:\\0_stock_macd\\_月K线金叉.xls')

        macd_d = mb.MACD_INDEX('d')
        macd_d.save_golden('D:\\0_stock_macd\\_周K线金叉.xls')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MP = Slt_Stock()
    MP.show()
    sys.exit(app.exec_())
