function copy(val, ...)
    local argv = {...}
    local argc = #argv
    for i, p in ipairs(argv) do
        if p.val == val then
            return p.res
        end
    end
    if type(val) == "table" then
        local res = {}
        for k, v in pairs(val) do
            res[k] = copy(v, {val = val, res = res}, ...)
        end
        return res
    else
        return val
    end
end
