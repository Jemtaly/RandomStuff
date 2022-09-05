function copy(val, rec)
    rec = rec or {}
    for v, c in pairs(rec) do
        if v == val then
            return c
        end
    end
    if type(val) == "table" then
        local res = {}
        rec[val] = res
        for k, v in pairs(val) do
            res[k] = copy(v, rec)
        end
        return res
    else
        return val
    end
end
