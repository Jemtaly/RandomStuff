data Memo = Memo { cur :: Char, lft :: [Char], rgt :: [Char] } deriving (Eq, Show)
data State = State { memo :: Memo, input :: [Char], output :: [Char] } deriving (Eq, Show)
data Instr = Lft | Rgt | Inc | Dec | Inp | Out | Rpt [Instr] deriving (Eq, Show)

-- Frontend
parse :: [Char] -> [Instr]
parse str = instrs
    where (instrs, "") = parse' str
parse' :: [Char] -> ([Instr], [Char])
parse' ('<' : xs) = (Lft : instrs, os)
    where (instrs, os) = parse' xs
parse' ('>' : xs) = (Rgt : instrs, os)
    where (instrs, os) = parse' xs
parse' ('+' : xs) = (Inc : instrs, os)
    where (instrs, os) = parse' xs
parse' ('-' : xs) = (Dec : instrs, os)
    where (instrs, os) = parse' xs
parse' (',' : xs) = (Inp : instrs, os)
    where (instrs, os) = parse' xs
parse' ('.' : xs) = (Out : instrs, os)
    where (instrs, os) = parse' xs
parse' ('[' : is) = (Rpt inner : instrs, os)
    where (inner, ']' : xs) = parse' is
          (instrs, os) = parse' xs
parse' os = ([], os)

-- Backend
succ' :: Char -> Char
succ' c = if c == '\255' then '\0' else succ c
pred' :: Char -> Char
pred' c = if c == '\0' then '\255' else pred c
app :: Instr -> State -> State
app Lft (State (Memo c (x : r) p) i o) = State (Memo x r (c : p)) i o
app Rgt (State (Memo c p (x : r)) i o) = State (Memo x (c : p) r) i o
app Inc (State (Memo c p q) i o) = State (Memo (succ' c) p q) i o
app Dec (State (Memo c p q) i o) = State (Memo (pred' c) p q) i o
app Inp (State (Memo c p q) (x : r) o) = State (Memo x p q) r o
app Out (State (Memo c p q) i o) = State (Memo c p q) i (c : o)
app (Rpt instrs) state = if cur (memo state) == '\0'
    then state
    else app (Rpt instrs) $ fold instrs state
fold :: [Instr] -> State -> State
fold [] state = state
fold (i : is) state = fold is $ app i state
run :: [Instr] -> [Char] -> [Char]
run instrs input = reverse $ output $ fold instrs (State (Memo '\0' infz infz) input [])
    where infz = repeat '\0'

hw = parse "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
main = do
    putStr $ run hw ""
