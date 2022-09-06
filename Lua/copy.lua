function copy(val, rec)
    if type(val) ~= "table" then
        return val
    end
    rec = rec or {}
    for v, c in pairs(rec) do
        if v == val then
            return c
        end
    end
    local cpy = {}
    rec[val] = cpy
    for k, v in pairs(val) do
        cpy[k] = copy(v, rec)
    end
    return cpy
end
