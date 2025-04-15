from dsl import *
from utils import *

MAX_LEN = 30 # max length of a single line

#  NOTE: HUGE prior assumption that 0 is always background
BGC = 0
# why?:
# if colors are truly random, then 'background' has to be > 50% of total sequence length
# this either restricts our task space 
# or requires us to make sequences super long to distinguish foreground objects from background

# implications:
# this means that all color intervals should start at 1
# reduces the number of colors to 9


def generate_sum_1c(diff_lb: float, diff_ub: float) -> dict:
    """ concat the objects of a single color"""
    w = unifint(diff_lb, diff_ub, (2, MAX_LEN))
    colors = interval(1, 10, 1) 
    fgc = choice(colors)
    gi = canvas(BGC, (1, w))
    n = unifint(diff_lb, diff_ub, (1, w-1))
    fg = sample(totuple(asindices(gi)), n)
    gi = fill(gi, fgc, fg)
    go = canvas(fgc, (1, n))
    return {'input': gi, 'output': go}

# def generate_sum_maxC(diff_lb: float, diff_ub: float) -> dict:
#     w = unifint(diff_lb, diff_ub, (3, MAX_LEN))
#     colors = interval(1, 10, 1) 
#     fgc = sample(colors, 1)
#     colors = remove(fgc, colors)
#     gi = canvas(BGC, (1, w))
#     n_fg = unifint(diff_lb, diff_ub, (1, (w-1)//2))
#     fg = sample(totuple(asindices(gi)), n_fg)
#     n_maxC = randint(1, n_fg-2)
#     c_maxC = sample(fg, n_maxC)
#     gi = fill(gi, fgc, c_maxC)

        
#     go = canvas(fgc, (1, n_maxC))
#     return {'input': gi, 'output': go}

# NOTE: just reverse the test cases for sort DESCENDING
def generate_sort_increasing_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ sort the lines of _distinct_ length and color in increasing order of length 
        all lines must have _unique_ length
    """
    while True:
        n = unifint(diff_lb, diff_ub, (2, 9))
        max_len = unifint(diff_lb, diff_ub, (9, 30))
        colors = interval(1, 10, 1)
        cs = sample(colors, n)
        ls = sample(interval(1, max_len, 1), n) # lengths are unique
        color_length_pairs = list(zip(cs, ls))
        lines = [canvas(c, (1, l)) for c, l in color_length_pairs]
        gi = lines[0]
        for i in range(1, len(lines)):
            gi = hconcat(gi, lines[i])
        sorted_lines = sorted(lines, key=lambda x: len(x[0]))
        go = sorted_lines[0]
        for i in range(1, len(sorted_lines)):
            go = hconcat(go, sorted_lines[i])
        if gi != go:
            break
    return {'input': gi, 'output': go}

def generate_sort_increasing_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ sort (and concat by removing background) the lines of _distinct_ length and color 
        in increasing order of length 
        all lines must have _unique_ length
    """
    while True:
        n = unifint(diff_lb, diff_ub, (2, 9))
        max_len = unifint(diff_lb, diff_ub, (9, 30))
        colors = interval(1, 10, 1)
        cs = sample(colors, n)
        ls = sample(interval(1, max_len, 1), n) # lengths are unique
        color_length_pairs = list(zip(cs, ls))
        lines = [canvas(c, (1, l)) for c, l in color_length_pairs]
        if choice([True, False]):
            gi = hconcat(canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))), lines[0])
        else:
            gi = lines[0]
        for i in range(1, len(lines)):
            if choice([True, False]):
                gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            gi = hconcat(gi, lines[i])
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
        sorted_lines = sorted(lines, key=lambda x: len(x[0]))
        go = sorted_lines[0]
        for i in range(1, len(sorted_lines)):
            go = hconcat(go, sorted_lines[i])
        if gi != go:
            break
    return {'input': gi, 'output': go}

def generate_sort_nondecreasing_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ sort the lines of _distinct_ length and color in increasing order of length 
        lines may have _duplicate_ length, if so preserve the order of appearance
    """
    while True:
        n = unifint(diff_lb, diff_ub, (2, 9))
        max_len = unifint(diff_lb, diff_ub, (9, 30))
        colors = interval(1, 10, 1)
        cs = sample(colors, n)
        rnge = interval(1, max_len, 1)
        ls = [choice(rnge) for _ in range(n)] # NOTE: lengths may not be unique
        color_length_pairs = list(zip(cs, ls))
        lines = [canvas(c, (1, l)) for c, l in color_length_pairs]
        gi = lines[0]
        for i in range(1, len(lines)):
            gi = hconcat(gi, lines[i])
        sorted_lines = sorted(lines, key=lambda x: len(x[0]))
        go = sorted_lines[0]
        for i in range(1, len(sorted_lines)):
            go = hconcat(go, sorted_lines[i])
        if gi != go:
            break
    return {'input': gi, 'output': go}

def generate_sort_nondecreasing_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ sort (and concat by removing background) the lines of _distinct_ length and color in increasing order of length 
        lines may have _duplicate_ length, if so preserve the order of appearance
    """
    while True:
        n = unifint(diff_lb, diff_ub, (2, 9))
        max_len = unifint(diff_lb, diff_ub, (9, 30))
        colors = interval(1, 10, 1)
        cs = sample(colors, n)
        rnge = interval(1, max_len, 1)
        ls = [choice(rnge) for _ in range(n)] # NOTE: lengths may not be unique
        color_length_pairs = list(zip(cs, ls))
        lines = [canvas(c, (1, l)) for c, l in color_length_pairs]
        if choice([True, False]):
            gi = hconcat(canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))), lines[0])
        else:
            gi = lines[0]
        for i in range(1, len(lines)):
            if choice([True, False]):
                gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            gi = hconcat(gi, lines[i])
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
        sorted_lines = sorted(lines, key=lambda x: len(x[0]))
        go = sorted_lines[0]
        for i in range(1, len(sorted_lines)):
            go = hconcat(go, sorted_lines[i])
        if gi != go:
            break
    return {'input': gi, 'output': go}