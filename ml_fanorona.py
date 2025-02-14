import math

def get_move_from_bitboards(b1, b2):
    # Trouver la différence entre les deux bitboards
    diff = b1 ^ b2
    
    # Initialiser les variables pour stocker les indices
    start_index = None
    end_index = None
    
    # Trouver les indices de départ et d'arrivée
    for i in range(9):
        if (diff >> i) & 1:
            if (b1 >> i) & 1:
                start_index = i
            else:
                end_index = i
    
    # Convertir les indices en coordonnées (row, col)
    start_row, start_col = divmod(start_index, 3)
    end_row, end_col = divmod(end_index, 3)
    
    return (start_row, start_col), (end_row, end_col)

class Node:
    def __init__(self, bitboards_player1=0, bitboards_player2=0, turn=1, use_alpha_beta=False):
        """
        Initialise l'état du jeu avec deux bitboards pour chaque joueur.
        - bitboards_player1 : bitboard du joueur 1
        - bitboards_player2 : bitboard du joueur 2
        - turn : 1 pour joueur 1, -1 pour joueur 2
        """
        self.bitboards_player1 = bitboards_player1  # Bitboard du joueur 1
        self.bitboards_player2 = bitboards_player2  # Bitboard du joueur 2
        self.turn = turn  # 1 pour Joueur 1, -1 pour Joueur 2
        self.use_alpha_beta = use_alpha_beta
        self.node_count = 0  # Compteur de nœuds visités

    def display_board(self):
        """Affiche le plateau de jeu en console."""

        board = ['.'] * 9  # 3x3 grid
        for i in range(9):
            if (self.bitboards_player1 >> i) & 1:
                board[i] = 'X'
            elif (self.bitboards_player2 >> i) & 1:
                board[i] = 'O'
        
        print("\n".join([" ".join(board[i:i+3]) for i in range(0, 9, 3)]))
    

    def get_successors(self):
        """
        Génère toutes les configurations possibles en déplaçant une pièce.
        Retourne une liste des nouveaux états possibles.
        """
        successors = []
        current_board = self.bitboards_player1 if self.turn == 1 else self.bitboards_player2
        opponent_board = self.bitboards_player2 if self.turn == 1 else self.bitboards_player1

        # Déplacements possibles sur un plateau 3x3 avec diagonales
        # Les directions doivent être ajustées pour éviter les sauts et les mouvements incorrects
        directions = {
            0: [1, 4, 3],   # Top-left corner
            1: [1, 3, -1],  # Top edge
            2: [3, 2, -1],  # Top-right corner
            3: [-3, 1, 3],  # Left edge
            4: [-3, -2, 1, 4, 3, 2, -1, -4],  # Center
            5: [-3, 3, -1], # Right edge
            6: [-3, -2, 1], # Bottom-left corner
            7: [-3, -1, 1], # Bottom edge
            8: [-3, -1, -4] # Bottom-right corner
        }

        for i in range(9):
            if (current_board >> i) & 1:  # Vérifie si le joueur a une pièce ici
                for d in directions[i]:
                    new_pos = i + d
                    if 0 <= new_pos < 9 and not ((current_board | opponent_board) >> new_pos) & 1:
                        # Crée le nouveau plateau en déplaçant la pièce
                        new_board = current_board & ~(1 << i) | (1 << new_pos)
                        if self.turn == 1:
                            successors.append(Node(new_board, self.bitboards_player2, -self.turn))
                        else:
                            successors.append(Node(self.bitboards_player1, new_board, -self.turn))
        return successors

    def print_board_successor(self, successors):
        """Affiche tous les états possibles après un coup."""
        print(f"Nombre de coups possibles: {len(successors)}")
        for idx, state in enumerate(successors):
            print(f"\nSuccesseur {idx + 1}:")
            state.display_board()
    
    def check_winner(self):
        """Vérifie si un joueur a gagné en alignant trois pièces et retourne le gagnant."""
        winning_patterns = [
            0b111000000, 0b000111000, 0b000000111,  # Lignes horizontales
            0b100100100, 0b010010010, 0b001001001,  # Colonnes verticales
            0b100010001, 0b001010100  # Diagonales
        ]
        for pattern in winning_patterns:
            if (self.bitboards_player1 & pattern) == pattern:
                return 1  # Joueur 1 gagne
            if (self.bitboards_player2 & pattern) == pattern:
                return -1  # Joueur 2 gagne
        return None  # Pas de gagnant

    def minimax(self, depth, maximizing_player, alpha=-float('inf'), beta=float('inf')):
        winner = self.check_winner()
        self.node_count += 1  # Incrémenter le compteur de nœuds

        if winner == 1:
            return 10
        elif winner == -1:
            return -10
     
        if (depth < 0): 
            return 0
        
        if maximizing_player:
            max_eval = -float('inf')
            for successor in self.get_successors():
                eval = successor.minimax(depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                if self.use_alpha_beta:
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            for successor in self.get_successors():
                eval = successor.minimax(depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                if self.use_alpha_beta:
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval
      
    
    def get_best_move(self):
        best_move = None
        best_value = -float('inf')

        for successor in self.get_successors():
            eval = successor.minimax(5, False)
            if eval > best_value:
                best_value = eval
                best_move = successor
        return best_move
    

if __name__ == "__main__":
    bitboards_player1 = 0b000100110
    bitboards_player2 = 0b011001000
    game = Node(bitboards_player1, bitboards_player2, 1, use_alpha_beta=True)
   

    while True:
        print("Etat du jeu")
        game.display_board()
        print(f"Node count : {game.node_count}")
        winner = game.check_winner()      
           
       
        if winner:
            print(f"Gagnant {winner}!")
            break
        
        if game.turn == 1:
            print("Tour du joueur 1")
           
            b1 = game.bitboards_player1
            game = game.get_best_move()
            b2 = game.bitboards_player1
            print("Mouvement a faire : ")
            print(get_move_from_bitboards(b1, b2))
            print()
        else:
            print("Tour du joueur 2")
            b1 = game.bitboards_player2
            game = game.get_best_move()
            b2 = game.bitboards_player2
            print("Mouvement a faire : ")
            print(get_move_from_bitboards(b1, b2))
            
            print()
        if not game:
            break


