function show(val, ...)
    if type(val) ~= "table" then
        return tostring(val)
    end
    local argv = {...}
    local argc = #argv
    for i, v in ipairs(argv) do
        if v == val then
            return string.rep(".", i)
        end
    end
    local str = "{\n"
    for k, v in pairs(val) do
        str = str .. string.rep("    ", argc + 1) .. (type(k) == "string" and k or "[" .. tostring(k) .. "]") .. " = " .. show(v, val, ...) .. ",\n"
    end
    return str .. string.rep("    ", argc) .. "}"
end
