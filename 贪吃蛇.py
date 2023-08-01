# 导入所需的模块
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"]="" # 隐藏 pygame 的欢迎信息
import pygame
import random
from cryptography.fernet import Fernet
import sys
import win32con, win32api

# 初始化游戏
pygame.init()

# 定义游戏窗口大小和游戏速度
window_width, window_height = 640, 480
game_speed = 15
stage_length = 5

# 定义颜色
white = pygame.Color(245, 245, 247)
black = pygame.Color(29, 29, 31)
red = pygame.Color(191, 0, 19)
green = pygame.Color(1, 217, 90)
blue = pygame.Color(0, 119, 237)
yellow = pygame.Color(249, 228, 121)

# 创建游戏窗口
game_window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Snake')

# 定义游戏时钟
clock = pygame.time.Clock()

# 定义蛇的初始位置和大小
snake_head = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_direction = "RIGHT"

# 定义食物的初始位置
food_position = [random.randrange(1, (window_width // 10)) * 10, random.randrange(1, (window_height // 10)) * 10]

# 定义初始分数
score = 0

# 凯撒密码
def caesar_cipher(text, shift, alphabets):
    def shift_alphabet(alphabet):
        return alphabet[shift:] + alphabet[:shift]

    shifted_alphabets = tuple(map(shift_alphabet, alphabets))
    joined_aphabets = ''.join(alphabets)
    joined_shifted_alphabets = ''.join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)
    return text.translate(table)

message = ''
shift = random.randint(0, 26)
alphabets = (u'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-=~!@#$%^&*()_+[];,./:<>?', u'abcdefghijklmnopqrstuvwxyz1234567890-=~!@#$%^&*()_+[];,./:<>?')

# 加密存档
def locksave():
    global score, message, shift, alphabets

    # 加载密钥
    with open('savekey.key', 'rb') as filekey:
        key = filekey.read()
 
    # 使用密钥初始化 Fernet 对象
    fernet = Fernet(key)

    # 加密文件
    encrypted = fernet.encrypt(str(score).encode())
 
    # 以写入模式打开文件并写入加密数据
    with open('snake.bcd', 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

    # 混淆
    message = str(score)
    encrypted_message = caesar_cipher(message, shift, alphabets)
    lock_text = 'message: ' + str(encrypted_message) + '\nshift: ' + str(shift) + '\nalphabets: ' + str(alphabets)
    encryptedd = fernet.encrypt(str(lock_text).encode())
    
    with open('score.save', 'wb') as encrypted_file:
        encrypted_file.write(encryptedd)

# 解密存档
def unlocksave():   
    # 加载密钥
    with open('savekey.key', 'rb') as filekey:
        key = filekey.read()
        
    # 使用密钥初始化 Fernet 对象
    fernet = Fernet(key)
 
    # 读取加密后的文件
    with open('snake.bcd', 'rb') as enc_file:
        encrypted = enc_file.read()
 
    # 解密文件
    top_score = fernet.decrypt(encrypted)

    return top_score

# 判断是否有存档文件
save_file = 'snake.bcd'
if os.path.isfile(save_file) and os.path.isfile('savekey.key') and os.path.isfile('score.save'):
    None
else:
    if os.path.isfile(save_file):
        os.remove(save_file)
    if os.path.isfile('savekey.key'):
        os.remove('savekey.key')
    if os.path.isfile('score.save'):
        os.remove('score.save')

    # 生成密钥
    key = Fernet.generate_key()

    # 写入密钥
    with open('savekey.key', 'wb') as filekey:
        filekey.write(key)

    win32api.SetFileAttributes('savekey.key', win32con.FILE_ATTRIBUTE_HIDDEN)

    # 新建存档
    locksave()

# 加载最高纪录
top_score = int(unlocksave())

# 游戏结束函数
def game_over():
    # 写存档
    if score > top_score:
        locksave()

    # 写文字
    font = pygame.font.Font('fonts.ttf', 80)
    text = font.render('Game Over', True, blue)
    game_window.blit(text, (window_width / 2 - text.get_width() / 2, window_height / 2 - text.get_height() / 2))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 监听键盘事件，控制蛇的移动方向
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_direction != "DOWN":
                snake_direction = "UP"
            elif event.key == pygame.K_DOWN and snake_direction != "UP":
                snake_direction = "DOWN"
            elif event.key == pygame.K_LEFT and snake_direction != "RIGHT":
                snake_direction = "LEFT"
            elif event.key == pygame.K_RIGHT and snake_direction != "LEFT":
                snake_direction = "RIGHT"

    # 更新蛇的位置
    if snake_direction == "UP":
        snake_head[1] -= 10
    elif snake_direction == "DOWN":
        snake_head[1] += 10
    elif snake_direction == "LEFT":
        snake_head[0] -= 10
    elif snake_direction == "RIGHT":
        snake_head[0] += 10

    # 增加蛇的长度
    snake_body.insert(0, list(snake_head))

    # 判断是否吃到食物
    if snake_head[0] == food_position[0] and snake_head[1] == food_position[1]:
        score += 1
        food_position = [random.randrange(1, (window_width // 10)) * 10, random.randrange(1, (window_height // 10)) * 10]

        # 检查蛇的长度是否达到阶段长度
        if len(snake_body) % stage_length == 0:
            game_speed += 1  # 增加游戏速度

        # 重写存档
        if score > top_score:
            locksave()

    else:
        snake_body.pop()

    # 判断游戏是否结束
    if snake_head[0] < 0 or snake_head[0] >= window_width or snake_head[1] < 0 or snake_head[1] >= window_height or \
            list(snake_head) in snake_body[1:]:
        game_over()

    # 绘制游戏窗口
    game_window.fill(black)
    for position in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(position[0], position[1], 10, 10))
    pygame.draw.rect(game_window, red, pygame.Rect(food_position[0], food_position[1], 10, 10))

    # 绘制分数与最高分数
    font = pygame.font.Font('fonts.ttf', 18)
    score_text = font.render("Score: " + str(score), True, white)
    game_window.blit(score_text, (5, 5))
    if top_score == 0:
        None
    elif top_score >= 0:
        if score <= top_score:
            score_text = font.render("Top Score: " + str(top_score), True, white)
            new_score_text = font.render("", True, white)
        elif score > top_score:
            score_text = font.render("Top Score: " + str(score), True, white)
            new_score_text = font.render("New High Score!", True, yellow)

        game_window.blit(new_score_text, (5, 45))
        game_window.blit(score_text, (5, 25))

    # 刷新游戏窗口
    pygame.display.flip()

    # 控制游戏速度
    clock.tick(game_speed)
