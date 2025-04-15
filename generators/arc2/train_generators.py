from dsl import *
from utils import *

def generate_00576224(diff_lb: float, diff_ub: float) -> dict:
    colors = interval(0, 10, 1) 
    # limit h and w based based on max size of 30x30 for output (3h x 3w)
    h = unifint(diff_lb, diff_ub, (2, 10))
    w = unifint(diff_lb, diff_ub, (2, 10))
    # make a random rectangle
    grid_rows = []
    for _ in range(h):
        current_row = []
        for _ in range(w):
            current_row.append(choice(colors)) # Assign a random color
        grid_rows.append(tuple(current_row))
    gi = tuple(grid_rows)
    # tranformation:
    # copy rectangle 3 times in the row direction
    # copy row 3 times in the column direction
    # each rectangle in middle row is mirrored horizontally
    # Create the three rows needed for the output grid
    # Row 1: gi | gi | gi
    row1 = hconcat(hconcat(gi, gi), gi)
    # Row 2: hmirror(gi) | hmirror(gi) | hmirror(gi)
    # mirror input grid along vertical axis
    gi_vmirror = vmirror(gi)
    row2 = hconcat(hconcat(gi_vmirror, gi_vmirror), gi_vmirror)
    # Row 3 is the same as Row 1
    row3 = row1
    go = vconcat(vconcat(row1, row2), row3)
    return {'input': gi, 'output': go}


def generate_009d5c81(diff_lb: float, diff_ub: float) -> dict:
    # NOTE: color shape that is in test must be in at least one of TRAIN examples
    # otherwise model will be forced to memorize all color indicating shapes which we don't want
    h = unifint(diff_lb, diff_ub, (10, 30))
    w = unifint(diff_lb, diff_ub, (10, 30))

    color_indicator = {
        # Color 0: 'I' shape (111 010 111)
        0: frozenset(((0,0), (0,1), (0,2), (1,1), (2,0), (2,1), (2,2))),
        # Color 1 (Blue): 'X' shape (101 010 101)
        1: frozenset(((0,0), (0,2), (1,1), (2,0), (2,2))),
        # Color 2 (Red): 'Plus' shape (010 111 010)
        2: frozenset(((0,1), (1,0), (1,1), (1,2), (2,1))),
        # Color 3 (Green): 'Crab' shape (101 010 111)
        3: frozenset(((0,0), (0,2), (1,1), (2,0), (2,1), (2,2))),
        # Color 4 (Yellow): 'Filled square' (111 111 111)
        4: frozenset(((0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2))),
        # Color 5 (Grey): 'U' shape (101 101 111)
        5: frozenset(((0,0), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2))),
        # Color 6 (Pink): 'Empty square center' (111 101 111)
        6: frozenset(((0,0), (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2))),
        # Color 7 (Orange): 'Home plate' shape (111 101 010)
        7: frozenset(((0,0), (0,1), (0,2), (1,0), (1,2), (2,1))),
        # Color 8 (Cyan): 'Diagonal' shape (100 010 001)
        8: frozenset(((0,0), (1,1), (2,2))),
        # Color 9 (Maroon): 'L' shape (100 100 111)
        9: frozenset(((0,0), (1,0), (2,0), (2,1), (2,2))),
    }

    colors = interval(0, 10, 1)
    target_color, bgc, indicator_color, obj_color = sample(colors, 4)
    gi = canvas(bgc, (h, w))
    # add color indicating shape to grid in random location
    indicator = color_indicator[target_color]
    di = randint(0, h - 3)
    dj = randint(0, w - 3)
    indicator = shift(indicator, (di, dj))
    gi = fill(gi, indicator_color, indicator)
    # create a random connected shape based on grid size
    inds = asindices(gi)
    forbidden: Indices = indicator | mapply(neighbors, indicator)
    inds = sfilter(
        inds,
        lambda loc: loc not in forbidden
    )
    # grow the object (Flood Fill on available bgc cells)
    obj = initset(choice(totuple(inds))) 
    max_cells = ((h * w) - len(forbidden)) // 2
    obj_size = unifint(diff_lb, diff_ub, (10, max_cells))
    for _ in range(obj_size):
        potential_next = mapply(neighbors, obj)
        valid_next = sfilter(
            potential_next,
            lambda loc: loc in potential_next and loc not in forbidden
        )
        next_cell = initset(choice(totuple(valid_next)))
        obj |= next_cell
    gi = fill(gi, obj_color, obj)
    # remove color indicating obj (make background color)
    go = fill(gi, bgc, indicator)
    # change color of connected obj to target color
    go = fill(go, target_color, obj)     
    return {'input': gi, 'output': go}


def generate_00dbd492(diff_lb: float, diff_ub: float) -> dict:
    # NOTE: all possible colors need to be shown in TRAIN examples
    # assumed transformation:
    width_to_fill = {
        5: 8, # width 5 = light blue 8
        7: 4, # width 7 = yellow 4
        9: 3, # width 9 = green 3
    }
    # make it harder:
    # regtangular grid
    h = unifint(diff_lb, diff_ub, (6, 30))
    w = unifint(diff_lb, diff_ub, (6, 30))
    # background can be any _other_ color
    # squares can be any _other_ color
    colors = remove(8, remove(4, remove(3, interval(0, 10, 1))))
    bgc, fgc = sample(colors, 2)
    gi = canvas(bgc, (h,w))
    # fill with as many squares as possible    
    boxes = []
    empty = asindices(gi)
    while empty:
        # Filter empty cells to find valid potential upper left corners for at least a 5x5 box
        usable_ul = sfilter(empty, lambda loc: loc[0] <= h - 5 and loc[1] <= w - 5)
        if not usable_ul: break 
        i,j = choice(totuple(usable_ul))
        valid_lr = []
        for l in (5,7,9):
            lr = (i+l-1, j+l-1)
            if backdrop(frozenset({(i,j), lr})).issubset(empty):
                valid_lr.append(lr)
        if valid_lr:
            lr = choice(valid_lr)
            bx = box(frozenset({(i,j), lr}))
            boxes.append(bx)
            empty -= backdrop(outbox(bx))
        else:
            empty -= initset((i,j))
    if not boxes: # in the super rare case that no boxes were made, try again
        return generate_00dbd492(diff_lb, diff_ub)
    for bx in boxes:
        bx = bx | initset(center(bx))
        gi = fill(gi, fgc, bx)
    go = tuple(e for e in gi)
    for bx in boxes:
        go = fill(go, width_to_fill[width(bx)], backdrop(inbox(bx)))
        bx = bx | initset(center(bx))
        go = fill(go, fgc, bx)
    return {'input': gi, 'output': go}
   
def generate_11dc524f(diff_lb: float, diff_ub: float) -> dict:
    # assumed transformation: 
    # graviate other object (with n**2 cells) toward nxn square until it hits
    # change nxn square to mirrored version of other object
    # other must have nx1 line that contacts first, rest can be random 
    # convert nxn square to mirrored version of other object
    h = unifint(diff_lb, diff_ub, (12, 30))
    w = unifint(diff_lb, diff_ub, (12, 30))
    # background can be any _other_ color
    # squares can be any _other_ color
    colors = interval(0, 10, 1)
    bgc, tgtc, objc, = sample(colors, 3)
    gi = canvas(bgc, (h,w))
    # add nxn square
    l = unifint(diff_lb, diff_ub, (3, 5))
    tgt = backdrop(frozenset({(0,0), (l-1,l-1)}))
    tgt = shift(tgt, (randint(2, h-l-2), randint(2, w-l-2)))
    gi = fill(gi, tgtc, tgt)
    neinei = mapply(neighbors, mapply(neighbors, tgt))
    empty = asindices(gi) - neinei
    dirs = [RIGHT, DOWN, LEFT, UP]
    shuffle(dirs)
    obj_dir = None
    for d in dirs:
        # find a direction that has enough space for obj
        space = sfilter(
            shoot(ulcorner(tgt), d),
            lambda loc: loc in empty
        )
        if len(space) >= l:
            obj_dir = d
            break
    if obj_dir is None: 
        return generate_11dc524f(diff_lb, diff_ub)
    if obj_dir == RIGHT:
        empty = sfilter(empty, lambda loc: loc[1] > rightmost(neinei))
    elif obj_dir == DOWN:
        empty = sfilter(empty, lambda loc: loc[0] > lowermost(neinei))
    elif obj_dir == LEFT:
        empty = sfilter(empty, lambda loc: loc[1] < leftmost(neinei))
    elif obj_dir == UP:
        empty = sfilter(empty, lambda loc: loc[0] < uppermost(neinei))
    # grow the object (Flood Fill on available bgc cells)
    if obj_dir[0] == 0:
        seed = connect(ulcorner(tgt), llcorner(tgt))
    else:
        seed = connect(ulcorner(tgt), urcorner(tgt))
    while seed.issubset(mapply(neighbors, tgt)):
        seed = shift(seed, obj_dir)
    obj = shift(seed, obj_dir)
    while size(obj) < l**2:
        nei = sfilter(mapply(neighbors, obj), lambda loc: loc in empty)
        next_cell = initset(choice(totuple(nei)))
        obj |= next_cell
    if square(obj): # if object is square it is not clear which to gravitate toward
        return generate_11dc524f(diff_lb, diff_ub)
    gi = fill(gi, objc, obj)
    go = canvas(bgc, (h,w))
    tgt_dir = (obj_dir[0] * -1, obj_dir[1] * -1)
    while not adjacent(obj, tgt):
        obj = shift(obj, tgt_dir)
    go = fill(go, objc, obj)
    mirrored = vmirror(obj) if obj_dir[0] == 0 else hmirror(obj)
    hw = width(obj) if obj_dir[0] == 0 else height(obj)
    for _ in range(hw):
        mirrored = shift(mirrored, tgt_dir)
    if not mirrored.issubset(asindices(go)):
        return generate_11dc524f(diff_lb, diff_ub)
    go = fill(go, tgtc, mirrored)
    return {'input': gi, 'output': go}

def generate_0b17323b(diff_lb: float, diff_ub: float) -> dict:
    # assumed transformation, continue the diagonal sequence starting at ~corner with red (2)
    h = unifint(diff_lb, diff_ub, (16, 30))
    w = unifint(diff_lb, diff_ub, (16, 30))
    colors = remove(2, interval(0, 10, 1))
    bgc, fgc = sample(colors, 2)
    gi = canvas(bgc, (h,w))
    inds = asindices(gi)
    corner = choice((ulcorner(inds), urcorner(inds), llcorner(inds), lrcorner(inds)))
    di = unifint(diff_lb, diff_ub, (1, 5))
    dj = unifint(diff_lb, diff_ub, (1, 5))
    pi, pj = choice((0,1)), choice((0,1))
    if corner == urcorner(inds):
        dj = -dj
        corner = (corner[0]+pi, corner[1]-pj)
    elif corner == llcorner(inds):
        di = -di
        corner = (corner[0]-pi, corner[1]+pj)
    elif corner == lrcorner(inds):
        di = -di
        dj = -dj
        corner = (corner[0]-pi, corner[1]-pj)
    else:
        corner = (corner[0]+pi, corner[1]+pj)
    corner = initset(corner)
    max_iter = max(min(h//di, w//dj), 4)
    k = choice(interval(3, max_iter, 1))
    for _ in range(k):
        gi = fill(gi, fgc, corner)
        corner = shift(corner, (di, dj))
    go = tuple(e for e in gi)
    while corner.issubset(asindices(go)):
        go = fill(go, 2, corner)
        corner = shift(corner, (di, dj))
    return {'input': gi, 'output': go}


def generate_1478ab18(diff_lb: float, diff_ub: float) -> dict:
    # input grid always has 4 cells that almost form corners of a square
    # one corner is moved inward by 1 cell (towards center of square)
    # assumed transformation:
    # create a triangle with right angle where the inward corner is 
    # that connects to adjacent corners
    h = unifint(diff_lb, diff_ub, (10, 30))
    w = unifint(diff_lb, diff_ub, (10, 30))
    colors = interval(0, 10, 1)
    bgc, fgc, tric = sample(colors, 3)
    gi = canvas(bgc, (h,w))
    l = unifint(diff_lb, diff_ub, (4, min(h, w)))
    corners = frozenset({(0,0), (l-1,0), (0,l-1), (l-1,l-1)})
    chosen = choice(totuple(corners))
    if chosen == ulcorner(corners):
        inward = shift(initset(chosen), (1,1))
        hypotenuse = connect(llcorner(corners), urcorner(corners))
        horizontal = connect(ulcorner(corners), urcorner(corners))
        vertical = connect(ulcorner(corners), llcorner(corners))
    elif chosen == urcorner(corners):
        inward = shift(initset(chosen), (1,-1))
        hypotenuse = connect(ulcorner(corners), lrcorner(corners))
        horizontal = connect(ulcorner(corners), urcorner(corners))
        vertical = connect(urcorner(corners), lrcorner(corners))
    elif chosen == llcorner(corners):
        inward = shift(initset(chosen), (-1,1))
        hypotenuse = connect(ulcorner(corners), lrcorner(corners))
        horizontal = connect(llcorner(corners), lrcorner(corners))
        vertical = connect(ulcorner(corners), llcorner(corners))
    elif chosen == lrcorner(corners):
        inward = shift(initset(chosen), (-1,-1))
        hypotenuse = connect(llcorner(corners), urcorner(corners))
        horizontal = connect(llcorner(corners), lrcorner(corners))
        vertical = connect(urcorner(corners), lrcorner(corners))
    tri = hypotenuse | horizontal | vertical
    corners -= initset(chosen)
    corners |= inward
    ul = (randint(0, h-l), randint(0, w-l))
    corners = shift(corners, ul)
    tri = shift(tri, ul)
    gi = fill(gi, fgc, corners)
    go = tuple(e for e in gi)
    go = fill(go, tric, tri)
    go = fill(go, fgc, corners)
    return {'input': gi, 'output': go}
    
def generate_22425bda(diff_lb: float, diff_ub: float) -> dict:
    # solution: in what order were the lines drawn?
    h = unifint(diff_lb, diff_ub, (10, 30))
    w = unifint(diff_lb, diff_ub, (10, 30))
    colors = interval(0, 10, 1)
    c = unifint(diff_lb, diff_ub, (1, 8))
    order = sample(colors, c+1) # plus 1 for background
    bgc = order.pop()
    go = (tuple(order[::-1]),)
    gi = canvas(bgc, (h,w))
    inds = asindices(gi)
    prev: Indices = frozenset()
    while order:
        color = order.pop()
        # just make sure every line intersects previous line
        line: Indices = frozenset()
        while True:
            if choice((True, False)): # top or bottom
                i = randint(0, w-1)
                j, dj = choice(((0,1),(w-1,-1)))
                di = choice((0,1))
                di = -di if i > w // 2 else di
                line = shoot((i,j), (di,dj))
            else: # left or right side
                i, di = choice(((0,1),(h-1,-1)))
                j = randint(0, h-1)
                dj = choice((0,1))
                dj = -dj if j > w // 2 else dj
                line = shoot((i,j), (di,dj))
            if not prev or (not prev.issubset(line) and line.intersection(prev)):
                break
        gi = fill(gi, color, line)
        prev = sfilter(line, lambda loc: loc in inds)
    return {'input': gi, 'output': go}


# NOTE: this task can be ambiguous if train examples don't include each color going in each direction
# 2/8 chance all 3 train examples have same color going in same direction
def generate_1d61978c(diff_lb: float, diff_ub: float) -> dict:
    h = unifint(diff_lb, diff_ub, (10, 30))
    w = unifint(diff_lb, diff_ub, (10, 30))
    colors = remove(8, remove(2, interval(0, 10, 1)))
    bgc, fgc = sample(colors, 2)
    gi = canvas(bgc, (h,w))
    total = unifint(diff_lb, diff_ub, (2, 30))
    l, r = frozenset(), frozenset()
    lines = 0
    while lines < total:
        iters = 0
        while True:
            i, j = randint(0, h-2), randint(1, w-2)
            k = randint(2, min(h, w))
            dj = choice((-1,1))
            line = connect((i,j), (i+k, j+k*dj))
            if line.intersection(mapply(neighbors, l | r)):
                iters += 1
                if iters > 5:
                    break
                continue
            if dj == 1: # r
                r |= line
            else: # l
                l |= line
            break
        lines += 1
    gi = fill(gi, fgc, l | r)
    go = canvas(bgc, (h,w))
    inds = asindices(gi)
    l = sfilter(l, lambda loc: loc in inds)
    r = sfilter(r, lambda loc: loc in inds)
    if size(l) == size(r):
        return generate_1d61978c(diff_lb, diff_ub) # try again
    elif size(l) > size(r):
        lc, rc = 8, 2
    else: 
        lc, rc = 2, 8
    go = fill(go, lc, l)
    go = fill(go, rc, r)
    return {'input': gi, 'output': go}
