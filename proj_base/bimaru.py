# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

import sys, random, copy
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
    """Representação interna de um tabuleiro de Bimaru."""
    def __init__(self, rows, columns, hints):
        
        self.rows = rows
        self.columns = columns
        self.board = [[None for j in range(len(rows))] for i in range(len(columns))]
        
        """Aplicar pistas dadas"""
        for i in range(len(hints)):
            x_cord = int(hints[i][0])
            y_cord = int(hints[i][1])
            self.board[x_cord][y_cord] = hints[i][2]


    def print_board(self):
        """Mostra o estado atual do tabuleiro."""

        for i in range(len(self.rows)):
            for j in range(len(self.columns)):
                if (self.board[i][j] == None):
                    print('.', end="")
                else:    
                    print(self.board[i][j], end="")
            print('\n')
            

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        
        return self.board[row][col]

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
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        # TODO
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass

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
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:

    #Exemplo 1:
    board = Board.parse_instance()
    # Criar uma instância de Bimaru:
    problem = Bimaru(board)

    sr = breadth_first_tree_search(problem)
    print(sr)

    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    pass
