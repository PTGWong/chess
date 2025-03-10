import pygame
import sys
from enum import Enum

# 初始化pygame
pygame.init()

# 常量定义
BOARD_SIZE = 8  # 棋盘大小 8x8
SQUARE_SIZE = 80  # 每个方格的像素大小
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE  # 窗口大小
FPS = 60  # 帧率

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_SQUARE = (118, 150, 86)  # 深绿色方格
LIGHT_SQUARE = (238, 238, 210)  # 浅色方格
HIGHLIGHT = (186, 202, 68)  # 高亮颜色
MOVE_HINT = (106, 135, 77, 200)  # 移动提示颜色（半透明）

# 棋子颜色枚举
class PieceColor(Enum):
    WHITE = 0
    BLACK = 1

# 棋子类型枚举
class PieceType(Enum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5

# 棋子类
class Piece:
    def __init__(self, piece_type, color, position):
        self.type = piece_type
        self.color = color
        self.position = position  # (row, col)
        self.has_moved = False  # 用于判断王车易位和兵的首次移动
        self.en_passant_vulnerable = False  # 用于吃过路兵判断
    
    def get_possible_moves(self, board):
        """获取棋子的所有可能移动位置"""
        moves = []
        row, col = self.position
        
        # 兵的移动
        if self.type == PieceType.PAWN:
            direction = -1 if self.color == PieceColor.WHITE else 1
            
            # 前进一步
            if 0 <= row + direction < BOARD_SIZE and board[row + direction][col] is None:
                moves.append((row + direction, col))
                
                # 初始位置可以前进两步
                initial_row = 6 if self.color == PieceColor.WHITE else 1
                if row == initial_row and board[row + 2*direction][col] is None:
                    moves.append((row + 2*direction, col))
            
            # 斜向吃子
            for dc in [-1, 1]:
                if 0 <= row + direction < BOARD_SIZE and 0 <= col + dc < BOARD_SIZE:
                    # 常规吃子
                    target = board[row + direction][col + dc]
                    if target is not None and target.color != self.color:
                        moves.append((row + direction, col + dc))
                    
                    # 吃过路兵
                    if row == (3 if self.color == PieceColor.WHITE else 4):
                        target = board[row][col + dc]
                        if (target is not None and target.type == PieceType.PAWN and 
                            target.color != self.color and target.en_passant_vulnerable):
                            moves.append((row + direction, col + dc))
        
        # 马的移动
        elif self.type == PieceType.KNIGHT:
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                    target = board[new_row][new_col]
                    if target is None or target.color != self.color:
                        moves.append((new_row, new_col))
        
        # 象的移动
        elif self.type == PieceType.BISHOP:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # 对角线方向
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    new_row, new_col = row + i*dr, col + i*dc
                    if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
                        break
                    target = board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.color != self.color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        
        # 车的移动
        elif self.type == PieceType.ROOK:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 水平和垂直方向
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    new_row, new_col = row + i*dr, col + i*dc
                    if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
                        break
                    target = board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.color != self.color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        
        # 后的移动（象+车的组合）
        elif self.type == PieceType.QUEEN:
            directions = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 1),
                (1, -1), (1, 0), (1, 1)
            ]
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    new_row, new_col = row + i*dr, col + i*dc
                    if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
                        break
                    target = board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.color != self.color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        
        # 王的移动
        elif self.type == PieceType.KING:
            # 常规移动
            directions = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 1),
                (1, -1), (1, 0), (1, 1)
            ]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                    target = board[new_row][new_col]
                    if target is None or target.color != self.color:
                        moves.append((new_row, new_col))
            
            # 王车易位（需要在ChessGame类中进一步检查）
            if not self.has_moved:
                # 短易位（王侧）
                if col + 3 < BOARD_SIZE:
                    rook = board[row][col + 3]
                    if (rook is not None and rook.type == PieceType.ROOK and 
                        not rook.has_moved and 
                        board[row][col + 1] is None and 
                        board[row][col + 2] is None):
                        moves.append((row, col + 2))  # 王移动两格
                
                # 长易位（后侧）
                if col - 4 >= 0:
                    rook = board[row][col - 4]
                    if (rook is not None and rook.type == PieceType.ROOK and 
                        not rook.has_moved and 
                        board[row][col - 1] is None and 
                        board[row][col - 2] is None and 
                        board[row][col - 3] is None):
                        moves.append((row, col - 2))  # 王移动两格
        
        return moves

# 国际象棋游戏类
class ChessGame:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_turn = PieceColor.WHITE
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.promotion_pawn = None  # 用于兵的升变
        self.setup_board()
        
        # 初始化pygame窗口
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("国际象棋")
        self.clock = pygame.time.Clock()
    
    def setup_board(self):
        """初始化棋盘布局"""
        # 放置黑方棋子
        self.board[0][0] = Piece(PieceType.ROOK, PieceColor.BLACK, (0, 0))
        self.board[0][1] = Piece(PieceType.KNIGHT, PieceColor.BLACK, (0, 1))
        self.board[0][2] = Piece(PieceType.BISHOP, PieceColor.BLACK, (0, 2))
        self.board[0][3] = Piece(PieceType.QUEEN, PieceColor.BLACK, (0, 3))
        self.board[0][4] = Piece(PieceType.KING, PieceColor.BLACK, (0, 4))
        self.board[0][5] = Piece(PieceType.BISHOP, PieceColor.BLACK, (0, 5))
        self.board[0][6] = Piece(PieceType.KNIGHT, PieceColor.BLACK, (0, 6))
        self.board[0][7] = Piece(PieceType.ROOK, PieceColor.BLACK, (0, 7))
        
        # 放置黑方兵
        for col in range(BOARD_SIZE):
            self.board[1][col] = Piece(PieceType.PAWN, PieceColor.BLACK, (1, col))
        
        # 放置白方兵
        for col in range(BOARD_SIZE):
            self.board[6][col] = Piece(PieceType.PAWN, PieceColor.WHITE, (6, col))
        
        # 放置白方棋子
        self.board[7][0] = Piece(PieceType.ROOK, PieceColor.WHITE, (7, 0))
        self.board[7][1] = Piece(PieceType.KNIGHT, PieceColor.WHITE, (7, 1))
        self.board[7][2] = Piece(PieceType.BISHOP, PieceColor.WHITE, (7, 2))
        self.board[7][3] = Piece(PieceType.QUEEN, PieceColor.WHITE, (7, 3))
        self.board[7][4] = Piece(PieceType.KING, PieceColor.WHITE, (7, 4))
        self.board[7][5] = Piece(PieceType.BISHOP, PieceColor.WHITE, (7, 5))
        self.board[7][6] = Piece(PieceType.KNIGHT, PieceColor.WHITE, (7, 6))
        self.board[7][7] = Piece(PieceType.ROOK, PieceColor.WHITE, (7, 7))
    
    def draw_board(self):
        """绘制棋盘"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # 绘制棋盘方格
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, 
                                (col * SQUARE_SIZE, row * SQUARE_SIZE, 
                                SQUARE_SIZE, SQUARE_SIZE))
                
                # 高亮选中的棋子
                if (self.selected_piece is not None and 
                    self.selected_piece.position == (row, col)):
                    pygame.draw.rect(self.screen, HIGHLIGHT, 
                                    (col * SQUARE_SIZE, row * SQUARE_SIZE, 
                                    SQUARE_SIZE, SQUARE_SIZE))
                
                # 显示可能的移动位置
                if (row, col) in self.valid_moves:
                    pygame.draw.circle(self.screen, MOVE_HINT, 
                                    (col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                    row * SQUARE_SIZE + SQUARE_SIZE // 2), 
                                    SQUARE_SIZE // 6)
    
    def draw_pieces(self):
        """绘制棋子"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is not None:
                    self.draw_piece(piece, row, col)
    
    def draw_piece(self, piece, row, col):
        """绘制单个棋子"""
        x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        color = WHITE if piece.color == PieceColor.WHITE else BLACK
        outline_color = BLACK if piece.color == PieceColor.WHITE else WHITE
        radius = SQUARE_SIZE // 2 - 10
        
        # 绘制棋子基本形状
        if piece.type == PieceType.PAWN:
            # 兵 - 简单圆形
            pygame.draw.circle(self.screen, color, (x, y), radius - 10)
            pygame.draw.circle(self.screen, outline_color, (x, y), radius - 10, 2)
            
        elif piece.type == PieceType.KNIGHT:
            # 马 - 马头形状（简化为三角形加圆形）
            points = [
                (x, y - radius + 5),
                (x - radius + 5, y + radius - 5),
                (x + radius - 5, y + radius - 5)
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, outline_color, points, 2)
            pygame.draw.circle(self.screen, color, (x, y), radius - 15)
            pygame.draw.circle(self.screen, outline_color, (x, y), radius - 15, 2)
            
        elif piece.type == PieceType.BISHOP:
            # 象 - 尖顶形状
            points = [
                (x, y - radius + 5),
                (x - radius + 10, y + radius - 5),
                (x + radius - 10, y + radius - 5)
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, outline_color, points, 2)
            pygame.draw.circle(self.screen, color, (x, y), radius - 10)
            pygame.draw.circle(self.screen, outline_color, (x, y), radius - 10, 2)
            
        elif piece.type == PieceType.ROOK:
            # 车 - 城堡形状（矩形）
            rect = pygame.Rect(x - radius + 10, y - radius + 10, 2 * radius - 20, 2 * radius - 20)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, outline_color, rect, 2)
            # 顶部的城垛
            for i in range(3):
                small_rect = pygame.Rect(x - radius + 15 + i * 15, y - radius + 5, 10, 10)
                pygame.draw.rect(self.screen, color, small_rect)
                pygame.draw.rect(self.screen, outline_color, small_rect, 1)
            
        elif piece.type == PieceType.QUEEN:
            # 后 - 皇冠形状（圆形加顶部装饰）
            pygame.draw.circle(self.screen, color, (x, y), radius - 5)
            pygame.draw.circle(self.screen, outline_color, (x, y), radius - 5, 2)
            # 皇冠顶部
            for i in range(3):
                offset = (i - 1) * 10
                pygame.draw.circle(self.screen, color, (x + offset, y - radius + 10), 5)
                pygame.draw.circle(self.screen, outline_color, (x + offset, y - radius + 10), 5, 1)
            
        elif piece.type == PieceType.KING:
            # 王 - 皇冠形状加十字
            pygame.draw.circle(self.screen, color, (x, y), radius - 5)
            pygame.draw.circle(self.screen, outline_color, (x, y), radius - 5, 2)
            # 十字
            pygame.draw.line(self.screen, outline_color, (x, y - radius // 2), (x, y + radius // 2), 3)
            pygame.draw.line(self.screen, outline_color, (x - radius // 2, y), (x + radius // 2, y), 3)
    
    def handle_click(self, pos):
        """处理鼠标点击事件"""
        if self.game_over or self.promotion_pawn is not None:
            return
            
        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE
        
        # 如果已经选中了棋子
        if self.selected_piece is not None:
            # 如果点击的是可移动位置，则移动棋子
            if (row, col) in self.valid_moves:
                self.move_piece(self.selected_piece, row, col)
                self.selected_piece = None
                self.valid_moves = []
            # 如果点击的是同一个棋子，则取消选择
            elif self.board[row][col] is self.selected_piece:
                self.selected_piece = None
                self.valid_moves = []
            # 如果点击的是同色的其他棋子，则选择新棋子
            elif (self.board[row][col] is not None and 
                  self.board[row][col].color == self.current_turn):
                self.selected_piece = self.board[row][col]
                self.valid_moves = self.get_valid_moves(self.selected_piece)
        # 如果没有选中棋子，且点击的是当前回合颜色的棋子
        elif (self.board[row][col] is not None and 
              self.board[row][col].color == self.current_turn):
            self.selected_piece = self.board[row][col]
            self.valid_moves = self.get_valid_moves(self.selected_piece)
    
    def move_piece(self, piece, new_row, new_col):
        """移动棋子"""
        old_row, old_col = piece.position
        
        # 处理吃过路兵
        if (piece.type == PieceType.PAWN and 
            old_col != new_col and 
            self.board[new_row][new_col] is None):
            # 吃过路兵情况下，需要移除被吃的兵
            self.board[old_row][new_col] = None
        
        # 处理王车易位
        if piece.type == PieceType.KING and abs(old_col - new_col) > 1:
            # 短易位
            if new_col > old_col:
                rook = self.board[old_row][7]
                self.board[old_row][5] = rook  # 移动车
                rook.position = (old_row, 5)
                rook.has_moved = True
                self.board[old_row][7] = None
            # 长易位
            else:
                rook = self.board[old_row][0]
                self.board[old_row][3] = rook  # 移动车
                rook.position = (old_row, 3)
                rook.has_moved = True
                self.board[old_row][0] = None
        
        # 重置所有兵的过路兵状态
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if (self.board[r][c] is not None and 
                    self.board[r][c].type == PieceType.PAWN):
                    self.board[r][c].en_passant_vulnerable = False
        
        # 设置过路兵状态
        if (piece.type == PieceType.PAWN and 
            abs(old_row - new_row) == 2):
            piece.en_passant_vulnerable = True
        
        # 移动棋子
        self.board[new_row][new_col] = piece
        self.board[old_row][old_col] = None
        piece.position = (new_row, new_col)
        piece.has_moved = True
        
        # 处理兵升变
        if (piece.type == PieceType.PAWN and 
            (new_row == 0 or new_row == 7)):
            self.promotion_pawn = piece
        else:
            # 切换回合
            self.current_turn = PieceColor.BLACK if self.current_turn == PieceColor.WHITE else PieceColor.WHITE
            
            # 检查游戏结束条件
            self.check_game_over()
    
    def promote_pawn(self, piece_type):
        """升变兵为指定类型的棋子"""
        if self.promotion_pawn is not None:
            row, col = self.promotion_pawn.position
            color = self.promotion_pawn.color
            self.board[row][col] = Piece(piece_type, color, (row, col))
            self.promotion_pawn = None
            
            # 切换回合
            self.current_turn = PieceColor.BLACK if self.current_turn == PieceColor.WHITE else PieceColor.WHITE
            
            # 检查游戏结束条件
            self.check_game_over()
    
    def get_valid_moves(self, piece):
        """获取棋子的有效移动位置（考虑将军限制）"""
        possible_moves = piece.get_possible_moves(self.board)
        valid_moves = []
        
        # 检查每个可能的移动是否会导致自己被将军
        for move in possible_moves:
            new_row, new_col = move
            old_row, old_col = piece.position
            
            # 临时移动棋子
            captured_piece = self.board[new_row][new_col]
            self.board[new_row][new_col] = piece
            self.board[old_row][old_col] = None
            piece.position = (new_row, new_col)
            
            # 检查是否被将军
            in_check = self.is_in_check(piece.color)
            
            # 恢复棋盘状态
            self.board[old_row][old_col] = piece
            self.board[new_row][new_col] = captured_piece
            piece.position = (old_row, old_col)
            
            if not in_check:
                valid_moves.append(move)
        
        return valid_moves
    
    def is_in_check(self, color):
        """检查指定颜色的王是否被将军"""
        # 找到王的位置
        king_position = None
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if (piece is not None and 
                    piece.type == PieceType.KING and 
                    piece.color == color):
                    king_position = (row, col)
                    break
            if king_position:
                break
        
        if not king_position:  # 如果找不到王（不应该发生）
            return False
        
        # 检查对方所有棋子是否可以攻击到王
        opponent_color = PieceColor.BLACK if color == PieceColor.WHITE else PieceColor.WHITE
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if (piece is not None and piece.color == opponent_color):
                    moves = piece.get_possible_moves(self.board)
                    if king_position in moves:
                        return True
        
        return False
    
    def check_game_over(self):
        """检查游戏是否结束"""
        # 检查当前回合是否有合法移动
        has_valid_move = False
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if (piece is not None and piece.color == self.current_turn):
                    valid_moves = self.get_valid_moves(piece)
                    if valid_moves:
                        has_valid_move = True
                        break
            if has_valid_move:
                break
        
        if not has_valid_move:
            self.game_over = True
            # 检查是否是将军导致的游戏结束（将死）
            if self.is_in_check(self.current_turn):
                self.winner = PieceColor.BLACK if self.current_turn == PieceColor.WHITE else PieceColor.WHITE
            else:  # 否则是和棋（逼和）
                self.winner = None
    
    def draw_promotion_menu(self):
        """绘制兵升变选择菜单"""
        if self.promotion_pawn is None:
            return
            
        row, col = self.promotion_pawn.position
        color = self.promotion_pawn.color
        
        # 绘制背景
        menu_width = SQUARE_SIZE * 4
        menu_height = SQUARE_SIZE
        menu_x = col * SQUARE_SIZE
        menu_y = row * SQUARE_SIZE
        
        # 调整菜单位置，确保在屏幕内
        if menu_x + menu_width > WINDOW_SIZE:
            menu_x = WINDOW_SIZE - menu_width
        if menu_y + menu_height > WINDOW_SIZE:
            menu_y = WINDOW_SIZE - menu_height
        
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, BLACK, (menu_x, menu_y, menu_width, menu_height), 2)
        
        # 绘制可选择的棋子
        piece_types = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
        for i, piece_type in enumerate(piece_types):
            piece = Piece(piece_type, color, (row, col))
            self.draw_piece(piece, menu_y // SQUARE_SIZE, menu_x // SQUARE_SIZE + i)
    
    def handle_promotion_click(self, pos):
        """处理兵升变选择的点击"""
        if self.promotion_pawn is None:
            return
            
        row, col = self.promotion_pawn.position
        menu_x = col * SQUARE_SIZE
        menu_y = row * SQUARE_SIZE
        
        # 调整菜单位置
        if menu_x + SQUARE_SIZE * 4 > WINDOW_SIZE:
            menu_x = WINDOW_SIZE - SQUARE_SIZE * 4
        if menu_y + SQUARE_SIZE > WINDOW_SIZE:
            menu_y = WINDOW_SIZE - SQUARE_SIZE
        
        # 检查点击位置
        if (menu_y <= pos[1] <= menu_y + SQUARE_SIZE):
            x_offset = pos[0] - menu_x
            if 0 <= x_offset <= SQUARE_SIZE * 4:
                piece_index = x_offset // SQUARE_SIZE
                piece_types = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
                if piece_index < len(piece_types):
                    self.promote_pawn(piece_types[piece_index])
    
    def run(self):
        """游戏主循环"""
        running = True
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        if self.promotion_pawn is not None:
                            self.handle_promotion_click(event.pos)
                        else:
                            self.handle_click(event.pos)
            
            # 绘制游戏界面
            self.screen.fill(WHITE)
            self.draw_board()
            self.draw_pieces()
            if self.promotion_pawn is not None:
                self.draw_promotion_menu()
            
            # 更新显示
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# 运行游戏
if __name__ == "__main__":
    game = ChessGame()
    game.run()