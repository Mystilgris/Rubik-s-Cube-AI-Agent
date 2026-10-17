"""CFOP using small, bidirectional searches over sticker positions.

Cross uses face turns; F2L uses slot insertion triggers; OLL uses the
edge-orientation algorithm and Sune; PLL uses T and Ua permutations.
Algorithms are rotated around U, so the cube never needs to be reoriented.
"""
from functools import lru_cache


def inverse(moves):
    return tuple(m if m.endswith('2') else m[:-1] if m.endswith("'")
                 else m + "'" for m in reversed(moves))


@lru_cache(maxsize=1)
def geometry():
    from Cube import RubiksCube
    stickers = [(f, r, c) for f in RubiksCube.FACE_COLORS
                for r in range(3) for c in range(3)]
    positions = [RubiksCube._3D_position(*s) for s in stickers]
    turns = {}
    for face in RubiksCube.FACE_LETTERS:
        for suffix in ('', "'", '2'):
            cube = RubiksCube()
            for i, (f, r, c) in enumerate(stickers):
                cube.faces[f][r][c] = i
            cube.turn(face + suffix)
            permutation = [0] * 54
            for dest, (f, r, c) in enumerate(stickers):
                permutation[cube.faces[f][r][c]] = dest
            turns[face + suffix] = tuple(permutation)
    return stickers, positions, turns


def algorithm(moves):
    turns = geometry()[2]
    permutation = tuple(range(54))
    for move in moves:
        permutation = tuple(turns[move][p] for p in permutation)
    return tuple(moves), permutation


def generators(sequences):
    result = {}
    for sequence in sequences:
        for moves in (tuple(sequence), inverse(sequence)):
            item = algorithm(moves)
            result[item[1]] = item
    return list(result.values())


def search(start, goal, actions, unordered=False):
    """Return algorithms connecting two projected states, with a memory bound."""
    def apply(state, permutation):
        state = tuple(permutation[p] for p in state)
        return tuple(sorted(state)) if unordered else state

    if start == goal:
        return []
    parents = [{start: None}, {goal: None}]
    fronts = [{start}, {goal}]
    while all(fronts):
        side = 0 if len(fronts[0]) <= len(fronts[1]) else 1
        following = set()
        for state in fronts[side]:
            for moves, permutation in actions:
                new = apply(state, permutation)
                if new in parents[side]:
                    continue
                parents[side][new] = (state, moves)
                if new in parents[1 - side]:
                    paths = []
                    for direction in (0, 1):
                        path, node = [], new
                        while parents[direction][node] is not None:
                            previous, steps = parents[direction][node]
                            path.append(steps)
                            node = previous
                        paths.append(path)
                    return [move for steps in reversed(paths[0]) for move in steps] + [
                        move for steps in paths[1] for move in inverse(steps)]
                following.add(new)
                if sum(map(len, parents)) > 500_000:
                    raise RuntimeError('CFOP search limit reached; cube was not changed.')
        fronts[side] = following
    raise ValueError('Cube cannot be solved by this stage; check its sticker state.')


def solve(cube):
    from Cube import RubiksCube
    stickers, positions, turns = geometry()
    # Identify each cubie by its color set, then each sticker by its own color.
    groups = {}
    for i, position in enumerate(positions):
        groups.setdefault(position, []).append(i)
    identities = {}
    for group in groups.values():
        colors = frozenset(cube.FACE_COLORS[stickers[i][0]] for i in group)
        for i in group:
            identities[colors, cube.FACE_COLORS[stickers[i][0]]] = i
    state = [None] * 54
    for group in groups.values():
        colors = frozenset(cube.faces[stickers[i][0]][stickers[i][1]][stickers[i][2]]
                           for i in group)
        for dest in group:
            f, r, c = stickers[dest]
            identity = identities.get((colors, cube.faces[f][r][c]))
            if identity is None or state[identity] is not None:
                raise ValueError('Invalid or duplicated cube pieces.')
            state[identity] = dest
    for i, (f, r, c) in enumerate(stickers):
        if r == c == 1 and state[i] != i:
            raise ValueError('Center colors must match the original cube orientation.')

    result = {}

    def stage(name, targets, actions, unordered=False):
        start = tuple(state[i] for i in targets)
        goal = tuple(targets)
        if unordered:
            start, goal = tuple(sorted(start)), tuple(sorted(goal))
        moves = search(start, goal, actions, unordered)
        for move in moves:
            state[:] = [turns[move][p] for p in state]
        result[name] = moves

    cross = [i for i, (x, y, z) in enumerate(positions)
             if y == -1 and abs(x) + abs(z) == 1]
    stage('Cross (yellow)', cross, generators([(m,) for m in turns]))

    # Three-move triggers affect a single bottom slot and the upper layer.
    triggers = [('U',), ('U2',)]
    for face in 'FRBL':
        for side in (face, face + "'"):
            for upper in ('U', "U'", 'U2'):
                triggers.append((side, upper, inverse((side,))[0]))
    actions = generators(triggers)
    protected = list(cross)
    for number, (x, z) in enumerate(((1, 1), (1, -1), (-1, -1), (-1, 1)), 1):
        pair = [i for i, p in enumerate(positions) if p in ((x, -1, z), (x, 0, z))]
        allowed = [(m, p) for m, p in actions if all(p[i] == i for i in protected)]
        stage(f'F2L pair {number}', pair, allowed)
        protected.extend(pair)

    # Rotate algorithms to cover all four slots while keeping yellow down.
    def rotations(text):
        ring = 'FRBL'
        for offset in range(4):
            yield tuple(ring[(ring.index(m[0]) + offset) % 4] + m[1:]
                        if m[0] in ring else m for m in text.split())

    oll = [('U',), ('U2',)]
    for text in ("F R U R' U' F'", "R U R' U R U2 R'"):
        oll.extend(rotations(text))
    top = [i for i, (f, _, _) in enumerate(stickers) if f == 'Up']
    stage('OLL (orient last layer)', top, generators(oll), unordered=True)

    pll = [('U',), ('U2',)]
    for text in ("R U R' U' R' F R2 U' R' U' R U R' F'",
                 "R U' R U R U R U' R' U' R2"):
        pll.extend(rotations(text))
    last = [i for i, p in enumerate(positions) if p[1] == 1]
    stage('PLL (permute last layer)', last, generators(pll))
    if state != list(range(54)):
        raise ValueError('Invalid cube state: final verification failed.')
    # Commit only after all four phases succeed.
    working = RubiksCube()
    working.faces = {f: [row[:] for row in grid] for f, grid in cube.faces.items()}
    for moves in result.values():
        for move in moves:
            working.turn(move)
    if not working.is_solved():
        raise RuntimeError('CFOP solution verification failed.')
    cube.faces = working.faces
    return result
