# Caterpillar World Saver

A fun 2D game where you control a caterpillar navigating through stages while converting or avoiding enemies.

## Features

- Control a caterpillar through maze-like environments
- Convert enemies by touching them with your head
- Avoid enemy collisions with your body
- Energy and lives system
- Progressive difficulty with increasing stages
- Custom sound effects and visual feedback

## Installation

### Option 1: Run directly with Python

1. Ensure you have Python 3.11 or later installed
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python caterpillar_game.py
   ```

### Option 2: Install as a package

1. Install the game package:
   ```bash
   pip install .
   ```
2. Run the game:
   ```bash
   caterpillar-game
   ```

## Controls

- Arrow keys: Move the caterpillar
- ESC: Pause game
- Mouse: Click buttons in menus

## Gameplay

- Convert enemies by touching them with your head
- Avoid enemy collisions with your body segments
- Energy depletes when hit by enemies
- Lose a life when energy is depleted
- Complete stages by converting all enemies
- Game over when all lives are lost

## Requirements

- Python 3.11 or later
- Pygame 2.5.2
- NumPy 1.26.4

## Development

To set up the development environment:

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
