import unittest

from cleartag.StreamInfo import StreamInfo
from cleartag.Track import Track
from cleartag.Xing import Xing
from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.TagType import TagType


def create_test_track():
    xing = Xing()
    stream_info = StreamInfo(tag_type=TagType.ID3, length=100.123, bitrate=128000, xing=xing)

    return Track(artists=["artist"], release_artists=["release artist"], date="release date", release_title="release title",
                 track_title="track title", track_number=1, total_tracks=1, disc_number=1, total_discs=1,
                 genres=["Bass"], stream_info=stream_info)

class TestTrack(unittest.TestCase):

    def test_init(self):
        track = create_test_track()

        assert track.artists == ["artist"]

    def test_validate(self):
        track = create_test_track()

        assert track.validate()

    def test_get_codec_setting(self):
        track = create_test_track()
        track.stream_info.mp3_method = Mp3Method.CBR
        assert track.get_codec_setting_str() == "CBR"

        track.stream_info.mp3_method = Mp3Method.VBR
        assert track.get_codec_setting_str() == "VBR"

        track.stream_info.mp3_method = Mp3Method.ABR
        assert track.get_codec_setting_str() == "ABR"

        track.stream_info.xing.lame_version = "1"
        track.stream_info.xing.lame_vbr_method = 1
        assert track.get_codec_setting_str() == "CBR"

        track.stream_info.xing.lame_vbr_method = 3
        track.stream_info.xing.xing_vbr_v = 0
        assert track.get_codec_setting_str() == "APE"

        track.stream_info.xing.xing_vbr_v = 2
        assert track.get_codec_setting_str() == "APS"

        track.stream_info.xing.xing_vbr_v = 4
        assert track.get_codec_setting_str() == "APM"

        track.stream_info.xing.xing_vbr_v = 1
        assert track.get_codec_setting_str() == "vbr-old V1"

        track.stream_info.xing.lame_vbr_method = 4
        assert track.get_codec_setting_str() == "V1"

        track.stream_info.xing.lame_vbr_method = 2
        assert track.get_codec_setting_str() == "ABR"

        track.stream_info.xing.lame_vbr_method = 6
        assert track.get_codec_setting_str() == "lame_vbr_method 6"

        track.stream_info.tag_type = TagType.FLAC
        track.stream_info.bits_per_sample = 16
        assert track.get_codec_setting_str() == "FLAC"

        track.stream_info.bits_per_sample = 24
        assert track.get_codec_setting_str() == "24bit FLAC"

        track.stream_info.tag_type = TagType.MP4
        assert track.get_codec_setting_str() == "UNKNOWN"



    def test_get_filename(self):
        track = create_test_track()

        assert track.get_filename() == "01 - track title.mp3"
        assert track.get_filename(include_artist=True) == "01 - artist - track title.mp3"

    def test_eq(self):
        track1 = create_test_track()

        track2 = create_test_track()

        assert track1 == track2

        track2.genres.append("peniscore")

        assert track1 != track2


    def test_repr(self):
        track = create_test_track()

        assert "release date" in track.__repr__()
