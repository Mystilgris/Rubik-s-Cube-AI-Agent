CS-445 Final Project - Rubik's Cube AI Agent
Project Due Date - Dec. 6th 2026
Team Members - Jason Zhou and Carter Luebbe
Project Description: Our aim is to develop an AI agent that can solve a scrambled 3x3 Rubik's Cube

Run the terminal interface with `py Cube.py` (or `python Cube.py`).

- `R`, `U'`, `F2`, etc.: turn one face using standard notation.
- `scramble`: apply 20 random turns and print the sequence.
- `scramble 40`: choose the number of scramble turns.
- `solve`: solve the current cube and print the moves for each CFOP stage.
- `show`: display the cube net.
- `quit`: exit.

The solver in `cfop.py` uses yellow on the bottom and white on top:
Cross aligns the four yellow edges with their side centers; F2L inserts four
corner/edge pairs; OLL orients the white last layer; PLL puts those pieces in
their final positions. Small bidirectional searches select face turns for the
cross, insertion triggers for F2L, edge-orientation/Sune algorithms for OLL,
and T/Ua permutations for PLL. This is a simplified CFOP solver, not the full
57-OLL/21-PLL speedcubing algorithm collection. Solutions are not move-optimal.
It reads the current stickers and does not reverse or store scramble history.
Scrambles are random move sequences, not uniformly sampled cube states.

`cube.scramble()` returns its moves. `cube.solve()` applies the solution and
returns an ordered dictionary of stage names and move lists. A failed solve
leaves the cube unchanged. The search has a 500,000-state limit per stage.
No third-party packages are required.
