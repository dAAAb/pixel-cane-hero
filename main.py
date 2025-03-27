# -*- coding: utf-8 -*-
import pygame
import sys
import random
import os
from pygame.locals import *

# 初始化pygame
pygame.init()

# 游戏设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
TILE_SIZE = 32

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# 创建窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('像素拐杖侠')
clock = pygame.time.Clock()

# 游戏变量
gravity = 0.5
scroll_thresh = 200
scroll = 0
bg_scroll = 0
game_over = False
score = 0
font = pygame.font.SysFont('Arial', 24)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE * 2))
        # 简单的像素图形 - 绿色西装老人
        self.image.fill(GREEN)
        # 使用pixel_ko.png作为头部
        head_image_path = os.path.join('assets', 'pixel_ko.png')
        if os.path.exists(head_image_path):
            head = pygame.image.load(head_image_path).convert_alpha()
        else:
            # 如果图片不存在，回退到简单的白色头部
            head = pygame.Surface((TILE_SIZE, TILE_SIZE // 2))
            head.fill(WHITE)
        self.image.blit(head, (0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 1  # 1 for right, -1 for left
        self.in_air = True
        self.cane = True  # 是否有完整拐杖
        self.cane_cooldown = 0
        self.attack_cooldown = 0

    def update(self, platforms):
        dx = 0
        dy = 0

        # 处理按键
        key = pygame.key.get_pressed()
        if key[K_LEFT]:
            dx = -5
            self.direction = -1
        if key[K_RIGHT]:
            dx = 5
            self.direction = 1
        if key[K_UP] and not self.jumped and not self.in_air:
            self.vel_y = -15
            self.jumped = True
            self.in_air = True
        if not key[K_UP]:
            self.jumped = False
        
        # 处理攻击 - 空格键
        if key[K_SPACE] and self.attack_cooldown == 0:
            self.attack()
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.cane_cooldown > 0:
            self.cane_cooldown -= 1
            if self.cane_cooldown == 0:
                self.cane = True

        # 应用重力
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # 检查碰撞
        self.in_air = True
        for platform in platforms:
            # 水平碰撞
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            
            # 垂直碰撞
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # 检查是否在平台上
                if self.vel_y < 0:
                    dy = platform.rect.bottom - self.rect.top
                    self.vel_y = 0
                # 检查是否在平台下
                elif self.vel_y >= 0:
                    dy = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        # 更新位置
        self.rect.x += dx
        self.rect.y += dy

        # 确保不会移出屏幕
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        
        # 检查是否坠落
        if self.rect.top > WINDOW_HEIGHT:
            return False
        
        return True
    
    def attack(self):
        self.attack_cooldown = 20
        if self.cane:
            # 1/3的几率拐杖会断掉并射出
            if random.random() < 0.3:
                self.cane = False
                self.cane_cooldown = 120  # 拐杖恢复时间
                cane_projectiles.add(CaneProjectile(self.rect.centerx, self.rect.centery, self.direction))
            return True
        return False
    
    def draw(self):
        screen.blit(self.image, (self.rect.x - scroll, self.rect.y))
        # 绘制拐杖
        if self.cane:
            cane = pygame.Surface((TILE_SIZE, TILE_SIZE // 4))
            cane.fill((139, 69, 19))  # 棕色拐杖
            if self.direction == 1:
                screen.blit(cane, (self.rect.right - scroll, self.rect.centery))
            else:
                screen.blit(cane, (self.rect.left - TILE_SIZE - scroll, self.rect.centery))


class CaneProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 4))
        self.image.fill((139, 69, 19))  # 棕色拐杖
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.direction = direction
        self.speed = 10
    
    def update(self):
        self.rect.x += self.speed * self.direction
        
        # 如果移出屏幕则删除
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()
        
        # 检查与敌人的碰撞
        for enemy in enemies:
            if pygame.sprite.collide_rect(self, enemy):
                enemy.kill()
                global score
                score += 10


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = random.choice([-1, 1])
        self.move_counter = 0
        self.move_distance = random.randint(30, 100)
    
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_counter >= self.move_distance:
            self.move_direction *= -1
            self.move_counter = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# 创建精灵组
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
cane_projectiles = pygame.sprite.Group()

# 创建地面
ground = Platform(0, WINDOW_HEIGHT - TILE_SIZE, WINDOW_WIDTH * 3, TILE_SIZE)
platforms.add(ground)
all_sprites.add(ground)

# 创建平台
for i in range(10):
    x = random.randint(0, WINDOW_WIDTH * 2)
    y = random.randint(WINDOW_HEIGHT // 2, WINDOW_HEIGHT - TILE_SIZE * 3)
    width = random.randint(3, 8) * TILE_SIZE
    platform = Platform(x, y, width, TILE_SIZE)
    platforms.add(platform)
    all_sprites.add(platform)

# 创建敌人
for i in range(5):
    x = random.randint(WINDOW_WIDTH // 2, WINDOW_WIDTH * 2)
    y = random.randint(0, WINDOW_HEIGHT - TILE_SIZE * 2)
    enemy = Enemy(x, y)
    enemies.add(enemy)
    all_sprites.add(enemy)

# 创建玩家
player = Player(100, WINDOW_HEIGHT - TILE_SIZE * 3)
all_sprites.add(player)

# 游戏主循环
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    
    if not game_over:
        # 更新玩家
        if not player.update(platforms):
            game_over = True
        
        # 更新拐杖投射物
        cane_projectiles.update()
        
        # 更新敌人
        enemies.update()
        
        # 检查玩家与敌人的碰撞
        if pygame.sprite.spritecollide(player, enemies, False):
            game_over = True
        
        # 更新屏幕滚动
        if player.rect.right > WINDOW_WIDTH - scroll_thresh and player.rect.x < WINDOW_WIDTH * 2:
            scroll += player.rect.right - (WINDOW_WIDTH - scroll_thresh)
            player.rect.right = WINDOW_WIDTH - scroll_thresh
    
    # 绘制背景
    screen.fill(BLACK)
    
    # 绘制精灵
    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - scroll, sprite.rect.y))
    
    # 绘制玩家
    player.draw()
    
    # 绘制拐杖投射物
    for projectile in cane_projectiles:
        screen.blit(projectile.image, (projectile.rect.x - scroll, projectile.rect.y))
    
    # 绘制分数
    score_text = font.render('Score: {}'.format(score), True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # 游戏结束画面
    if game_over:
        game_over_text = font.render('Game Over!', True, WHITE)
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 - 20))
        restart_text = font.render('Press R to restart', True, WHITE)
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 20))
        
        # 重启游戏
        key = pygame.key.get_pressed()
        if key[K_r]:
            # 重置游戏
            all_sprites.empty()
            platforms.empty()
            enemies.empty()
            cane_projectiles.empty()
            
            # 重新创建地面
            ground = Platform(0, WINDOW_HEIGHT - TILE_SIZE, WINDOW_WIDTH * 3, TILE_SIZE)
            platforms.add(ground)
            all_sprites.add(ground)
            
            # 重新创建平台
            for i in range(10):
                x = random.randint(0, WINDOW_WIDTH * 2)
                y = random.randint(WINDOW_HEIGHT // 2, WINDOW_HEIGHT - TILE_SIZE * 3)
                width = random.randint(3, 8) * TILE_SIZE
                platform = Platform(x, y, width, TILE_SIZE)
                platforms.add(platform)
                all_sprites.add(platform)
            
            # 重新创建敌人
            for i in range(5):
                x = random.randint(WINDOW_WIDTH // 2, WINDOW_WIDTH * 2)
                y = random.randint(0, WINDOW_HEIGHT - TILE_SIZE * 2)
                enemy = Enemy(x, y)
                enemies.add(enemy)
                all_sprites.add(enemy)
            
            # 重新创建玩家
            player = Player(100, WINDOW_HEIGHT - TILE_SIZE * 3)
            all_sprites.add(player)
            
            # 重置游戏变量
            scroll = 0
            game_over = False
            score = 0
    
    pygame.display.update()

pygame.quit()
sys.exit()
