from ursina import *
import random
import math

# --- Settings & App Meta ---
app = Ursina()
window.title = "Ultimate 3D Cricket Pro"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# Colors
COLOR_PITCH = color.rgb(210, 180, 140)
COLOR_GRASS = color.rgb(20, 100, 20)
COLOR_BALL = color.rgb(200, 20, 20)

# --- Game State ---
class GameState:
    def __init__(self):
        self.score = 0
        self.wickets = 0
        self.balls = 0
        self.state = 'MENU' # MENU, LOADING, PLAYING, BATTING, RESULT, GAMEOVER
        self.active_ball = False

gs = GameState()

# --- Environment ---
Sky()
ground = Entity(model='plane', scale=300, texture='grass', color=COLOR_GRASS, collider='box')
pitch = Entity(model='cube', scale=(5, 0.1, 24), color=COLOR_PITCH, y=0.01)
# Creases
crease_bat = Entity(model='plane', scale=(5, 1, 0.1), color=color.white, z=-10, y=0.02)
crease_bowl = Entity(model='plane', scale=(5, 1, 0.1), color=color.white, z=10, y=0.02)

# Boundary Rope
boundary = Entity(model='circle', scale=100, color=color.white, rotation_x=90, y=0.03, double_sided=True)

# Stadium (Simple)
stadium = Entity(model='cylinder', scale=(250, 40, 250), color=color.rgb(60, 60, 60), y=-10, side_visible=True, double_sided=True)

# Wickets (Stumps)
class Wickets(Entity):
    def __init__(self, z_pos):
        super().__init__(position=(0, 0, z_pos))
        self.stumps = []
        for x_off in [-0.3, 0, 0.3]:
            s = Entity(parent=self, model='cylinder', scale=(0.1, 1.5, 0.1), color=color.white, x=x_off, y=0.75)
            self.stumps.append(s)
        # Bails
        Entity(parent=self, model='cube', scale=(0.8, 0.05, 0.05), color=color.white, y=1.5)

stumps_batsman = Wickets(-11.5)
stumps_bowler = Wickets(11.5)

# --- Entities ---
class Ball(Entity):
    def __init__(self):
        super().__init__(model='sphere', scale=0.3, color=COLOR_BALL, position=(0, 5, 12), collision=True)
        self.visible = False
        self.velocity = Vec3(0, 0, 0)
        self.gravity = -18
        self.bounce_factor = 0.7
        self.trail = []

    def reset_ball(self):
        self.position = (0, 5, 12)
        self.visible = False
        self.velocity = Vec3(0, 0, 0)
        gs.active_ball = False
        # Clear trail if any
        for t in self.trail: destroy(t)
        self.trail = []

    def update(self):
        if not gs.active_ball: return
        
        # Physics
        self.velocity.y += self.gravity * time.dt
        self.position += self.velocity * time.dt
        
        # Trail
        if (gs.balls % 1 == 0):
            t = Entity(model='sphere', scale=0.1, color=color.orange, alpha=0.5, position=self.position)
            self.trail.append(t)
            if len(self.trail) > 10:
                destroy(self.trail.pop(0))

        # Bounce on pitch
        if self.y < 0.15:
            self.y = 0.15
            self.velocity.y = abs(self.velocity.y) * self.bounce_factor
            # Small dust particle
            dust = Entity(model='sphere', scale=0.2, color=COLOR_PITCH, position=self.position, alpha=0.5)
            dust.animate_scale(1.5, duration=0.2)
            dust.fade_out(duration=0.3)
            destroy(dust, delay=0.4)

        # Boundary Detection
        dist_from_origin = self.position.xz.length()
        if dist_from_origin > 50:
            self.handle_boundary()

        # Bowled / Out Detection
        if self.z < -11.5 and abs(self.x) < 0.5 and self.y < 1.6:
            self.out("BOWLED!")

        # Missed Ball Detection
        if self.z < -15 and gs.active_ball:
            self.missed()

    def handle_boundary(self):
        runs = 6 if self.y > 2 else 4
        gs.score += runs
        show_popup(f"{runs} RUNS!", color.yellow)
        self.reset_ball()
        invoke(start_bowling, delay=1.5)

    def out(self, reason):
        gs.wickets += 1
        show_popup(reason, color.red)
        self.reset_ball()
        camera.shake(duration=0.5)
        if gs.wickets >= 10:
            gs.state = 'GAMEOVER'
        else:
            invoke(start_bowling, delay=2)

    def missed(self):
        gs.active_ball = False
        self.reset_ball()
        invoke(start_bowling, delay=1)

ball = Ball()

class Batsman(Entity):
    def __init__(self):
        super().__init__(model='cube', scale=(1, 2, 0.5), color=color.blue, position=(0, 1, -11))
        self.bat = Entity(parent=self, model='cube', scale=(0.3, 2, 0.1), color=color.brown, x=0.5, y=0.5, z=0.4)
        self.bat.rotation_x = -45
        self.swinging = False

    def update(self):
        if gs.state != 'PLAYING': return
        
        # Movement
        if held_keys['left arrow'] or held_keys['a']: self.x -= 4 * time.dt
        if held_keys['right arrow'] or held_keys['d']: self.x += 4 * time.dt
        self.x = clamp(self.x, -2, 2)

        # Batting
        if held_keys['space'] and not self.swinging:
            self.swing()

    def swing(self):
        self.swinging = True
        self.bat.animate_rotation_x(60, duration=0.1, curve=curve.linear)
        
        # Hit detection
        if ball.visible and (ball.z < -10 and ball.z > -12.5):
            dist = distance_2d(self.x, self.z, ball.x, ball.z)
            if dist < 1.0:
                self.hit_ball(dist)
        
        invoke(self.reset_swing, delay=0.2)
    
    def reset_swing(self):
        self.bat.animate_rotation_x(-45, duration=0.1)
        self.swinging = False

    def hit_ball(self, accuracy):
        # Calculate exit velocity
        power = 1.2 - accuracy # 0.2 to 1.2
        ball.velocity.z = abs(ball.velocity.z) * (1.2 + power)
        ball.velocity.x = (ball.x - self.x) * 10 + random.uniform(-5, 5)
        ball.velocity.y = random.uniform(5, 15) * power
        
        show_popup("CRACK!", color.white)
        camera.shake(duration=0.3)
        # Follow camera
        camera.animate_position((ball.x, ball.y + 10, ball.z - 20), duration=2, curve=curve.out_expo)

batsman = Batsman()

class Bowler(Entity):
    def __init__(self):
        super().__init__(model='cube', scale=(1, 2, 1), color=color.red, position=(0, 1, 13))
    
    def prepare(self):
        self.z = 15
        self.animate_z(11.5, duration=1, curve=curve.linear)
        invoke(self.release, delay=1)
        
    def release(self):
        ball.visible = True
        ball.position = (self.x, 2, self.z)
        gs.active_ball = True
        gs.balls += 1
        # Randomize delivery
        ball.velocity = Vec3(random.uniform(-1, 1), random.uniform(2, 5), -random.uniform(25, 35))
        # Camera reset
        camera.animate_position((0, 6, -20), duration=0.5)

bowler = Bowler()

# --- UI ---
score_ui = Text(text='Score: 0 | Wickets: 0', position=(-0.85, 0.45), scale=2, color=color.white)
msg_ui = Text(text='', scale=4, color=color.yellow, origin=(0, 0), y=0.2)

def update_score():
    score_ui.text = f'Score: {gs.score} | Wickets: {gs.wickets}'

def show_popup(msg, col):
    p = Text(text=msg, scale=1, color=col, origin=(0,0), y=0.3)
    p.animate_scale(10, duration=0.4, curve=curve.out_expo)
    p.fade_out(duration=1)
    destroy(p, delay=1.5)
    update_score()

# --- Game Flow ---
def start_bowling():
    if gs.state == 'GAMEOVER': return
    gs.state = 'PLAYING'
    bowler.prepare()

def input(key):
    if key == 'enter' and (gs.state == 'MENU' or gs.state == 'GAMEOVER'):
        start_game()

def start_game():
    gs.score = 0
    gs.wickets = 0
    gs.state = 'PLAYING'
    update_score()
    start_bowling()
    menu.enabled = False

# Overlay
menu = Entity(parent=camera.ui)
menu_bg = Entity(parent=menu, model='quad', scale=(2, 2), color=color.black66)
menu_text = Text(parent=menu, text="LUMINA CRICKET 3D\nPress ENTER to Start", origin=(0,0), scale=4)

camera.position = (0, 6, -20)
camera.rotation_x = 10

app.run()
