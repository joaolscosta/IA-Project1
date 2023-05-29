# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 123:
# 103603 Pedro Tavares
# 102078 João Costa

import sys, copy
import numpy as np
from sys import stdin

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id


class Board:
    #Internal representation of a Bimaru board
    def __init__(self, rows, columns, hints):
        
        self.rows = rows
        self.columns = columns
        self.empty_row_space = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        self.empty_column_space = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        self.rows.pop(0)
        self.columns.pop(0)
        self.hints_num = 0
        self.hints = []
        self.hints_actions_num = 0
        self.board = np.array([[None for j in range(len(rows))] for i in range(len(columns))])
        self.boats_4 = 0
        self.boats_3 = 0
        self.boats_2 = 0
        self.boats_1 = 0
        self.valid_path = True

        for i in range(10):
            self.rows[i] = int(self.rows[i])
            self.columns[i] = int(self.columns[i])

        #Place hints in board
        for i in range(len(hints)):
            x_cord = int(hints[i][0])
            y_cord = int(hints[i][1])
            self.board[x_cord][y_cord] = hints[i][2]
            if (hints[i][2] == 'C'):
                circle_water(self, hints[i][0], hints[i][1], 1, "horizontal")
                self.rows[x_cord] = int(self.rows[x_cord]) - 1
                self.columns[y_cord] = int(self.columns[y_cord]) - 1
                self.empty_row_space[x_cord] -= 1
                self.empty_column_space[y_cord] -= 1
                self.boats_1 += 1

            elif (hints[i][2] == 'W'):
                self.empty_row_space[x_cord] -= 1
                self.empty_column_space[y_cord] -= 1

            elif (self.board[x_cord][y_cord] == 'T' or
            self.board[x_cord][y_cord] == 'M' or self.board[x_cord][y_cord] == 'B' or
            self.board[x_cord][y_cord] == 'R' or self.board[x_cord][y_cord] == 'L'):
                self.rows[x_cord] = int(self.rows[x_cord]) - 1
                self.columns[y_cord] = int(self.columns[y_cord]) - 1
                self.empty_row_space[x_cord] -= 1
                self.empty_column_space[y_cord] -= 1
                self.hints_actions_num += 1
                self.hints_num += 1
                self.hints.append((hints[i][0], hints[i][1], hints[i][2]))
        
        check_completed_boats(self, self.hints)
        self.hints_actions = check_hints_actions(self, self.hints)
        for i in range(10):
            if (self.rows[i] == 0):
                fill_water(self, i, "horizontal")
            if (self.columns[i] == 0):
                fill_water(self, i, "vertical")

            

    #Print the board
    def print(self):

        for i in range(len(self.rows)):
            for j in range(len(self.columns)):
                if (self.board[i][j] == None or self.board[i][j] == 'w'):
                    print('.', end="")
                else:    
                    print(self.board[i][j], end="")
            print('\n', end="")
    

    def __getitem__(self, item):
         return self.board[item]
            

    #Returns the value in the given position
    def get_value(self, row: int, col: int) -> str:
        return self.board[row][col]


    #Returns the value above and below the given position
    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        
        if (row-1 >= 0 and row+1 <= 10):
            return (self.board[row-1][col], self.board[row+1][col])
        if (row-1 < 0 and row+1 <= 10):
            return (None, self.board[row+1][col])
        if (row-1 >= 0 and row+1 > 10):
            return (self.board[row-1][col], None)
        else:
            return (None, None)


    #Returns the left and right value of the given position
    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""

        if (col-1 >= 0 and col+1 <= 10):
            return (self.board[row][col-1], self.board[row][col+1])
        if (col-1 < 0 and col+1 <= 10):
            return (None, self.board[row][col+1])
        if (col-1 >= 0 and col+1 > 10):
            return (self.board[row][col-1], None)
        else:
            return (None, None)


    #Read the arguments from standard input (stdin) and return a class board instance
    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board."""
        
        rows = stdin.readline().split()
        columns = stdin.readline().split()
        hints_num = stdin.readline().split()
        hints = [0]*int(hints_num[0])

        for i in range(int(hints_num[0])):
            line = stdin.readline().split()
            hints[i] = (line[1], line[2], line[3])

        board = Board(rows, columns, hints)
        return board


class Bimaru(Problem):
    #The constructor specifies the initial state
    def __init__(self, board: Board):
        state = BimaruState(board)
        self.initial = state


    #Receives a state and return a list with possible actions that can be made
    def actions(self, state: BimaruState):

        actions_list = []
        
        if (state.board.valid_path == False):
            return []

        
        exact_actions = check_exact_boats(state.board)
        if (len(exact_actions) > 0):
            return exact_actions

        #Place a boat
        if (state.board.boats_4 < 1 or state.board.boats_3 < 2 or
        state.board.boats_2 < 3 or state.board.boats_1 < 4):
            for x in place_boat(state):
                actions_list.append(x)

        #Reevaluate hints actions list
        if (state.board.hints_actions_num > 0):
            state.board.hints_actions = check_hints_actions(state.board, state.board.hints)
        else:
            state.board.hints_actions = []

        for x in state.board.hints_actions:
            if (len(x) > 0):
                for k in x:
                    actions_list.append(k)

        return actions_list


    #Receives a state and an action and return the state after aplying the action
    def result(self, state: BimaruState, action):

        state_copy = copy.deepcopy(state)
        
        for a in action:
            #Filled lines go with -1 so they don't be selected again
            if (a == "boat_4"):
                state_copy.board.boats_4 += 1
            elif (a == "boat_3"):
                state_copy.board.boats_3 += 1
            elif (a == "boat_2"):
                state_copy.board.boats_2 += 1
            elif (a == "boat_1"):
                state_copy.board.boats_1 += 1
            elif (type(a) is tuple and a[0] == "hint"):
                state_copy.board.hints.remove(a[1])
                state_copy.board.hints_actions_num -= 1
                if (a[2] > 0):
                    circle_water(state_copy.board, int(a[1][0]), int(a[1][1]), a[2], a[3])
            else:
                state_copy.board[a[0]][a[1]] = a[2]
                state_copy.board.rows[a[0]] -= 1
                state_copy.board.columns[a[1]] -= 1
                if (state_copy.board.rows[a[0]] == 0):
                    fill_water(state_copy.board, a[0], "horizontal")
                if (state_copy.board.columns[a[1]] == 0):
                    fill_water(state_copy.board, a[1], "vertical")
                state_copy.board.empty_row_space[a[0]] -= 1
                state_copy.board.empty_column_space[a[1]] -= 1
                if (a[2] == 'c'):
                    circle_water(state_copy.board, a[0], a[1], 1, "horizontal")
                elif (a[2] == 't' and len(action) == 5):
                    circle_water(state_copy.board, a[0], a[1], 4, "vertical")
                elif (a[2] == 't' and len(action) == 4):
                    circle_water(state_copy.board, a[0], a[1], 3, "vertical")
                elif (a[2] == 't' and len(action) == 3):
                    circle_water(state_copy.board, a[0], a[1], 2, "vertical")
                elif (a[2] == 'l' and len(action) == 5):
                    circle_water(state_copy.board, a[0], a[1], 4, "horizontal")
                elif (a[2] == 'l' and len(action) == 4):
                    circle_water(state_copy.board, a[0], a[1], 3, "horizontal")
                elif (a[2] == 'l' and len(action) == 3):
                    circle_water(state_copy.board, a[0], a[1], 2, "horizontal")

        return BimaruState(state_copy.board)


    #Receives a state and checks if it is a solution for the problem
    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        
        for i in range(10):
            if (state.board.rows[i] > 0 or state.board.columns[i] > 0):
                return False
            
        if(state.board.boats_4 != 1 or
           state.board.boats_3 != 2 or
           state.board.boats_2 != 3 or
           state.board.boats_1 != 4):
            return False

        return True


#Check if in a row or column the spaces left are boats
def check_exact_boats(board: Board):

    size = 0
    actions = []

    for i in range(10):
        if (board.rows[i] != 0 and board.rows[i] == board.empty_row_space[i]):
            size = board.rows[i]
            for j in range(10):
                if (board[i][j] == None):
                    if (size >= 4 and can_place_boat(board, i, j, 4, "horizontal")):
                        actions.append(["boat_4", (i, j, 'l'), (i, j+1, 'm'), (i, j+2, 'm'), (i, j+3, 'r')])
                        return actions
                    elif(size >= 3 and can_place_boat(board, i, j, 3, "horizontal")):
                        actions.append(["boat_3", (i, j, 'l'), (i, j+1, 'm'), (i, j+2, 'r')])
                        return actions
                    elif(size >= 2 and can_place_boat(board, i, j, 2, "horizontal")):
                        actions.append(["boat_2", (i, j, 'l'), (i, j+1, 'r')])
                        return actions
                    elif(size >= 1 and can_place_boat(board, i, j, 1, "horizontal")):
                        if (can_place_boat(board, i, j, 4, "vertical")):
                            actions.append(["boat_4", (i, j, 't'), (i+1, j, 'm'), (i+2, j, 'm'), (i+3, j, 'b')])
                        if (can_place_boat(board, i, j, 3, "vertical")):
                            actions.append(["boat_3", (i, j, 't'), (i+1, j, 'm'), (i+2, j, 'b')])
                        if (can_place_boat(board, i, j, 2, "vertical")):
                            actions.append(["boat_2", (i, j, 't'), (i+1, j, 'b')])
                        if (can_place_boat(board, i-1, j, 4, "vertical")):
                            actions.append(["boat_4", (i-1, j, 't'), (i, j, 'm'), (i+1, j, 'm'), (i+2, j, 'b')])
                        if (can_place_boat(board, i-1, j, 3, "vertical")):
                            actions.append(["boat_3", (i-1, j, 't'), (i, j, 'm'), (i+1, j, 'b')])
                        if (can_place_boat(board, i-1, j, 2, "vertical")):
                            actions.append(["boat_2", (i-1, j, 't'), (i, j, 'b')])
                        if (can_place_boat(board, i-2, j, 4, "vertical")):
                            actions.append(["boat_4", (i-2, j, 't'), (i-1, j, 'm'), (i, j, 'm'), (i+1, j, 'b')])
                        if (can_place_boat(board, i-2, j, 3, "vertical")):
                            actions.append(["boat_3", (i-2, j, 't'), (i-1, j, 'm'), (i, j, 'b')])
                        if (can_place_boat(board, i-3, j, 4, "vertical")):
                            actions.append(["boat_4", (i-3, j, 't'), (i-2, j, 'm'), (i-1, j, 'm'), (i, j, 'b')])
                        actions.append(["boat_1", (i, j, 'c')])
                        return actions

        if (board.columns[i] != 0 and board.columns[i] == board.empty_column_space[i]):
            size = board.columns[i]
            for j in range(10):
                if (board[j][i] == None):
                    if (size >= 4 and can_place_boat(board, j, i, 4, "vertical")):
                        actions.append(["boat_4", (j, i, 't'), (j+1, i, 'm'), (j+2, i, 'm'), (j+3, i, 'b')])
                        return actions
                    elif (size >= 3 and can_place_boat(board, j, i, 3, "vertical")):
                        actions.append(["boat_3", (j, i, 't'), (j+1, i, 'm'), (j+2, i, 'b')])
                        return actions
                    elif (size >= 2 and can_place_boat(board, j, i, 2, "vertical")):
                        actions.append(["boat_2", (j, i, 't'), (j+1, i, 'b')])
                        return actions
                    elif (size >= 1 and can_place_boat(board, j, i, 1, "vertical")):
                        if (can_place_boat(board, j, i, 4, "horizontal")):
                            actions.append(["boat_4", (j, i, 'l'), (j, i+1, 'm'), (j, i+2, 'm'), (j, i+3, 'r')])
                        if (can_place_boat(board, j, i, 3, "horizontal")):
                            actions.append(["boat_3", (j, i, 'l'), (j, i+1, 'm'), (j, i+2, 'r')])
                        if (can_place_boat(board, j, i, 2, "horizontal")):
                            actions.append(["boat_2", (j, i, 'l'), (j, i+1, 'r')])
                        if (can_place_boat(board, j, i-1, 4, "horizontal")):
                            actions.append(["boat_4", (j, i-1, 'l'), (j, i, 'm'), (j, i+1, 'm'), (j, i+2, 'r')])
                        if (can_place_boat(board, j, i-1, 3, "horizontal")):
                            actions.append(["boat_3", (j, i-1, 'l'), (j, i, 'm'), (j, i+1, 'r')])
                        if (can_place_boat(board, j, i-1, 2, "horizontal")):
                            actions.append(["boat_2", (j, i-1, 'l'), (j, i, 'r')])
                        if (can_place_boat(board, j, i-2, 4, "horizontal")):
                            actions.append(["boat_4", (j, i-2, 'l'), (j, i-1, 'm'), (j, i, 'm'), (j, i+1, 'r')])
                        if (can_place_boat(board, j, i-2, 3, "horizontal")):
                            actions.append(["boat_3", (j, i-2, 'l'), (j, i-1, 'm'), (j, i, 'r')])
                        if (can_place_boat(board, j, i-3, 4, "horizontal")):
                            actions.append(["boat_4", (j, i-3, 'l'), (j, i-2, 'm'), (j, i-1, 'm'), (j, i, 'r')])
                        actions.append(["boat_1", (j, i, 'c')])
                        return actions

    return actions


#Find in the board a place to put a boat (starting with bigger ones)
def place_boat(state: BimaruState):
    
    action_list = []

    #Try to place the bigger boats first
    if (state.board.boats_4 < 1):
        for i in range(10):
            if (state.board.rows[i] >= 4):
                for j in range(7):
                        if (check_boat_position(state.board, i, j, 4, "horizontal")):
                            action_list.append(["boat_4", (i, j, 'l'), (i, j+1, 'm'), (i, j+2, 'm'), (i, j+3, 'r')])
            if (state.board.columns[i] >= 4):
                for j in range(7):
                        #Check there is no boat around the possible position
                        if (check_boat_position(state.board, j, i, 4, "vertical")):
                            action_list.append(["boat_4", (j, i, 't'), (j+1, i, 'm'), (j+2, i, 'm'), (j+3, i, 'b')])
    
    elif (state.board.boats_3 < 2):
        for i in range(10):
            if (state.board.rows[i] >= 3):
                for j in range(8):
                        if (check_boat_position(state.board, i, j, 3, "horizontal")):
                            action_list.append(["boat_3", (i, j, 'l'), (i, j+1, 'm'), (i, j+2, 'r')])
            if (state.board.columns[i] >= 3):
                for j in range(8):
                        #Check there is no boat around the possible position
                        if (check_boat_position(state.board, j, i, 3, "vertical")):
                            action_list.append(["boat_3", (j, i, 't'), (j+1, i, 'm'), (j+2, i, 'b')])
    
    elif (state.board.boats_2 < 3):
        for i in range(10):
            if (state.board.rows[i] >= 2):
                for j in range(9):
                        if (check_boat_position(state.board, i, j, 2, "horizontal")):
                            action_list.append(["boat_2", (i, j, 'l'), (i, j+1, 'r')])
            if (state.board.columns[i] >= 2):
                for j in range(9):
                        #Check there is no boat around the possible position
                        if (check_boat_position(state.board, j, i, 2, "vertical")):
                            action_list.append(["boat_2", (j, i, 't'), (j+1, i, 'b')])
    
    elif (state.board.boats_1 < 4):
        for i in range(10):
            if (state.board.rows[i] >= 1):
                for j in range(10):
                        if (check_boat_position(state.board, i, j, 1, "horizontal")):
                            action_list.append(["boat_1", (i, j, 'c')])

    return action_list
               

#Check if a possible boat position is empty
def check_boat_position(board: Board, row, column, size, direction):

    if (direction == 'horizontal'):
        for i in range(size):
            if (board[row][column+i] != None):
                return False
            if (board.columns[column+i] < 1):
                return False

    else:
        for i in range(size):
            if (board[row+i][column] != None):
                return False
            if (board.rows[row+i] < 1):
                return False

    return True


#Circle the given boat with water
def circle_water(board: Board, row, column, size, direction):

    x_cord = int(row)
    y_cord = int(column)

    if (direction == "horizontal"):
        if (is_valid_position(x_cord-1,y_cord-1)):
            if (board[x_cord-1][y_cord-1] != None and board[x_cord-1][y_cord-1] != 'w' and
                board[x_cord-1][y_cord-1] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord-1][y_cord-1] == None):
                board[x_cord-1][y_cord-1] = 'w'
                board.empty_row_space[x_cord-1] -= 1
                board.empty_column_space[y_cord-1] -= 1
        if (is_valid_position(x_cord,y_cord-1)):
            if (board[x_cord][y_cord-1] != None and board[x_cord][y_cord-1] != 'w' and
                board[x_cord][y_cord-1] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord][y_cord-1] == None):
                board[x_cord][y_cord-1] = 'w'
                board.empty_row_space[x_cord] -= 1
                board.empty_column_space[y_cord-1] -= 1
        if (is_valid_position(x_cord+1,y_cord-1)):
            if (board[x_cord+1][y_cord-1] != None and board[x_cord+1][y_cord-1] != 'w' and
                board[x_cord+1][y_cord-1] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord+1][y_cord-1] == None):
                board[x_cord+1][y_cord-1] = 'w'
                board.empty_row_space[x_cord+1] -= 1
                board.empty_column_space[y_cord-1] -= 1
        if (is_valid_position(x_cord-1,y_cord+size)):
            if (board[x_cord-1][y_cord+size] != None and board[x_cord-1][y_cord+size] != 'w' and
                board[x_cord-1][y_cord+size] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord-1][y_cord+size] == None):
                board[x_cord-1][y_cord+size] = 'w'
                board.empty_row_space[x_cord-1] -= 1
                board.empty_column_space[y_cord+size] -= 1
        if (is_valid_position(x_cord,y_cord+size)):
            if (board[x_cord][y_cord+size] != None and board[x_cord][y_cord+size] != 'w' and
                board[x_cord][y_cord+size] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord][y_cord+size] == None):
                board[x_cord][y_cord+size] = 'w'
                board.empty_row_space[x_cord] -= 1
                board.empty_column_space[y_cord+size] -= 1
        if (is_valid_position(x_cord+1,y_cord+size)):
            if (board[x_cord+1][y_cord+size] != None and board[x_cord+1][y_cord+size] != 'w' and
                board[x_cord+1][y_cord+size] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord+1][y_cord+size] == None):
                board[x_cord+1][y_cord+size] = 'w'
                board.empty_row_space[x_cord+1] -= 1
                board.empty_column_space[y_cord+size] -= 1
        for i in range(size):
            if (is_valid_position(x_cord-1,y_cord+i)):
                if (board[x_cord-1][y_cord+i] != None and board[x_cord-1][y_cord+i] != 'w' and
                board[x_cord-1][y_cord+i] != 'W'):
                    board.valid_path = False
                    return
                if(board[x_cord-1][y_cord+i] == None):
                    board[x_cord-1][y_cord+i] = 'w'
                    board.empty_row_space[x_cord-1] -= 1
                    board.empty_column_space[y_cord+i] -= 1
            if (is_valid_position(x_cord+1,y_cord+i)):
                if (board[x_cord+1][y_cord+i] != None and board[x_cord+1][y_cord+i] != 'w' and
                board[x_cord+1][y_cord+i] != 'W'):
                    board.valid_path = False
                    return
                if(board[x_cord+1][y_cord+i] == None):
                    board[x_cord+1][y_cord+i] = 'w'
                    board.empty_row_space[x_cord+1] -= 1
                    board.empty_column_space[y_cord+i] -= 1
    else:
        if (is_valid_position(x_cord-1,y_cord-1)):
            if (board[x_cord-1][y_cord-1] != None and board[x_cord-1][y_cord-1] != 'w' and
            board[x_cord-1][y_cord-1] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord-1][y_cord-1] == None):
                board[x_cord-1][y_cord-1] = 'w'
                board.empty_row_space[x_cord-1] -= 1
                board.empty_column_space[y_cord-1] -= 1
        if (is_valid_position(x_cord-1,y_cord)):
            if (board[x_cord-1][y_cord] != None and board[x_cord-1][y_cord] != 'w' and
            board[x_cord-1][y_cord] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord-1][y_cord] == None):
                board[x_cord-1][y_cord] = 'w'
                board.empty_row_space[x_cord-1] -= 1
                board.empty_column_space[y_cord] -= 1
        if (is_valid_position(x_cord-1,y_cord+1)):
            if (board[x_cord-1][y_cord+1] != None and board[x_cord-1][y_cord+1] != 'w' and
            board[x_cord-1][y_cord+1] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord-1][y_cord+1] == None):
                board[x_cord-1][y_cord+1] = 'w'
                board.empty_row_space[x_cord-1] -= 1
                board.empty_column_space[y_cord+1] -= 1
        if (is_valid_position(x_cord+size,y_cord-1)):
            if (board[x_cord+size][y_cord-1] != None and board[x_cord+size][y_cord-1] != 'w' and
            board[x_cord+size][y_cord-1] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord+size][y_cord-1] == None):
                board[x_cord+size][y_cord-1] = 'w'
                board.empty_row_space[x_cord+size] -= 1
                board.empty_column_space[y_cord-1] -= 1
        if (is_valid_position(x_cord+size,y_cord)):
            if (board[x_cord+size][y_cord] != None and board[x_cord+size][y_cord] != 'w' and
            board[x_cord+size][y_cord] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord+size][y_cord] == None):
                board[x_cord+size][y_cord] = 'w'
                board.empty_row_space[x_cord+size] -= 1
                board.empty_column_space[y_cord] -= 1
        if (is_valid_position(x_cord+size,y_cord+1)):
            if (board[x_cord+size][y_cord+1] != None and board[x_cord+size][y_cord+1] != 'w' and
            board[x_cord+size][y_cord+1] != 'W'):
                board.valid_path = False
                return
            if(board[x_cord+size][y_cord+1] == None): 
                board[x_cord+size][y_cord+1] = 'w'
                board.empty_row_space[x_cord+size] -= 1
                board.empty_column_space[y_cord+1] -= 1
        for i in range(size):
            if (is_valid_position(x_cord+i,y_cord-1)):
                if (board[x_cord+i][y_cord-1] != None and board[x_cord+i][y_cord-1] != 'w' and
                board[x_cord+i][y_cord-1] != 'W'):
                    board.valid_path = False
                    return
                if(board[x_cord+i][y_cord-1] == None): 
                    board[x_cord+i][y_cord-1] = 'w'
                    board.empty_row_space[x_cord+i] -= 1
                    board.empty_column_space[y_cord-1] -= 1
            if (is_valid_position(x_cord+i,y_cord+1)):
                if (board[x_cord+i][y_cord+1] != None and board[x_cord+i][y_cord+1] != 'w' and
                board[x_cord+i][y_cord+1] != 'W'):
                    board.valid_path = False
                    return
                if(board[x_cord+i][y_cord+1] == None):
                    board[x_cord+i][y_cord+1] = 'w'
                    board.empty_row_space[x_cord+i] -= 1
                    board.empty_column_space[y_cord+1] -= 1


#Fills a row or column with water
def fill_water(board: Board, value, direction):

    if (direction == "horizontal"):
        for i in range(10):
            if (board[value][i] == None):
                board[value][i] = 'w'
                board.empty_row_space[value] -= 1
                board.empty_column_space[i] -= 1

    else:
        for i in range(10):
            if (board[i][value] == None):
                board[i][value] = 'w'
                board.empty_row_space[i] -= 1
                board.empty_column_space[value] -= 1


#Check if in hints list is a completed boat
def check_completed_boats(board: Board, hints: list):
    for x in hints:
        x_cord = int(x[0])
        y_cord = int(x[1])
        board[x_cord][y_cord] = None
        board.rows[x_cord] += 1
        board.columns[y_cord] += 1
        if (x[2] == 'T'):
            pos_x = str(x_cord)
            pos_y = str(y_cord)
        
            if(is_valid_position(x_cord+1, y_cord) and board[x_cord+1][y_cord] == 'M' and 
            is_valid_position(x_cord+2, y_cord) and board[x_cord+2][y_cord] == 'M' and 
            is_valid_position(x_cord+3, y_cord) and board[x_cord+3][y_cord] == 'B'):
                board.hints_actions_num -= 4
                pos_x1 = str(x_cord + 1)
                pos_x2 = str(x_cord + 2)
                pos_x3 = str(x_cord + 3)
                
                board.hints.remove((pos_x, pos_y, 'T'))
                board.hints.remove((pos_x1, pos_y, 'M'))
                board.hints.remove((pos_x2, pos_y, 'M'))
                board.hints.remove((pos_x3, pos_y, 'B'))
                
                board.boats_4 += 1
            if(is_valid_position(x_cord+1, y_cord) and board[x_cord+1][y_cord] == 'M' and
            is_valid_position(x_cord+2, y_cord) and board[x_cord+2][y_cord] == 'B'):
                board.hints_actions_num -= 3
                pos_x1 = str(x_cord + 1)
                pos_x2 = str(x_cord + 2)
                
                board.hints.remove((pos_x, pos_y, 'T'))
                board.hints.remove((pos_x1, pos_y, 'M'))
                board.hints.remove((pos_x2, pos_y, 'B'))
                
                board.boats_3 += 1
            if(is_valid_position(x_cord+1, y_cord) and board[x_cord+1][y_cord] == 'B'):
                board.hints_actions_num -= 2

                pos_x1 = str(x_cord + 1)
                
                board.hints.remove((pos_x, pos_y, 'T'))
                board.hints.remove((pos_x1, pos_y, 'B'))
                
                board.boats_2 += 1
        
        if (x[2] == 'L'):
            pos_x = str(x_cord)
            pos_y = str(y_cord)
        
            if(is_valid_position(x_cord, y_cord+1) and board[x_cord][y_cord+1] == 'M' and
            is_valid_position(x_cord, y_cord+2) and board[x_cord][y_cord+2] == 'M' and
            is_valid_position(x_cord, y_cord+3) and board[x_cord][y_cord+3] == 'R'):
                board.hints_actions_num -= 4
                pos_y1 = str(y_cord + 1)
                pos_y2 = str(y_cord + 2)
                pos_y3 = str(y_cord + 3)
                
                board.hints.remove((pos_x, pos_y, 'L'))
                board.hints.remove((pos_x, pos_y1, 'M'))
                board.hints.remove((pos_x, pos_y2, 'M'))
                board.hints.remove((pos_x, pos_y3, 'R'))
                
                board.boats_4 += 1
            if(is_valid_position(x_cord, y_cord+1) and board[x_cord][y_cord+1] == 'M' and
            is_valid_position(x_cord, y_cord+2) and board[x_cord][y_cord+2] == 'R'):
                board.hints_actions_num -= 3
                pos_y1 = str(y_cord + 1)
                pos_y2 = str(y_cord + 2)
                
                board.hints.remove((pos_x, pos_y, 'L'))
                board.hints.remove((pos_x, pos_y1, 'M'))
                board.hints.remove((pos_x, pos_y2, 'R'))
                
                board.boats_3 += 1
            if(is_valid_position(x_cord, y_cord+1) and board[x_cord][y_cord+1] == 'R'):
                board.hints_actions_num -= 2
                pos_y1 = str(y_cord + 1)
                
                board.hints.remove((pos_x, pos_y, 'L'))
                board.hints.remove((pos_x, pos_y1, 'R'))
                
                board.boats_2 += 1

        board[x_cord][y_cord] = x[2]
        board.rows[x_cord] -= 1
        board.columns[y_cord] -= 1
    return 0


#Check what actions can be made from the given hints
def check_hints_actions(board: Board, hints: list):

    hints_action = [[] for i in range(board.hints_actions_num)]
    hints_counter = 0

    for x in hints:
        x_cord = int(x[0])
        y_cord = int(x[1])
        board[x_cord][y_cord] = None
        board.rows[x_cord] += 1
        board.columns[y_cord] += 1
        if (x[2] == 'T'):
            if (is_valid_position(x_cord+2, y_cord) and board[x_cord + 2][y_cord] == 'B'):
                x_cord_str = str(x_cord+2)
                y_cord_str = str(y_cord)
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 3, "vertical"),
                ("hint", (x_cord_str, y_cord_str, 'B'), 0, ""), "boat_3",
                (x_cord+1, y_cord, 'm')])
            if (is_valid_position(x_cord+3, y_cord) and board[x_cord + 3][y_cord] == 'B'):
                x_cord_str = str(x_cord+3)
                y_cord_str = str(y_cord)
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 4, "vertical"),
                ("hint", (x_cord_str, y_cord_str, 'B'), 0, ""), "boat_4",
                (x_cord+1, y_cord, 'm'), (x_cord+2, y_cord, 'm')])
            if (can_place_boat(board, x_cord, y_cord, 2, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 2, "vertical"), "boat_2",
                (x_cord+1, y_cord, 'b')])
            if (can_place_boat(board, x_cord, y_cord, 3, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 3, "vertical"), "boat_3",
                (x_cord+1, y_cord, 'm'), (x_cord+2, y_cord, 'b')])
            if (can_place_boat(board, x_cord, y_cord, 4, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 4, "vertical"), "boat_4",
                (x_cord+1, y_cord, 'm'), (x_cord+2, y_cord, 'm'), (x_cord+3, y_cord, 'b')])
            hints_counter += 1

        elif (x[2] == 'B'):
            if (can_place_boat(board, x_cord-1, y_cord, 2, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_2",
                (x_cord-1, y_cord, 't')])
            if (can_place_boat(board, x_cord-2, y_cord, 3, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_3",
                (x_cord-1, y_cord, 'm'), (x_cord-2, y_cord, 't')])
            if (can_place_boat(board, x_cord-3, y_cord, 4, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_4",
                (x_cord-1, y_cord, 'm'),  (x_cord-2, y_cord, 'm'), (x_cord-3, y_cord, 't')])
            hints_counter += 1

        elif (x[2] == 'L'):
            if (is_valid_position(x_cord, y_cord+2) and board[x_cord][y_cord + 2] == 'R'):
                x_cord_str = str(x_cord)
                y_cord_str = str(y_cord+2)
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 3, "horizontal"),
                ("hint", (x_cord_str, y_cord_str, 'R'), 0, ""), "boat_3",
                (x_cord, y_cord+1, 'm')])
            if (is_valid_position(x_cord, y_cord+3) and board[x_cord][y_cord + 3] == 'R'):
                x_cord_str = str(x_cord)
                y_cord_str = str(y_cord+3)
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 4, "horizontal"),
                ("hint", (x_cord_str, y_cord_str, 'R'), 0, ""), "boat_4",
                (x_cord, y_cord+1, 'm'), (x_cord, y_cord+2, 'm')])
            if (can_place_boat(board, x_cord, y_cord, 2, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 2, "horizontal"), "boat_2",
                (x_cord, y_cord+1, 'r')])
            if (can_place_boat(board, x_cord, y_cord, 3, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 3, "horizontal"), "boat_3",
                (x_cord, y_cord+1, 'm'), (x_cord, y_cord+2, 'r')])
            if (can_place_boat(board, x_cord, y_cord, 4, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 4, "horizontal"), "boat_4",
                (x_cord, y_cord+1, 'm'), (x_cord, y_cord+2, 'm'), (x_cord, y_cord+3, 'r')])
            hints_counter += 1

        elif (x[2] == 'R'):
            if (can_place_boat(board, x_cord, y_cord-1, 2, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_2",
                (x_cord, y_cord-1, 'l')])
            if (can_place_boat(board, x_cord, y_cord-2, 3, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_3",
                (x_cord, y_cord-1, 'm'), (x_cord, y_cord-2, 'l')])
            if (can_place_boat(board, x_cord, y_cord-3, 4, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_4",
                (x_cord, y_cord-1, 'm'), (x_cord, y_cord-2, 'm'), (x_cord, y_cord-3, 'l')])
            hints_counter += 1

        elif (x[2] == 'M'):
            if (can_place_boat(board, x_cord-1, y_cord, 3, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_3",
                (x_cord-1, y_cord, 't'), (x_cord+1, y_cord, 'b')])
            if (can_place_boat(board, x_cord-2, y_cord, 4, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_4",
                (x_cord-2, y_cord, 't'),  (x_cord-1, y_cord, 'm'), (x_cord+1, y_cord, 'b')])
            if (can_place_boat(board, x_cord-1, y_cord, 4, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_4",
                (x_cord-1, y_cord, 't'),  (x_cord+1, y_cord, 'm'), (x_cord+2, y_cord, 'b')])
            if (can_place_boat(board, x_cord, y_cord-1, 3, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_3",
                (x_cord, y_cord-1, 'l'), (x_cord, y_cord+1, 'r')])
            if (can_place_boat(board, x_cord, y_cord-2, 4, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_4",
                (x_cord, y_cord-2, 'l'), (x_cord, y_cord-1, 'm'), (x_cord, y_cord+1, 'r')])
            if (can_place_boat(board, x_cord, y_cord-1, 4, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2]), 0, ""), "boat_4",
                (x_cord, y_cord-1, 'l'), (x_cord, y_cord+1, 'm'), (x_cord, y_cord+2, 'r')])
            hints_counter += 1

        board[x_cord][y_cord] = x[2]
        board.rows[x_cord] -= 1
        board.columns[y_cord] -= 1

    return hints_action


#Check if the position is in the board
def is_valid_position(row, column):
        if (row >= 0 and row <= 9 and column >= 0 and column <= 9):
            return True
        else:
            return False


#Check if the given boat is possible to place
def can_place_boat(board, row, column, size, direction):

    if (is_valid_position(row, column) == False):
        return False

    if (size == 4 and board.boats_4 >= 1):
        return False
    if (size == 3 and board.boats_3 >= 2):
        return False
    if (size == 2 and board.boats_2 >= 3):
        return False
    if (size == 1 and board.boats_1 >= 4):
        return False

    if (direction == "horizontal"):
        for i in range(size):
            if (is_valid_position(row, column + i) == False):
                return False
            if (board[row][column + i] != None):
                return False
            if (board.columns[column + i] < 1):
                return False
        if (board.rows[row] < size):
            return False
        if (is_empty_space(board, row - 1, column - 1) == False or 
            is_empty_space(board, row, column - 1) == False or
            is_empty_space(board, row + 1, column - 1) == False or 
            is_empty_space(board, row - 1, column + size) == False or
            is_empty_space(board, row, column + size) == False or 
            is_empty_space(board, row + 1, column + size) == False):
                return False
        if (size == 4 or size == 3 or size == 2 or size == 1):
            i=0
            while (i<size):
                if (is_empty_space(board, row-1, column+i) == False or
                    is_empty_space(board, row+1, column+i) == False):
                    return False
                i += 1
    else:
        for i in range(size):
            if (is_valid_position(row + i, column) == False):
                return False
            if (board[row + i][column] != None):
                return False
            if (board.rows[row + i] < 1):
                return False
        if (board.columns[column] < size):
            return False
        if (is_empty_space(board, row - 1, column - 1) == False or 
            is_empty_space(board, row -1, column) == False or
            is_empty_space(board, row - 1, column + 1) == False or 
            is_empty_space(board, row + size, column - 1) == False or
            is_empty_space(board, row + size, column) == False or 
            is_empty_space(board, row + size, column + 1) == False):
                return False
        if (size == 4  or size == 3 or size == 2 or size == 1):
            for i in range(size):
                if (is_empty_space(board, row + i, column - 1) == False or
                    is_empty_space(board, row + i, column + 1) == False):
                    return False

    return True


#Check if the given position isn't occupied by another boat
def is_empty_space(board, row, column):
        if (row >= 0 and row <= 9 and column >= 0 and column <= 9):
            if (board.get_value(row, column) == 'W' or
            board.get_value(row, column) == 'w' or
            board.get_value(row, column) == None):
                return True
            else:
                return False
        else:
            return True

if __name__ == "__main__":

    board = Board.parse_instance()

    # Criar uma instância de Bimaru:
    problem = Bimaru(board)

    goal = depth_first_tree_search(problem)
    if (goal == None):
        print(goal)
    else:
        goal.state.board.print()
    
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    pass
