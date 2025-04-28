from dsl import *
from utils import *

MAX_LEN = 10 # max length of an object (line of a single color)
MAX_LINES = 10 # max number of lines

#  NOTE: HUGE prior assumption that 0 is always background
BGC = 0
COLORS = interval(1, 10, 1)
# why?:
# if colors are truly random, then 'background' has to be > 50% of total sequence length
# this either restricts our task space 
# or requires us to make sequences super long to distinguish foreground objects from background

# implications:
# this means that all color intervals should start at 1
# reduces the number of colors to 9

def generate_count_lines_1c_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ count the lines of a single color """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    c = choice(colors)
    gi = ((),)
    if choice([True, False]): gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    for _ in range(n):
        gi = hconcat(gi, canvas(c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    go = canvas(BGC, (1, n))
    return {'input': gi, 'output': go}

def generate_count_lines_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ count the number of lines """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        gi = hconcat(gi, canvas(c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
    go = canvas(BGC, (1, n))
    return {'input': gi, 'output': go}

def generate_count_lines_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ count the number of lines, removing background """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    prev_c = None
    for _ in range(n):
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            c = choice(colors)
        else:
            c = choice([color for color in colors if color != prev_c])
        gi = hconcat(gi, canvas(c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        prev_c = c
    if choice([True, False]): gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    go = canvas(BGC, (1, n))
    return {'input': gi, 'output': go}
    
def generate_count_max_lines_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ count the number of lines of the color with the most lines """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    freq = [0] * 10
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        gi = hconcat(gi, canvas(c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        prev_c = c
        freq[c] += 1
    # TODO: sort orders by second key if first key is a tie so model may learn ordering of colors
    ordered = sorted([(count, c) for c, count in enumerate(freq)], reverse=True)
    # if there's a tie, add an extra line to break the tie
    max_c = ordered[0][1]
    if ordered[0][0] == ordered[1][0]:
        if max_c == prev_c: # if the most frequent color is the same as the previous color, use the second most frequent color
            max_c = ordered[1][1]
        gi = hconcat(gi, canvas(max_c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        freq[max_c] += 1
    go = canvas(max_c, (1, freq[max_c]))
    return {'input': gi, 'output': go}

def generate_count_max_lines_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ count the lines of the color with the most lines, removing background """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    freq = [0] * 10
    prev_c = None
    for _ in range(n):
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            c = choice(colors)
        else:
            c = choice([color for color in colors if color != prev_c])
        gi = hconcat(gi, canvas(c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        prev_c = c
        freq[c] += 1
    ordered = sorted([(count, c) for c, count in enumerate(freq)], reverse=True)
    # if there's a tie, add an extra line to break the tie
    max_c = ordered[0][1]
    if ordered[0][0] == ordered[1][0]:
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
        elif max_c == prev_c: # if the most frequent color is the same as the previous color, use the second most frequent color
            max_c = ordered[1][1]
        gi = hconcat(gi, canvas(max_c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        freq[max_c] += 1
    if choice([True, False]): gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    go = canvas(max_c, (1, freq[max_c]))
    return {'input': gi, 'output': go}

def generate_count_min_lines_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ count the number of lines of the color with the least lines """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    freq = [0] * 10
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        gi = hconcat(gi, canvas(c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        prev_c = c
        freq[c] += 1
    ordered = sorted([(count, c) for c, count in enumerate(freq) if count > 0])
    # if there's a tie, add an extra line to break the tie
    while ordered[0][0] == ordered[1][0]:
        add_c = ordered[1][1]
        if add_c == prev_c: # if the least frequent color is the same as the previous color, use the second least frequent color
            add_c = ordered[2][1] if len(ordered) > 2 else ordered[0][1]
        gi = hconcat(gi, canvas(add_c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        freq[add_c] += 1
        prev_c = add_c
        ordered = sorted([(count, c) for c, count in enumerate(freq) if count > 0])
    min_c = ordered[0][1]
    go = canvas(min_c, (1, freq[min_c]))
    return {'input': gi, 'output': go}

def generate_count_min_lines_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ count the number of lines of the color with the least lines, removing background """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    freq = [0] * 10
    prev_c = None
    for _ in range(n):
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            c = choice(colors)
        else:
            c = choice([color for color in colors if color != prev_c])
        gi = hconcat(gi, canvas(c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        prev_c = c
        freq[c] += 1
    ordered = sorted([(count, c) for c, count in enumerate(freq) if count > 0])
    # if there's a tie, add an extra line to break the tie
    while ordered[0][0] == ordered[1][0]:
        add_c = ordered[1][1]
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
        elif add_c == prev_c: # if the least frequent color is the same as the previous color, use the second least frequent color
            add_c = ordered[2][1] if len(ordered) > 2 else ordered[0][1]
        gi = hconcat(gi, canvas(add_c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        freq[add_c] += 1
        prev_c = add_c
        ordered = sorted([(count, c) for c, count in enumerate(freq) if count > 0])
    min_c = ordered[0][1]
    if choice([True, False]): gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    go = canvas(min_c, (1, freq[min_c]))
    return {'input': gi, 'output': go}

def generate_sum_1c_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ concat the objects of a single color, removing background """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1) 
    fgc = choice(colors)
    gi = ((),)
    if choice([True, False]):
        gi = hconcat(canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))), gi)
    for _ in range(n):
        gi = hconcat(gi, canvas(fgc, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10))))) # TODO: always ends with background
    go = canvas(fgc, (1, colorcount(gi, fgc)))
    return {'input': gi, 'output': go}

def generate_sum_max_lines_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ sum the lines of the color with the most lines"""
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    freq = [(0, 0)] * 10
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(c, (1, l)))
        freq[c] = (freq[c][0] + 1, freq[c][1] + l)
    ordered = sorted([(count, c) for c, (count, _) in enumerate(freq)], reverse=True)
    # if there's a tie, add an extra line to break the tie
    max_c = ordered[0][1]
    if ordered[0][0] == ordered[1][0]:
        if max_c == prev_c: # if the most frequent color is the same as the previous color, use the second most frequent color
            max_c = ordered[1][1]
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(max_c, (1, l)))
        freq[max_c] = (freq[max_c][0] + 1, freq[max_c][1] + l)
    go = canvas(max_c, (1, freq[max_c][1]))
    return {'input': gi, 'output': go}

def generate_sum_max_lines_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ sum the lines of the color with the most lines, removing background """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    freq = [(0, 0)] * 10
    prev_c = None
    for _ in range(n):
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            c = choice(colors)
        else:
            c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(c, (1, l)))
        freq[c] = (freq[c][0] + 1, freq[c][1] + l)
    ordered = sorted([(count, c) for c, (count, _) in enumerate(freq)], reverse=True)
    # if there's a tie, add an extra line to break the tie
    max_c = ordered[0][1]
    if ordered[0][0] == ordered[1][0]:
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
        elif max_c == prev_c: # if the most frequent color is the same as the previous color, use the second most frequent color
            max_c = ordered[1][1]
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(max_c, (1, l)))
        freq[max_c] = (freq[max_c][0] + 1, freq[max_c][1] + l)
    if choice([True, False]): gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    go = canvas(max_c, (1, freq[max_c][1]))
    return {'input': gi, 'output': go}

# NOTE: if count min is 1, then this is essentially select min line
def generate_sum_min_lines_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ sum the lines of the color with the least lines """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    freq = [(0, 0)] * 10
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(c, (1, l)))
        freq[c] = (freq[c][0] + 1, freq[c][1] + l)
    ordered = sorted([(count, c) for c, (count, _) in enumerate(freq) if count > 0])
    # if there's a tie, add an extra line to break the tie
    while ordered[0][0] == ordered[1][0]:
        add_c = ordered[1][1]
        if add_c == prev_c: # if the least frequent color is the same as the previous color, use the second least frequent color
            add_c = ordered[2][1] if len(ordered) > 2 else ordered[0][1]
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(add_c, (1, l)))
        freq[add_c] = (freq[add_c][0] + 1, freq[add_c][1] + l)
        prev_c = add_c
        ordered = sorted([(count, c) for c, (count, _) in enumerate(freq) if count > 0])
    if choice([True, False]): gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    min_c = ordered[0][1]
    go = canvas(min_c, (1, freq[min_c][1]))
    return {'input': gi, 'output': go}

# NOTE: if count min is 1, then this is essentially select min line
def generate_sum_min_lines_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ sum the lines of the color with the least lines, removing background """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    freq = [(0, 0)] * 10
    prev_c = None
    for _ in range(n):
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            c = choice(colors)
        else:
            c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(c, (1, l)))
        freq[c] = (freq[c][0] + 1, freq[c][1] + l)
    ordered = sorted([(count, c) for c, (count, _) in enumerate(freq) if count > 0])
    # if there's a tie, add an extra line to break the tie
    while ordered[0][0] == ordered[1][0]:
        add_c = ordered[1][1]
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
        elif add_c == prev_c: # if the least frequent color is the same as the previous color, use the second least frequent color
            add_c = ordered[2][1] if len(ordered) > 2 else ordered[0][1]
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(add_c, (1, l)))
        freq[add_c] = (freq[add_c][0] + 1, freq[add_c][1] + l)
        prev_c = add_c
        ordered = sorted([(count, c) for c, (count, _) in enumerate(freq) if count > 0])
    if choice([True, False]): gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    min_c = ordered[0][1]
    go = canvas(min_c, (1, freq[min_c][1]))
    return {'input': gi, 'output': go}

def generate_sum_max_combined_length_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ sum the lines of the color with the most lines, removing background """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    combined_len = [0] * 10
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(c, (1, l)))
        combined_len[c] += l
    ordered = sorted([(length, c) for c, length in enumerate(combined_len)], reverse=True)
    # if there's a tie, add an extra line to break the tie
    max_c = ordered[0][1]
    if ordered[0][0] == ordered[1][0]:
        if max_c == prev_c: # if the most frequent color is the same as the previous color, use the second most frequent color
            max_c = ordered[1][1]
        gi = hconcat(gi, canvas(max_c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        combined_len[max_c] += 1
    go = canvas(max_c, (1, combined_len[max_c]))
    return {'input': gi, 'output': go}

def generate_sum_max_combined_length_remove_background(diff_lb: float, diff_ub: float) -> dict:
    """ sum the lines of the color with the most lines, removing background """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    combined_len = [0] * 10
    prev_c = None
    for _ in range(n):
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            c = choice(colors)
        else:
            c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        gi = hconcat(gi, canvas(c, (1, l)))
        combined_len[c] += l
    ordered = sorted([(length, c) for c, length in enumerate(combined_len)], reverse=True)
    # if there's a tie, add an extra line to break the tie
    max_c = ordered[0][1]
    if ordered[0][0] == ordered[1][0]:
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
        elif max_c == prev_c: # if the most frequent color is the same as the previous color, use the second most frequent color
            max_c = ordered[1][1]
        gi = hconcat(gi, canvas(max_c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN)))))
        combined_len[max_c] += 1
    if choice([True, False]): gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    go = canvas(max_c, (1, combined_len[max_c]))
    return {'input': gi, 'output': go}

# NOTE: just reverse the test cases for sort DESCENDING
def generate_sort_increasing_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ sort the lines of _distinct_ length and color in increasing order of length 
        all lines must have _unique_ length
    """
    while True:
        n = unifint(diff_lb, diff_ub, (2, 9))
        colors = interval(1, 10, 1)
        cs = sample(colors, n)
        ls = sample(interval(1, MAX_LEN, 1), n) # lengths are unique
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
        colors = interval(1, 10, 1)
        cs = sample(colors, n)
        ls = sample(interval(1, MAX_LEN, 1), n) # lengths are unique
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
        colors = interval(1, 10, 1)
        cs = sample(colors, n)
        rnge = interval(1, MAX_LEN, 1)
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
        colors = interval(1, 10, 1)
        cs = sample(colors, n)
        rnge = interval(1, MAX_LEN, 1)
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