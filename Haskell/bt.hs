balancedTernary :: Integer -> String
balancedTernary n = reverse $ temp n where
    temp 0 = ""
    temp x = ch : temp q where
        ch = case r of
            0 -> 'T'
            1 -> '0'
            2 -> '1'
        (q, r) = (x + 1) `divMod` 3
