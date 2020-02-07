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
    def __init__(self, width = 100, height = 100):
        self.restricted_colors = [[0, 0, 0], [255, 255, 255], [1,1,1,1], [1,1,1,0]]
        self.colors_broad_or_inc = [0, 0, 0]
        self.cells_recrystalised = []
        self.usedcolors = []
        self.cells_recrystalised_cord = []
        self.width = width
        self.height = height
        self.calculate_cells()
        self.calculate_cells_available()
        self.create_board()

    def calculate_cells(self):
        self.cells = np.zeros((self.height, self.width), dtype=list)
        self.cells_energy_distributed = np.zeros((self.height, self.width), dtype=list)

    def calculate_cells_available(self):
        self.cells_available = self.cells.size - 2 * (self.width + self.height) + 4

    def create_board(self):
        for i in range(self.height):
            for j in range(self.width):
                self.cells[i, j] = [255, 255, 255]

    def reset_board (self):
        self.create_board()

    def create_cell (self, state, posx, posy):
        if state == "grain_init":
            cell_color = self.gen_color()
            self.cells_available -= 1
        elif state == "grain_recryst":
            cell_color = self.gen_color()
            self.cells_available -= 1
            if cell_color not in self.cells_recrystalised:
                self.cells_recrystalised.append(cell_color)
        elif state == "grain_growth":
            cell_color = self.grain_determine_Moore(posx, posy)[1]
            if cell_color not in self.restricted_colors:
                self.cells_available -= 1
                print(self.cells_available)
                print(cell_color)
        self.cells[posy, posx] = cell_color

    def initial_grains_onboard (self, amountofgrains, mode = None):
        for grain in range(amountofgrains):
            while True:
                posx_init = random.randint(1, self.width - 2)
                posy_init = random.randint(1, self.height - 2)
                if self.cells[posy_init, posx_init] == [255, 255, 255]:
                    self.create_cell('grain_init', posx_init, posy_init)
                    break

    def clean_grains(self):
        for j in range(1, self.height - 1):
            for i in range(1, self.width - 1):
                if self.cells[j,i] != [0, 0, 0]:
                    self.cells[j,i] = [255,255,255]

    def grains_process(self):

        while [255,255,255] in self.cells[1:self.height - 2, 1:self.width - 2].flatten().tolist():
            self.old_board = self.board_copy(self.cells)
            for j in range(1, self.height - 1):
                for i in range(1, self.width - 1):
                    if self.old_board[j, i] == [255,255,255]:
                        self.create_cell("grain_growth", i, j)
            if np.array_equal(self.old_board, self.cells):
                break
        self.old_board = self.board_copy(self.cells)

    def grain_determine_Moore(self, row, col):
        #TO DO SPRAWDZIC CZY NIE JEST ODROWTNIE?
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


    def grain_determine_border(self, size):
        if size != 0:
            for l in range(size):
                for j in range(1, self.height - 1):
                    for i in range(1, self.width -1):
                        cell_neighborhood = self.grain_determine_Moore(i,j)[2]
                        if len(cell_neighborhood) > 1:
                            print(l)
                            self.cells[j,i] = [0,0,0]
                self.old_board = self.board_copy(self.cells)


    def gen_color(self):
        while True:
            color = [rn.randint(0, 255), rn.randint(0, 255), rn.randint(0, 255)]
            if color not in self.usedcolors and color not in self.restricted_colors:
                break
        self.usedcolors.append(color)
        return color

    def board_copy(self, board):
        copy_board = np.copy(board)
        return copy_board

    def init_MC(self,amountofgtains):
        colors = []
        self.usedcolors = []
        for x in range(amountofgtains):
            colorr = self.gen_color()
            colors.append(colorr)
            self.usedcolors.append(colorr)
        print(self.usedcolors)
        for j in range(1, self.height - 1):
            for i in range(1, self.width - 1):
                if self.cells[j,i] != [0,0,0]:
                    color = random.choice(colors)
                    self.cells[j,i] = color

    def simulation_MC(self):
        print(self.usedcolors)
        for x in range(self.iterations):
            print(x)
            self.old_board = self.board_copy(self.cells)
            for j in range(1, self.height - 1):
                for i in range(1, self.width - 1):
                    color = random.choice(self.usedcolors) #losowac z calkowitej puli dostepnych kolorow czy tylko z nowych po rekrystalizacji
                    energy_start = self.estimate_energy(i, j, self.old_board[j,i], True)
                    energy_finnish = self.estimate_energy(i, j, color)
                    energy_diff = energy_finnish - energy_start
                    if energy_diff <= 0:
                        self.cells[j, i] = color

    def estimate_energy(self, x, y, color, energy_distributed = False):
        energy = 0
        neighbours_dict = self.grain_determine_Moore(x,y)[0]
        for key in neighbours_dict.keys():
            if list(key) != color:
                energy += neighbours_dict[key]
        if energy_distributed == True:
            energy += self.cells_energy_distributed[y,x]
        return energy


    def energy_color(self, energy):
        low_energy = [10, 100, 200]
        medium_energy = [30, 130, 255]
        high_energy = [130, 200, 50]

        if energy == 2:
            return low_energy
        elif energy > 2 and energy < 5:
            return [(low_energy[0] + (medium_energy[0] - low_energy[0]) * (energy / 5)),
                    (low_energy[1] + (medium_energy[1] - low_energy[1]) * (energy / 5)),
                    (low_energy[2] + (medium_energy[2] - low_energy[2]) * (energy / 5))]
        elif energy == 5:
            return medium_energy
        elif energy > 5 and energy < 7:
            return [(medium_energy[0] + (high_energy[0] - medium_energy[0]) * (energy / 7)),
                    (medium_energy[1] + (high_energy[1] - medium_energy[1]) * (energy / 7)),
                    (medium_energy[2] + (high_energy[2] - medium_energy[2]) * (energy / 7))]
        else:
            return high_energy

    def energy_distribution(self, grain_energy, boundary_energy, size):
        self.cells_energy = self.board_copy(self.cells)
        if isinstance(grain_energy, int) and isinstance(boundary_energy, int):
            for j in range(1, self.height - 1):
                for i in range(1, self.width - 1):
                    cell_neighborhood = self.grain_determine_Moore(i, j)[2]
                    if len(cell_neighborhood) > 1:
                        self.cells[j, i] = [0, 0, 0]
            self.cells_energy = self.board_copy(self.cells)
            for j in range(1, self.height - 1):
                for i in range(1, self.width - 1):
                    if self.cells_energy[j,i] not in self.restricted_colors:
                        self.cells_energy[j,i] = self.energy_color(grain_energy)
                        self.cells_energy_distributed[j,i] = grain_energy
                    elif self.cells_energy[j,i] == [0,0,0]:
                        self.cells_energy[j, i] = self.energy_color(boundary_energy)
                        self.cells_energy_distributed[j, i] = boundary_energy
        elif isinstance(grain_energy, int):
            for j in range(1, self.height - 1):
                for i in range(1, self.width - 1):
                    if self.cells_energy[j,i] not in self.restricted_colors:
                        self.cells_energy[j,i] = self.energy_color(grain_energy)
                        self.cells_energy_distributed[j, i] = grain_energy



    def recrystalisation_nucl(self, amountofgrains, mode = None):
        print (self.cells_recrystalised)
        print (mode)
        if mode == 'satured':
            for grain in range(self.amountofgrains):
                while True:
                    posx_init = random.randint(1, self.width - 2)
                    posy_init = random.randint(1, self.height - 2)
                    if self.cells[posy_init, posx_init] not in self.cells_recrystalised and [posy_init, posx_init] not in self.cells_recrystalised_cord:
                        self.create_cell('grain_recryst', posx_init, posy_init)
                        self.cells_recrystalised_cord.append([[posy_init, posx_init]])
                        self.amountofgrains -= 1
                        print(self.amountofgrains)
                        break
        elif mode =='constant':
            for grain in range(self.amountofgrains):
                while True:
                    posx_init = random.randint(1, self.width - 2)
                    posy_init = random.randint(1, self.height - 2)
                    if self.cells[posy_init, posx_init] not in self.cells_recrystalised and [posy_init, posx_init] not in self.cells_recrystalised_cord:
                        self.create_cell('grain_recryst', posx_init, posy_init)
                        self.cells_recrystalised_cord.append([[posy_init, posx_init]])
                        print(self.amountofgrains)
                        break
        elif mode =='increased':
            for grain in range(self.amountofgrains):
                while True:
                    posx_init = random.randint(1, self.width - 2)
                    posy_init = random.randint(1, self.height - 2)
                    if self.cells[posy_init, posx_init] not in self.cells_recrystalised and [posy_init, posx_init] not in self.cells_recrystalised_cord:
                        self.create_cell('grain_recryst', posx_init, posy_init)
                        self.cells_recrystalised_cord.append([[posy_init, posx_init]])
                        print(self.amountofgrains)
                        break
            self.amountofgrains += amountofgrains
        else:
            pass



    def simulation_recrystalisation(self, amountofgrains, mode = None):
        self.amountofgrains = amountofgrains

        for x in range(self.iterations):
            print(x)
            neighbours_all = {}
            neighbours_checked_all = {}
            self.recrystalisation_nucl(amountofgrains, mode)
            self.old_board = self.board_copy(self.cells)
            for j in range(1, self.height - 1):
                for i in range(1, self.width - 1):
                    neighbours_all[(j, i)] = [(j - 1, i), (j + 1, i),
                                              (j, i - 1),
                                              (j, i + 1), (j - 1, i - 1),
                                              (j - 1, i + 1),
                                              (j + 1, i - 1),
                                              (j + 1, i + 1)]
            while True:
                posx_init = random.randint(1, self.width - 2)
                posy_init = random.randint(1, self.height - 2)
                if len(neighbours_all[(posy_init, posx_init)]) != 0:
                    neighbour_random = random.choice(neighbours_all[(posy_init, posx_init)])
                else:
                    break
                print('SPRAWDZAM')
                print(self.cells_recrystalised)
                print(self.cells[neighbour_random[0], neighbour_random[1]])
                # if all(elem in self.cells for elem in self.cells_recrystalised):
                #     print('TAK')
                if self.cells[neighbour_random[0], neighbour_random[1]] in self.cells_recrystalised:#TO DO if comparison works with numpy
                    print('pierwsza petla')
                    color = self.cells[neighbour_random[0], neighbour_random[1]]
                    energy_start = self.estimate_energy(posx_init, posy_init, self.old_board[posy_init,posx_init])
                    energy_finnish = self.estimate_energy(posx_init, posy_init, color)
                    energy_diff = energy_finnish - energy_start
                    if energy_diff <= 0:
                        print('druga petla')
                        self.cells[posy_init, posx_init] = color
                        self.cells_energy_distributed[posy_init, posx_init] = 0
                        self.cells_energy[posy_init, posx_init] = [255,0,0]
                elif len(neighbours_all[(posy_init, posx_init)]) == 0:
                    break
                else:
                    print('trzecia petla')
                    print (len(neighbours_all[(posy_init, posx_init)]))
                    print (neighbours_all[(posy_init, posx_init)])
                    if (posy_init, posx_init) in neighbours_checked_all.keys():
                        print(neighbours_checked_all[(posy_init, posx_init)])
                    print(neighbours_all[(posy_init, posx_init)])
                    if (posy_init, posx_init) not in neighbours_checked_all.keys():
                        neighbours_checked_all[(posy_init, posx_init)] = [neighbour_random]
                    elif (posy_init, posx_init) in neighbours_checked_all.keys():
                        print(neighbours_checked_all[(posy_init, posx_init)])
                        neighbours_checked_all[(posy_init, posx_init)].append(neighbour_random)
                    neighbours_all[(posy_init, posx_init)].remove(neighbour_random)
                    if (posy_init, posx_init) in neighbours_checked_all.keys():
                        print(neighbours_checked_all[(posy_init, posx_init)])
                    print(neighbours_all[(posy_init, posx_init)])


































