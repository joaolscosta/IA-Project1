# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 123:
# 103603 Pedro Tavares
# 102078 João Costa

import sys, copy
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

    # TODO: outros metodos da classe


class Board:
    #Internal representation of a Bimaru board
    def __init__(self, rows, columns, hints):
        
        self.rows = rows
        self.columns = columns
        self.rows.pop(0)
        self.columns.pop(0)
        self.hints = []
        self.board = [[None for j in range(len(rows))] for i in range(len(columns))]
        self.boats_4 = 0
        self.boats_3 = 0
        self.boats_2 = 0
        self.boats_1 = 0
        self.hints_actions_num = 0

        for i in range(10):
            self.rows[i] = int(self.rows[i])
            self.columns[i] = int(self.columns[i])

        #Place hints in board
        for i in range(len(hints)):
            x_cord = int(hints[i][0])
            y_cord = int(hints[i][1])
            self.board[x_cord][y_cord] = hints[i][2]
            if (hints[i][2] == 'C'):
                circle_water(self, hints[i][0], hints[i][1])
                self.rows[x_cord] = int(self.rows[x_cord]) - 1
                self.columns[y_cord] = int(self.columns[y_cord]) - 1
                self.boats_1 += 1

            elif (self.board[x_cord][y_cord] == 'T' or
            self.board[x_cord][y_cord] == 'M' or self.board[x_cord][y_cord] == 'B' or
            self.board[x_cord][y_cord] == 'R' or self.board[x_cord][y_cord] == 'L'):
                self.rows[x_cord] = int(self.rows[x_cord]) - 1
                self.columns[y_cord] = int(self.columns[y_cord]) - 1
                self.hints_actions_num += 1
                self.hints.append((hints[i][0], hints[i][1], hints[i][2]))
        
        check_completed_boats(self, self.hints)
        self.hints_actions = check_hints_actions(self, self.hints)
            

    #Prints the board
    def print(self):
        """Mostra o estado atual do tabuleiro."""

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

    # TODO: outros metodos da classe


class Bimaru(Problem):
    #The constructor specifies the initial state
    def __init__(self, board: Board):
        state = BimaruState(board)
        self.initial = state


    #Receives a state and return a list with possible actions that can be made
    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        actions_list = []
        
        #fill rows or columns already completed
        for i in range(10):
            if (state.board.rows[i] == 0 or state.board.columns[i] == 0):
                actions_list.append(fill_water(state))
                break
        
        #Place a boat
        if (state.board.boats_4 < 1 or state.board.boats_3 < 2 or
        state.board.boats_2 < 3 or state.board.boats_1 < 4):
            for x in place_boat(state):
                actions_list.append(x)

        #Reevaluate hints actions list
        state.board.hints_actions = check_hints_actions(state.board, state.board.hints)

        for x in state.board.hints_actions:
            if (len(x) > 0):
                for k in x:
                    actions_list.append(k)

        return actions_list


    #Receives a state and an action and return the state after aplying the action
    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        
        aux = copy.deepcopy(state)
        
        for a in action:
            #Filled lines go with -1 so they don't be selected again
            if (type(a) is list):
                for i in range(len(a[0])):
                    aux.board.rows[a[0][i]] = -1
                for i in range(len(a[1])):
                    aux.board.columns[a[1][i]] = -1
            elif (a == "boat_4"):
                aux.board.boats_4 += 1
            elif (a == "boat_3"):
                aux.board.boats_3 += 1
            elif (a == "boat_2"):
                aux.board.boats_2 += 1
            elif (a == "boat_1"):
                aux.board.boats_1 += 1
            elif (type(a) is tuple and a[0] == "hint"):
                aux.board.hints.remove(a[1])
                aux.board.hints_actions_num -= 1
            else:
                aux.board[a[0]][a[1]] = a[2]
                if (a[2] == 't' or a[2] == 'm' or a[2] == 'b' or
                a[2] == 'r' or a[2] == 'l' or a[2] == 'c'):
                    aux.board.rows[a[0]] -= 1
                    aux.board.columns[a[1]] -= 1

        return BimaruState(aux.board)


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
        

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass


#Find completed rows and columns , and fill empty spaces with water 
def fill_water(state: BimaruState):
    
    fill_list = []
    aux_list = [[], []]

    for i in range(10):
        if (state.board.rows[i] == 0):
            aux_list[0].append(i)
            for j in range(10):
                if (state.board[i][j] == None):
                    fill_list.append((i, j, 'w'))
    
    for i in range(10):
        if (state.board.columns[i] == 0):
            aux_list[1].append(i)
            for j in range(10):
                if (state.board[j][i] == None):
                    fill_list.append((j, i, 'w'))

    fill_list.append(aux_list)
    return fill_list


#Find in the board a place to put a boat (starting with bigger ones)
def place_boat(state: BimaruState):
    
    action_list =[]

    #Try to place the bigger boats first
    if (state.board.boats_4 < 1):
        for i in range(10):
            if (state.board.rows[i] >= 4):
                for j in range(7):
                        if (can_place_boat(state.board, i, j, 4, "horizontal")):
                            action_list.append(["boat_4", (i, j, 'l'), (i, j+1, 'm'), (i, j+2, 'm'), (i, j+3, 'r')])
            if (state.board.columns[i] >= 4):
                for j in range(7):
                        #Check there is no boat around the possible position
                        if (can_place_boat(state.board, j, i, 4, "vertical")):
                            action_list.append(["boat_4", (j, i, 't'), (j+1, i, 'm'), (j+2, i, 'm'), (j+3, i, 'b')])
    
    elif (state.board.boats_3 < 2):
        for i in range(10):
            if (state.board.rows[i] >= 3):
                for j in range(8):
                        if (can_place_boat(state.board, i, j, 3, "horizontal")):
                            action_list.append(["boat_3", (i, j, 'l'), (i, j+1, 'm'), (i, j+2, 'r')])
            if (state.board.columns[i] >= 3):
                for j in range(8):
                        #Check there is no boat around the possible position
                        if (can_place_boat(state.board, j, i, 3, "vertical")):
                            action_list.append(["boat_3", (j, i, 't'), (j+1, i, 'm'), (j+2, i, 'b')])
    
    elif (state.board.boats_2 < 3):
        for i in range(10):
            if (state.board.rows[i] >= 2):
                for j in range(9):
                        if (can_place_boat(state.board, i, j, 2, "horizontal")):
                            action_list.append(["boat_2", (i, j, 'l'), (i, j+1, 'r')])
            if (state.board.columns[i] >= 2):
                for j in range(9):
                        #Check there is no boat around the possible position
                        if (can_place_boat(state.board, j, i, 2, "vertical")):
                            action_list.append(["boat_2", (j, i, 't'), (j+1, i, 'b')])
    
    elif (state.board.boats_1 < 4):
        for i in range(10):
            if (state.board.rows[i] >= 1):
                for j in range(10):
                        if (can_place_boat(state.board, i, j, 1, "horizontal")):
                            action_list.append(["boat_1", (i, j, 'c')])

    return action_list


#Circle the given boat with water
def circle_water(board: Board, row, column):

    x_cord = int(row)
    y_cord = int(column)
    
    if (is_valid_position(x_cord-1,y_cord-1)):
        board[x_cord-1][y_cord-1] = 'w'
    if (is_valid_position(x_cord-1,y_cord)):
        board[x_cord-1][y_cord] = 'w'
    if (is_valid_position(x_cord-1,y_cord+1)):
        board[x_cord-1][y_cord+1] = 'w'
    if (is_valid_position(x_cord,y_cord-1)):
        board[x_cord][y_cord-1] = 'w'
    if (is_valid_position(x_cord,y_cord+1)):
        board[x_cord][y_cord+1] = 'w'
    if (is_valid_position(x_cord+1,y_cord-1)):
        board[x_cord+1][y_cord-1] = 'w'
    if (is_valid_position(x_cord+1,y_cord)):
        board[x_cord+1][y_cord] = 'w'
    if (is_valid_position(x_cord+1,y_cord+1)):
        board[x_cord+1][y_cord+1] = 'w'


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
        
            if(board[x_cord+1][y_cord] == 'M' and board[x_cord+2][y_cord] == 'M' and board[x_cord+3][y_cord] == 'B'):
                board.hints_actions_num -= 4
                pos_x1 = str(x_cord + 1)
                pos_x2 = str(x_cord + 2)
                pos_x3 = str(x_cord + 3)
                
                board.hints.remove((pos_x, pos_y, 'T'))
                board.hints.remove((pos_x1, pos_y, 'M'))
                board.hints.remove((pos_x2, pos_y, 'M'))
                board.hints.remove((pos_x3, pos_y, 'B'))
                
                board.boats_4 += 1
            if(board[x_cord+1][y_cord] == 'M' and board[x_cord+2][y_cord] == 'B'):
                board.hints_actions_num -= 3
                pos_x1 = str(x_cord + 1)
                pos_x2 = str(x_cord + 2)
                
                board.hints.remove((pos_x, pos_y, 'T'))
                board.hints.remove((pos_x1, pos_y, 'M'))
                board.hints.remove((pos_x2, pos_y, 'B'))
                
                board.boats_3 += 1
            if(board[x_cord+1][y_cord] == 'B'):
                board.hints_actions_num -= 2

                pos_x1 = str(x_cord + 1)
                
                board.hints.remove((pos_x, pos_y, 'T'))
                board.hints.remove((pos_x1, pos_y, 'B'))
                
                board.boats_2 += 1
        
        if (x[2] == 'L'):
            pos_x = str(x_cord)
            pos_y = str(y_cord)
        
            if(board[x_cord][y_cord+1] == 'M' and board[x_cord][y_cord+2] == 'M' and board[x_cord][y_cord+3] == 'R'):
                board.hints_actions_num -= 4
                pos_y1 = str(y_cord + 1)
                pos_y2 = str(y_cord + 2)
                pos_y3 = str(y_cord + 3)
                
                board.hints.remove((pos_x, pos_y, 'L'))
                board.hints.remove((pos_x, pos_y1, 'M'))
                board.hints.remove((pos_x, pos_y2, 'M'))
                board.hints.remove((pos_x, pos_y3, 'R'))
                
                board.boats_4 += 1
            if(board[x_cord][y_cord+1] == 'M' and board[x_cord][y_cord+2] == 'R'):
                board.hints_actions_num -= 3
                pos_y1 = str(y_cord + 1)
                pos_y2 = str(y_cord + 2)
                
                board.hints.remove((pos_x, pos_y, 'L'))
                board.hints.remove((pos_x, pos_y1, 'M'))
                board.hints.remove((pos_x, pos_y2, 'R'))
                
                board.boats_3 += 1
            if(board[x_cord][y_cord+1] == 'R'):
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
    
    if (board.hints_actions_num <= 0):
        return []

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
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])),
                ("hint", (x_cord_str, y_cord_str, 'B')), "boat_3",
                (x_cord+1, y_cord, 'm')])
            if (is_valid_position(x_cord+3, y_cord) and board[x_cord + 3][y_cord] == 'B'):
                x_cord_str = str(x_cord+3)
                y_cord_str = str(y_cord)
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])),
                ("hint", (x_cord_str, y_cord_str, 'B')), "boat_4",
                (x_cord+1, y_cord, 'm'), (x_cord+2, y_cord, 'm')])
            if (can_place_boat(board, x_cord, y_cord, 2, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_2",
                (x_cord+1, y_cord, 'b')])
            if (can_place_boat(board, x_cord, y_cord, 3, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_3",
                (x_cord+1, y_cord, 'm'), (x_cord+2, y_cord, 'b')])
            if (can_place_boat(board, x_cord, y_cord, 4, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_4",
                (x_cord+1, y_cord, 'm'), (x_cord+2, y_cord, 'm'), (x_cord+3, y_cord, 'b')])
            hints_counter += 1

        elif (x[2] == 'B'):
            if (can_place_boat(board, x_cord-1, y_cord, 2, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_2",
                (x_cord-1, y_cord, 't')])
            if (can_place_boat(board, x_cord-2, y_cord, 3, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_3",
                (x_cord-1, y_cord, 'm'), (x_cord-2, y_cord, 't')])
            if (can_place_boat(board, x_cord-3, y_cord, 4, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_4",
                (x_cord-1, y_cord, 'm'),  (x_cord-2, y_cord, 'm'), (x_cord-3, y_cord, 't')])
            hints_counter += 1

        elif (x[2] == 'L'):
            if (is_valid_position(x_cord, y_cord+2) and board[x_cord][y_cord + 2] == 'R'):
                x_cord_str = str(x_cord)
                y_cord_str = str(y_cord+2)
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])),
                ("hint", (x_cord_str, y_cord_str, 'R')), "boat_3",
                (x_cord, y_cord+1, 'm')])
            if (is_valid_position(x_cord, y_cord+3) and board[x_cord][y_cord + 3] == 'R'):
                x_cord_str = str(x_cord)
                y_cord_str = str(y_cord+3)
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])),
                ("hint", (x_cord_str, y_cord_str, 'R')), "boat_4",
                (x_cord, y_cord+1, 'm'), (x_cord, y_cord+2, 'm')])
            if (can_place_boat(board, x_cord, y_cord, 2, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_2",
                (x_cord, y_cord+1, 'r')])
            if (can_place_boat(board, x_cord, y_cord, 3, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_3",
                (x_cord, y_cord+1, 'm'), (x_cord, y_cord+2, 'r')])
            if (can_place_boat(board, x_cord, y_cord, 4, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_4",
                (x_cord, y_cord+1, 'm'), (x_cord, y_cord+2, 'm'), (x_cord, y_cord+3, 'r')])
            hints_counter += 1

        elif (x[2] == 'R'):
            if (can_place_boat(board, x_cord, y_cord-1, 2, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_2",
                (x_cord, y_cord-1, 'l')])
            if (can_place_boat(board, x_cord, y_cord-2, 3, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_3",
                (x_cord, y_cord-1, 'm'), (x_cord, y_cord-2, 'l')])
            if (can_place_boat(board, x_cord, y_cord-3, 4, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_4",
                (x_cord, y_cord-1, 'm'), (x_cord, y_cord-2, 'm'), (x_cord, y_cord-3, 'l')])
            hints_counter += 1

        elif (x[2] == 'M'):
            if (can_place_boat(board, x_cord-1, y_cord, 3, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_3",
                (x_cord-1, y_cord, 't'), (x_cord+1, y_cord, 'b')])
            if (can_place_boat(board, x_cord-2, y_cord, 4, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_4",
                (x_cord-2, y_cord, 't'),  (x_cord-1, y_cord, 'm'), (x_cord+1, y_cord, 'b')])
            if (can_place_boat(board, x_cord-1, y_cord, 4, "vertical")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_4",
                (x_cord-1, y_cord, 't'),  (x_cord+1, y_cord, 'm'), (x_cord+2, y_cord, 'b')])
            if (can_place_boat(board, x_cord, y_cord-1, 3, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_3",
                (x_cord, y_cord-1, 'l'), (x_cord, y_cord+1, 'r')])
            if (can_place_boat(board, x_cord, y_cord-2, 4, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_4",
                (x_cord, y_cord-2, 'l'), (x_cord, y_cord-1, 'm'), (x_cord, y_cord+1, 'r')])
            if (can_place_boat(board, x_cord, y_cord-1, 4, "horizontal")):
                hints_action[hints_counter].append([("hint", (x[0], x[1], x[2])), "boat_4",
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
    # TODO:

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
