import Board
import os
import numpy as np
from PyQt4.uic import loadUiType
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtGui import *
Ui_MainWindow, QMainWindow = loadUiType('gui_automata.ui')


class Controller (QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Controller, self).__init__()
        self.setupUi(self)
        self.width = 300
        self.height = 300
        self.cc_initial()
        self.inclusion_before = False
        self.inclusion_after = False
        self.pushButton.clicked.connect(lambda: self.nucleating_init(self.spinBox.value(), self.spinBox_4.value(), self.spinBox_5.value()))
        self.pushButton_2.clicked.connect(lambda: self.grains_growth())
        self.pushButton_3.clicked.connect(lambda: self.cc_initial())
        self.toolButton.clicked.connect(lambda: self.export_txt())
        self.toolButton_2.clicked.connect(lambda: self.export_bmp())
        self.toolButton_3.clicked.connect(lambda: self.import_bmp())
        self.toolButton_4.clicked.connect(lambda: self.import_txt())
        self.pushButton_4.clicked.connect(lambda: self.add_inclusion(self.comboBox_3))

    def showdialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)

        msg.setText("Wprowadzono niepoprawne dane")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        retval = msg.exec_()
        print("value of pressed message box button:", retval)

    def cc_initial(self):
        self.new_board = Board.Board(self.width,self.height)
        self.widget.set_Widget(self.width, self.height)

    def grid_size(self, set_width, set_height):
        self.width = set_width
        self.height = set_height
        self.new_board = Board.Board(self.width,self.height)
        self.widget.set_Widget(self.width, self.height)


    def nucleating_init(self, number_of_grains, set_width, set_height):
        self.grid_size(set_width, set_height)
        if self.inclusion_before is True:
            self.new_board.add_inclusion(self.spinBox_2.value(), self.spinBox_3.value(), self.comboBox.currentText(), self.comboBox_3.currentText())
        self.numberofgrains = number_of_grains
        self.grains_number_verify(number_of_grains)
        print(self.new_board.cells_available)
        self.new_board.initial_grains_onboard(self.numberofgrains)
        self.widget.set_Widget(self.width, self.height, self.new_board.cells)
    def grains_number_verify(self, numberofgrains):
        self.numberofgrains = numberofgrains
        if numberofgrains > self.new_board.cells_available:
            self.numberofgrains = self.new_board.cells_available


    def grains_growth(self):
        self.new_board.grains_process()
        #self.new_board.grain_determine_border()
        if self.inclusion_after is True:
            self.new_board.add_inclusion(self.spinBox_2.value(), self.spinBox_3.value(), self.comboBox.currentText(), self.comboBox_3.currentText())
        self.widget.set_Widget(self.width,self.height, self.new_board.cells)



    def add_inclusion(self, timeofadd):
        if timeofadd.currentText() == 'before grow':
            self.inclusion_before = True
        elif timeofadd.currentText() == 'after grow':
            self.inclusion_after = True





















































    def add_inclusion_after(self, shape, size):
        if shape == 'circle':
            self.widget.shape = 'circle'
            self.widget.size = size
        elif shape == 'square':
            self.widget.shape = 'square'
            self.widget.size = size



    def export_bmp(self):
        picture = QPixmap.grabWidget(self.widget, width = self.width, height = self.height)
        number = 1
        while os.path.exists(f'microstructure{number}.bmp'):
            number += 1
        picture.save(f'microstructure{number}.bmp', 'bmp')

    def export_txt(self):
        file = f'#123Qt#584\n{self.width} |:| {self.height} |:| {self.numberofgrains}\n'
        for y in range(self.height):
            for x in range(self.width):
                file += f'{x} |:| {y} |:| {self.new_board.cells[y,x]}\n'
        number = 1
        while os.path.exists(f'microstructure{number}.txt'):
            number += 1
        f = open(f'microstructure{number}.txt', 'w+')
        f.write(file)
        f.close()

    def import_bmp(self, mode = 'original'):
        filename = self.lineEdit_4.text()
        image = Image.open(filename, 'r')

        if image.mode == 'RGB':
            if mode == 'original':
                self.width, self.height = image.size
                self.width = min(max(self.width, 200), 500)
                self.height = min(max(self.height, 200), 500)
            elif self.checkBox_4.is_checked() is True:
                self.width = self.spinBox_4.value()
                self.height = self.spinBox_5.value()
            self.grid_size(self.width, self.height)
            cells_type = list(image.getdata())
            self.new_board.cells = np.array(cells_type).reshape((self.width, self.height, 3))
            self.widget.set_Widget(self.width, self.height, self.new_board.cells)

    def import_txt(self):
        filename = self.lineEdit_5.text()
        with open(filename) as f:
            for i, line in enumerate(f):
                string_list = line.replace('[', '').replace(']','')
                string_list = string_list.strip('\n')
                string_list = string_list.split('|:|')
                if i == 0:
                    string_list[0] = '#123Qt#594'
                elif i == 1:
                    self.width = int(string_list[0])
                    self.height = int(string_list [1])
                    self.numberofgrains = int(string_list [2])
                    self.grid_size(self.width, self.height)
                else:
                    self.new_board.cells[int(string_list[1]), int(string_list[0])] = list(map(int, string_list[2].split(',' )))
        self.widget.set_Widget(self.width, self.height, self.new_board.cells)




if __name__ == '__main__':
    import sys



    app = QtGui.QApplication(sys.argv)
    main = Controller()
    main.show()
    sys.exit(app.exec_())
