import pygame
import random
import math
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Load images
def load_image(name, scale=1):
    try:
        image = pygame.Surface((50, 40))
        image.fill(BLUE)
        if scale != 1:
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] * scale)))
        return image
    except:
        print(f"Error loading image: {name}")
        return pygame.Surface((50, 40))

# Load sounds
def load_sound(name):
    try:
        return pygame.mixer.Sound(f"sounds/{name}")
    except:
        print(f"Error loading sound: {name}")
        return None

# Create sounds directory if it doesn't exist
if not os.path.exists("sounds"):
    os.makedirs("sounds")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("player.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5
        self.health = 100
        self.shoot_delay = 250  # milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.shield = 100
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

        # Power-up timeout
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > 5000:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.top)
                bullet2 = Bullet(self.rect.right, self.rect.top)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("enemy.png", 0.6)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 3)
        self.health = 30

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed = random.randint(1, 3)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 7

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.type = random.choice(['shield', 'gun'])
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == 8:
                self.kill()

# Button class for menu
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Create buttons
start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 25, 200, 50, "Начать играть", BLUE, (0, 0, 200))
quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Выйти из игры", RED, (200, 0, 0))

# Game variables
score = 0
high_score = 0
clock = pygame.time.Clock()
running = True

# Load high score
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0

# Game loop
while running:
    # Keep loop running at the right speed
    clock.tick(60)
    
    # Process input/events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == MENU:
            mouse_pos = pygame.mouse.get_pos()
            start_button.check_hover(mouse_pos)
            quit_button.check_hover(mouse_pos)
            
            if start_button.is_clicked(mouse_pos, event):
                game_state = PLAYING
                # Reset game
                all_sprites.empty()
                enemies.empty()
                bullets.empty()
                powerups.empty()
                player = Player()
                all_sprites.add(player)
                score = 0
                for i in range(8):
                    enemy = Enemy()
                    all_sprites.add(enemy)
                    enemies.add(enemy)
            
            if quit_button.is_clicked(mouse_pos, event):
                running = False
        
        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
        
        elif game_state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = MENU

    # Update
    if game_state == PLAYING:
        all_sprites.update()

        # Check for collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullet_list in hits.items():
            enemy.health -= 10
            if enemy.health <= 0:
                score += 10
                expl = Explosion(enemy.rect.center, 50)
                all_sprites.add(expl)
                enemy.kill()
                # Chance to spawn powerup
                if random.random() > 0.9:
                    pow = PowerUp(enemy.rect.center)
                    all_sprites.add(pow)
                    powerups.add(pow)
                # Spawn new enemy
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)

        hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in hits:
            player.shield -= 20
            expl = Explosion(hit.rect.center, 50)
            all_sprites.add(expl)
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            if player.shield <= 0:
                player.health -= 1
                player.shield = 100
                if player.health <= 0:
                    game_state = GAME_OVER
                    # Save high score
                    if score > high_score:
                        high_score = score
                        with open("highscore.txt", "w") as f:
                            f.write(str(high_score))

        # Check for powerup collisions
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                player.shield += random.randrange(10, 30)
                if player.shield >= 100:
                    player.shield = 100
            if hit.type == 'gun':
                player.power += 1
                player.power_time = pygame.time.get_ticks()

    # Draw / render
    screen.fill(BLACK)
    
    if game_state == MENU:
        # Draw menu
        font = pygame.font.Font(None, 74)
        title = font.render("SPACE SHOOTER", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(title, title_rect)
        
        start_button.draw(screen)
        quit_button.draw(screen)
        
        font = pygame.font.Font(None, 36)
        high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(high_score_text, (WIDTH//2 - 100, HEIGHT//2 + 150))
    
    elif game_state == PLAYING:
        # Draw game
        all_sprites.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw health bar
        pygame.draw.rect(screen, RED, (10, 50, 200, 20))
        pygame.draw.rect(screen, GREEN, (10, 50, player.health * 2, 20))
        
        # Draw shield bar
        pygame.draw.rect(screen, BLUE, (10, 80, 200, 20))
        pygame.draw.rect(screen, WHITE, (10, 80, player.shield * 2, 20))
    
    elif game_state == GAME_OVER:
        # Draw game over screen
        font = pygame.font.Font(None, 74)
        game_over = font.render("GAME OVER", True, RED)
        game_over_rect = game_over.get_rect(center=(WIDTH//2, HEIGHT//3))
        screen.blit(game_over, game_over_rect)
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Final Score: {score}', True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(score_text, score_rect)
        
        restart_text = font.render("Press ENTER to return to menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        screen.blit(restart_text, restart_rect)

    # Flip the display
    pygame.display.flip()

pygame.quit() 