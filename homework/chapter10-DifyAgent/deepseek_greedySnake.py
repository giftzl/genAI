import pygame
import sys
import random
import time
import json
from enum import Enum

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

# 颜色定义
BACKGROUND = (15, 56, 15)
GRID_COLOR = (30, 80, 30)
SNAKE_HEAD = (0, 200, 0)
SNAKE_BODY = (0, 180, 60)
FOOD_COLOR = (220, 50, 50)
SPECIAL_FOOD_COLOR = (220, 200, 0)
OBSTACLE_COLOR = (100, 100, 150)
TEXT_COLOR = (255, 255, 200)
BUTTON_COLOR = (70, 130, 70)
BUTTON_HOVER = (100, 180, 100)

# 方向枚举
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# 游戏模式
class GameMode(Enum):
    CLASSIC = 1
    TIMED = 2
    OBSTACLE = 3
    ENDLESS = 4

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("贪吃蛇游戏")
clock = pygame.time.Clock()

# 字体 - 使用系统字体并确保字体可用
try:
    # 尝试加载中文字体
    font_large = pygame.font.Font("simhei.ttf", 72)  # 黑体
except:
    try:
        # 尝试其他中文字体
        font_large = pygame.font.Font("simsun.ttc", 72)  # 宋体
    except:
        # 使用默认字体（可能不支持中文）
        font_large = pygame.font.SysFont(None, 72)

try:
    font_medium = pygame.font.Font("simhei.ttf", 48)
except:
    try:
        font_medium = pygame.font.Font("simsun.ttc", 48)
    except:
        font_medium = pygame.font.SysFont(None, 48)

try:
    font_small = pygame.font.Font("simhei.ttf", 36)
except:
    try:
        font_small = pygame.font.Font("simsun.ttc", 36)
    except:
        font_small = pygame.font.SysFont(None, 36)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.score = 0
        self.grow_to = 3
        self.color_index = 0
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        dx, dy = self.direction.value
        new_x = (head[0] + dx) % GRID_WIDTH
        new_y = (head[1] + dy) % GRID_HEIGHT
        new_position = (new_x, new_y)
        
        if new_position in self.positions[1:]:
            return False  # 游戏结束
        
        self.positions.insert(0, new_position)
        
        if len(self.positions) > self.grow_to:
            self.positions.pop()
            
        self.color_index = (self.color_index + 1) % 10
        return True
    
    def render(self, surface):
        for i, pos in enumerate(self.positions):
            # 蛇头使用特殊颜色
            if i == 0:
                color = SNAKE_HEAD
            else:
                # 渐变效果
                color_factor = (i % 5) * 20
                color = (max(0, SNAKE_BODY[0] - color_factor), 
                         max(0, SNAKE_BODY[1] - color_factor), 
                         SNAKE_BODY[2])
            
            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 100, 0), rect, 1)
            
    def change_direction(self, direction):
        # 防止180度转向
        dx, dy = direction.value
        current_dx, current_dy = self.direction.value
        
        if (dx * -1, dy * -1) != (current_dx, current_dy):
            self.direction = direction

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.is_special = False
        self.spawn_time = 0
        self.randomize_position()
    
    def randomize_position(self, snake_positions=None, obstacles=None):
        if snake_positions is None:
            snake_positions = []
        if obstacles is None:
            obstacles = []
            
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), 
                            random.randint(0, GRID_HEIGHT - 1))
            if (self.position not in snake_positions and 
                self.position not in obstacles):
                break
                
        # 10%概率生成特殊食物
        self.is_special = random.random() < 0.1
        self.spawn_time = time.time()
    
    def render(self, surface):
        color = SPECIAL_FOOD_COLOR if self.is_special else FOOD_COLOR
        rect = pygame.Rect(self.position[0] * GRID_SIZE, 
                          self.position[1] * GRID_SIZE, 
                          GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (150, 0, 0), rect, 1)
        
        # 特殊食物添加闪烁效果
        if self.is_special and int(time.time() * 3) % 2 == 0:
            inner_rect = pygame.Rect(
                self.position[0] * GRID_SIZE + 4,
                self.position[1] * GRID_SIZE + 4,
                GRID_SIZE - 8,
                GRID_SIZE - 8
            )
            pygame.draw.rect(surface, (255, 255, 200), inner_rect)

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (40, 90, 40), self.rect, 3, border_radius=10)
        
        # 确保文本渲染使用正确的字体
        text_surf = font_small.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                return self.action()
        return False

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.mode = GameMode.CLASSIC
        self.game_over = False
        self.paused = False
        self.high_score = self.load_high_score()
        self.start_time = 0
        self.game_time = 0
        self.obstacles = []
        self.generate_obstacles()
        self.menu_active = True
        self.current_screen = "main_menu"
        self.init_menu()
        
    def init_menu(self):
        # 创建菜单按钮
        center_x = SCREEN_WIDTH // 2
        self.menu_buttons = [
            Button(center_x - 100, 200, 200, 50, "开始游戏", self.start_game),
            Button(center_x - 100, 270, 200, 50, "选择模式", self.show_mode_menu),
            Button(center_x - 100, 340, 200, 50, "高分记录", self.show_high_score),
            Button(center_x - 100, 410, 200, 50, "退出游戏", sys.exit)
        ]
        
        # 模式选择按钮
        self.mode_buttons = [
            Button(center_x - 150, 200, 300, 50, "经典模式", lambda: self.select_mode(GameMode.CLASSIC)),
            Button(center_x - 150, 270, 300, 50, "限时模式", lambda: self.select_mode(GameMode.TIMED)),
            Button(center_x - 150, 340, 300, 50, "障碍模式", lambda: self.select_mode(GameMode.OBSTACLE)),
            Button(center_x - 150, 410, 300, 50, "无尽模式", lambda: self.select_mode(GameMode.ENDLESS)),
            Button(center_x - 100, 480, 200, 50, "返回菜单", self.show_main_menu)
        ]
        
        # 游戏结束按钮
        self.game_over_buttons = [
            Button(center_x - 100, 400, 200, 50, "重新开始", self.restart_game),
            Button(center_x - 100, 470, 200, 50, "返回菜单", self.show_main_menu)
        ]
    
    def start_game(self):
        self.menu_active = False
        self.game_over = False
        self.paused = False
        self.start_time = time.time()
        return True
        
    def show_mode_menu(self):
        self.current_screen = "mode_menu"
        return True
        
    def show_high_score(self):
        self.current_screen = "high_score"
        return True
        
    def show_main_menu(self):
        self.current_screen = "main_menu"
        return True
        
    def select_mode(self, mode):
        self.mode = mode
        self.restart_game()
        self.start_game()
        return True
        
    def restart_game(self):
        self.snake.reset()
        self.food.randomize_position(self.snake.positions, self.obstacles)
        self.game_over = False
        self.paused = False
        self.start_time = time.time()
        self.game_time = 0
        self.generate_obstacles()
        return True
        
    def load_high_score(self):
        try:
            with open("high_score.json", "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except:
            return 0
            
    def save_high_score(self):
        if self.snake.score > self.high_score:
            self.high_score = self.snake.score
            with open("high_score.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
                
    def generate_obstacles(self):
        self.obstacles = []
        if self.mode == GameMode.OBSTACLE:
            for _ in range(15):
                while True:
                    obstacle = (random.randint(0, GRID_WIDTH - 1), 
                               random.randint(0, GRID_HEIGHT - 1))
                    if (obstacle not in self.snake.positions and 
                        obstacle != self.food.position and
                        obstacle not in self.obstacles):
                        self.obstacles.append(obstacle)
                        break
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if self.menu_active:
                mouse_pos = pygame.mouse.get_pos()
                if self.current_screen == "main_menu":
                    for button in self.menu_buttons:
                        button.check_hover(mouse_pos)
                        if button.handle_event(event):
                            return
                elif self.current_screen == "mode_menu":
                    for button in self.mode_buttons:
                        button.check_hover(mouse_pos)
                        if button.handle_event(event):
                            return
                elif self.current_screen == "high_score":
                    for button in self.game_over_buttons[:1]:  # 只显示返回按钮
                        button.check_hover(mouse_pos)
                        if button.handle_event(event):
                            return
            elif self.game_over:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.game_over_buttons:
                    button.check_hover(mouse_pos)
                    if button.handle_event(event):
                        return
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(Direction.RIGHT)
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_active = True
                        self.current_screen = "main_menu"
    
    def update(self):
        if self.menu_active or self.game_over or self.paused:
            return
            
        # 更新时间
        if self.mode == GameMode.TIMED:
            self.game_time = 60 - (time.time() - self.start_time)
            if self.game_time <= 0:
                self.game_over = True
                self.save_high_score()
                return
        
        # 更新蛇的位置
        if not self.snake.update():
            self.game_over = True
            self.save_high_score()
            return
            
        # 检查是否吃到食物
        head = self.snake.get_head_position()
        if head == self.food.position:
            # 计算分数
            points = 3 if self.food.is_special else 1
            self.snake.score += points
            self.snake.grow_to += points
            
            # 生成新食物
            self.food.randomize_position(self.snake.positions, self.obstacles)
            
            # 播放音效
            pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=bytearray(1000)))  # 简化音效
            
        # 检查碰撞障碍物
        if self.mode == GameMode.OBSTACLE and head in self.obstacles:
            self.game_over = True
            self.save_high_score()
            
        # 检查经典模式撞墙
        if self.mode == GameMode.CLASSIC:
            if (head[0] < 0 or head[0] >= GRID_WIDTH or 
                head[1] < 0 or head[1] >= GRID_HEIGHT):
                self.game_over = True
                self.save_high_score()
    
    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))
    
    def draw_obstacles(self):
        for pos in self.obstacles:
            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, 
                             GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, OBSTACLE_COLOR, rect)
            pygame.draw.rect(screen, (70, 70, 100), rect, 2)
    
    def draw_ui(self):
        # 绘制分数
        score_text = font_small.render(f"分数: {self.snake.score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))
        
        # 绘制最高分
        high_score_text = font_small.render(f"最高分: {self.high_score}", True, TEXT_COLOR)
        screen.blit(high_score_text, (20, 60))
        
        # 绘制时间（限时模式）
        if self.mode == GameMode.TIMED:
            time_text = font_small.render(f"时间: {int(self.game_time)}秒", True, TEXT_COLOR)
            screen.blit(time_text, (SCREEN_WIDTH - 150, 20))
        
        # 暂停提示
        if self.paused:
            pause_text = font_medium.render("游戏暂停", True, TEXT_COLOR)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, 30))
            screen.blit(pause_text, text_rect)
    
    def draw_menu(self):
        # 绘制半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 30, 0, 200))
        screen.blit(overlay, (0, 0))
        
        if self.current_screen == "main_menu":
            # 标题
            title = font_large.render("贪吃蛇游戏", True, TEXT_COLOR)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
            screen.blit(title, title_rect)
            
            # 绘制按钮
            for button in self.menu_buttons:
                button.draw(screen)
                
        elif self.current_screen == "mode_menu":
            # 标题
            title = font_medium.render("选择游戏模式", True, TEXT_COLOR)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
            screen.blit(title, title_rect)
            
            # 绘制按钮
            for button in self.mode_buttons:
                button.draw(screen)
                
        elif self.current_screen == "high_score":
            # 标题
            title = font_medium.render("高分记录", True, TEXT_COLOR)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
            screen.blit(title, title_rect)
            
            # 高分显示
            score_text = font_large.render(str(self.high_score), True, TEXT_COLOR)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 250))
            screen.blit(score_text, score_rect)
            
            # 返回按钮
            self.game_over_buttons[1].draw(screen)
    
    def draw_game_over(self):
        # 绘制半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 游戏结束文本
        game_over_text = font_large.render("游戏结束", True, TEXT_COLOR)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(game_over_text, text_rect)
        
        # 分数显示
        score_text = font_medium.render(f"最终分数: {self.snake.score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(score_text, score_rect)
        
        # 最高分显示
        high_score_text = font_small.render(f"最高分: {self.high_score}", True, TEXT_COLOR)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        screen.blit(high_score_text, high_score_rect)
        
        # 绘制按钮
        for button in self.game_over_buttons:
            button.draw(screen)
    
    def render(self):
        screen.fill(BACKGROUND)
        
        if not self.menu_active:
            self.draw_grid()
            self.draw_obstacles()
            self.snake.render(screen)
            self.food.render(screen)
            self.draw_ui()
            
            if self.game_over:
                self.draw_game_over()
        else:
            self.draw_menu()
        
        pygame.display.flip()

# 创建游戏实例
game = Game()

# 主游戏循环
while True:
    game.handle_events()
    game.update()
    game.render()
    clock.tick(FPS)