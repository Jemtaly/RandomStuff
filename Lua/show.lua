function show(val, ...)
    local argv = {...}
    local argc = #argv
    for i, v in ipairs(argv) do
        if v == val then
            return string.rep("../", i)
        end
    end
    if type(val) == "table" then
        local res = "{\n"
        for k, v in pairs(val) do
            res = res .. string.rep("    ", argc + 1)
            if type(k) == "string" then
                res = res .. k
            else
                res = res .. "[" .. k .. "]"
            end
            res = res .. " = " .. show(v, val, ...) .. ",\n"
        end
        return res .. string.rep("    ", argc) .. "}"
    else
        return tostring(val)
    end
end
