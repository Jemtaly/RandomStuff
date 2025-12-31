from typing import TypeVar, Callable, Mapping, Iterable, Sequence, Tuple, overload

V = TypeVar("V")
E = TypeVar("E")


def find_all_cycles_from_dict(gdict: Mapping[V, Iterable[Tuple[E, V]]]) -> list[list[E]]:
    order = {point: i for i, point in enumerate(gdict)}
    glist = [[(edge, order[child]) for edge, child in children] for children in gdict.values()]
    return find_all_cycles_from_list(glist)


def find_all_cycles_from_list(glist: Sequence[Iterable[Tuple[E, int]]]) -> list[list[E]]:
    cycles: list[list[E]] = []

    visited = [False for _ in glist]
    edges: list[E] = []

    def visit(i: int):
        if i < k:
            return
        if visited[i]:
            if i == k:
                cycles.append(edges.copy())
            return
        visited[i] = True
        for edge, j in glist[i]:
            edges.append(edge)
            visit(j)
            edges.pop()
        visited[i] = False

    for k in range(len(glist)):
        visit(k)

    return cycles


def dict_to_get_dist(d: Mapping[Tuple[V, V], float]) -> Callable[[V, V], float]:
    return lambda p, q: d.get((p, q), float("inf"))


@overload
def get_total_dist(verts: Iterable[V], get_dist: Callable[[V, V], float], src: V, dst: None = None) -> dict[V, float]:
    ...


@overload
def get_total_dist(verts: Iterable[V], get_dist: Callable[[V, V], float], src: V, dst: V) -> float:
    ...


def get_total_dist(verts: Iterable[V], get_dist: Callable[[V, V], float], src: V, dst: V | None = None) -> float | dict[V, float]:
    before: dict[V, float] = {}
    future: dict[V, float] = {p: float("inf") for p in verts}

    future[src] = 0.0
    while future:
        cur, cur_dist = min(future.items(), key=lambda item: item[1])
        if cur == dst:
            return cur_dist
        before[cur] = cur_dist
        del future[cur]
        for nxt in future:
            future[nxt] = min(future[nxt], cur_dist + get_dist(cur, nxt))

    assert dst is None
    return before


def test_find_all_cycles():
    graph = {
        "A": [("A.b_0", "B"), ("A.c_0", "C")],
        "B": [("B.c_0", "C")],
        "C": [("C.a_0", "A")],
    }
    print(find_all_cycles_from_dict(graph))


def test_get_total_dist():
    points = {"A", "B", "C", "D"}
    distances = {
        ("A", "B"): 1.0,
        ("A", "C"): 4.0,
        ("B", "C"): 2.0,
        ("B", "D"): 6.0,
        ("C", "D"): 3.0,
    }
    get_dist = dict_to_get_dist(distances)
    print(get_total_dist(points, get_dist, "A", "D"))
    print(get_total_dist(points, get_dist, "A"))


if __name__ == "__main__":
    test_find_all_cycles()
    test_get_total_dist()
