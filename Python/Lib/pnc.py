def perm2cycles(permut):
    P = dict(enumerate(permut))
    cycles = []
    while P:
        k, v = P.popitem()
        cycle = [k]
        while v != k:
            cycle.append(v)
            v = P.pop(v)
        cycles.append(cycle)
    return cycles
def cycles2perm(cycles):
    P = {}
    for cycle in cycles:
        for i in range(len(cycle)):
            P[cycle[i - 1]] = cycle[i]
    return [P[i] for i in range(len(P))]
