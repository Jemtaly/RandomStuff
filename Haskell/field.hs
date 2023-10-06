{-# LANGUAGE TypeFamilies #-}
rpo opr idn inv elm eln = opr elm (inv eln)
lpo opr idn inv elm eln = opr (inv elm) eln
for opr idn inv elm n
    | n == 0 = idn
    | otherwise =
        let sum = for opr idn inv elm $ (n + 1) `div` 3
            pro = sum `opr` sum `opr` sum
        in case n `mod` 3 of
            0 -> pro
            1 -> pro `opr` elm
            2 -> pro `opr` inv elm
-- Algebraic Structures
class Algebraic g where
    type Elm g
class Algebraic g => SemiGroup g where
    add :: g -> Elm g -> Elm g -> Elm g
class SemiGroup g => MonoId g where
    rei :: g -> Elm g
    sum :: Foldable f => g -> f (Elm g) -> Elm g
    sum g = foldr (add g) (rei g)
class MonoId g => AbelianGroup g where
    neg :: g -> Elm g -> Elm g
    sub :: g -> Elm g -> Elm g -> Elm g
    dot :: g -> Elm g -> Integer -> Elm g
    sub g = rpo (add g) (rei g) (neg g)
    dot g = for (add g) (rei g) (neg g)
class AbelianGroup g => Ring g where
    mul :: g -> Elm g -> Elm g -> Elm g
class Ring g => UnitRing g where
    one :: g -> Elm g
    pro :: Foldable f => g -> f (Elm g) -> Elm g
    pro g = foldr (mul g) (one g)
class UnitRing g => Field g where
    rcp :: g -> Elm g -> Elm g
    dvs :: g -> Elm g -> Elm g -> Elm g
    pow :: g -> Elm g -> Integer -> Elm g
    dvs g = rpo (mul g) (one g) (rcp g)
    pow g = for (mul g) (one g) (rcp g)
exgcd x y
    | y == 0 = (abs x, (signum x, 0))
    | otherwise =
        let(g, (a, b)) = exgcd y (x `mod` y)
        in (g, (b, a - x `div` y * b))
-- ECC AbelianGroup
data ECC = ECC Integer Integer Integer deriving (Eq, Show)
data Point = Point Integer Integer | Inf deriving (Eq, Show)
instance Algebraic ECC where
    type Elm ECC = Point
instance SemiGroup ECC where
    add (ECC a b q) Inf p = p
    add (ECC a b q) p Inf = p
    add (ECC a b q) (Point s t) (Point z w)
        | s == z && (t + w) `mod` q == 0 = Inf
        | otherwise = Point x y where
            tan = if s == z
                then inv (t + w) * (s * z * 3 + a)
                else inv (z - s) * (w - t)
            x = (tan * tan - s - z) `mod` q
            y = (tan * (s - x) - t) `mod` q
            inv = snd . snd . exgcd q
instance MonoId ECC where
    rei (ECC a b q) = Inf
instance AbelianGroup ECC where
    neg (ECC a b q) Inf = Inf
    neg (ECC a b q) (Point x y) = Point x $ if y == 0 then 0 else q - y
-- Galois Field
data Gal = Gal Integer deriving (Eq, Show)
instance Algebraic Gal where
    type Elm Gal = Integer
instance SemiGroup Gal where
    add (Gal p) a b = (a + b) `mod` p
instance MonoId Gal where
    rei (Gal p) = 0
instance AbelianGroup Gal where
    neg (Gal p) a = (p - a) `mod` p
instance Ring Gal where
    mul (Gal p) a b = (a * b) `mod` p
instance UnitRing Gal where
    one (Gal p) = 1
instance Field Gal where
    rcp (Gal p) x =
        let (g, (a, _)) = exgcd x p
        in if g == 1
            then a `mod` p
            else error "not invertible"
-- Fibonacci Field
data Fib = Fib deriving (Eq, Show)
instance Algebraic Fib where
    type Elm Fib = (Integer, Integer)
instance SemiGroup Fib where
    add Fib (x, y) (z, w) = (x + z, y + w)
instance MonoId Fib where
    rei Fib = (0, 0)
instance AbelianGroup Fib where
    neg Fib (x, y) = (0 - x, 0 - y)
instance Ring Fib where
    mul Fib (x, y) (z, w) =
        let t = (y - x) * (w - z)
        in (x * z + t, y * w + t)
instance UnitRing Fib where
    one Fib = (1, 1)
instance Field Fib where
    rcp Fib (x, y) =
        let c = 3 * x * y - x * x - y * y
        in if x `mod` c == 0 && y `mod` c == 0
            then (y `div` c, x `div` c)
            else error "not invertible"
