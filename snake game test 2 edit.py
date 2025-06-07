import pygame
import time
import random

# Initialize pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0,)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Display settings
WIDTH = 600
HEIGHT = 400
SNAKE_SIZE = 10
SPEED = 15

# Initialize display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock to control game speed
clock = pygame.time.Clock()

# Font settings
font_style = pygame.font.SysFont("bahnschrift", 25)
def message(msg, color, x, y):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [x, y])

def gameLoop():
    game_over = False
    game_close = False
    
    x = WIDTH / 2
    y = HEIGHT / 2
    x_change = 0
    y_change = 0
    
    snake = []
    length = 1
    
    food_x = round(random.randrange(0, WIDTH - SNAKE_SIZE) / 10.0) * 10.0
    food_y = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / 10.0) * 10.0
    
    while not game_over:
        while game_close:
            screen.fill(BLACK)
            message("You Lost! Press Q-Quit or C-Play Again", RED, WIDTH / 6, HEIGHT / 3)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()
                        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type ==pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -SNAKE_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = SNAKE_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -SNAKE_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = SNAKE_SIZE
                    x_change = 0
                    
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True
            
        x += x_change
        y += y_change
        screen.fill(BLACK)
        pygame.draw.rect(screen, GREEN, [food_x, food_y, SNAKE_SIZE, SNAKE_SIZE])
        
        snake.append([x, y])
        if len(snake) > length:
            del snake[0]
        
        for segment in snake[:-1]:
            if segment == [x, y]:
                game_close = True
                
        for segment in snake:
            pygame.draw.rect(screen, BLUE, [segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE])
        
        pygame.display.update()
        
        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, WIDTH - SNAKE_SIZE) / 10.0) * 10.0
            food_y = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / 10.0) * 10.0
            length += 1
            
        clock.tick(SPEED)
        
    pygame.quit()
    quit()
    
gameLoop()