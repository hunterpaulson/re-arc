from dsl import *
from utils import *
import random
import collections

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
    """ sum the lines of the color the longest combined length, removing background """
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
    """ sum the lines of the color with the longest combined length, removing background """
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

# alternatively, delete odd length lines
def generate_keep_even_length(diff_lb: float, diff_ub: float) -> dict:
    """ keep the lines of even length, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    keep = []
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        if l % 2 == 0:
            obj = asobject(line)
            obj = shift(obj, (0, width_before))
            keep.append(obj)
    go = canvas(BGC, (1, width(gi)))
    for obj in keep:
        go = paint(go, obj)
    return {'input': gi, 'output': go}

# alternatively, delete even length lines
def generate_keep_odd_length(diff_lb: float, diff_ub: float) -> dict:
    """ keep the lines of odd length, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    keep = []
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        if l % 2 == 1:
            obj = asobject(line)
            obj = shift(obj, (0, width_before))
            keep.append(obj)
    go = canvas(BGC, (1, width(gi)))
    for obj in keep:
        go = paint(go, obj)
    return {'input': gi, 'output': go}

# NOTE: for small MAX_LINES, this may look like delete colors that only occur once
# alternatively, delete colors with an odd number of lines
def generate_keep_even_count(diff_lb: float, diff_ub: float) -> dict:
    """ keep the colors with an even number of lines, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    objs_of_color = [[] for _ in range(10)]
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        objs_of_color[c].append(obj)
    go = canvas(BGC, (1, width(gi)))
    for objs in objs_of_color:
        if len(objs) % 2 == 0:
            for obj in objs:
                go = paint(go, obj)
    return {'input': gi, 'output': go}

# NOTE: for small MAX_LINES, this may be a no-op or look like delete colors that occur more than once
# alternatively, delete colors with an odd number of lines
def generate_keep_odd_count(diff_lb: float, diff_ub: float) -> dict:
    """ keep the colors with an odd number of lines, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    objs_of_color = [[] for _ in range(10)]
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        objs_of_color[c].append(obj)
    go = canvas(BGC, (1, width(gi)))
    for objs in objs_of_color:
        if len(objs) % 2 == 1:
            for obj in objs:
                go = paint(go, obj)
    return {'input': gi, 'output': go}

def generate_keep_last(diff_lb: float, diff_ub: float) -> dict:
    """ keep the last line, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    obj = prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        line = canvas(c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN))))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
    go = canvas(BGC, (1, width(gi)))
    go = paint(go, obj)
    return {'input': gi, 'output': go}

# NOTE: you can reverse the test cases for keep_last_by_color
# NOTE: for small MAX_LINES, this may look like no-op
def generate_keep_first_by_color(diff_lb: float, diff_ub: float) -> dict:
    """ keep the first line of each color, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    objs_of_color = [[] for _ in range(10)]
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        line = canvas(c, (1, unifint(diff_lb, diff_ub, (1, MAX_LEN))))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        objs_of_color[c].append(obj)
    go = canvas(BGC, (1, width(gi)))
    for objs in objs_of_color:
        if objs:
            go = paint(go, objs[0])
    return {'input': gi, 'output': go}

# NOTE: you can reverse the test cases for keep_last_by_color
# NOTE: for MAX_LEN >> MAX_LINES, this may look like no-op
def generate_keep_first_by_length(diff_lb: float, diff_ub: float) -> dict:
    """ keep the first line of each length, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    objs_of_length = [[] for _ in range(MAX_LEN+1)]
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        objs_of_length[l].append(obj)
    go = canvas(BGC, (1, width(gi)))
    for objs in objs_of_length:
        if objs:
            go = paint(go, objs[0])
    return {'input': gi, 'output': go}

def generate_keep_middle(diff_lb: float, diff_ub: float) -> dict:
    """ keep the middle line in the sequence, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (1, MAX_LINES//2)) * 2 + 1 # force odd number of lines
    colors = interval(1, 10, 1)
    gi = ((),)
    prev_c = None
    middle = None
    for i in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        if i == n//2:
            middle = obj
    go = canvas(BGC, (1, width(gi)))
    go = paint(go, middle)
    return {'input': gi, 'output': go}

def generate_keep_every_other(diff_lb: float, diff_ub: float) -> dict:
    """ keep every other line in the sequence, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    prev_c = None
    keep = []
    for i in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        if i % 2 == 0:
            keep.append(obj)
    go = canvas(BGC, (1, width(gi)))
    for obj in keep:
        go = paint(go, obj)
    return {'input': gi, 'output': go}

def generate_keep_every_third(diff_lb: float, diff_ub: float) -> dict:
    """ keep every third line in the sequence, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (3, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    prev_c = None
    keep = []
    for i in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        if (i+1) % 3 == 0:
            keep.append(obj)
    go = canvas(BGC, (1, width(gi)))
    for obj in keep:
        go = paint(go, obj)
    return {'input': gi, 'output': go}

def generate_keep_max_length_distinct(diff_lb: float, diff_ub: float) -> dict:
    """ keep the line with the maximum length, distinct lengths preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    objs_of_color = [[] for _ in range(10)]
    lengths = sample(interval(1, MAX_LEN+1, 1), n)
    prev_c = None
    for l in lengths:
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        objs_of_color[c].append(obj)
    go = canvas(BGC, (1, width(gi)))
    max_length = max(width(obj) for objs in objs_of_color for obj in objs)
    for objs in objs_of_color:
        for obj in objs:
            if width(obj) == max_length:
                go = paint(go, obj)
    return {'input': gi, 'output': go}

def generate_keep_min_length_distinct(diff_lb: float, diff_ub: float) -> dict:
    """ keep the line with the minimum length, distinct lengths preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    objs_of_color = [[] for _ in range(10)]
    lengths = sample(interval(1, MAX_LEN+1, 1), n)
    prev_c = None
    for l in lengths:
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        objs_of_color[c].append(obj)
    go = canvas(BGC, (1, width(gi)))
    min_length = min(width(obj) for objs in objs_of_color for obj in objs)
    for objs in objs_of_color:
        for obj in objs:
            if width(obj) == min_length:
                go = paint(go, obj)
    return {'input': gi, 'output': go}

def generate_keep_max_length_multiple(diff_lb: float, diff_ub: float) -> dict:
    """ keep the lines with the maximum length, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    objs_of_color = [[] for _ in range(10)]
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        objs_of_color[c].append(obj)
    go = canvas(BGC, (1, width(gi)))
    max_length = max(width(obj) for objs in objs_of_color for obj in objs)
    for objs in objs_of_color:
        for obj in objs:
            if width(obj) == max_length:
                go = paint(go, obj)
    return {'input': gi, 'output': go}

def generate_keep_min_length_multiple(diff_lb: float, diff_ub: float) -> dict:
    """ keep the lines with the minimum length, preserving original spacing """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    objs_of_color = [[] for _ in range(10)]
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        width_before = width(gi)
        gi = hconcat(gi, line)
        obj = asobject(line)
        obj = shift(obj, (0, width_before))
        objs_of_color[c].append(obj)
    go = canvas(BGC, (1, width(gi)))
    min_length = min(width(obj) for objs in objs_of_color for obj in objs)
    for objs in objs_of_color:
        for obj in objs:
            if width(obj) == min_length:
                go = paint(go, obj)
    return {'input': gi, 'output': go}

# NOTE: this is a no-op
def generate_copy_0x(diff_lb: float, diff_ub: float) -> dict:
    """ generate a copy of the input"""
    n = unifint(diff_lb, diff_ub, (1, MAX_LINES * MAX_LEN))
    colors = interval(1, 10, 1)
    gi = (tuple(choices(colors, k=n)),)
    go = gi
    return {'input': gi, 'output': go}

def generate_copy_1x(diff_lb: float, diff_ub: float) -> dict:
    """ concatenate a copy of the input with itself"""
    n = unifint(diff_lb, diff_ub, (1, MAX_LINES * MAX_LEN // 2))
    colors = interval(1, 10, 1)
    gi = (tuple(choices(colors, k=n)),)
    go = hconcat(gi, gi)
    return {'input': gi, 'output': go}

def generate_copy_2x(diff_lb: float, diff_ub: float) -> dict:
    """ concatenate a copy of the input with itself twice"""
    n = unifint(diff_lb, diff_ub, (1, MAX_LINES * MAX_LEN // 3))
    colors = interval(1, 10, 1)
    gi = (tuple(choices(colors, k=n)),)
    go = hconcat(gi, hconcat(gi, gi))
    return {'input': gi, 'output': go}

def generate_mirror(diff_lb: float, diff_ub: float) -> dict:
    """copy the input and concatenate it with a mirrored copy of the input"""
    n = unifint(diff_lb, diff_ub, (1, MAX_LINES * MAX_LEN // 2))
    colors = interval(1, 10, 1)
    gi = (tuple(choices(colors, k=n)),)
    go = hconcat(gi, vmirror(gi))
    return {'input': gi, 'output': go}

def generate_mirror_copy_mirror(diff_lb: float, diff_ub: float) -> dict:
    """ concatenate a mirrored copy of the input, a copy of the input, and a mirrored copy of the input"""
    n = unifint(diff_lb, diff_ub, (1, MAX_LINES * MAX_LEN // 3))
    colors = interval(1, 10, 1)
    gi = (tuple(choices(colors, k=n)),)
    go = hconcat(vmirror(gi), hconcat(gi, vmirror(gi)))
    return {'input': gi, 'output': go}

def generate_select_longest_distinct(diff_lb: float, diff_ub: float) -> dict:
    """ output the longest line """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    go = None
    lengths = sample(interval(1, MAX_LEN+1, 1), n)
    max_length = max(lengths)
    prev_c = None
    for l in lengths:
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        line = canvas(c, (1, l))
        gi = hconcat(gi, line)
        if l == max_length:
            go = line
    return {'input': gi, 'output': go}

def generate_select_longest_multiple(diff_lb: float, diff_ub: float) -> dict:
    """ output the lines with longest length in the order of appearance """
    n = unifint(diff_lb, diff_ub, (3, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    go = ((),)
    max_length = choice(interval(2, MAX_LEN+1, 1))
    lengths = [max_length] * 2 # at least two with max length
    lengths.extend(choices(interval(1, max_length+1, 1), k=n-2))
    shuffle(lengths)
    prev_c = None
    for l in lengths:
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        line = canvas(c, (1, l))
        gi = hconcat(gi, line)
        if l == max_length:
            go = hconcat(go, line)
    return {'input': gi, 'output': go}

def generate_select_shortest_distinct(diff_lb: float, diff_ub: float) -> dict:
    """ output the shortest line """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    go = None
    lengths = sample(interval(1, MAX_LEN+1, 1), n)
    min_length = min(lengths)
    prev_c = None
    for l in lengths:
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        line = canvas(c, (1, l))
        gi = hconcat(gi, line)
        if l == min_length:
            go = line
    return {'input': gi, 'output': go}

def generate_select_shortest_multiple(diff_lb: float, diff_ub: float) -> dict:
    """ output the lines with shortest length in the order of appearance """
    n = unifint(diff_lb, diff_ub, (3, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    go = ((),)
    min_length = choice(interval(1, MAX_LEN, 1))
    lengths = [min_length] * 2 # at least two with min length
    lengths.extend(choices(interval(min_length, MAX_LEN+1, 1), k=n-2))
    shuffle(lengths)
    prev_c = None
    for l in lengths:
        c = choice([color for color in colors if color != prev_c])
        prev_c = c
        line = canvas(c, (1, l))
        gi = hconcat(gi, line)
        if l == min_length:
            go = hconcat(go, line)
    return {'input': gi, 'output': go}

def generate_select_longest_connected(diff_lb: float, diff_ub: float) -> dict:
    """ output the longest connected sequence of lines """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    objs = []
    current = None
    prev_c = None
    for _ in range(n):
        if choice([True, False]): # randomly break the sequence
            if current is not None:
                objs.append(current)
                current = None
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            c = choice(colors)
        else:
            c = choice([color for color in colors if color != prev_c])
        prev_c = c
        l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
        line = canvas(c, (1, l))
        gi = hconcat(gi, line)
        if current is None:
            current = line
        else:
            current = hconcat(current, line)
    objs.append(current)
    if choice([True, False]):
        gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    go = max(objs, key=lambda x: len(x[0]))
    return {'input': gi, 'output': go}

def generate_select_most_frequent_line_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ output the line that appears the most """
    n = unifint(diff_lb, diff_ub, (3, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    mode_length = choice(interval(1, MAX_LEN, 1))
    mode_color = choice(colors)
    m = unifint(diff_lb, diff_ub, (2, (n+1)//2)) # number of mode lines
    mode_lengths = [mode_length] * m
    go = canvas(mode_color, (1, mode_length))
    # NOTE: technically possible with high MAX_LINES that another mode is generated, but hopefully unlikely
    other_lengths = choices(interval(1, MAX_LEN+1, 1), k=n-m)
    mode_prev = False
    prev_c = None
    while mode_lengths or other_lengths:
        place_mode = choice([True, False])
        if not mode_lengths or mode_prev:
            place_mode = False
        elif not other_lengths or len(mode_lengths) > len(other_lengths): # will only be greater by one since m <= (n+1)//2
            place_mode = True

        if place_mode:
            gi = hconcat(gi, canvas(mode_color, (1, mode_lengths.pop())))
            mode_prev = True
            prev_c = mode_color
        else:
            c = choice([color for color in colors if color not in {prev_c, mode_color}])
            gi = hconcat(gi, canvas(c, (1, other_lengths.pop())))
            mode_prev = False
            prev_c = c
    return {'input': gi, 'output': go}

def generate_select_most_frequent_line_background(diff_lb: float, diff_ub: float) -> dict:
    """ output the line that appears the most, ignoring background"""
    n = unifint(diff_lb, diff_ub, (3, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    mode_length = choice(interval(1, MAX_LEN, 1))
    mode_color = choice(colors)
    m = unifint(diff_lb, diff_ub, (2, (n+1)//2)) # number of mode lines
    mode_lengths = [mode_length] * m
    go = canvas(mode_color, (1, mode_length))
    # NOTE: technically possible with high MAX_LINES that another mode is generated, but hopefully unlikely
    other_lengths = choices(interval(1, MAX_LEN+1, 1), k=n-m) # TODO: ensure no other length occurs more than mode length
    mode_prev = False
    prev_c = None
    while mode_lengths or other_lengths:
        place_mode, gap = choices([True, False], k=2)
        if not mode_lengths or (not gap and mode_prev):
            place_mode = False
        elif not other_lengths or len(mode_lengths) > len(other_lengths): # will only be greater by one since m <= (n+1)//2
            place_mode = True

        if gap:
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
        if place_mode:
            gi = hconcat(gi, canvas(mode_color, (1, mode_lengths.pop())))
            mode_prev = True
            prev_c = mode_color
        else:
            if gap:
                c = choice(colors)
            else:
                c = choice([color for color in colors if color != prev_c])
            gi = hconcat(gi, canvas(c, (1, other_lengths.pop())))
            mode_prev = False
            prev_c = c
    if choice([True, False]):
        gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
    return {'input': gi, 'output': go}

def generate_select_most_frequent_color_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ output the the color with the most distinct lines """
    n = unifint(diff_lb, diff_ub, (3, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    mode_color = choice(colors)
    m = unifint(diff_lb, diff_ub, (2, (n+1)//2)) # number of lines with mode color
    mode_lengths = choices(interval(1, MAX_LEN+1, 1), k=m)
    go = canvas(mode_color, (1, 1))
    # NOTE: technically possible with high MAX_LINES that another mode is generated, but hopefully unlikely
    other_lengths = choices(interval(1, MAX_LEN+1, 1), k=n-m)
    mode_prev = False
    prev_c = None
    while mode_lengths or other_lengths:
        place_mode = choice([True, False])
        if not mode_lengths or mode_prev:
            place_mode = False
        elif not other_lengths or len(mode_lengths) > len(other_lengths): # will only be greater by one since m <= (n+1)//2
            place_mode = True

        if place_mode:
            gi = hconcat(gi, canvas(mode_color, (1, mode_lengths.pop())))
            mode_prev = True
            prev_c = mode_color
        else:
            c = choice([color for color in colors if color not in {prev_c, mode_color}])
            gi = hconcat(gi, canvas(c, (1, other_lengths.pop())))
            mode_prev = False
            prev_c = c
    return {'input': gi, 'output': go}

def generate_select_most_frequent_length_no_background(diff_lb: float, diff_ub: float) -> dict:
    """ output the most frequent length. answer in background color"""
    n = unifint(diff_lb, diff_ub, (3, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    lengths = {}
    prev_c = None
    for _ in range(n):
        c = choice([color for color in colors if color != prev_c])
        l = choice(interval(1, MAX_LEN+1, 1))
        lengths[l] = lengths.get(l, 0) + 1
        gi = hconcat(gi, canvas(c, (1, l)))
        prev_c = c
    ordered_lengths = sorted(lengths.keys(), key=lambda x: lengths[x], reverse=True)
    # if there is a tie, add an extra line to break the tie
    mode_length = ordered_lengths[0]
    if len(ordered_lengths) > 1 and lengths[ordered_lengths[0]] == lengths[ordered_lengths[1]]:
        c = choice([color for color in colors if color != prev_c])
        gi = hconcat(gi, canvas(c, (1, mode_length)))
    go = canvas(BGC, (1, mode_length))
    return {'input': gi, 'output': go}

def generate_select_most_frequent_length_ignore_background(diff_lb: float, diff_ub: float) -> dict:
    """ output the most frequent length, ignoring background, answer in background color"""
    n = unifint(diff_lb, diff_ub, (3, MAX_LINES))
    colors = interval(1, 10, 1)
    gi = ((),)
    lengths = {}
    prev_c = None
    for _ in range(n):
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            c = choice(colors)
        else:
            c = choice([color for color in colors if color != prev_c])
        l = choice(interval(1, MAX_LEN+1, 1))
        lengths[l] = lengths.get(l, 0) + 1
        gi = hconcat(gi, canvas(c, (1, l)))
        prev_c = c
    ordered_lengths = sorted(lengths.keys(), key=lambda x: lengths[x], reverse=True)
    # if there is a tie, add an extra line to break the tie
    mode_length = ordered_lengths[0]
    if len(ordered_lengths) > 1 and lengths[ordered_lengths[0]] == lengths[ordered_lengths[1]]:
        if choice([True, False]):
            gi = hconcat(gi, canvas(BGC, (1, unifint(diff_lb, diff_ub, (1, 10)))))
            c = choice(colors)
        else:
            c = choice([color for color in colors if color != prev_c])
        gi = hconcat(gi, canvas(c, (1, mode_length)))
    go = canvas(BGC, (1, mode_length))
    return {'input': gi, 'output': go}

def _shuffle_no_adjacent_duplicates_backtracking(ints: list[int]) -> list[int]:
    """
    Attempts to shuffle a list of objects with repeated items such that
    no two identical objects are adjacent, using a backtracking approach.

    Args:
        objects_list: A list of objects to be shuffled.

    Returns:
        A new list with the objects shuffled according to the rule,
        or None if no such arrangement is possible.
    """
    n = len(ints)
    if n == 0:
        return []

    counts = collections.Counter(ints)
    # Optional: Early impossibility check.
    # For an arrangement to be possible, the count of the most frequent element (max_freq)
    # must satisfy: max_freq <= (n - max_freq) + 1  (or max_freq <= ceil(n/2))
    # if counts:
    #     max_freq_val = max(counts.values())
    #     if max_freq_val > (n - max_freq_val) + 1:
    #         # print("Early check: No solution possible due to high frequency of an element.")
    #         return None

    result_arrangement = []

    # This is the recursive backtracking solver
    def solve():
        # Base case: if the arrangement is complete
        if len(result_arrangement) == n:
            return True

        last_item_placed = result_arrangement[-1] if result_arrangement else None

        # Get all unique item types that are still available
        # Shuffle them to introduce randomness in the choice of the next item
        possible_next_items = [item for item, count in counts.items() if count > 0]
        random.shuffle(possible_next_items) # Key for randomness

        for item in possible_next_items:
            # Constraint: item must be different from the last one placed (if any)
            if item != last_item_placed:
                # Try placing this item
                result_arrangement.append(item)
                counts[item] -= 1

                # Recurse to place the next item
                if solve():
                    return True

                # Backtrack if the recursion didn't lead to a solution
                counts[item] += 1 # Restore count
                result_arrangement.pop() # Remove item from arrangement
        
        # If no item could be validly placed at this step
        return False

    if solve():
        return result_arrangement
    else:
        # No solution found after trying all possibilities
        return None

def generate_select_missing_pair(diff_lb: float, diff_ub: float) -> dict:
    """ output the line that doesn't have a duplicate in the input """
    n = unifint(diff_lb, diff_ub, (3, MAX_LINES//2))
    colors = interval(1, 10, 1)
    cart = list(product(colors, interval(1, MAX_LEN+1, 1))) # guarantee no duplicates
    items = sample(cart, n) * 2 # sample and duplicate once into pairs
    odd_one_out = choice(items)
    items.remove(odd_one_out)
    color_lengths = {c: [] for c in colors}
    for c, l in items:
        color_lengths[c].append(l)
    for c in colors:
        # ensure no color has count > n+1//2 or shuffle is impossible
        while len(color_lengths[c]) > (len(items) + 1) // 2:
            print(f"{color_lengths=}")
            l = color_lengths[c].pop()
            print(f"popped {l} from {c}")
            try:
                color_lengths[c].remove(l) # try to remove pair too
                push = [l, l] # push both to new color
            except ValueError:
                push = [l] # push odd one out to new color
            color_lengths[min(colors, key=lambda c: len(color_lengths[c]))].extend(push)
            print(f"{color_lengths=}")
    for c in colors:
        shuffle(color_lengths[c])
    cs = []
    for c in colors:
        cs.extend([c] * len(color_lengths[c]))
    cs = _shuffle_no_adjacent_duplicates_backtracking(cs)
    gi = ((),)
    for c in cs:
        gi = hconcat(gi, canvas(c, (1, color_lengths[c].pop())))
    c, l = odd_one_out
    go = canvas(c, (1, l))
    return {'input': gi, 'output': go}

def generate_select_missing_pair_by_color(diff_lb: float, diff_ub: float) -> dict:
    """ output the line that doesn't have a duplicate in the input by color """
    n = unifint(diff_lb, diff_ub, (2, 9)) # only have 9 colors
    colors = interval(1, 10, 1)
    cs = sample(colors, n) * 2
    odd_one_out = choice(cs)
    cs.remove(odd_one_out)
    cs = _shuffle_no_adjacent_duplicates_backtracking(cs)
    items = list(zip(cs, choices(interval(1, MAX_LEN, 1), k=2*n -1)))
    gi = ((),)
    for c, l in items:
        gi = hconcat(gi, canvas(c, (1, l)))
    go = canvas(odd_one_out, (1, 1))
    return {'input': gi, 'output': go}

def generate_select_missing_pair_by_length(diff_lb: float, diff_ub: float) -> dict:
    """ output the line that doesn't have a duplicate in the input by length """
    n = unifint(diff_lb, diff_ub, (2, MAX_LINES//2))
    colors = interval(1, 10, 1)
    ls = sample(interval(1, MAX_LEN, 1), n) * 2
    odd_one_out = choice(ls)
    ls.remove(odd_one_out)
    cs = choices(colors, k=2*n -1)  # TODO: make sure none has count > n+1//2
    cs = _shuffle_no_adjacent_duplicates_backtracking(cs)
    items = list(zip(cs, ls))
    gi = ((),)
    for c, l in items:
        gi = hconcat(gi, canvas(c, (1, l)))
    go = canvas(BGC, (1, odd_one_out))
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
    """ sort the lines of _distinct_ color in increasing order of length 
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
    """ sort (and concat by removing background) the lines of _distinct_ color in increasing order of length 
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

# NOTE: these have human priors so maybe they aren't in the spirit of ARC

def generate_addition(diff_lb: float, diff_ub: float) -> dict:
    """ add two lines """
    colors = interval(1, 10, 1)
    c_a, c_b = choice(colors), choice(colors) # can be same color
    l_a = unifint(diff_lb, diff_ub, (1, MAX_LEN))
    l_b = unifint(diff_lb, diff_ub, (1, MAX_LEN))
    obj_a = canvas(c_a, (1, l_a))
    obj_b = canvas(c_b, (1, l_b))
    gi = hconcat(obj_a, canvas(BGC, (1, 1)))
    gi = hconcat(gi, obj_b)
    go = canvas(c_a, (1, l_a + l_b))
    return {'input': gi, 'output': go}

def generate_subtraction(diff_lb: float, diff_ub: float) -> dict:
    """ subtract two lines """
    colors = interval(1, 10, 1)
    c_a, c_b = choice(colors), choice(colors) # can be same color
    l_a = unifint(diff_lb, diff_ub, (1, MAX_LEN))
    l_b = unifint(diff_lb, diff_ub, (1, MAX_LEN))
    if l_a == l_b:
        l_a = l_a + 1
    elif l_a < l_b:
        l_a, l_b = l_b, l_a
    obj_a = canvas(c_a, (1, l_a))
    obj_b = canvas(c_b, (1, l_b))
    gi = hconcat(obj_a, canvas(BGC, (1, 1)))
    gi = hconcat(gi, obj_b)
    go = canvas(c_a, (1, l_a - l_b))
    return {'input': gi, 'output': go}

def generate_multiplication(diff_lb: float, diff_ub: float) -> dict:
    """ multiply two lines """
    colors = interval(1, 10, 1)
    c_a, c_b = choice(colors), choice(colors) # can be same color
    l_a = unifint(diff_lb, diff_ub, (1, MAX_LEN))
    l_b = unifint(diff_lb, diff_ub, (1, MAX_LEN))
    obj_a = canvas(c_a, (1, l_a))
    obj_b = canvas(c_b, (1, l_b))
    gi = hconcat(obj_a, canvas(BGC, (1, 1)))
    gi = hconcat(gi, obj_b)
    go = canvas(c_a, (1, l_a * l_b))
    return {'input': gi, 'output': go}

def generate_division(diff_lb: float, diff_ub: float) -> dict:
    """ divide one line by another line """
    colors = interval(1, 10, 1)
    c_a, c_b = choice(colors), choice(colors) # can be same color
    l_b = unifint(diff_lb, diff_ub, (1, MAX_LEN))
    # make l_a some multiple of l_b
    l_a = l_b * unifint(diff_lb, diff_ub, (1, MAX_LEN))
    obj_a = canvas(c_a, (1, l_a))
    obj_b = canvas(c_b, (1, l_b))
    gi = hconcat(obj_a, canvas(BGC, (1, 1)))
    gi = hconcat(gi, obj_b)
    go = canvas(c_a, (1, l_a // l_b))
    return {'input': gi, 'output': go}

def generate_square(diff_lb: float, diff_ub: float) -> dict:
    """ square a line """
    colors = interval(1, 10, 1)
    c = choice(colors)
    l = unifint(diff_lb, diff_ub, (1, MAX_LEN))
    gi = canvas(c, (1, l))
    go = canvas(c, (1, l * l))
    return {'input': gi, 'output': go}

def _shuffle_adjacent_different_color(items_orig: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Arranges a list of (color, length) tuples such that no two adjacent tuples
    have the same color, with a randomized selection process.

    Args:
        items_orig: A list of (color, length) tuples.

    Returns:
        A new list with items arranged according to the constraint, or an
        empty list if the arrangement is impossible or not found within attempts.
    """
    n = len(items_orig)
    if n == 0:
        return []

    # Global feasibility check: count of any color must not be more than (n+1)//2.
    counts_global = collections.Counter(item[0] for item in items_orig)
    for color_val, count in counts_global.items():
        if count > (n + 1) // 2:
            return [] # Impossible from the start

    # Number of attempts to find a valid random shuffle
    # Increased attempts for better chance with randomness, especially for tricky inputs.
    for _attempt in range(250):
        # For each attempt, work with copies of item collections and counts
        # Shuffle available_items initially to ensure that when we pop items of a chosen color,
        # we get them in a random order if multiple identical (color, length) tuples exist.
        # However, the problem is about specific tuple instances, so we pop from lists of items of that color.
        
        # Store items grouped by color for the current attempt
        # This allows picking a specific instance of an item of a chosen color.
        current_items_by_color_attempt = collections.defaultdict(list)
        # To ensure items are picked randomly if multiple of same color exist,
        # shuffle a copy of original items before distributing them by color.
        shuffled_input_items = list(items_orig)
        random.shuffle(shuffled_input_items)
        for color, length in shuffled_input_items:
            current_items_by_color_attempt[color].append((color, length))
        
        current_counts_attempt = counts_global.copy()
        
        result_list = []
        prev_color = -1 # Sentinel for previous color (no valid color)
        possible_this_attempt = True

        for _i in range(n): # For each of the n positions in the output list
            # Identify colors that can be placed in the current slot
            possible_colors_for_slot = [
                c for c, count in current_counts_attempt.items() 
                if count > 0 and c != prev_color
            ]

            if not possible_colors_for_slot:
                possible_this_attempt = False # No valid color to pick (violates prev_color or all counts zero)
                break

            safe_to_pick_this_step = [] # List of colors that are "safe" to pick now

            for candidate_color in possible_colors_for_slot:
                # Simulate picking this candidate_color to check its safety
                current_counts_attempt[candidate_color] -= 1
                remaining_slots = n - (len(result_list) + 1)
                
                is_safe_candidate = True
                if remaining_slots < 0: # Should not happen in a correct loop over n items
                    is_safe_candidate = False
                elif remaining_slots == 0: # This is the last item; if we got here, it's safe
                    pass 
                else: # remaining_slots > 0, so more items need to be placed
                    # Check 1: Dominance. No remaining color should be too frequent for the remaining_slots.
                    for c_check in current_counts_attempt: # Check all colors with their new counts
                        if current_counts_attempt[c_check] > 0 and \
                           current_counts_attempt[c_check] > (remaining_slots + 1) // 2:
                            is_safe_candidate = False
                            break
                    if not is_safe_candidate:
                        current_counts_attempt[candidate_color] += 1 # Backtrack simulation for this candidate
                        continue # Try the next candidate_color

                    # Check 2: Avoid getting stuck. If candidate_color is chosen, ensure the *next* step is possible.
                    # The next item cannot be candidate_color. If only items of candidate_color type are left,
                    # then this path is unsafe.
                    if current_counts_attempt[candidate_color] > 0: # If candidate_color itself has remaining items
                        can_pick_a_different_next_item = False
                        for c_other in current_counts_attempt:
                            if c_other != candidate_color and current_counts_attempt[c_other] > 0:
                                can_pick_a_different_next_item = True
                                break
                        if not can_pick_a_different_next_item:
                            # Only candidate_color items are left, but next one cannot be candidate_color.
                            is_safe_candidate = False
                
                # Backtrack the simulation for this candidate_color before trying the next one or deciding
                current_counts_attempt[candidate_color] += 1 

                if is_safe_candidate:
                    safe_to_pick_this_step.append(candidate_color)
            
            if not safe_to_pick_this_step:
                possible_this_attempt = False # No safe color to pick for the current slot
                break
            
            # Randomly choose from the identified safe colors
            chosen_color = random.choice(safe_to_pick_this_step)
            
            # Add the chosen item to the result list
            # Pop an actual (color, length) tuple from our stored lists for this attempt.
            item_to_add = current_items_by_color_attempt[chosen_color].pop()
            result_list.append(item_to_add)
            
            # Update counts and prev_color for the current attempt
            current_counts_attempt[chosen_color] -= 1
            prev_color = chosen_color

        if possible_this_attempt and len(result_list) == n:
            return result_list # Successfully found a shuffle in this attempt
        
        print(f"{_attempt} failed")
            
    return [] # Failed to find a valid shuffle after all attempts