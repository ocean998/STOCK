
import Select as sl
import macd_base as mb
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import stock_base as stb

class MACD_Calc(QThread):
    signal = pyqtSignal()    # 括号里填写信号传递的参数
    def __init__(self, msg='提示对话框'):
        super().__init__()
        self.msg = msg
        

class show_MessageBox(QThread):
    signal = pyqtSignal()  # 括号里填写信号传递的参数
    def __init__(self, macd='golden_60', textEdit=None):
        super().__init__()
        self.macd = macd
        self.textEdit = textEdit

    def __del__(self):
        self.wait()

    def golden_60(self):
        macd_60 = mb.MACD_INDEX('60')
        macd_60.save_golden('D:\\0_stock_macd\\_周K线金叉.xls')
        stock_code = stb.get_stock_code(macd_60.save_name)
        cnt = stock_code.shape[0]
        code = '周线金叉60分钟级别金叉共 ' + str(cnt) + ' 只'
        self.textEdit.append(code)
        for x in range(cnt):
            code = stock_code.iloc[x]['stock_code']
            self.textEdit.append(code)

    def golden_15(self):
        macd_15 = mb.MACD_INDEX('15')
        macd_15.save_golden('D:\\0_stock_macd\\_日K线金叉.xls')
        stock_code = stb.get_stock_code(macd_15.save_name)

        cnt = stock_code.shape[0]
        code = '日线金叉15分钟级别金叉共 ' + str(cnt) + ' 只'
        self.textEdit.append(code)
        for x in range(cnt):
            code = stock_code.iloc[x]['stock_code']
            self.textEdit.append(code)

    def bottom_60(self):
        bottom_60 = mb.MACD_INDEX('60')
        bottom_60.save_bottom('D:\\0_stock_macd\\_周K线金叉.xls')
        stock_code = stb.get_stock_code(bottom_60.save_name)

        cnt = stock_code.shape[0]
        code = '周线金叉60分钟底背离共 ' + str(cnt) + ' 只'
        self.textEdit.append(code)
        for x in range(cnt):
            code = stock_code.iloc[x]['stock_code']
            self.textEdit.append(code)

    def init_mwd(self):
        macd_m = mb.MACD_INDEX('m')
        macd_m.save_golden('all')

        macd_w = mb.MACD_INDEX('w')
        macd_w.save_golden('D:\\0_stock_macd\\_月K线金叉.xls')

        macd_d = mb.MACD_INDEX('d')
        macd_d.save_golden('D:\\0_stock_macd\\_周K线金叉.xls')

    def run(self):
        # 进行任务操作
        # super().acquire()
        if self.macd == 'golden_60':
            self.golden_60()
        if self.macd == 'golden_15':
            self.golden_15()
        if self.macd == 'bottom_60':
            self.bottom_60()
        if self.macd == 'init_mwd':
            self.init_mwd()
        # super().release()
        self.signal.emit()    # 发射信号


class Slt_Stock(QtWidgets.QMainWindow, sl.Ui_MainWindow):
    '''根据界面、逻辑分离原则 初始化界面部分'''

    def __init__(self, parent=None):
        super(Slt_Stock, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.btn_golden_60)
        self.pushButton_3.clicked.connect(self.btn_bottom_60)
        self.pushButton_4.clicked.connect(self.btn_golden_15)
        self.pushButton.clicked.connect(self.btn_init_MWD)
        self.operating = ''

    def btn_golden_60(self):
        print('self.operating:', self.operating)
        if len(self.operating) == 0:
            self.operating = '正在获取网络数据计算 周线金叉60分钟级别金叉，请稍等！'
            print('self.operating:', self.operating)
            self.statusbar.showMessage('正在获取网络数据计算 周线金叉60分钟级别金叉，请稍等！')
            self.thread = MACD_Calc('golden_60', self.textEdit)
            self.thread.signal.connect(self.golden_60)
            self.thread.start()  # 启动线程
        else:
            print('准备弹出框', self.operating)
            QMessageBox.question(self, self.operating, QMessageBox.Yes)
            return

    def golden_60(self):
        self.statusbar.showMessage('周线金叉60分钟级别金叉，计算完成！')
        self.operating = ''

    def btn_bottom_60(self):
        print('self.operating:', self.operating)
        if len(self.operating) == 0:
            self.operating = '正在获取网络数据计算 周线金叉且60分钟级别底背离，请稍等！'
            print('self.operating:', self.operating)
            self.statusbar.showMessage('正在获取网络数据计算 周线金叉且60分钟级别底背离，请稍等！')
            self.thread = MACD_Calc('bottom_60', self.textEdit_2)
            self.thread.signal.connect(self.bottom_60)
            self.thread.start()  # 启动线程
        else:
            print(' 准备弹出框', self.operating)
            QMessageBox.question(self, self.operating, QMessageBox.Yes)
            return

    def bottom_60(self):
        self.statusbar.showMessage('周线金叉且60分钟级别底背离，计算完成！')
        self.operating = ''

    def btn_golden_15(self):
        if len(self.operating) == 0:
            self.operating = '正在获取网络数据计算 周线金叉且15分钟级别金叉，请稍等！'
            self.statusbar.showMessage('正在获取网络数据计算 周线金叉且15分钟级别金叉，请稍等！')
            self.thread = MACD_Calc('golden_15', self.textEdit_3)
            self.thread.signal.connect(self.golden_15)
            self.thread.start()  # 启动线程
        else:
            QMessageBox.question(self, self.operating, QMessageBox.Yes)
            return

    def golden_15(self):
        self.statusbar.showMessage('日线金叉且15分钟级别金叉，计算完成！')
        self.operating = ''

    def btn_init_MWD(self):
        if len(self.operating) == 0:
            self.operating = '正在获取网络数据计算完成月、周、日金叉初始化，时间较长请稍等！'
            self.statusbar.showMessage('正在获取网络数据计算完成月、周、日金叉初始化，时间较长请稍等！')
            self.thread = MACD_Calc('init_mwd', self.textEdit_2)
            self.thread.signal.connect(self.init_MWD)
            self.thread.start()  # 启动线程
        else:
            QMessageBox.question(self, self.operating, QMessageBox.Yes)
            return

    def init_MWD(self):
        '''初始化 月 周 日 分别在上级别基础上金叉'''
        self.statusbar.showMessage('月、周、日金叉初始化，计算完成！')
        self.operating = ''


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MP = Slt_Stock()
    MP.show()
    sys.exit(app.exec_())
