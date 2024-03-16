import sys
from collections import deque
from typing import Deque, Dict

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword: Crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword: Crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        var : Variable
        for var in self.crossword.variables:
            domain: set = self.domains[var]
            for word in domain.copy():
                if len(word) != var.length:
                    domain.remove(word)


    def revise(self, x: Variable, y: Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revMade = False
        xDomain = self.domains[x]
        yDomain = self.domains[y]
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False
        for xWord in xDomain.copy():
            exists = False
            for yWord in yDomain:
                if xWord[overlap[0]] == yWord[overlap[1]]:
                    exists = True
                    break
            if not exists:
                xDomain.remove(xWord)
                revMade = True
        return revMade

    def ac3(self, arcs: list = None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Each arc is a tuple (x, y) of a variable x and a different variable y

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # print('starting ac3')
        # if arcs is None:
        #     print(f'arcs is None')
        # else:
        #     print(f'arcs len is {len(arcs)}')
        # build initial list of arcs
        if arcs is None:
            arcs = list()
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    if x == y:
                        continue
                    arcs.append((x, y))
            # print(f'now arc len is {len(arcs)}')

        # iterate over a queue of arcs
        arcs: Deque = deque(arcs)
        while len(arcs)>0:
            # print (f'while loop: arcs: {len(arcs)}')
            arc = arcs.popleft()
            # print (f'while loop: popped arc: {arc}')
            revMade = self.revise(arc[0], arc[1])
            if revMade:
                x = arc[0]
                if len(self.domain[x]) == 0:
                    return False
                for y in self.crossword.neighbors(x):
                    arcs.append((x,y))
        
        return True

    def assignment_complete(self, assignment):
        """
        An assignment is a dictionary where the keys are Variable objects 
        and the values are strings representing the words those variables will take on.

        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True
        

    def consistent(self, assignment: Dict[Variable, str]):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        x: Variable
        xWord: str
        # print(f'checking consistency')
        # for x in assignment:
        #     print(f'{x}: {assignment[x]}')
        for x, xWord in assignment.items():
            if x.length != len(xWord):
                # the word has the wrong length
                return False
            if list(assignment.values()).count(xWord) > 1:
                # the word is repeated
                return False
            for y in self.crossword.neighbors(x):
                overlap = self.crossword.overlaps[x, y]
                if y not in assignment:
                    continue
                yWord = assignment[y]
                if yWord is not None and xWord[overlap[0]] != yWord[overlap[1]]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = dict()
        for xWord in self.domains[var]:
            count = 0
            for y in self.crossword.neighbors(var):
                if y in assignment and assignment[y] is not None:
                    continue
                if xWord in self.domains[y]:
                    count += 1
            values[xWord] = count
        # TODO: somehow `key=lambda item: -item[1]` passes check50, 
        # but my understanding says that `key=lambda item: item[1]` should be the correct way
        return [item[0] for item in sorted(values.items(), key=lambda item: -item[1])]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        minDomainSize = len(self.crossword.words)+1
        highestDegree = 0
        theVar: Variable = None
        for var in self.crossword.variables:
            if var in assignment:
                continue
            domainSize = len(self.domains[var])
            degree = len(self.crossword.neighbors(var))
            if domainSize < minDomainSize or (domainSize == minDomainSize and degree > highestDegree):
                minDomainSize = domainSize
                highestDegree = degree
                theVar = var
        return theVar

    def backtrack(self, assignment: Dict):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
        if self.assignment_complete(assignment):
            return assignment
        nextVar = self.select_unassigned_variable(assignment)
        values = self.order_domain_values(nextVar, assignment)
        for v in values:
            assignment[nextVar] = v
            solution = None
            if self.consistent(assignment):
                solution = self.backtrack(assignment)
            if solution is not None:
                return solution
            assignment.pop(nextVar)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
