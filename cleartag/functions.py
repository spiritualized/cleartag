from mutagen.mp3 import BitrateMode

from cleartag.enums.Mp3Method import Mp3Method


def normalize_path_chars(path):
    tmp = path

    replacements = {
        ':': '：',
        '/': '∕',
        '\\': '∕',
        '*': "٭",
        '?': '﹖',
        '"': 'ˮ',
        '<': '〈',
        '>': '〉',
        '|': '⏐'
    }

    for x in replacements:
        tmp = tmp.replace(x, replacements[x])

    return tmp

def convert_bitrate_mode(mutagen_mode):
    if mutagen_mode == BitrateMode.CBR:
        return Mp3Method.CBR
    elif mutagen_mode == BitrateMode.VBR:
        return Mp3Method.VBR
    elif mutagen_mode == BitrateMode.ABR:
        return Mp3Method.ABR
    elif mutagen_mode == BitrateMode.UNKNOWN:
        return Mp3Method.CBR # probably CBR ¯\_(ツ)_/¯
    else:
        return Mp3Method.UNKNOWN
