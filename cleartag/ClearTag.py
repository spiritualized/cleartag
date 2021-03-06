import math
import os
from typing import Optional, Dict, Tuple

import bitstring
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4Tags
from mutagen.flac import VCFLACDict, FLAC
from mutagen.mp3 import EasyMP3
from mutagen.oggvorbis import OggVCommentDict
from ordered_set import OrderedSet

from cleartag.Exceptions import ClearTagError
from cleartag.StreamInfo import StreamInfo
from cleartag.Track import Track
from cleartag.Xing import Xing
from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.TagType import TagType
from cleartag.enums.XingHeader import XingHeader
from cleartag.functions import convert_bitrate_mode

__id3v1_comment_key = "COMM:ID3v1 Comment:eng"
__comment_keys = ["COMM", "TXXX:COMMENT"]


def get_comment(mutagen_file) -> Tuple[Optional[str], bool]:
    """return a tuple containing the comment, and a boolean indicating consistency"""

    if not isinstance(mutagen_file, EasyMP3):
        return (mutagen_file.tags["comment"][0], False) if "comment" in mutagen_file.tags else (None, False)

    tags = mutagen_file.tags._EasyID3__id3._DictProxy__dict

    always_write = __id3v1_comment_key in tags

    keys = [x for x in tags if x in __comment_keys or x.startswith("COMM::")]
    vals = {str(tags[x]) for x in keys}
    if len(vals) > 1:
        always_write = True

    if "COMM::eng" in keys:
        return str(tags["COMM::eng"]), always_write
    elif len(keys):
        return str(tags[next(iter(keys))]), always_write

    return None, always_write


def set_comment(mutagen_file, comment: str) -> None:

    # if not an mp3 file
    if not isinstance(mutagen_file, EasyMP3):
        if comment:
            mutagen_file.tags["comment"] = [comment]
        elif "comment" in mutagen_file.tags:
            del mutagen_file.tags["comment"]
        return

    tags = mutagen_file.tags._EasyID3__id3._DictProxy__dict

    keys = [x for x in tags if x in __comment_keys or x.startswith("COMM::")]

    if __id3v1_comment_key in tags:
        del tags[__id3v1_comment_key]

    # if there are existing comments
    if keys:
        for key in keys:
            if comment:
                tags[key].text = [comment]
            else:
                del tags[key]
        return

    # create a new comment
    if comment:
        tags["COMM"] = mutagen.id3.COMM(encoding=3, text=comment)

def get_int(str_in):
    return int(str_in) if str_in.isdigit() else None


def read_tags(file_path: str) -> Track:
    assert os.path.isfile(file_path)

    try:
        file = mutagen.File(file_path, easy=True)
    except Exception as e:
        raise ClearTagError("Could not read tags from {0}".format(file_path)) from e

    artists = []
    release_artists = []
    date = None
    release_title = None
    track_title = None
    genres = []
    track_number = None
    total_tracks = None
    disc_number = None
    total_discs = None
    comment = None
    always_write = False

    # if a file is untagged, file.tags will not be set
    if file.tags:
        artists = file.tags["artist"] if "artist" in file.tags else []
        release_artists = file.tags["albumartist"] if "albumartist" in file.tags else []
        date = file.tags["date"][0] if "date" in file.tags else None
        release_title = file.tags["album"][0] if "album" in file.tags else None
        track_title = file.tags["title"][0] if "title" in file.tags else None
        genres = file.tags["genre"] if "genre" in file.tags else []
        comment, always_write = get_comment(file)

        track_number = get_int(file.tags["tracknumber"][0].split("/")[0]) if "tracknumber" in file.tags else None
        total_tracks = None
        if "tracknumber" in file.tags and len(file.tags["tracknumber"][0].split("/")) == 2:
            total_tracks = get_int(file.tags["tracknumber"][0].split("/")[1])
        disc_number = get_int(file.tags["discnumber"][0].split("/")[0]) if "discnumber" in file.tags else None
        total_discs = None
        if "discnumber" in file.tags and len(file.tags["discnumber"][0].split("/")) == 2:
            total_discs = get_int(file.tags["discnumber"][0].split("/")[1])

        # Convert any 0's to None
        track_number = track_number if track_number else None
        total_tracks = total_tracks if total_tracks else None
        disc_number = disc_number if disc_number else None
        total_discs = total_discs if total_discs else None

        # purge any empty strings
        artists = [x for x in artists if x != '']
        release_artists = [x for x in release_artists if x != '']
        date = date if date != '' else None
        release_title = release_title if release_title != '' else None
        track_title = track_title if track_title != '' else None
        genres = [x for x in genres if x != '']
        comment = comment if comment != '' else None

    xing = None
    tag_type = TagType.UNKNOWN
    bits_per_sample = None
    mp3_method = None

    if isinstance(file, EasyMP3):
        xing = read_xing(file_path)
        tag_type = TagType.ID3
        if xing:
            mp3_method = xing.method
        else:
            mp3_method = convert_bitrate_mode(file.info.bitrate_mode)
    elif isinstance(file.tags, VCFLACDict):
        tag_type = TagType.FLAC
        bits_per_sample = file.info.bits_per_sample
    elif isinstance(file.tags, EasyMP4Tags):
        tag_type = TagType.MP4
    elif isinstance(file.tags, OggVCommentDict):
        tag_type = TagType.VORBIS

    stream_info = StreamInfo(tag_type, file.info.length, file.info.bitrate, bits_per_sample, mp3_method, xing)

    return Track(artists=artists,
                 release_artists=release_artists,
                 date=date,
                 release_title=release_title,
                 track_title=track_title,
                 track_number=track_number,
                 total_tracks=total_tracks,
                 disc_number=disc_number,
                 total_discs=total_discs,
                 genres=genres,
                 comment=comment,
                 always_write=always_write,
                 stream_info=stream_info)


def write_tags(file_path: str, track: Track) -> None:
    assert os.path.isfile(file_path)
    assert isinstance(track, Track), "A valid Track object is required"

    assert isinstance(track.date, str) or track.date is None, "'Date/Year' must be a string"
    assert isinstance(track.release_title, str) or track.release_title is None, "'Album Title' must be a string"
    assert isinstance(track.track_title, str) or track.track_title is None, "'Track Title' must be a string"
    assert isinstance(track.comment, str) or track.comment is None, "'Comment' must be a string"

    assert isinstance(track.track_number, int) or track.track_number is None, "Track number must be an int"
    assert isinstance(track.total_tracks, int) or track.total_tracks is None, "Total tracks must be an int"
    assert isinstance(track.disc_number, int) or track.disc_number is None, "Disc number must be an int"
    assert isinstance(track.total_discs, int) or track.total_discs is None, "Total discs must be an int"

    # Remove duplicates, empty strings, None
    track.artists = list(dict.fromkeys([x for x in track.artists if isinstance(x, str) and x != ""]))
    track.release_artists = list(dict.fromkeys([x for x in track.release_artists if isinstance(x, str) and x != ""]))
    track.genres = list(dict.fromkeys([x for x in track.genres if isinstance(x, str) and x != ""]))

    file = mutagen.File(file_path, easy=True)
    if not file.tags:
        if isinstance(file, EasyMP3):
            file.tags = EasyID3()
        elif isinstance(file, FLAC):
            file.tags = VCFLACDict()
        else:
            raise ValueError("Tags missing in unknown format {0}".format(type(file)))

    track_number = None
    if track.track_number:
        if track.total_tracks:
            track_number = "{0}/{1}".format(track.track_number, track.total_tracks)
        else:
            track_number = "{0}".format(track.track_number)

    disc_number = None
    if track.disc_number:
        if track.total_discs:
            disc_number = "{0}/{1}".format(track.disc_number, track.total_discs)
        else:
            disc_number = "{0}".format(track.disc_number)

    if track.artists:
        file.tags["artist"] = track.artists
    elif "artist" in file.tags:
        del file.tags["artist"]

    if track.release_artists:
        file.tags["albumartist"] = track.release_artists
    elif "albumartist" in file.tags:
        del file.tags["albumartist"]

    if track.date:
        file.tags["date"] = track.date
    elif "date" in file.tags:
        del file.tags["date"]

    if track.release_title:
        file.tags["album"] = track.release_title
    elif "album" in file.tags:
        del file.tags["album"]

    if track.track_title:
        file.tags["title"] = track.track_title
    elif "title" in file.tags:
        del file.tags["title"]

    if track_number:
        file.tags["tracknumber"] = track_number
    elif "tracknumber" in file.tags:
        del file.tags["tracknumber"]

    if disc_number:
        file.tags["discnumber"] = disc_number
    elif "discnumber" in file.tags:
        del file.tags["discnumber"]

    if track.genres:
        file.tags["genre"] = track.genres
    elif "genre" in file.tags:
        del file.tags["genre"]

    set_comment(file, track.comment)

    file.save()


def decode_lame_version(bytes_in):
    try:
        return bytes_in.decode()
    except UnicodeDecodeError:
        pass

    return bytes_in.decode("windows-1252")


def read_xing(path) -> Xing:

    stream = bitstring.ConstBitStream(filename=path)

    search_start = 0
    search_end = stream.len

    # detect the ID3 tag so we can skip it
    id3_start = stream.find("0x494433", end=min(10*1000*8, stream.length), bytealigned=True)
    if len(id3_start):
        stream.bytepos += 6
        id3_header_size = 0
        for byte in stream.read("bytes:4"):
            id3_header_size = (id3_header_size << 7) | byte

        search_start = id3_start[0] + id3_header_size * 8
        search_end = min(search_start + 10 * 1000 * 8, stream.length)  # search up to 10KB following the ID3 tag

        # if the range is invalid, search the entire file
        if os.path.getsize(path) < search_start * 8:
            search_start = 0

    # look for Xing
    xing_header = __get_xing_header(stream, search_start, search_end)
    if xing_header:
        return xing_header

    info = stream.find("0x496E666F", bytealigned=True, start=search_start, end=search_end)
    if info:
        return Xing(XingHeader.INFO, Mp3Method.CBR)

    vbri = stream.find("0x56425249", bytealigned=True, start=search_start, end=search_end)
    if vbri:
        return Xing(XingHeader.VBRI, Mp3Method.VBR)

    # Assume CBR...
    return Xing(XingHeader.NONE, Mp3Method.CBR)


def __get_xing_header(stream: bitstring.ConstBitStream, search_start: int, search_end: int) -> Optional[Xing]:
    # look for Xing
    xing_header = stream.find("0x58696E67", bytealigned=True, start=search_start, end=search_end)

    if xing_header:

        xing_vbr_v = None
        xing_vbr_q = None
        lame_version = None
        lame_tag_revision = None
        lame_vbr_method = None
        lame_nspsytune = None
        lame_nssafejoint = None
        lame_nogap_next = None
        lame_nogap_previous = None

        header_type = XingHeader.XING
        method = Mp3Method.VBR
        stream.bytepos += 4
        xing_flags = stream.read("uint:32")
        if xing_flags & 1:					# skip frames field
            stream.bytepos += 4
        if xing_flags & 2:					# skip bytes field
            stream.bytepos += 4
        if xing_flags & 4:					# skip TOC
            stream.bytepos += 100  # 816
        if xing_flags & 8:
            xing_vbr_quality = stream.read("uint:32")
            xing_vbr_v = 10 - math.ceil(xing_vbr_quality/10)
            xing_vbr_q = 10 - xing_vbr_quality % 10

        # LAME versions < 3.90 do not contain encoder info, and will not be picked up by this. Treat as VBR
        lame_version_bytes = stream.read("bytes:9")
        if lame_version_bytes[0:4] == b"LAME":
            header_type = XingHeader.LAME

            lame_version = decode_lame_version(lame_version_bytes[4:]).strip()
            lame_tag_revision = stream.read("uint:4")
            lame_vbr_method = stream.read("uint:4")  # 928
            stream.bytepos += 9
            lame_nspsytune = stream.read("bool")
            lame_nssafejoint = stream.read("bool")
            lame_nogap_next = stream.read("bool")
            lame_nogap_previous = stream.read("bool")

            if lame_version[-1] == ".":
                lame_version = lame_version[:-1]

        return Xing(header_type, method, xing_vbr_v, xing_vbr_q, lame_version, lame_tag_revision, lame_vbr_method,
                    lame_nspsytune, lame_nssafejoint, lame_nogap_next, lame_nogap_previous)
