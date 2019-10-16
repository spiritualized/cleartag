import unittest

from mutagen.mp3 import BitrateMode

from cleartag.enums.Mp3Method import Mp3Method
from cleartag.functions import convert_bitrate_mode, normalize_path_chars


class TestFunctions(unittest.TestCase):

    def test_convert_bitrate_mode(self):

        assert convert_bitrate_mode(BitrateMode.CBR) == Mp3Method.CBR
        assert convert_bitrate_mode(BitrateMode.ABR) == Mp3Method.ABR
        assert convert_bitrate_mode(BitrateMode.VBR) == Mp3Method.VBR
        assert convert_bitrate_mode(None) == Mp3Method.UNKNOWN

    def test_normalize_path_chars(self):

        assert normalize_path_chars("release title: something") == "release title： something"
