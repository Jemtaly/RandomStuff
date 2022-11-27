function copy(val, map)
    if type(val) ~= "table" then
        return val
    end
    map = map or {}
    for v, c in pairs(map) do
        if v == val then
            return c
        end
    end
    local cpy = {}
    map[val] = cpy
    for k, v in pairs(val) do
        cpy[k] = copy(v, map)
    end
    return cpy
end
