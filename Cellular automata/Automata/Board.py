from PyQt4.uic import loadUiType
from xlrd import open_workbook
from PyQt4 import QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import random as rn
import random
import numpy as np
from namedlist import namedlist as nl


class Board:

    cells_container = []
    cell = nl('Cell', 'type x y color')
#wrzucic zabezpieczenie odnosnie wartosci maksymalne x, y
    def __init__(self, width = 300, height = 300):
        self.restricted_colors = [[0, 0, 0], [255, 255, 255], [1,1,1,1], [1,1,1,0]]
        self.colors_broad_or_inc = [0, 0, 0]
        self.usedcolors = [[255, 255, 255], [0, 0, 0]]
        self.width = width
        self.height = height
        self.calculate_cells()
        self.calculate_cells_available()
        self.create_board()

    def calculate_cells(self):
        self.cells = np.zeros((self.height, self.width), dtype=list)

    def calculate_cells_available(self):
        self.cells_available = self.cells.size - 2 * (self.width + self.height) + 4

    def create_board(self):
        for i in range(self.height):
            for j in range(self.width):
                self.cells[i, j] = [255, 255, 255]

    def reset_board (self):
        self.create_board()

    def create_cell (self, state, posx, posy):
        if self.cells[posy, posx] == [255,255,255]:
            if state == "grain_init":
                cell_color = self.gen_color()
                self.cells_available -= 1
            elif state == "grain_growth":
                cell_color = self.grain_determine_Moore(posx, posy)[1]
                if cell_color not in self.restricted_colors:
                    self.cells_available -= 1
                    print(self.cells_available)
                    print(cell_color)
            self.cells[posy, posx] = cell_color

    def initial_grains_onboard (self, amountofgrains):
        for grain in range(amountofgrains):
            while True:
                posx_init = random.randint(1, self.width - 2)
                posy_init = random.randint(1, self.height - 2)
                if self.cells[posy_init, posx_init] == [255, 255, 255]:
                    break
            self.create_cell('grain_init', posx_init, posy_init)


    def grains_process(self):

        while [255,255,255] in self.cells[1:self.height - 2, 1:self.width - 2].flatten().tolist():
            self.old_board = self.board_copy(self.cells)
            for j in range(1, self.height - 1):
                for i in range(1, self.width - 1):
                    if self.old_board[j, i] == [255,255,255]:
                        self.create_cell("grain_growth", i, j)
            if np.array_equal(self.old_board, self.cells):
                break
        self.output.close()


    def grain_determine_Moore(self, row, col):
        cell_neighbours = []
        color_dict = {}
        neighbours_dict = {}
        Cell = nl('Cell', 'color x y')

        for x, y in (
                (row - 1, col), (row + 1, col), (row, col - 1),
                (row, col + 1), (row - 1, col - 1), (row - 1, col + 1),
                (row + 1, col - 1), (row + 1, col + 1)):

            cell_color = self.old_board[y, x]
            cell_neighbours.append(Cell(tuple(cell_color), y, x))

            if cell_color not in self.restricted_colors:
                if tuple(cell_color) not in color_dict.keys():
                    color_dict[tuple(cell_color)] = 1
                else:
                    color_dict[tuple(cell_color)] += 1
            if tuple(cell_color) not in neighbours_dict.keys():
                neighbours_dict[tuple(cell_color)] = 1
            else:
                neighbours_dict[tuple(cell_color)] += 1
        if len(color_dict) == 0:
            new_grain_color = (255,255,255)
        else:
            new_grain_color = max(color_dict, key = lambda k: color_dict[k])
        return color_dict, list(new_grain_color), neighbours_dict

    def add_inclusion(self, inc_amount, inc_size, inc_type, inc_mode):
        if inc_mode == 'before grow':
            x = np.arange(0, self.width)
            y = np.arange(0, self.height)
            inc_color = np.empty(1, object)
            board_copy = self.board_copy(self.cells)
            for grain in range(inc_amount):
                posx_init = random.randint(1, self.width - 2)
                posy_init = random.randint(1, self.height - 2)
                if inc_type == "circle":
                    inc_color[0] = [1, 1, 1, 0]
                    mask = (x[np.newaxis, :] - posx_init) ** 2 + (y[:, np.newaxis] - posy_init) ** 2 < inc_size ** 2
                    self.cells[mask] = inc_color
                elif inc_type == "square":
                    inc_color[0] = [1, 1, 1, 1]
                    self.cells[posx_init : posx_init + inc_size, posy_init:posy_init + inc_size] = inc_color
                for j in range(self.height):
                    for i in range (self.width):
                        if self.cells[j,i] != board_copy [j,i]:
                            self.cells_available -= 1
        elif inc_mode == 'after grow':
            x = np.arange(0, self.width)
            y = np.arange(0, self.height)
            inc_color = np.empty(1, object)
            for grain in range(inc_amount):
                while True:
                    posx_init = random.randint(1, self.width - 2)
                    posy_init = random.randint(1, self.height - 2)
                    if self.cells[posy_init, posx_init] == [0,0,0]:
                        break
                if inc_type == "circle":
                    inc_color[0] = [1, 1, 1, 0]
                    mask = (x[np.newaxis, :] - posx_init) ** 2 + (y[:, np.newaxis] - posy_init) ** 2 < inc_size ** 2
                    self.cells[mask] = inc_color
                elif inc_type == "square":
                    inc_color[0] = [1, 1, 1, 1]
                    self.cells[posx_init: posx_init + inc_size, posy_init:posy_init + inc_size] = inc_color


    def grain_determine_border(self):
        for j in range(1, self.height - 1):
            for i in range(1, self.width -1):
                cell_neighborhood = self.grain_determine_Moore(i,j)[2]
                if len(cell_neighborhood) > 1:
                    self.cells[j,i] = [0,0,0]

    def gen_color(self):
        while True:
            color = [rn.randint(0, 255), rn.randint(0, 255), rn.randint(0, 255)]
            if color not in self.usedcolors:
                break
        self.usedcolors.append(color)
        return color

    def board_copy(self, board):
        copy_board = np.copy(board)
        return copy_board








































