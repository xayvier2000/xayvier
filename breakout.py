# Import required libraries
import pygame, sqlite3, random

# Initialize Pygame and set up game constants
pygame.init()
DIMS = {'SCREEN': (800, 600), 'PADDLE': (100, 15), 'BRICK': (60, 20), 'BALL': 10}
COLORS = {'WHITE': (255,255,255), 'BLUE': (0,0,255), 'RED': (255,0,0), 'GREEN': (0,255,0)}

class Breakout:
    def __init__(self):
        # Set up the game window and initial settings
        self.screen = pygame.display.set_mode(DIMS['SCREEN'])
        pygame.display.set_caption("Breakout Game")
        self.font = pygame.font.Font(None, 36)
        self.db_path = r"C:\\Users\\BIS1\\Desktop\\Notes Python\\highscores.db"
        # Create high scores database if it doesn't exist
        with sqlite3.connect(self.db_path) as conn:
            conn.cursor().execute('CREATE TABLE IF NOT EXISTS highscores (name TEXT, score INTEGER)')
        self.reset_game(1, True)
        
    def reset_game(self, level, full_reset=False):
        # Reset game state for new level or game over
        if full_reset: self.score, self.lives, self.level = 0, 3, level
        else: self.level = level
        # Position paddle and ball
        self.paddle = pygame.Rect(DIMS['SCREEN'][0]//2 - DIMS['PADDLE'][0]//2, DIMS['SCREEN'][1]-30, *DIMS['PADDLE'])
        self.ball = pygame.Rect(DIMS['SCREEN'][0]//2 - DIMS['BALL'], DIMS['SCREEN'][1]-50, DIMS['BALL']*2, DIMS['BALL']*2)
        # Set ball speed based on level
        self.ball_dx = self.ball_dy = 4 + (level - 1); self.ball_dy *= -1
        # Generate bricks with increasing difficulty per level
        self.bricks = [pygame.Rect(col*(DIMS['BRICK'][0]+5)+(DIMS['SCREEN'][0]-(min(10+level-1,13)*(DIMS['BRICK'][0])))//2,
                        row*(DIMS['BRICK'][1]+5)+80, *DIMS['BRICK'])
                        for row in range(min(5+level-1,8)) for col in range(min(10+level-1,13))]
                        
    def get_high_score(self):
        # Retrieve highest score from database
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.cursor().execute("SELECT name,score FROM highscores ORDER BY score DESC LIMIT 1").fetchone()
                return result if result else (None, 0)
        except: return (None, 0)
    
    def save_high_score(self):
        # Save new high score if current score is higher
        if self.score > self.get_high_score()[1]:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM highscores")
                c.execute("INSERT INTO highscores VALUES (?,?)", (self.player_name, self.score))
                
    def run(self):
        # Handle player name input screen
        name_input = ""; clock = pygame.time.Clock()
        while True:
            self.screen.fill(COLORS['WHITE'])
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name_input.strip():
                        self.player_name = name_input.strip()
                        return self.game_loop()
                    elif event.key == pygame.K_BACKSPACE: name_input = name_input[:-1]
                    elif len(name_input) < 15 and (event.unicode.isalnum() or event.unicode.isspace()):
                        name_input += event.unicode
            # Draw name input prompt
            self.screen.blit(self.font.render("Enter your name (press Enter when done):", True, COLORS['RED']),
                            (DIMS['SCREEN'][0]//4, DIMS['SCREEN'][1]//2-50))
            self.screen.blit(self.font.render(name_input+"|", True, COLORS['RED']),
                            (DIMS['SCREEN'][0]//4, DIMS['SCREEN'][1]//2))
            pygame.display.flip(); clock.tick(60)
            
    def game_loop(self):
        # Main game loop
        clock = pygame.time.Clock()
        while True:
            self.screen.fill(COLORS['WHITE'])
            if pygame.event.get(pygame.QUIT): return
            
            # Handle paddle movement
            keys = pygame.key.get_pressed()
            self.paddle.x = max(0, min(DIMS['SCREEN'][0]-DIMS['PADDLE'][0],
                                self.paddle.x + (keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*8))
            
            # Move ball
            self.ball.x += self.ball_dx; self.ball.y += self.ball_dy
            
            # Handle ball collision with walls
            if self.ball.left <= 0: self.ball.left,self.ball_dx = 0,abs(self.ball_dx)
            elif self.ball.right >= DIMS['SCREEN'][0]: self.ball.right,self.ball_dx = DIMS['SCREEN'][0],-abs(self.ball_dx)
            if self.ball.top <= 0: self.ball.top,self.ball_dy = 0,abs(self.ball_dy)
            
            # Handle ball collision with walls
            if self.ball.colliderect(self.paddle):
                self.ball.bottom = self.paddle.top
                self.ball_dx = max(min(-((self.paddle.centerx-self.ball.centerx)/(DIMS['PADDLE'][0]/2))*5, 8), -8)
                self.ball_dy = -max(abs(self.ball_dy), 4)
                
            # Handle ball collision with bricks
            for brick in self.bricks[:]:
                if self.ball.colliderect(brick):
                    self.bricks.remove(brick); self.score += 10*self.level
                    self.ball_dx,self.ball_dy = ([-self.ball_dx,self.ball_dx][self.ball.centerx>=brick.left and
                                                self.ball.centerx<=brick.right], [-self.ball_dy,self.ball_dy]
                                                [self.ball.centerx<brick.left or self.ball.centerx>brick.right])
                    
            # Check for lost ball and handle lives
            if self.ball.top >= DIMS['SCREEN'][1]:
                self.lives -= 1
                if self.lives <= 0: self.save_high_score(); self.reset_game(1, True)
                # Randomize the ball's direction and speed slightly to make the game less predictable
                else: self.ball = pygame.Rect(DIMS['SCREEN'][0]//2 - DIMS['BALL'], DIMS['SCREEN'][1]-50, DIMS['BALL']*2, DIMS['BALL']*2)
                self.ball_dx = random.choice([-4,4])    # Random horizontal speed direction
                self.ball_dy = -4                        # Keep the vertical direction going up initially
                
            # Check for level completion
            if not self.bricks: self.reset_game(self.level+1)
            
            # Draw game elements
            [pygame.draw.rect(self.screen,COLORS['GREEN'],brick) for brick in self.bricks]
            pygame.draw.rect(self.screen, COLORS['BLUE'], self.paddle)
            pygame.draw.circle(self.screen, COLORS['RED'], self.ball.center, DIMS['BALL'])
            
            # Update and display scores
            high_score = self.get_high_score()
            [self.screen.blit(self.font.render(text,True,COLORS['RED']),pos) for text,pos in
             [(f"Score: {self.score}",(10,10)),(f"Lives: {self.lives}",(DIMS['SCREEN'][0]//2-50,10)),
              (f"Level: {self.level}",(DIMS['SCREEN'][0]-150,10)),
              (f"High Score: {max(self.score,high_score[1])} ({self.player_name if self.score>high_score[1] else high_score[0] or self.player_name})",
               (10,40))]]
            
            pygame.display.flip(); clock.tick(60)
            
# Start the game
if __name__ == "__main__": Breakout().run()
            