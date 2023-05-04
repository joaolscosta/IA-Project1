# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

import sys
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

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

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
    board.print_board()

    print(board.adjacent_vertical_values(3, 3))
    print(board.adjacent_horizontal_values(3, 3))

    print(board.adjacent_vertical_values(1, 0))
    print(board.adjacent_horizontal_values(1, 0))

    print(board.get_value(0,0))

    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    pass
