#
# BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2012 <courgette@bigbrotherbot.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
""" Module that is able to deal with on-screen string width """
letter_widths = {
    ' ': 1.25,
    '!': 1.0638297872340425,
    '"': 1.5384615384615385,
    '#': 3.0303030303030303,
    '$': 2.5839793281653747,
    '%': 3.1746031746031744,
    '&': 2.6246719160104988,
    "'": 0.9523809523809523,
    '(': 1.2048192771084338,
    ')': 1.2330456226880395,
    '*': 1.9569471624266144,
    '+': 2.127659574468085,
    ',': 0.9615384615384616,
    '-': 1.0869565217391304,
    '.': 0.9523809523809523,
    '/': 1.3157894736842106,
    '0': 2.577319587628866,
    '1': 1.4265335235378032,
    '2': 2.5062656641604013,
    '3': 2.525252525252525,
    '4': 2.4330900243309004,
    '5': 2.5,
    '6': 2.5,
    '7': 2.2675736961451247,
    '8': 2.577319587628866,
    '9': 2.5,
    ':': 0.9523809523809523,
    ';': 0.9523809523809523,
    '<': 2.127659574468085,
    '=': 2.127659574468085,
    '>': 2.127659574468085,
    '?': 2.638522427440633,
    '@': 4.3478260869565215,
    'A': 2.5641025641025643,
    'B': 2.5641025641025643,
    'C': 2.7777777777777777,
    'D': 2.7777777777777777,
    'E': 2.3255813953488373,
    'F': 2.109704641350211,
    'G': 2.762430939226519,
    'H': 2.73972602739726,
    'I': 0.9174311926605505,
    'J': 2.4906600249066004,
    'K': 2.4390243902439024,
    'L': 2.2675736961451247,
    'M': 3.076923076923077,
    'N': 2.7472527472527473,
    'O': 2.7777777777777777,
    'P': 2.5,
    'Q': 2.7472527472527473,
    'R': 2.577319587628866,
    'S': 2.706359945872801,
    'T': 2.350176263219742,
    'U': 2.73972602739726,
    'V': 2.557544757033248,
    'W': 3.5714285714285716,
    'X': 2.5641025641025643,
    'Y': 2.5380710659898478,
    'Z': 2.512562814070352,
    '[': 1.2345679012345678,
    '\\': 0.6493506493506493,
    ']': 1.2345679012345678,
    '^': 2.127659574468085,
    '_': 2.127659574468085,
    '`': 0.9174311926605505,
    'a': 2.2222222222222223,
    'b': 2.2831050228310503,
    'c': 2.2222222222222223,
    'd': 2.277904328018223,
    'e': 2.237136465324385,
    'f': 1.408450704225352,
    'g': 2.2883295194508007,
    'h': 2.3255813953488373,
    'i': 0.9090909090909091,
    'j': 0.9090909090909091,
    'k': 2.028397565922921,
    'l': 0.9090909090909091,
    'm': 3.3557046979865772,
    'n': 2.3255813953488373,
    'o': 2.272727272727273,
    'p': 2.2831050228310503,
    'q': 2.277904328018223,
    'r': 1.4598540145985401,
    's': 2.242152466367713,
    't': 1.408450704225352,
    'u': 2.3255813953488373,
    'v': 2.2222222222222223,
    'w': 3.278688524590164,
    'x': 2.127659574468085,
    'y': 2.2222222222222223,
    'z': 2.0408163265306123,
    '{': 1.3986013986013985,
    '|': 0.8771929824561403,
    '}': 1.3888888888888888,
    '~': 2.127659574468085
}

def width(txt):
    width = 0
    for c in txt:
        width += letter_widths[c]
    return width

def ljust(txt, pct, fill_char=' '):
    result = txt
    fill_char_size = letter_widths[fill_char]
    remaining_size = pct - width(txt)
    result += fill_char * int(remaining_size / fill_char_size)
    return result

def center(txt, pct, fill_char=' '):
    fill_char_size = letter_widths[fill_char]
    remaining_size = pct - width(txt)
    half_remaining_chars = int(remaining_size / fill_char_size / 2)
    return fill_char * half_remaining_chars + txt + fill_char * half_remaining_chars

def rjust(txt, pct, fill_char=' '):
    fill_char_size = letter_widths[fill_char]
    remaining_size = pct - width(txt)
    return fill_char * int(remaining_size / fill_char_size) + txt



