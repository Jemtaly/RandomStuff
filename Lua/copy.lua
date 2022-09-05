function copy(val, ...)
    local argv = {...}
    local argc = #argv
    for _, p in ipairs(argv) do
        for v, c in pairs(p) do
            if v == val then
                return c
            end
        end
    end
    if type(val) == "table" then
        local res = {}
        local prs = {}
        prs[val] = res
        for k, v in pairs(val) do
            local cpy = copy(v, prs, ...)
            res[k] = cpy
            prs[v] = cpy
        end
        return res
    else
        return val
    end
end
