import os
import unittest
from unittest.mock import MagicMock

import bitstring
import mockito
import mutagen
from mockito.mocking import mock
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4, EasyMP4Tags
from mutagen.flac import FLAC, VCFLACDict
from mutagen.mp3 import EasyMP3, BitrateMode

from cleartag.ClearTag import read_tags, write_tags, read_xing
from cleartag.Track import Track
from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.XingHeader import XingHeader

test_metadata = {
    "artist": ["test artist"],
    "albumartist": ["test release artist"],
    "date": ["2011-12-31"],
    "album": ["test release title"],
    "title": ["test track title"],
    "tracknumber": ["1/1"],
    "discnumber": ["1/1"],
    "genre": ["example genre"]
}

def create_file_mock(file_class, tag_class) -> MagicMock:

    mock_file = MagicMock(file_class)
    mock_file.tags = MagicMock(tag_class)
    mock_file.tags.__getitem__.side_effect = test_metadata.__getitem__
    mock_file.tags.__iter__.side_effect = test_metadata.__iter__
    mock_file.tags.__contains__.side_effect = test_metadata.__contains__

    mock_file.info = MagicMock()
    mock_file.info.bitrate_mode = BitrateMode.CBR
    mock_file.info.length = 100.123
    mock_file.info.bitrate = 128000

    return mock_file


class TestClearTag(unittest.TestCase):

    def test_read_tags_mp3(self):
        easy_mp3 = create_file_mock(EasyMP3, EasyID3)
        mockito.when(os.path).isfile(mockito.ANY).thenReturn(True)
        mockito.when(mutagen).File(mockito.ANY, easy=True).thenReturn(easy_mp3)

        mockMP3 = bitstring.ConstBitStream(hex="0x496E666F")
        mockito.when(bitstring).ConstBitStream(filename=mockito.ANY).thenReturn(mockMP3)

        track = read_tags("placeholder/path")

        assert track.artists == test_metadata["artist"]
        assert track.release_artists == test_metadata["albumartist"]
        assert track.date == test_metadata["date"][0]
        assert track.release_title == test_metadata["album"][0]
        assert track.track_title == test_metadata["title"][0]
        assert track.track_number == int(test_metadata["tracknumber"][0].split("/")[0])
        assert track.total_tracks == int(test_metadata["tracknumber"][0].split("/")[1])
        assert track.disc_number == int(test_metadata["discnumber"][0].split("/")[0])
        assert track.total_discs == int(test_metadata["discnumber"][0].split("/")[1])

        mockito.unstub()

    def test_read_tags_flac(self):
        flac = create_file_mock(FLAC, VCFLACDict)
        mockito.when(os.path).isfile(mockito.ANY).thenReturn(True)
        mockito.when(mutagen).File(mockito.ANY, easy=True).thenReturn(flac)

        track = read_tags("placeholder/path")

        assert track.artists == test_metadata["artist"]
        assert track.release_artists == test_metadata["albumartist"]
        assert track.date == test_metadata["date"][0]
        assert track.release_title == test_metadata["album"][0]
        assert track.track_title == test_metadata["title"][0]
        assert track.track_number == int(test_metadata["tracknumber"][0].split("/")[0])
        assert track.total_tracks == int(test_metadata["tracknumber"][0].split("/")[1])
        assert track.disc_number == int(test_metadata["discnumber"][0].split("/")[0])
        assert track.total_discs == int(test_metadata["discnumber"][0].split("/")[1])

        mockito.unstub()

    def test_read_tags_mp4(self):
        mp4 = create_file_mock(EasyMP4, EasyMP4Tags)
        mockito.when(os.path).isfile(mockito.ANY).thenReturn(True)
        mockito.when(mutagen).File(mockito.ANY, easy=True).thenReturn(mp4)

        track = read_tags("placeholder/path")

        assert track.artists == test_metadata["artist"]
        assert track.release_artists == test_metadata["albumartist"]
        assert track.date == test_metadata["date"][0]
        assert track.release_title == test_metadata["album"][0]
        assert track.track_title == test_metadata["title"][0]
        assert track.track_number == int(test_metadata["tracknumber"][0].split("/")[0])
        assert track.total_tracks == int(test_metadata["tracknumber"][0].split("/")[1])
        assert track.disc_number == int(test_metadata["discnumber"][0].split("/")[0])
        assert track.total_discs == int(test_metadata["discnumber"][0].split("/")[1])

        mockito.unstub()

    def test_write_tags(self):
        save_func = mock()
        easy_mp3 = mock({'tags': test_metadata, 'save': save_func}, spec=mutagen.FileType)
        mockito.when(os.path).isfile(mockito.ANY).thenReturn(True)
        mockito.when(mutagen).File(mockito.ANY, easy=True).thenReturn(easy_mp3)

        track = Track(artists=["new artist"],
                      release_artists=["new release artist"],
                      date="2000",
                      release_title="new release title",
                      track_title="new track title",
                      track_number=1,
                      total_tracks=1,
                      disc_number=1,
                      total_discs=1,
                      genres=["witch house"])

        write_tags("placeholder/path", track)

        save_func.assert_called_once()

        mockito.unstub()

    def test_write_empty_tags(self):
        save_func = mock()
        easy_mp3 = mock({'tags': test_metadata, 'save': save_func}, spec=mutagen.FileType)
        mockito.when(os.path).isfile(mockito.ANY).thenReturn(True)
        mockito.when(mutagen).File(mockito.ANY, easy=True).thenReturn(easy_mp3)

        track = Track()

        write_tags("placeholder/path", track)

        save_func.assert_called_once()

        mockito.unstub()

    def test_read_Xing_LAME(self):
        mockMP3 = bitstring.ConstBitStream(hex="58696e670000000f000023430069e2a800010306080a0c0f1214171a1c1e21242628" +
                                               "2a2d30323537393c3f4244474a4d505254575a5d5f616466696b6e707376787b7d80" +
                                               "8284878a8c8f9295989b9d9fa2a4a7a8abadb0b2b5b7babcbfc2c4c7cacdd0d3d5d8" +
                                               "dbdee0e2e5e8ebeef1f3f6fafdff0000004e4c414d4520454f532e03be0000000000" +
                                               "00000034")

        mockito.when(bitstring).ConstBitStream(filename=mockito.ANY).thenReturn(mockMP3)
        xing = read_xing("placeholder/path")

        assert xing.lame_version == "EOS"

        mockito.unstub()

    def test_read_Xing_Info(self):
        mockMP3 = bitstring.ConstBitStream(hex="0x496E666F")

        mockito.when(bitstring).ConstBitStream(filename=mockito.ANY).thenReturn(mockMP3)
        xing = read_xing("placeholder/path")

        assert xing.header_type == XingHeader.INFO

        mockito.unstub()

    def test_read_Xing_VBRI(self):
        mockMP3 = bitstring.ConstBitStream(hex="0x56425249")

        mockito.when(bitstring).ConstBitStream(filename=mockito.ANY).thenReturn(mockMP3)
        xing = read_xing("placeholder/path")

        assert xing.header_type == XingHeader.VBRI

        mockito.unstub()

    def test_read_Xing_no_match(self):
        mockMP3 = bitstring.ConstBitStream()

        mockito.when(bitstring).ConstBitStream(filename=mockito.ANY).thenReturn(mockMP3)
        xing = read_xing("placeholder/path")

        assert xing.header_type == XingHeader.NONE
        assert xing.method == Mp3Method.CBR

        mockito.unstub()

    def test_real(self):

        path = "C:\\testhash\\aps.mp3"
        # path = "C:\\testhash\\102 - Mesmerizing The Ultra.mp3"
        #path = "C:\\testhash\\flac.flac"
        # path = "C:\\testhash\\mp4.mp4"

        track = read_tags(path)
        print(track)
        #track.genres.append("cock rock")
        #write_tags(path, track)

        track = read_tags(path)
        print(track)
