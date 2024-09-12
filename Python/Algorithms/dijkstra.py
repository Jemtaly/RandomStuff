def distance(src_pos, dst_pos, points, from_to):
    unvised = {p: float("inf") for p in points}
    cur_pos = src_pos
    cur_dis = 0.0
    while cur_pos != dst_pos:
        del unvised[cur_pos]
        min_dis = float("inf")
        for nxt_pos in unvised:
            nxt_dis = unvised[nxt_pos]
            nxt_dis = min(nxt_dis, cur_dis + from_to(cur_pos, nxt_pos))
            if nxt_dis < min_dis:
                min_pos = nxt_pos
                min_dis = nxt_dis
            unvised[nxt_pos] = nxt_dis
        cur_pos = min_pos
        cur_dis = min_dis
    return cur_dis
