import itertools
import logging
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        self.logger = logging.getLogger(self.__class__.__name__)

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")
    
    def to_str(self):
        str = ""
        for i in range(self.height):
            str += "--" * self.width + "-\n"
            for j in range(self.width):
                if self.board[i][j]:
                    str += "|X"
                else:
                    str += "| "
            str += "|\n"
        str += "--" * self.width + "-\n"

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cells = set(cells)
        self.mines = set()
        self.safes = set()
        self.count = count
        self.infer_knowledge()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def to_str(self):
        return f"cells: {self.cells}, count: {self.count}, safes: {self.safes}, mines: { self.mines}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if (cell not in self.cells):
            return
        self.cells.remove(cell)
        self.mines.add(cell)
        self.count -= 1           

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            return 
        self.cells.remove(cell)
        self.safes.add(cell)

    def infer_knowledge(self) -> bool:
        """
        Updates internal knowledge representation if new knowledge can be derived locally.
        Returns True if new knowledge was derived.
        """
        if self.count==0:
            self.safes.update(self.cells)
            self.cells.clear() 
            return True
        if len(self.cells) == self.count:
            self.mines |= self.cells
            self.cells.clear()
            self.count = 0
            return True
        return False

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        self.logger = logging.getLogger(self.__class__.__name__)

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        if cell in self.mines:
            return
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        if cell in self.safes:
            return
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1
        self.moves_made.add(cell)
        # 2
        self.mark_safe(cell)
        # 3 new sentence
        s = self.build_sentence(cell, count)
        self.knowledge.append(s)

        # 4) mark any additional cells as safe or as mines
        #    if it can be concluded based on the AI's knowledge base
        # 5) add any new sentences to the AI's knowledge base
        #    if they can be inferred from existing knowledge
        self.infer_new_knowledge()

        self.simplify_knowledge()
        self.logger.debug(f'end {self.to_str()}')

    def build_sentence(self, cell, count):
        cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Ignore the out of bound
                if not 0 <= i < self.height or not 0 <= j < self.width:
                    continue
                cells.add((i, j))
        s = Sentence(cells, count)
        # mark known safe cells
        for c in self.safes:
            s.mark_safe(c)
        # mark known mines cells
        for c in self.mines:
            s.mark_mine(c)
        return s

    def infer_new_knowledge(self):
        changed = False
        # create and add new sentences
        new_k = []
        for s in self.knowledge:
            s.infer_knowledge()     
            if len(s.cells)==0 or s.count == 0:
                continue
            for s2 in self.knowledge:
                if s.cells == s2.cells and s.count == s2.count:
                    continue
                s3 = None
                if s2.cells <= s.cells:
                    s3: Sentence = Sentence(s.cells - s2.cells, s.count - s2.count)
                if s.cells <= s2.cells:
                    s3 = Sentence(s2.cells - s.cells, s2.count - s.count)
                if s3 is not None and s3 not in self.knowledge and s3 not in new_k:
                    new_k.append(s3)
        for s in new_k:
            self.knowledge.append(s)
        
        changed = changed or len(new_k) != 0

        # update safes and mines from partial knowledge sentences
        for s in self.knowledge:
            for cell in s.safes:
                if cell not in self.safes:
                    changed = True
                    self.mark_safe(cell)
            for cell in s.mines:
                if cell not in self.mines:
                    changed = True
                    self.mark_mine(cell)

        # update safes and mines into partial knowledge sentences
        for cell in self.safes:
            for s in self.knowledge:
                if cell not in s.known_safes():
                    s.mark_safe(cell)
        for cell in self.mines:
            for s in self.knowledge:
                if cell not in s.known_mines():
                    s.mark_mine(cell)
        
        # infer knowledge in each sentence
        for s in self.knowledge:
            prev_len = len(s.cells)
            s.infer_knowledge()
            changed = changed or prev_len != len(s.cells)

        if changed:
            self.infer_new_knowledge()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes - self.moves_made:
            return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(0, self.height):
            for j in range(0, self.width):
                cell = (i, j)
                if cell in self.moves_made:
                    continue
                if cell in self.mines:
                    continue
                return cell
        return None            
    
    def to_str(self):
        str = f'AI knows: safes: {self.safes}, moves made: {self.moves_made}, mines: {self.mines},\n'
        str += 'knowledge: [\n'
        for s in self.knowledge:
            str += f'{s.to_str()}\n'
        str += ']'
        return str
    
    def simplify_knowledge(self):
        new_k = []
        for s in self.knowledge:
            if s.count == 0:
                continue
            exists = False
            for s2 in new_k:
                if s.cells == s2.cells and s.count == s2.count:
                    exists = True
                    break   
            if not exists:
                new_k.append(s)
        self.knowledge = new_k