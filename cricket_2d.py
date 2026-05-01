#Lumina cricket game 
import pygame
import random
import math
import sys
import os

# --- Configuration & Constants ---
WIDTH, HEIGHT = 800, 800
FPS = 60

# Colors (Premium Modern Palette)
GREEN_DARK = (15, 40, 15)
GREEN_VIBRANT = (46, 125, 50)
PITCH_COLOR = (245, 222, 179)
WHITE_DIM = (220, 220, 220)
WHITE_BRIGHT = (255, 255, 255)
BALL_RED = (230, 0, 0)
BALL_HIGHLIGHT = (255, 100, 100)
BAT_WOOD = (101, 67, 33)
ACCENT_YELLOW = (255, 215, 0)
BLACK_GLASS = (20, 20, 20, 180)
SHADOW_COLOR = (0, 0, 0, 100)

# Game Layout
PITCH_X = WIDTH // 2
BATSMAN_Y = 700
BOWLER_Y = 150
PITCH_WIDTH = 140
PITCH_HEIGHT = 600

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.life = 30
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class CricketGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Lumina Cricket Pro 2D")
        self.clock = pygame.time.Clock()
        
        # Load fonts - fallback if specific fonts not found
        try:
            self.font_title = pygame.font.SysFont("Verdana", 72, bold=True)
            self.font_score = pygame.font.SysFont("Consolas", 36, bold=True)
            self.font_ui = pygame.font.SysFont("Verdana", 24)
        except:
            self.font_title = pygame.font.SysFont("Arial", 72, bold=True)
            self.font_score = pygame.font.SysFont("Arial", 36, bold=True)
            self.font_ui = pygame.font.SysFont("Arial", 24)
        
        # Load Assets
        self.grass_img = None
        if os.path.exists("assets/grass.png"):
            try:
                self.grass_img = pygame.image.load("assets/grass.png")
                self.grass_img = pygame.transform.smoothscale(self.grass_img, (WIDTH, HEIGHT))
            except:
                pass
        
        self.reset_game()
        self.high_score = 0
        
    def reset_game(self):
        self.score = 0
        self.wickets = 0
        self.balls_bowled = 0
        self.state = "MENU" # MENU, READY, BOWL, PLAYING, RESULT, GAMEOVER
        
        self.ball_pos = [WIDTH // 2, BOWLER_Y]
        self.ball_vel = [0, 0]
        self.ball_z = 10 # Simulate height
        self.ball_vz = 0
        self.ball_active = False
        
        self.batsman_x = WIDTH // 2
        self.bat_angle = 45 # Idle angle
        self.swing_active = False
        self.swing_timer = 0
        
        self.particles = []
        self.shake_intensity = 0
        self.popup_msg = ""
        self.popup_timer = 0
        self.msg_color = ACCENT_YELLOW

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.state = "READY"
                elif self.state == "READY":
                    if event.key == pygame.K_SPACE:
                        self.bowl_ball()
                elif self.state == "PLAYING" or self.state == "READY":
                    if event.key == pygame.K_SPACE and not self.swing_active:
                        self.swing()
                elif self.state == "GAMEOVER":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.state = "READY"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.batsman_x -= 6
        if keys[pygame.K_RIGHT]: self.batsman_x += 6
        self.batsman_x = max(WIDTH//2 - PITCH_WIDTH//2 + 20, min(WIDTH//2 + PITCH_WIDTH//2 - 20, self.batsman_x))

    def bowl_ball(self):
        self.ball_active = True
        self.state = "PLAYING"
        self.ball_pos = [WIDTH // 2 + random.randint(-10, 10), BOWLER_Y]
        # Speed varies based on "delivery"
        self.ball_vel = [random.uniform(-1.5, 1.5), random.uniform(8, 12)]
        self.ball_z = 40 # Bowler's hand height
        self.ball_vz = -2 # Initial drop

    def swing(self):
        self.swing_active = True
        self.swing_timer = 12 # frames
        
        # Collision Check
        dist_x = abs(self.ball_pos[0] - self.batsman_x)
        dist_y = abs(self.ball_pos[1] - BATSMAN_Y)
        
        if dist_y < 40 and dist_x < 50 and self.ball_active:
            self.hit_ball(dist_x)

    def hit_ball(self, accuracy):
        # The closer accuracy is to 0, the better the shot
        power = (1.0 - (accuracy / 60.0)) * 1.5
        self.ball_vel[1] = -abs(self.ball_vel[1]) * (1.2 + power)
        self.ball_vel[0] = (self.ball_pos[0] - self.batsman_x) * 0.4 + random.uniform(-4, 4)
        self.ball_vz = 8 * power # Send it flying
        self.shake_intensity = 15 if power > 1.2 else 5
        
        # Pop-up text
        if power > 1.3:
            self.trigger_popup("SMASH!!", ACCENT_YELLOW)
        else:
            self.trigger_popup("SHOT!", WHITE_BRIGHT)
            
        # Particles
        for _ in range(12):
            self.particles.append(Particle(self.ball_pos[0], self.ball_pos[1], WHITE_BRIGHT))

    def trigger_popup(self, msg, color):
        self.popup_msg = msg
        self.popup_timer = 45
        self.msg_color = color

    def update(self):
        # Physics
        if self.ball_active:
            self.ball_pos[0] += self.ball_vel[0]
            self.ball_pos[1] += self.ball_vel[1]
            self.ball_z += self.ball_vz
            self.ball_vz -= 0.35 # Gravity
            
            # Bounce
            if self.ball_z < 0:
                self.ball_z = 0
                self.ball_vz = abs(self.ball_vz) * 0.6
                self.ball_vel[0] *= 0.95 # Ground friction
                self.ball_vel[1] *= 0.95
                
                # Dust particles on bounce
                if abs(self.ball_vz) > 1:
                    for _ in range(3):
                        self.particles.append(Particle(self.ball_pos[0], self.ball_pos[1], PITCH_COLOR))

            # Out check (Missed / Hit wickets)
            if self.ball_pos[1] > BATSMAN_Y + 30 and self.ball_vel[1] > 0:
                if abs(self.ball_pos[0] - WIDTH//2) < 15 and self.ball_z < 20:
                    self.out("BOWLED!")
                elif self.ball_pos[1] > HEIGHT:
                    # Dot ball or bye - not out, but reset
                    self.state = "READY"
                    self.ball_active = False

            # Boundary check
            dist_sq = (self.ball_pos[0] - WIDTH//2)**2 + (self.ball_pos[1] - HEIGHT//2)**2
            if dist_sq > 380**2:
                self.calc_runs()

        # Particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        # Shake
        if self.shake_intensity > 0:
            self.shake_intensity -= 1

        # Swing animation
        if self.swing_active:
            self.swing_timer -= 1
            self.bat_angle = -60 + (12 - self.swing_timer) * 10
            if self.swing_timer <= 0:
                self.swing_active = False
                self.bat_angle = 45

    def out(self, reason):
        self.wickets += 1
        self.trigger_popup(reason, (255, 50, 50))
        self.ball_active = False
        if self.wickets >= 10:
            self.state = "GAMEOVER"
        else:
            self.state = "READY"
            self.shake_intensity = 10

    def calc_runs(self):
        # Runs based on speed and height
        # If it's high and fast, it's a 6
        if self.ball_z > 15:
            runs = 6
        else:
            runs = 4
        
        self.score += runs
        self.trigger_popup(f"{runs} RUNS!", ACCENT_YELLOW)
        self.ball_active = False
        self.state = "READY"
        
        if self.score > self.high_score: self.high_score = self.score

    def draw(self):
        # Apply screen shake
        ox = random.randint(-self.shake_intensity, self.shake_intensity) if self.shake_intensity > 0 else 0
        oy = random.randint(-self.shake_intensity, self.shake_intensity) if self.shake_intensity > 0 else 0
        
        # 1. Background
        if self.grass_img:
            self.screen.blit(self.grass_img, (ox, oy))
        else:
            self.screen.fill(GREEN_DARK)
            pygame.draw.circle(self.screen, GREEN_VIBRANT, (WIDTH//2 + ox, HEIGHT//2 + oy), 380)

        # 2. Pitch
        p_rect = pygame.Rect(WIDTH//2 - PITCH_WIDTH//2 + ox, HEIGHT//2 - PITCH_HEIGHT//2 + oy, PITCH_WIDTH, PITCH_HEIGHT)
        pygame.draw.rect(self.screen, PITCH_COLOR, p_rect)
        # Creases
        pygame.draw.line(self.screen, WHITE_DIM, (WIDTH//2 - PITCH_WIDTH//2 + ox, BATSMAN_Y - 20 + oy), (WIDTH//2 + PITCH_WIDTH//2 + ox, BATSMAN_Y - 20 + oy), 3)
        pygame.draw.line(self.screen, WHITE_DIM, (WIDTH//2 - PITCH_WIDTH//2 + ox, BOWLER_Y + 40 + oy), (WIDTH//2 + PITCH_WIDTH//2 + ox, BOWLER_Y + 40 + oy), 3)
        # Stumps (Simple Top-down view)
        for i in [-15, 0, 15]:
            pygame.draw.circle(self.screen, (220, 180, 50), (WIDTH//2 + i + ox, BATSMAN_Y + 15 + oy), 4)

        # 3. Ball Shadow
        if self.ball_active:
            s_scale = max(0.5, 1.0 - (self.ball_z / 100.0))
            shadow_pos = (int(self.ball_pos[0] + self.ball_z*0.5 + ox), int(self.ball_pos[1] + self.ball_z*0.2 + oy))
            # Use a surfacing since circle doesn't support alpha directly in simple draw
            s_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(s_surf, (0, 0, 0, 70), (10, 10), int(8 * s_scale))
            self.screen.blit(s_surf, (shadow_pos[0]-10, shadow_pos[1]-10))

        # 4. Particles
        for p in self.particles:
            p.draw(self.screen)

        # 5. Batsman
        # Body
        pygame.draw.circle(self.screen, (30, 80, 200), (int(self.batsman_x + ox), BATSMAN_Y + oy), 20)
        # Bat
        bat_len = 50
        rad = math.radians(self.bat_angle)
        bx = self.batsman_x + math.sin(rad) * bat_len
        by = BATSMAN_Y + math.cos(rad) * bat_len
        pygame.draw.line(self.screen, BAT_WOOD, (self.batsman_x + ox, BATSMAN_Y + oy), (bx + ox, by + oy), 10)

        # 6. Ball
        if self.ball_active:
            b_size = int(6 + self.ball_z * 0.1)
            pygame.draw.circle(self.screen, BALL_RED, (int(self.ball_pos[0] + ox), int(self.ball_pos[1] + oy)), b_size)
            pygame.draw.circle(self.screen, BALL_HIGHLIGHT, (int(self.ball_pos[0] - 2 + ox), int(self.ball_pos[1] - 2 + oy)), b_size // 3)

        # 7. UI / Scoreboard
        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        # Glassmorphism style scoreboard
        overlay = pygame.Surface((300, 100), pygame.SRCALPHA)
        overlay.fill(BLACK_GLASS)
        self.screen.blit(overlay, (20, 20))
        
        score_surf = self.font_score.render(f"{self.score}/{self.wickets}", True, WHITE_BRIGHT)
        self.screen.blit(score_surf, (40, 30))
        hs_surf = self.font_ui.render(f"High: {self.high_score}", True, ACCENT_YELLOW)
        self.screen.blit(hs_surf, (40, 75))

        if self.state == "MENU":
            modal = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            modal.fill((0, 0, 0, 200))
            self.screen.blit(modal, (0,0))
            
            t1 = self.font_title.render("LUMINA CRICKET", True, ACCENT_YELLOW)
            r1 = t1.get_rect(center=(WIDTH//2, HEIGHT//3))
            self.screen.blit(t1, r1)
            
            t2 = self.font_ui.render("Use Arrow Keys to Move | SPACE to Bat", True, WHITE_BRIGHT)
            r2 = t2.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(t2, r2)
            
            t3 = self.font_ui.render("Press SPACE to Start", True, WHITE_BRIGHT)
            r3 = t3.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
            # Blinking effect
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                self.screen.blit(t3, r3)

        elif self.state == "READY":
            t = self.font_ui.render("PRESS SPACE TO BOWL", True, WHITE_BRIGHT)
            r = t.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(t, r)

        elif self.state == "GAMEOVER":
            modal = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            modal.fill((80, 0, 0, 180))
            self.screen.blit(modal, (0,0))
            t = self.font_title.render("GAME OVER", True, WHITE_BRIGHT)
            r = t.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(t, r)
            t2 = self.font_ui.render(f"Final Score: {self.score} | Press SPACE to Restart", True, WHITE_BRIGHT)
            r2 = t2.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
            self.screen.blit(t2, r2)

        if self.popup_timer > 0:
            p_surf = self.font_title.render(self.popup_msg, True, self.msg_color)
            p_rect = p_surf.get_rect(center=(WIDTH//2, HEIGHT//3))
            # Floating / Fading effect
            p_rect.y -= (45 - self.popup_timer) * 2
            alpha = min(255, self.popup_timer * 6)
            p_surf.set_alpha(alpha)
            self.screen.blit(p_surf, p_rect)
            self.popup_timer -= 1

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = CricketGame()
    game.run()
