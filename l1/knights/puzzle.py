from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Or(AKnight, AKnave), 
    Or(And(AKnight, Not(AKnave)), And(AKnave, Not(AKnight))), 
    # A says "I am both a knight and a knave."
    Or(
        And(AKnight, And(AKnave, AKnight)),
        And(AKnave, Not(And(AKnave, AKnight)))
    ),
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Or(AKnight, AKnave), 
    Or(And(AKnight, Not(AKnave)), And(AKnave, Not(AKnight))), 
    Or(BKnight, BKnave),
    Or(And(BKnight, Not(BKnave)), And(BKnave, Not(BKnight))), 
    Or(CKnight, CKnave),
    Or(And(CKnight, Not(CKnave)), And(CKnave, Not(CKnight))), 
    # A says "We are both knaves."
    Or(
        And(AKnight, And(AKnave, BKnave)),
        And(AKnave, Not(And(AKnave, BKnave)))
    ),
    # B says nothing.
    Or(
        And(BKnight, Not(BKnave)), 
        And(BKnave, Not(BKnight))
    )
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnight, AKnave), 
    Or(And(AKnight, Not(AKnave)), And(AKnave, Not(AKnight))), 
    Or(BKnight, BKnave),
    Or(And(BKnight, Not(BKnave)), And(BKnave, Not(BKnight))), 
    Or(CKnight, CKnave),
    Or(And(CKnight, Not(CKnave)), And(CKnave, Not(CKnight))), 
    # A says "We are the same kind."
    Or(
        And(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
        And(AKnave, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),
    ),
    # B says "We are of different kinds."
    Or(
        And(BKnight, Or(And(AKnave, BKnight), And(AKnight, BKnave))),
        And(BKnave, Not(Or(And(AKnave, BKnight), And(AKnight, BKnave)))),
    )
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, AKnave), 
    Or(And(AKnight, Not(AKnave)), And(AKnave, Not(AKnight))), 
    Or(BKnight, BKnave),
    Or(And(BKnight, Not(BKnave)), And(BKnave, Not(BKnight))), 
    Or(CKnight, CKnave),
    Or(And(CKnight, Not(CKnave)), And(CKnave, Not(CKnight))), 
    # A says either "I am a knight." or "I am a knave.", but you don't know which.
    Or(
        And(AKnight, Or(AKnight, AKnave)),
        And(AKnave, Not(Or(AKnight, AKnave)))
        # And(AKnave, Or(Not(AKnight), Not(AKnave)))
    ),
    # B says "A said 'I am a knave'."
    Or(
        And(BKnight, Or(
            And(AKnight, AKnave), 
            And(AKnave, Not(AKnave))
        )),
        And(BKnave, 
            Not(Or(
                And(AKnight, AKnave), 
                And(AKnave, Not(AKnave))
            ))
        ),
    ),
    # B says "C is a knave."
    Or(
        And(BKnight, CKnave),
        And(BKnave, Not(CKnave))
    ),
    # C says "A is a knight."
    Or(
        And(CKnight, AKnight),
        And(CKnave, Not(AKnight))
    )
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
