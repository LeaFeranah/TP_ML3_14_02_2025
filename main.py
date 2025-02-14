import tkinter as tk
from tkinter import messagebox
from ml_fanorona import Node as FnrnNode, get_move_from_bitboards


def bitboards_to_matrix(bitboards_player1, bitboards_player2):
    matrix = [[None for _ in range(3)] for _ in range(3)]
    for i in range(9):
        if bitboards_player1 & (1 << i):
            matrix[i // 3][i % 3] = "Blancs"
        elif bitboards_player2 & (1 << i):
            matrix[i // 3][i % 3] = "Noir"
    return matrix

def get_move(bitboard_before, bitboard_after):
    # Calculer la différence entre les deux bitboards
    diff_bitboard = bitboard_before ^ bitboard_after
    
    # Trouver les indices des cases modifiées
    row = None
    end_pos = None
    
    for i in range(9):
        if (diff_bitboard >> i) & 1:
            if (bitboard_before >> i) & 1:
                start_pos = i
            else:
                end_pos = i
    
    return start_pos, end_pos


def bitboard_to_coords(bitboard):
    # Trouver la position du bit modifié
    for i in range(9):
        if (bitboard >> i) & 1:
            # Convertir la position du bit en coordonnées (row, col)
            row = i // 3
            col = i % 3
            return row, col
    return None  # Si aucun bit n'est set, retourner None

def board_to_node(board): 
    new_bb = matrix_to_bitboards(self.board)
    bitboards_game = FnrnNode(new_bb[0], new_bb[1])
    return bitboards_game

def matrix_to_bitboards(matrix):
    bitboards_player1 = 0
    bitboards_player2 = 0
    for row in range(3):
        for col in range(3):
            index = row * 3 + col
            if matrix[row][col] == "Blancs":
                bitboards_player1 |= (1 << index)
            elif matrix[row][col] == "Noir":
                bitboards_player2 |= (1 << index)
    return bitboards_player1, bitboards_player2

class Fanorona:
    def __init__(self, root):
        self.root = root
        self.root.title("Fanorona 3x3")
        self.root.configure(bg="#F5DEB3")  # Fond couleur bois

        self.current_player = "Blancs"
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.bitboards_game = FnrnNode(0, 0, 1, True)
        self.pieces_placed = {"Blancs": 0, "Noir": 0}
        self.selected_piece = None
        self.piece_ovals = {}

        self.create_ui()

    def create_ui(self):
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="#F5DEB3", highlightthickness=0)
        self.canvas.pack(pady=50)  # Centrer le plateau verticalement

        # Dessiner le plateau avec les lignes de connexion
        self.draw_board()

        # Boutons de contrôle
        self.info_label = tk.Label(self.root, text=f" Tour des : {self.current_player}", font=("Arial", 14), bg="#F5DEB3")
        self.info_label.pack()

        self.reset_button = tk.Button(self.root, text="Rejouer", command=self.reset_game, bg="#8B4513", fg="white", font=("Arial", 12), relief="flat", borderwidth=0)
        self.reset_button.pack(pady=10)

        # Ajouter un style pour un effet de bordure arrondie
        self.reset_button.configure(highlightbackground="#8B4513", highlightcolor="#8B4513", highlightthickness=0)
        self.reset_button.bind("<Enter>", self.on_enter)
        self.reset_button.bind("<Leave>", self.on_leave)

        # Gérer les clics sur le plateau
        self.canvas.bind("<Button-1>", self.handle_click)

    def draw_board(self):
        self.intersections = []

        # Dessiner les lignes
        for i in range(3):
            self.canvas.create_line(50, 50 + i * 100, 250, 50 + i * 100, fill="brown", width=2)  # Horizontales
            self.canvas.create_line(50 + i * 100, 50, 50 + i * 100, 250, fill="brown", width=2)  # Verticales
        self.canvas.create_line(50, 50, 250, 250, fill="brown", width=2)  # Diagonale principale
        self.canvas.create_line(250, 50, 50, 250, fill="brown", width=2)  # Diagonale secondaire

        # Dessiner les intersections
        for row in range(3):
            for col in range(3):
                x, y = 50 + col * 100, 50 + row * 100
                self.intersections.append((x, y))
                self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="brown")  # Taille ajustée

    def handle_click(self, event):
        x, y = event.x, event.y

        # Trouver l'intersection la plus proche
        for idx, (ix, iy) in enumerate(self.intersections):
            if abs(x - ix) <= 20 and abs(y - iy) <= 20:
                row, col = divmod(idx, 3)
                if self.board[row][col] == self.current_player:
                    self.select_piece(row, col)
                elif self.selected_piece:
                    self.move_piece(row, col, ix, iy)
                elif self.board[row][col] is None and self.pieces_placed[self.current_player] < 3:
                    self.place_piece(row, col, ix, iy)
                break

    def place_piece(self, row, col, x, y):
        # Placer le pion
        color = "white" if self.current_player == "Blancs" else "black"
        oval = self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill=color, outline="")
        self.piece_ovals[(row, col)] = oval
        self.board[row][col] = self.current_player
        new_bb = matrix_to_bitboards(self.board)
        turn = 1 if self.current_player == "Blancs" else -1 if self.current_player == "Noir" else 0
        self.bitboards_game = FnrnNode(new_bb[0], new_bb[1], turn)
        self.bitboards_game.display_board()
        self.pieces_placed[self.current_player] += 1

        if self.check_winner(row, col):
            messagebox.showinfo("FIN DE PARTIE", f" Les {self.current_player} gagnent !")
            self.reset_game()
            return

        # Changer de joueur
        self.current_player = "Noir" if self.current_player == "Blancs" else "Blancs"
        self.info_label.config(text=f" Tours des : {self.current_player} ")

    def select_piece(self, row, col):
        # Réinitialiser la bordure de l'ancien pion sélectionné
        if self.selected_piece:
            prev_row, prev_col = self.selected_piece
            prev_oval = self.piece_ovals[(prev_row, prev_col)]
            self.canvas.itemconfig(prev_oval, outline="")

        # Sélectionner le nouveau pion
        self.selected_piece = (row, col)
        selected_oval = self.piece_ovals[(row, col)]
        self.canvas.itemconfig(selected_oval, outline="red", width=2)
        self.info_label.config(text=f"{self.current_player}: Deplacez vers une case vide")

    def is_valid_move(self, prev_row, prev_col, new_row, new_col):
        # Définir les déplacements valides en suivant les lignes du plateau
        valid_moves = {
            (0, 0): [(0, 1), (1, 0), (1, 1)],
            (0, 1): [(0, 0), (0, 2), (1, 1)],
            (0, 2): [(0, 1), (1, 1), (1, 2)],
            (1, 0): [(0, 0), (1, 1), (2, 0)],
            (1, 1): [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)],
            (1, 2): [(0, 2), (1, 1), (2, 2)],
            (2, 0): [(1, 0), (1, 1), (2, 1)],
            (2, 1): [(2, 0), (1, 1), (2, 2)],
            (2, 2): [(1, 1), (1, 2), (2, 1)]
        }

        return (new_row, new_col) in valid_moves.get((prev_row, prev_col), [])

    def move_piece(self, row, col, x, y):
        if self.board[row][col] is not None:
            messagebox.showwarning("Mouvement impossible", "La case est déja occupée!")
            return

        prev_row, prev_col = self.selected_piece

        if not self.is_valid_move(prev_row, prev_col, row, col):
            messagebox.showwarning("Mouvement impossible", "Essayez autre chose")
            return

        # Déplacer le pion
        self.board[prev_row][prev_col] = None
        self.board[row][col] = self.current_player

        new_bb = matrix_to_bitboards(self.board)
        turn = 1 if self.current_player == "Blancs" else -1 if self.current_player == "Noir" else 0
        self.bitboards_game = FnrnNode(new_bb[0], new_bb[1], turn)
        self.bitboards_game.display_board()
        

        # Effacer l'ancienne position
        prev_oval = self.piece_ovals.pop((prev_row, prev_col))
        self.canvas.delete(prev_oval)

        # Dessiner la nouvelle position
        color = "white" if self.current_player == "Blancs" else "black"
        new_oval = self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill=color, outline="")
        self.piece_ovals[(row, col)] = new_oval

        self.selected_piece = None

        if self.check_winner(row, col):
            messagebox.showinfo("FIN DE PARTIE ", f" Les {self.current_player} gagnent !")
            self.reset_game()
            return  

        self.current_player = "Noir" if self.current_player == "Blancs" else "Blancs"
        self.info_label.config(text=f" Tour des: {self.current_player}")

        # # Changer de joueur

        if (self.current_player == "Noir"):
              b1 = self.bitboards_game.bitboards_player2
              best_move = self.bitboards_game.get_best_move()
              b2 = best_move.bitboards_player2
              (selected_index), (dest_index) = get_move_from_bitboards(b1, b2)
                 #   row, col = dest_index
              print(selected_index)
              print(dest_index)
            #   self.selected_piece = selected_index     
            #   self.move_piece(row, col, x, y)

    def check_winner(self, row, col):
        # Vérifier les lignes, colonnes et diagonales pour une victoire
        # Ligne
        if all(self.board[row][c] == self.current_player for c in range(3)):
            return True
        # Colonne
        if all(self.board[r][col] == self.current_player for r in range(3)):
            return True
        # Diagonales
        if row == col and all(self.board[i][i] == self.current_player for i in range(3)):
            return True
        if row + col == 2 and all(self.board[i][2 - i] == self.current_player for i in range(3)):
            return True

        return False

    def reset_game(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.pieces_placed = {"Blancs": 0, "Noir": 0}
        self.selected_piece = None
        self.piece_ovals.clear()
        self.canvas.delete("all")
        self.draw_board()
        self.current_player = "Blancs"
        self.info_label.config(text=f" Tour des : {self.current_player}")

    def on_enter(self, event):
        event.widget.config(bg="#A0522D")

    def on_leave(self, event):
        event.widget.config(bg="#8B4513")

if __name__ == "__main__":
    root = tk.Tk()
    Fanorona(root)
    root.mainloop()
