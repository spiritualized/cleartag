import unittest

from cleartag.StreamInfo import StreamInfo
from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.TagType import TagType
from cleartag.tests import test_Xing

def create_test_streaminfo():
    return StreamInfo(TagType.ID3, 100.123, 128000, 16, Mp3Method.VBR, test_Xing.create_xing())

class TestStreamInfo(unittest.TestCase):

    def test_init(self):
        stream_info = create_test_streaminfo()

        assert stream_info.xing == test_Xing.create_xing()

    def test_get_ext(self):
        assert StreamInfo(TagType.ID3, 100.123, 128000, 16, Mp3Method.VBR).get_ext() == "mp3"
        assert StreamInfo(TagType.FLAC, 100.123, 128000, 16, Mp3Method.VBR).get_ext() == "flac"
        assert StreamInfo(TagType.MP4, 100.123, 128000, 16, Mp3Method.VBR).get_ext() == "mp4"

    def test_eq(self):
        stream_info1 = create_test_streaminfo()

        stream_info2 = create_test_streaminfo()

        assert stream_info1 == stream_info2

        stream_info2.xing.lame_version = "edited"

        assert stream_info1 != stream_info2

    def test_repr(self):
        stream_info = create_test_streaminfo()
        assert "Header type:" in stream_info.__repr__()
