# Horror Tetris

A modified version of Tetris built using the `cmu_graphics` library.
This version includes an optional **Horror Bonus Mode** that introduces
panic events, flashing visuals, intense audio, and a jumpscare mechanic.

---

!!! Player Discretion Advised !!!

The bonus mode contains:
- Flashing visual effects
- Intense sound effects
- A sudden jumpscare image

Please enable at your own discretion.

---

## Base Game

Standard Tetris gameplay:
- Falling tetrominoes
- Line clearing
- Score tracking
- Game over when pieces stack to the top

---

## Horror Bonus Mode

When enabled (`b` key):

- Random **PANIC events** occur.
- The screen flashes briefly.
- Intense audio plays during the panic state.
- You MUST press **SPACE** immediately to hard-drop the current piece.
- If you fail to press SPACE in time, a jumpscare appears, and the game ends.

---

## Controls

- Arrow keys → move/rotate
- Space → hard drop (also used to survive PANIC)
- r → restart game
- b → toggle bonus mode

---

## Requirements

- Python 3
- `cmu_graphics` library installed
- All image and sound assets located in the `hw5_tetris_bonus_assets` folder
