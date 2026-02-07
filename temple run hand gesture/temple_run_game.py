import pygame
import time
import os
import random
from PIL import Image

pygame.init()
screen = pygame.display.set_mode((400, 600))
pygame.display.set_caption("Temple Run - Gesture Controlled")
clock = pygame.time.Clock()

# Load runner.gif frames
gif = Image.open("runner.gif")
frames = []
try:
    while True:
        frame = gif.copy().convert("RGBA")
        mode = frame.mode
        size = frame.size
        data = frame.tobytes()
        py_image = pygame.image.fromstring(data, size, mode)
        py_image = pygame.transform.scale(py_image, (40, 40))
        frames.append(py_image)
        gif.seek(gif.tell() + 1)
except EOFError:
    pass

# Constants
OBSTACLE_WIDTH = 10
OBSTACLE_HEIGHT = 15  # Fixed height
OBSTACLE_SPEED = 5
SPAWN_INTERVAL = 100
JUMP_HEIGHT = 180
JUMP_DURATION = 20

# Fonts
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 30)
score_font = pygame.font.SysFont(None, 35)

# Load high score
high_score_file = "high_score.txt"
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as f:
        high_score = int(f.read())
else:
    high_score = 0

# Game reset function
def reset_game():
    return {
        "player": pygame.Rect(180, 500, 40, 40),
        "is_jumping": False,
        "is_sliding": False,
        "jump_progress": 0,
        "slide_progress": 0,
        "obstacles": [],
        "spawn_timer": 0,
        "frame_index": 0,
        "game_over": False,
        "score": 0,
        "frame_count": 0,
        "game_over_time": None,
    }

# Initialize state
state = reset_game()

# Main loop
running = True
while running:
    screen.fill((30, 30, 30))
    gesture = "NONE"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not state["game_over"]:
        # Read gesture
        try:
            with open("gesture.txt", "r") as f:
                gesture = f.read().strip()
        except FileNotFoundError:
            gesture = "NONE"

        # Movement
        if gesture == "LEFT" and state["player"].x > 0:
            state["player"].x -= 20
        elif gesture == "RIGHT" and state["player"].x < 360:
            state["player"].x += 20
        elif gesture == "JUMP" and not state["is_jumping"]:
            state["is_jumping"] = True
            state["jump_progress"] = 0
        elif gesture == "SLIDE" and not state["is_sliding"]:
            state["is_sliding"] = True
            state["slide_progress"] = 0

        # Jump logic
        y_offset = 0
        if state["is_jumping"]:
            if state["jump_progress"] < JUMP_DURATION:
                t = state["jump_progress"] / JUMP_DURATION
                y_offset = -JUMP_HEIGHT * (1 - (t - 0.5) ** 2 * 4)
                state["jump_progress"] += 1
            else:
                state["is_jumping"] = False

        # Slide logic
        h_offset = 0
        if state["is_sliding"]:
            if state["slide_progress"] < 10:
                h_offset = 20
                state["slide_progress"] += 1
            else:
                state["is_sliding"] = False

        # Animate character
        state["frame_index"] = (state["frame_index"] + 1) % len(frames)
        frame = pygame.transform.scale(frames[state["frame_index"]], (40, 40 - h_offset))
        adjusted = pygame.Rect(state["player"].x, state["player"].y + y_offset, 40, 40 - h_offset)
        screen.blit(frame, (adjusted.x, adjusted.y))

        # Spawn obstacle with constant size
        state["spawn_timer"] += 1
        if state["spawn_timer"] >= SPAWN_INTERVAL:
            y_pos = 600 - OBSTACLE_HEIGHT - 50  # Appears near bottom
            state["obstacles"].append(pygame.Rect(400, y_pos, OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
            state["spawn_timer"] = 0

        # Move and draw obstacles
        for obs in list(state["obstacles"]):
            obs.x -= OBSTACLE_SPEED
            pygame.draw.rect(screen, (255, 255, 0), obs)
            if adjusted.colliderect(obs):
                state["game_over"] = True
                state["game_over_time"] = time.time()
                if state["score"] > high_score:
                    high_score = state["score"]
                    with open(high_score_file, "w") as f:
                        f.write(str(high_score))
                break

        # Remove off-screen obstacles
        state["obstacles"] = [obs for obs in state["obstacles"] if obs.x > -OBSTACLE_WIDTH]

        # Update score
        state["frame_count"] += 1
        if state["frame_count"] % 5 == 0:
            state["score"] += 1

        # Draw score
        score_text = score_font.render(f"Score: {state['score']}", True, (255, 255, 255))
        high_score_text = score_font.render(f"High Score: {high_score}", True, (255, 215, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))

    else:
        # Game over screen
        msg = font.render("Game Over", True, (255, 0, 0))
        final_score = small_font.render(f"Final Score: {state['score']}", True, (255, 255, 255))
        screen.blit(msg, (100, 240))
        screen.blit(final_score, (100, 290))

        if time.time() - state["game_over_time"] > 2:
            state = reset_game()

    pygame.display.flip()
    clock.tick(15)
    time.sleep(0.03)

pygame.quit()
