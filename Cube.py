class RubiksCube:

    # Face colors
    FACE_COLORS = {
        "Up": "White",
        "Down": "Yellow",
        "Front": "Red",
        "Back": "Orange",
        "Right": "Blue",
        "Left": "Green"
    }

    # Face Orientation/Vector in terms of 3D space in x,y,z
    FACE_VECTORS = {
        "Up": (0, 1, 0),
        "Down": (0, -1, 0),
        "Front": (0, 0, 1),
        "Back": (0, 0, -1),
        "Right": (1, 0, 0),
        "Left": (-1, 0, 0)
    }

    FACE_LETTERS = {"U": "Up", "D": "Down", "F": "Front", "B": "Back", "R": "Right", "L": "Left"}

    def __init__(self):
        self.faces = {
            face: [[color] * 3 for _ in range(3)] for face, color in self.FACE_COLORS.items()
        }

    @staticmethod
    def _3D_position(face, row, col):
        # Convert sticker face position into a 3D sticker position i.e 2D position to 3D position
        if face == "Up":
            return (col - 1, 1, row - 1)
        if face == "Down":
            return (col - 1, -1, 1 - row)
        if face == "Front":
            return (col - 1, 1 - row, 1)
        if face == "Back":
            return (1 - col, 1 - row, -1)
        if face == "Right":
            return (1, 1 - row, 1 - col)
        if face == "Left":
            return (-1, 1 - row, col - 1)

    @staticmethod
    def _2D_position(position, vector):
        # Convert 3D sticker position into sticker face position i.e. 3D position to 2D position
        x, y, z = position
        if vector == (0, 1, 0):    return "Up", z + 1, x + 1
        if vector == (0, -1, 0):   return "Down", 1 - z, x + 1
        if vector == (0, 0, 1):    return "Front", 1 - y, x + 1
        if vector == (0, 0, -1):   return "Back", 1 - y, 1 - x
        if vector == (1, 0, 0):    return "Right", 1 - y, 1 - z
        if vector == (-1, 0, 0):   return "Left", 1 - y, z + 1

    @staticmethod
    def _rotate_vector(vector, axis):
        # Rotate a vector 90 degrees clockwise around the outward axis

        # Calculates how much the vector points/aligns with the axis
        dot_product = sum(a * b for a, b in zip(vector, axis))
        # Calculates direction of the rotation
        cross_product = (
            axis[1] * vector[2] - axis[2] * vector[1],
            axis[2] * vector[0] - axis[0] * vector[2],
            axis[0] * vector[1] - axis[1] * vector[0],
        )
        return tuple((axis[i] * dot_product) - cross_product[i] for i in range(3))

    def _turn_clockwise(self, face):
        axis = self.FACE_VECTORS[face]
        old_faces = {f: [row[:] for row in grid] for f, grid in self.faces.items()}
        new_faces = {f: [row[:] for row in grid] for f, grid in old_faces.items()}

        # Rotate every sticker on the selected layer, including the face itself.
        for source_face, grid in old_faces.items():
            for row in range(3):
                for col in range(3):
                    position = self._3D_position(source_face, row, col)
                    vector = self.FACE_VECTORS[source_face]

                    # A sticker belongs to the turned layer if its position
                    # lies on the outer plane perpendicular to this face's axis.
                    if sum(position[i] * axis[i] for i in range(3)) != 1:
                        continue

                    new_position = self._rotate_vector(position, axis)
                    new_vector = self._rotate_vector(vector, axis)
                    dest_face, dest_row, dest_col = self._2D_position(
                        new_position, new_vector
                    )
                    new_faces[dest_face][dest_row][dest_col] = grid[row][col]

        self.faces = new_faces

    def turn(self, move):
        # Perform a turn U, D, L, R, F, B; apostrophe means reverse/prime; 2 means half-turn.
        if not move:
            raise ValueError("Move cannot be empty.")
        face = self.FACE_LETTERS.get(move[0].upper())
        suffix = move[1:]
        if face not in self.faces or suffix not in ("", "'", "2"):
            raise ValueError(f"Invalid move: {move}")

        # A half-turn is two quarter-turns. Counterclockwise is three clockwise turns.
        repetitions = 2 if suffix == "2" else (3 if suffix == "'" else 1)
        for _ in range(repetitions):
            self._turn_clockwise(face)

    @staticmethod
    def _color_sticker(color):
        ansi_colors = {
            "White": "\033[107m",
            "Yellow": "\033[103m",
            "Red": "\033[101m",
            "Orange": "\033[48;5;208m",
            "Blue": "\033[104m",
            "Green": "\033[102m",
        }
        reset_formatting = "\033[0m"
        return f"{ansi_colors[color]}  {reset_formatting}"

    def display_face(self, face):
        print(f"{face}:")
        for row in self.faces[face]:
            print("".join(self._color_sticker(color) for color in row))
        print()

    def display(self):
        # Get the color stickers for three lines of a face
        def face_lines(face):
            return [
                "".join(self._color_sticker(color) for color in row)
                for row in self.faces[face]
            ]

        up = face_lines("Up")
        left = face_lines("Left")
        front = face_lines("Front")
        right = face_lines("Right")
        back = face_lines("Back")
        down = face_lines("Down")

        # Each face occupies 6 characters per sticker row.
        face_width = 6

        print(" " * face_width + "UP")
        print("LEFT " + "FRONT " + "RIGHT " + "BACK")
        print(" " * face_width + "DOWN")

        for line in up:
            print(" " * face_width + line)

        for i in range(3):
            print(left[i] + front[i] + right[i] + back[i])

        for line in down:
            print(" " * face_width + line)

        print()

def main():
    cube = RubiksCube()
    cube.display()
    while True:
        move = input("Move ('U', 'D', 'L', 'R', 'F', 'B'), can do double by adding 2 i.e. 'R2' or do prime i.e. 'R', 'show' to display cube, or 'quit': ").strip()
        if move.lower() == "quit":
            break
        if move.lower() == "show":
            cube.display()
        try:
            cube.turn(move)
            cube.display()
        except ValueError as e:
            print(e)

if __name__ == "__main__":
    main()
