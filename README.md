# Bootleg-Tetris

[![AGPL-3.0-or-later license][license-badge]](LICENSE)
[![CI][ci-badge]][ci-workflow]

A simple recreation of competitive two-player Tetris

## Installation

```shell
git clone https://github.com/Vessel9817/Bootleg-Tetris
cd Bootleg-Tetris
py -3.13 -m venv './venv'
'./venv/Scripts/activate'
pip install .
py -m bootleg_tetris
```

## Controls

### Player 1

- `W`: Rotate clockwise
- `A`: Move left
- `S`: Move down (soft drop)
- `D`: Move right
- `T`: Rotate 180 degrees
- `F`: Rotate counterclockwise
- `G`: Move down to the bottom (hard drop)
- `H`: Hold block for later

### Player 2

- `NUM 8`: Rotate clockwise
- `NUM 4`: Move left
- `NUM 5`: Move down (soft drop)
- `NUM 6`: Move right
- `I`: Rotate 180 degrees
- `J`: Rotate counterclockwise
- `K`: Move down to the bottom (hard drop)
- `L`: Hold block for later

## Features

### Implemented

- SRS rotation
- Block holding
- Local 2 player
- Competitive play
- Sending garbage lines
- Point system
- Level system

### Not implemented

- Title screen
- Pause menu
- A visualization of how many lines are about to be received
- Highscores
- Sound effects
- Holding down move keys
- Control customization
- Extra modes
  - Singleplayer modes
  - Multiplayer race modes
  - Cooperative multiplayer?
- Game continuation after another player game-overs
- Sending extra lines from T-spins
- Sending extra lines from compounded single line clears

### Not planned

- Online play
- 3+ player support

[license-badge]: https://raw.githubusercontent.com/Vessel9817/bootleg-tetris/refs/heads/main/badge.svg
[ci-badge]: https://github.com/Vessel9817/Bootleg-Tetris/actions/workflows/ci.yml/badge.svg
[ci-workflow]: https://github.com/Vessel9817/Bootleg-Tetris/actions/workflows/ci.yml
