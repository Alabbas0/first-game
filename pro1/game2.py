import tkinter as tk
import math
import random

# Class representing a player in the game
class Player:
    def __init__(self, canvas, game, start_x=100, start_y=100):
        self.canvas = canvas  # The canvas on which the player is drawn
        self.game = game  # The game instance
        self.x, self.y = start_x, start_y  # Initial position
        self.speed = 5  # Movement speed
        self.health = 3  # Initial health
        # Load player image and scale it
        self.image = tk.PhotoImage(file="V.png").subsample(5, 5)
        self.id = canvas.create_image(self.x, self.y, image=self.image, anchor=tk.CENTER)

    def move(self, dx, dy):
        """Move the player by dx, dy and update its position on the canvas."""
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.canvas.coords(self.id, self.x, self.y)

    def shoot(self, target_x, target_y):
        """Create a bullet aimed at the target coordinates if the game is not over."""
        if not self.game.is_game_over:
            return Bullet(self.canvas, self.x, self.y, target_x, target_y, self.game)

    def check_collision(self, enemy):
        """Check if the player has collided with a given enemy."""
        if math.hypot(self.x - enemy.x, self.y - enemy.y) < 20:
            self.health -= 1  # Reduce health on collision
            self.game.update_lives()  # Update the displayed health
            if self.health <= 0:
                self.game.game_over()  # End the game if health drops to zero
            return True
        return False

# Class representing an enemy in the game
class Enemy:
    def __init__(self, canvas, x, y):
        self.canvas = canvas  # The canvas on which the enemy is drawn
        self.x, self.y = x, y  # Initial position
        self.speed = 2  # Movement speed
        # Load enemy image and scale it
        self.image = tk.PhotoImage(file="eeee.png").subsample(5, 5)
        self.id = canvas.create_image(self.x, self.y, image=self.image, anchor=tk.CENTER)

    def move_towards(self, player_x, player_y):
        """Move the enemy towards the player's position."""
        dx, dy = player_x - self.x, player_y - self.y
        distance = max(math.hypot(dx, dy), 1)  # Avoid division by zero
        self.x += (dx / distance) * self.speed
        self.y += (dy / distance) * self.speed
        self.canvas.coords(self.id, self.x, self.y)

    def is_hit(self, bullet_x, bullet_y):
        """Check if the enemy has been hit by a bullet."""
        return math.hypot(self.x - bullet_x, self.y - bullet_y) < 20

# Class representing a bullet in the game
class Bullet:
    def __init__(self, canvas, start_x, start_y, target_x, target_y, game):
        self.canvas = canvas  # The canvas on which the bullet is drawn
        self.x, self.y = start_x, start_y  # Initial position
        self.speed = 10  # Speed of the bullet
        # Calculate angle and velocity based on target coordinates
        self.angle = math.atan2(target_y - start_y, target_x - start_x)
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)
        self.id = canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill="yellow")
        self.game = game  # The game instance
        self.alive = True  # Bullet is initially alive
        self.move()  # Start moving the bullet

    def move(self):
        """Move the bullet and check for collisions or boundaries."""
        if not self.alive or self.game.is_game_over:
            return
        self.x += self.dx
        self.y += self.dy
        if not self.is_in_bounds():
            self.game.remove_bullet(self)  # Remove bullet if out of bounds
        else:
            self.canvas.coords(self.id, self.x - 5, self.y - 5, self.x + 5, self.y + 5)
            self.check_collision()  # Check if the bullet hits any enemy
            if self.alive:
                self.canvas.after(50, self.move)  # Continue moving the bullet

    def is_in_bounds(self):
        """Check if the bullet is within the canvas boundaries."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        return 0 <= self.x <= width and 0 <= self.y <= height

    def check_collision(self):
        """Check if the bullet has hit any enemy and update game state."""
        for enemy in self.game.enemies[:]:
            if enemy.is_hit(self.x, self.y):
                self.game.remove_enemy(enemy)  # Remove the hit enemy
                self.game.remove_bullet(self)  # Remove the bullet
                self.game.score += 1  # Increment score
                self.game.update_score()  # Update score display
                break

# Main game class
class Game:
    def __init__(self, root):
        self.root = root  # The Tkinter root window
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        self.player = Player(self.canvas, self)  # Create the player
        self.enemies = []  # List to keep track of enemies
        self.bullets = []  # List to keep track of bullets
        self.pressed_keys = set()  # Track pressed keys
        self.mouse_x, self.mouse_y = None, None  # Track mouse position
        self.is_game_over = False  # Flag to indicate if the game is over
        self.score = 0  # Initialize score
        self.setup_ui()  # Set up the user interface
        self.setup_events()  # Set up event handlers
        self.update()  # Start the game update loop
        self.shoot_continuously()  # Start continuous shooting
        self.spawn_enemies_periodically()  # Start periodic enemy spawning

    def setup_ui(self):
        """Set up the user interface elements (score and lives display)."""
        self.score_text = self.canvas.create_text(10, 10, anchor="nw", text=f"Score: {self.score}", font=("Arial", 16))
        self.lives_text = self.canvas.create_text(10, 40, anchor="nw", text=f"Lives: {self.player.health}", font=("Arial", 16))

    def setup_events(self):
        """Bind events to handlers for key presses, key releases, and mouse movement."""
        self.root.bind("<KeyPress>", lambda e: self.pressed_keys.add(e.keysym))
        self.root.bind("<KeyRelease>", lambda e: self.pressed_keys.discard(e.keysym))
        self.root.bind("<Motion>", self.track_mouse)

    def spawn_enemies(self, count):
        """Spawn a specified number of enemies at random positions."""
        for _ in range(count):
            x, y = random.randint(50, 750), random.randint(50, 550)
            self.enemies.append(Enemy(self.canvas, x, y))

    def spawn_enemies_periodically(self):
        """Periodically spawn enemies at intervals."""
        if not self.is_game_over:
            self.spawn_enemies(3)  # Spawn 3 enemies at a time
            self.root.after(5000, self.spawn_enemies_periodically)  # Call again after 5000ms

    def track_mouse(self, event):
        """Update the tracked mouse position."""
        self.mouse_x, self.mouse_y = event.x, event.y

    def update(self):
        """Update game state, including player movement, enemy movement, and collisions."""
        if self.is_game_over:
            return

        dx = (('d' in self.pressed_keys) - ('a' in self.pressed_keys))
        dy = (('s' in self.pressed_keys) - ('w' in self.pressed_keys))
        self.player.move(dx, dy)  # Move player based on pressed keys

        for enemy in self.enemies[:]:
            enemy.move_towards(self.player.x, self.player.y)  # Move enemies towards player
            if self.player.check_collision(enemy):
                self.remove_enemy(enemy)  # Handle collision with player

        self.root.after(50, self.update)  # Continue updating game state

    def shoot_continuously(self):
        """Continuously shoot bullets towards the mouse cursor."""
        if not self.is_game_over and self.mouse_x is not None and self.mouse_y is not None:
            bullet = self.player.shoot(self.mouse_x, self.mouse_y)
            if bullet:
                self.bullets.append(bullet)
        self.root.after(500, self.shoot_continuously)  # Call again after 500ms

    def remove_enemy(self, enemy):
        """Remove an enemy from the canvas and the list."""
        self.canvas.delete(enemy.id)
        self.enemies.remove(enemy)
        self.update_score()  # Update score after removing an enemy

    def remove_bullet(self, bullet):
        """Remove a bullet from the canvas and the list."""
        if bullet in self.bullets:
            bullet.alive = False
            self.canvas.delete(bullet.id)
            self.bullets.remove(bullet)

    def update_score(self):
        """Update the score display on the canvas."""
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

    def update_lives(self):
        """Update the lives display on the canvas."""
        self.canvas.itemconfig(self.lives_text, text=f"Lives: {self.player.health}")

    def game_over(self):
        """Handle game over scenario."""
        self.is_game_over = True
        self.canvas.create_rectangle(0, 0, 800, 600, fill="black")  # Cover screen with black
        self.canvas.create_text(400, 300, text=f"Game Over! Final Score: {self.score}", font=("Arial", 24), fill="red")
        self.root.unbind("<KeyPress>")
        self.root.unbind("<KeyRelease>")
        self.root.unbind("<Motion>")
        self.root.after(5000, self.show_close_message)  # Show close message after 5 seconds

    def show_close_message(self):
        """Display a message to close the window to exit."""
        self.canvas.create_text(400, 350, text="Close the window to exit.", font=("Arial", 16), fill="blue")

if __name__ == "__main__":
    root = tk.Tk()  # Create the main Tkinter window
    game = Game(root)  # Create and start the game
    root.mainloop()  # Start the Tkinter event loop
