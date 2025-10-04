import time
import platform
import smtplib
import csv
from email.message import EmailMessage

# Safe beep wrapper
def safe_beep(frequency=1000, duration=200):
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(frequency, duration)

def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def get_level(rating):
    return f"Level {int(rating ** 0.5)}"

class Player:
    def __init__(self, name, rating=2500, k_factor=20):
        self.name = name
        self.rating = rating
        self.k_factor = k_factor
        self.old_names = []

    def __str__(self):
        tier = get_tier(self.rating)
        level = get_level(self.rating)
        progress = get_progress_bar(self.rating)
        return f"{self.name}: {round(self.rating)} ({tier}, {level}) [K={self.k_factor}] {progress}"

def get_tier(rating):
    if rating < 500:
        return color_text("Noob 🐣", "38;5;130")
    elif rating < 1000:
        return color_text("Beginner 🧑‍🎓", "37")
    elif rating < 1500:
        return color_text("Novice 🚹", "38;5;209")
    elif rating < 2000:
        return color_text("Intermediate 🧠", "38;5;225")
    elif rating < 2500:
        return color_text("Advanced 🧪", "38;5;228")
    elif rating < 3000:
        return color_text("Expert 🢼", "38;5;117")
    elif rating < 3500:
        return color_text("Elite 🧮", "38;5;201")
    elif rating < 4000:
        return color_text("Master 🧙", "38;5;46")
    elif rating < 4500:
        return color_text("Grandmaster 🏆", "34")
    elif rating < 5000:
        return color_text("Supergrandmaster 🫸", "31")
    else:
        return color_text("Legendary 🐉", "38;5;51")

def get_tier_color_code(rating):
    if rating < 500:
        return "38;5;130"
    elif rating < 1000:
        return "37"
    elif rating < 1500:
        return "38;5;209"
    elif rating < 2000:
        return "38;5;225"
    elif rating < 2500:
        return "38;5;228"
    elif rating < 3000:
        return "38;5;117"
    elif rating < 3500:
        return "38;5;201"
    elif rating < 4000:
        return "38;5;46"
    elif rating < 4500:
        return "34"
    elif rating < 5000:
        return "31"
    else:
        return "38;5;51"

def get_progress_bar(rating):
    tiers = [
        (1, 499), (500, 999), (1000, 1499), (1500, 1999), (2000, 2499),
        (2500, 2999), (3000, 3499), (3500, 3999), (4000, 4499), (4500, 4999),
        (5000, 9999)
    ]
    for low, high in tiers:
        if low <= rating <= high:
            progress = (rating - low) / (high - low)
            filled = int(progress * 10)
            empty = 10 - filled
            color = get_tier_color_code(rating)
            bar = "[" + "█" * filled + "░" * empty + "]"
            return f"\033[{color}m{bar}\033[0m"
    return "[██████████]"

def calculate_expected_score(player_a, player_b):
    return 1 / (1 + 10 ** ((player_b.rating - player_a.rating) / 400))

def update_ratings(player_a, player_b, result):
    expected_a = calculate_expected_score(player_a, player_b)
    expected_b = calculate_expected_score(player_b, player_a)

    avg = (player_a.rating + player_b.rating) / 2
    adjusted_k_a = player_a.k_factor / 50
    adjusted_k_b = player_b.k_factor / 50
    adjust_value_a = avg ** adjusted_k_a
    adjust_value_b = avg ** adjusted_k_b

    old_rating_a = player_a.rating
    old_rating_b = player_b.rating

    player_a.rating += adjust_value_a * (result - expected_a)
    player_b.rating += adjust_value_b * ((1 - result) - expected_b)

    player_a.rating = max(1, min(9999, player_a.rating))
    player_b.rating = max(1, min(9999, player_b.rating))

    return old_rating_a, old_rating_b, player_a.rating, player_b.rating

def undo_last_match(players, match_history, redo_stack):
    if not match_history:
        print("❌ No match to undo.")
        return

    name_a, name_b, old_rating_a, old_rating_b, new_rating_a, new_rating_b = match_history.pop()

    if name_a in players and name_b in players:
        redo_stack.append((name_a, name_b, new_rating_a, new_rating_b, old_rating_a, old_rating_b))
        players[name_a].rating = old_rating_a
        players[name_b].rating = old_rating_b
        print(f"↩️ Undid last match between {name_a} and {name_b}. Ratings restored.")
        safe_beep(700, 200)
    else:
        print("❌ One or both players not found. Cannot undo.")

def redo_last_match(players, redo_stack, match_history):
    if not redo_stack:
        print("❌ No match to redo.")
        return

    name_a, name_b, old_rating_a, old_rating_b, new_rating_a, new_rating_b = redo_stack.pop()

    if name_a in players and name_b in players:
        players[name_a].rating = new_rating_a
        players[name_b].rating = new_rating_b
        match_history.append((name_a, name_b, old_rating_a, old_rating_b, new_rating_a, new_rating_b))
        print(f"🔁 Redid match between {name_a} and {name_b}. Ratings reapplied.")
        safe_beep(750, 200)
    else:
        print("❌ One or both players not found. Cannot redo.")

def show_leaderboard(players):
    sorted_players = sorted(players.values(), key=lambda p: p.rating, reverse=True)
    print("\n📊 Elo Leaderboard:")
    safe_beep(1000, 200)
    for i, player in enumerate(sorted_players, start=1):
        print(f"{i}. {player}")

def export_leaderboard(players, filename="leaderboard.txt"):
    sorted_players = sorted(players.values(), key=lambda p: p.rating, reverse=True)
    with open(filename, "w", encoding='utf-8') as file:
        file.write("📊 Elo Leaderboard:\n")
        for i, player in enumerate(sorted_players, start=1):
            file.write(f"{i}. {str(player)}\n")
    print(f"📁 Leaderboard exported to {filename}")
    safe_beep(1200, 200)

def export_leaderboard_csv(players):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"leaderboard_{timestamp}.csv"
    sorted_players = sorted(players.values(), key=lambda p: p.rating, reverse=True)
    with open(filename, "w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Rating", "Tier", "Progress"])
        for player in sorted_players:
            tier = get_tier(player.rating)
            progress = get_progress_bar(player.rating)
            writer.writerow([player.name, round(player.rating), tier, progress])
    print(f"📁 CSV Leaderboard exported to {filename}")
    safe_beep(1300, 200)

def loading_animation(text="Processing"):
    for i in range(3):
        print(f"{text}{'.' * (i + 1)}", end='\r')
        time.sleep(0.4)
    print(" " * len(text + "..."), end='\r')

def average_rating(players):
    if not players:
        return 0
    total = sum(player.rating for player in players.values())
    return total / len(players)

def email_leaderboard(players, recipient_email):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"leaderboard_{timestamp}.csv"
    sorted_players = sorted(players.values(), key=lambda p: p.rating, reverse=True)

    with open(filename, "w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Rating", "Tier", "Progress"])
        for player in sorted_players:
            tier = get_tier(player.rating)
            progress = get_progress_bar(player.rating)
            writer.writerow([player.name, round(player.rating), tier, progress])

    msg = EmailMessage()
    msg['Subject'] = '📊 Elo Leaderboard Export'
    msg['From'] = 'your_email@example.com'  # REPLACE WITH YOUR EMAIL
    msg['To'] = recipient_email
    msg.set_content('Attached is the latest Elo leaderboard.')

    with open(filename, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='text', subtype='csv', filename=filename)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('your_email@example.com', 'your_app_password')  # REPLACE WITH YOUR EMAIL AND APP PASSWORD
            smtp.send_message(msg)
        print(f"📤 Leaderboard emailed to {recipient_email}")
        safe_beep(1400, 200)
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# helper to replace player names inside match history / redo stacks
def _replace_name_in_match_lists(from_name, to_name, match_history, match_redo):
    def replace_in_list(lst):
        for idx, rec in enumerate(lst):
            if len(rec) >= 2:
                a, b = rec[0], rec[1]
                changed = False
                if a == from_name:
                    a = to_name
                    changed = True
                if b == from_name:
                    b = to_name
                    changed = True
                if changed:
                    lst[idx] = (a, b) + tuple(rec[2:])
    replace_in_list(match_history)
    replace_in_list(match_redo)

def rename_player(players, old_name, new_name, rename_history, rename_redo, match_history, match_redo):
    if not old_name or not new_name:
        print("❌ Names cannot be empty.")
        return

    if old_name not in players:
        print(f"❌ Player '{old_name}' not found.")
        return

    if new_name in players:
        print(f"❌ Player '{new_name}' already exists.")
        return

    players[new_name] = players.pop(old_name)
    players[new_name].old_names.append(old_name)
    players[new_name].name = new_name

    _replace_name_in_match_lists(old_name, new_name, match_history, match_redo)
    rename_history.append((old_name, new_name))
    rename_redo.clear()
    print(f"✅ Renamed '{old_name}' to '{new_name}'.")
    safe_beep(900, 200)

def undo_rename(players, rename_history, rename_redo, match_history, match_redo):
    if not rename_history:
        print("❌ No rename to undo.")
        return

    old_name, new_name = rename_history.pop()
    if new_name not in players:
        print("❌ Cannot undo rename: current name not found.")
        rename_history.append((old_name, new_name))
        return

    players[old_name] = players.pop(new_name)
    players[old_name].name = old_name
    if players[old_name].old_names:
        try:
            players[old_name].old_names.pop()
        except Exception:
            pass

    _replace_name_in_match_lists(new_name, old_name, match_history, match_redo)
    rename_redo.append((old_name, new_name))
    print(f"↩️ Undo rename: '{new_name}' reverted to '{old_name}'.")
    safe_beep(950, 200)

# 🔍 Search players by tier
def search_players_by_tier(players):
    tier_input = input("Enter tier name (e.g., 'Expert 🢼'): ").strip()
    found = [p for p in players.values() if get_tier(p.rating).strip() == tier_input.strip()]
    if not found:
        print("❌ No players found in that tier.")
    else:
        print(f"\n🎯 Players in {tier_input}:")
        for player in found:
            print(player)

# 📈 Show rating distribution
def show_rating_distribution(players):
    distribution = {}
    for player in players.values():
        tier = get_tier(player.rating)
        distribution[tier] = distribution.get(tier, 0) + 1

    print("\n📊 Rating Distribution:")
    for tier, count in sorted(distribution.items(), key=lambda x: x[0]):
        print(f"{tier}: {count} player(s)")

# ⚔️ Compare two players
def compare_players(players):
    name1 = input("Enter first player name: ")
    name2 = input("Enter second player name: ")

    if name1 not in players or name2 not in players:
        print("❌ Both players must be registered.")
        return

    p1 = players[name1]
    p2 = players[name2]
    expected1 = calculate_expected_score(p1, p2)
    expected2 = calculate_expected_score(p2, p1)

    print(f"\n📊 Comparison:")
    print(f"{p1.name}: {round(p1.rating)} ({get_tier(p1.rating)}, {get_level(p1.rating)})")
    print(f"{p2.name}: {round(p2.rating)} ({get_tier(p2.rating)}, {get_level(p2.rating)})")
    print(f"Expected win chance:")
    print(f"  {p1.name}: {round(expected1 * 100, 2)}%")
    print(f"  {p2.name}: {round(expected2 * 100, 2)}%")

# --- Ultimate Tic-Tac-Toe Game Logic ---

class SubBoard:
    def __init__(self):
        self.grid = [[' ' for _ in range(3)] for _ in range(3)]
        self.winner = None

    def make_move(self, row, col, player_symbol):
        if self.grid[row][col] == ' ':
            self.grid[row][col] = player_symbol
            if self.check_win(player_symbol):
                self.winner = player_symbol
            return True
        return False

    def check_win(self, player_symbol):
        lines = self.grid + list(zip(*self.grid)) + [
            [self.grid[i][i] for i in range(3)],
            [self.grid[i][2 - i] for i in range(3)]
        ]
        return any(line.count(player_symbol) == 3 for line in lines)

    def is_full(self):
        return all(cell != ' ' for row in self.grid for cell in row)

class UltimateTicTacToe:
    def __init__(self, player_x, player_o):
        self.sub_boards = [SubBoard() for _ in range(9)]
        self.meta_board = [' ' for _ in range(9)]
        self.players = {'X': player_x, 'O': player_o}
        self.current_player = 'X'
        self.active_board = None
        self.move_history = []

    def colorize(self, val):
        if val == 'X':
            return '\033[36mX\033[0m'
        elif val == 'O':
            return '\033[31mO\033[0m'
        else:
            return val

    def print_board(self):
        print("\nUltimate Tic Tac Toe Board:\n")
        for row_block in range(3):
            for row in range(3):
                line = ''
                for col_block in range(3):
                    board_index = row_block * 3 + col_block
                    sub = self.sub_boards[board_index].grid[row]
                    cell_labels = [
                        self.colorize(sub[i]) if sub[i] != ' ' else str(3 * row + i + 1)
                        for i in range(3)
                    ]
                    line += ' ' + ' | '.join(cell_labels)
                    if col_block < 2:
                        line += ' ||'
                print(line)
            if row_block < 2:
                print('=' * 65)

    def get_global_coords(self, sub_board_num, cell_num):
        sub_board_num -= 1
        cell_num -= 1
        sub_row = sub_board_num // 3
        sub_col = sub_board_num % 3
        cell_row = cell_num // 3
        cell_col = cell_num % 3
        global_row = sub_row * 3 + cell_row
        global_col = sub_col * 3 + cell_col
        return global_row, global_col

    def get_sub_index(self, row, col):
        return (row // 3) * 3 + (col // 3)

    def get_local_coords(self, row, col):
        return row % 3, col % 3

    def is_valid_move(self, row, col):
        sub_index = self.get_sub_index(row, col)
        local_row, local_col = self.get_local_coords(row, col)
        if self.sub_boards[sub_index].grid[local_row][local_col] != ' ':
            return False
        if self.sub_boards[sub_index].winner or self.sub_boards[sub_index].is_full():
            return False
        if self.active_board is None:
            return True
        if self.sub_boards[self.active_board].winner or self.sub_boards[self.active_board].is_full():
            return True
        return sub_index == self.active_board

    def make_move(self, row, col):
        if not self.is_valid_move(row, col):
            print("❌ Invalid move. You must play in the correct sub-board.")
            return False
        sub_index = self.get_sub_index(row, col)
        local_row, local_col = self.get_local_coords(row, col)
        board = self.sub_boards[sub_index]

        self.move_history.append({
            'sub_index': sub_index,
            'local_row': local_row,
            'local_col': local_col,
            'player': self.current_player,
            'active_board': self.active_board,
            'meta_before': self.meta_board[sub_index],
            'sub_winner_before': board.winner
        })

        board.make_move(local_row, local_col, self.current_player)
        if board.winner:
            self.meta_board[sub_index] = self.current_player

        next_board = local_row * 3 + local_col
        if self.sub_boards[next_board].winner or self.sub_boards[next_board].is_full():
            self.active_board = None
        else:
            self.active_board = next_board

        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True

    def undo_move(self):
        if not self.move_history:
            print("⚠️ No moves to undo.")
            return False

        last = self.move_history.pop()
        board = self.sub_boards[last['sub_index']]
        board.grid[last['local_row']][last['local_col']] = ' '
        board.winner = last['sub_winner_before']
        self.meta_board[last['sub_index']] = last['meta_before']
        self.active_board = last['active_board']
        self.current_player = last['player']
        print(f"↩️ Undid move by Player {self.current_player}")
        return True

    def check_meta_win(self):
        lines = [
            self.meta_board[0:3], self.meta_board[3:6], self.meta_board[6:9],
            self.meta_board[0:9:3], self.meta_board[1:9:3], self.meta_board[2:9:3],
            [self.meta_board[i] for i in [0, 4, 8]], [self.meta_board[i] for i in [2, 4, 6]]
        ]
        for line in lines:
            if line.count('X') == 3:
                return 'X'
            if line.count('O') == 3:
                return 'O'
        return None

    def play(self, players, match_history, redo_stack):
        print("🎮 Welcome to Ultimate Tic Tac Toe!")
        print("Enter your move as: sub-board (1–9) and cell (1–9), or type 'undo'")
        print("Sub-board and cell layout:")
        print(" 1 | 2 | 3\n 4 | 5 | 6\n 7 | 8 | 9\n")

        p_x = self.players['X']
        p_o = self.players['O']

        while True:
            self.print_board()
            winner = self.check_meta_win()
            if winner:
                result = 1 if winner == 'X' else 0
                loading_animation("Updating ratings")
                old_a, old_b, new_a, new_b = update_ratings(p_x, p_o, result)
                match_history.append((p_x.name, p_o.name, old_a, old_b, new_a, new_b))
                redo_stack.clear()
                print(f"\n🏆 Player {winner} ({self.players[winner].name}) wins the game!")
                print("Returning to the main menu...")
                break

            print(f"\n🔹 Player {self.current_player}'s turn ({self.players[self.current_player].name}).")
            if self.active_board is not None and not (
                self.sub_boards[self.active_board].winner or self.sub_boards[self.active_board].is_full()
            ):
                print(f"➡️ You must play in sub-board {self.active_board + 1}")
            else:
                print("🆓 You can play in any sub-board.")
            move = input("Enter sub-board and cell (e.g. 5 3), or type 'undo': ").strip().lower()
            if move == 'undo':
                self.undo_move()
                continue
            try:
                sub_board, cell = map(int, move.split())
                if not (1 <= sub_board <= 9 and 1 <= cell <= 9):
                    print("⚠️ Please enter numbers between 1 and 9.")
                    continue
                row, col = self.get_global_coords(sub_board, cell)
                if not self.make_move(row, col):
                    sub_index = self.get_sub_index(row, col)
                    if self.sub_boards[sub_index].winner or self.sub_boards[sub_index].is_full():
                        print("❌ Invalid move: The chosen sub-board is already completed.")
                    elif self.active_board is not None and not (self.sub_boards[self.active_board].winner or self.sub_boards[self.active_board].is_full()) and sub_index != self.active_board:
                        print("❌ Invalid move: You must play in sub-board {self.active_board + 1}.")
                    else:
                        print("❌ Invalid move: The chosen cell is already occupied.")
                    continue
            except Exception:
                print("⚠️ Invalid input. Please enter two numbers separated by space or 'undo'.")

# --- Main Program Loop ---

def main():
    players = {}
    match_history = []
    redo_stack = []
    rename_history = []
    rename_redo = []

    while True:
        print("\n--- Main Menu ---")
        print("1. Add Player")
        print("2. Play Ultimate Tic Tac Toe")
        print("3. Show Leaderboard")
        print("4. Change Player's K-factor")
        print("5. Remove Player")
        print("6. Export Leaderboard to File")
        print("7. Export Leaderboard to CSV")
        print("8. Email Leaderboard")
        print("9. Search Players by Tier")
        print("10. Show Rating Distribution")
        print("11. Compare Two Players")
        print("12. Undo Last Match")
        print("13. Redo Last Match")
        print("14. Rename Player")
        print("15. Undo Rename Player")
        print("16. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter player name: ")
            if name in players:
                print("Player already exists.")
                continue
            rating_input = input("Enter starting rating (or press Enter for 2500): ")
            k_factor_input = input("Enter starting K-factor (or press Enter for 20): ")
            try:
                rating = int(rating_input) if rating_input else 2500
                k_factor = int(k_factor_input) if k_factor_input else 20
                rating = max(1, min(9999, rating))
                k_factor = max(10, min(40, k_factor))
                players[name] = Player(name, rating, k_factor)
                print(f"{name} added with rating {rating} and K-factor {k_factor}.")
                safe_beep(600, 200)
            except ValueError:
                print("❌ Invalid input. Rating and K-factor must be numbers.")

        elif choice == "2":
            if len(players) < 2:
                print("❌ You need at least two players to start a game.")
                continue
            name_x = input("Enter name for Player X: ")
            name_o = input("Enter name for Player O: ")
            if name_x not in players or name_o not in players:
                print("❌ Both players must be registered.")
                continue
            if name_x == name_o:
                print("❌ Players must be different.")
                continue
            game = UltimateTicTacToe(players[name_x], players[name_o])
            game.play(players, match_history, redo_stack)

        elif choice == "3":
            show_leaderboard(players)

        elif choice == "4":
            name = input("Enter player name to change K-factor: ")
            if name not in players:
                print("❌ Player not found.")
                continue
            try:
                new_k = int(input(f"Enter new K-factor for {name} (10-40): "))
                if 10 <= new_k <= 40:
                    players[name].k_factor = new_k
                    print(f"🔧 K-factor for {name} updated to {new_k}.")
                else:
                    print("❌ K-factor must be between 1 and 40.")
            except ValueError:
                print("❌ Invalid number. Try again.")

        elif choice == "5":
            name = input("Enter the player name to remove: ")
            if name in players:
                del players[name]
                print(f"🗑️ {name} has been removed from the leaderboard.")
            else:
                print("❌ Player not found.")

        elif choice == "6":
            export_leaderboard(players)

        elif choice == "7":
            export_leaderboard_csv(players)

        elif choice == "8":
            recipient = input("Enter recipient email: ")
            email_leaderboard(players, recipient)

        elif choice == "9":
            search_players_by_tier(players)

        elif choice == "10":
            show_rating_distribution(players)

        elif choice == "11":
            compare_players(players)

        elif choice == "12":
            undo_last_match(players, match_history, redo_stack)

        elif choice == "13":
            redo_last_match(players, redo_stack, match_history)

        elif choice == "14":
            old = input("Enter current player name to rename: ").strip()
            new = input("Enter new name: ").strip()
            rename_player(players, old, new, rename_history, rename_redo, match_history, redo_stack)

        elif choice == "15":
            undo_rename(players, rename_history, rename_redo, match_history, redo_stack)

        elif choice == "16":
            print("👋 Thanks for using our Ultimate Tic Tac Toe Elo rating system!")
            break

        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":

    main()
