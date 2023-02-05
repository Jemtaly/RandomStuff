revBase :: Int -> Integer -> String
revBase b n = map ((['0' .. '9'] ++ ['A' .. 'Z']) !!) $ temp n where
    temp 0 = []
    temp x = fromIntegral r : temp q where
        (q, r) = x `divMod` toInteger b
powMod :: Integer -> Integer -> Integer -> Integer
powMod _ 0 _ = 1
powMod b p m = if even p
    then powMod (b * b `mod` m) (p `div` 2) m
    else powMod b (p - 1) m * b `mod` m
isPrime :: Integer -> Bool
isPrime n = if n < 40
    then elem n chklst
    else odd n && all test chklst where
        chklst = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        test a = head ds == 1 || elem (n - 1) ds where
            ds = take k $ iterate temp $ powMod a s n
        temp x = x * x `mod` n
        (k, s) = head $ filter (odd . snd) $ zip [0 .. ] $ iterate (`div` 2) (n - 1)
truncatablePrimes :: Int -> [[Integer]]
truncatablePrimes b = map snd $ iterate nxt (1, [0]) where
    nxt (n, x) = (n * toInteger b, [k | t <- x, i <- [1 .. b - 1], let k = n * toInteger i + t, isPrime k])
