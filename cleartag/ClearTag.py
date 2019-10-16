import math
import os

import bitstring
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4Tags
from mutagen.flac import VCFLACDict

from cleartag.StreamInfo import StreamInfo
from cleartag.Track import Track
from cleartag.Xing import Xing
from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.TagType import TagType
from cleartag.enums.XingHeader import XingHeader
from cleartag.functions import convert_bitrate_mode


def read_tags(file_path: str) -> Track:
    assert os.path.isfile(file_path)

    file = mutagen.File(file_path, easy=True)

    artists = file.tags["artist"] if "artist" in file.tags else []
    release_artists = file.tags["albumartist"] if "albumartist" in file.tags else []
    date = file.tags["date"][0] if "date" in file.tags else None
    release_title = file.tags["album"][0] if "album" in file.tags else None
    track_title = file.tags["title"][0] if "title" in file.tags else None
    genres = file.tags["genre"] if "genre"in file.tags else []

    track_number = int(file.tags["tracknumber"][0].split("/")[0]) if "tracknumber" in file.tags else None
    total_tracks = None
    if "tracknumber" in file.tags and len(file.tags["tracknumber"][0].split("/")) == 2:
        total_tracks = int(file.tags["tracknumber"][0].split("/")[1])
    disc_number = int(file.tags["discnumber"][0].split("/")[0]) if "discnumber" in file.tags else None
    total_discs = None
    if "discnumber" in file.tags and len(file.tags["discnumber"][0].split("/")) == 2:
        total_discs = int(file.tags["discnumber"][0].split("/")[1])

    xing = None
    tag_type = TagType.UNKNOWN
    bits_per_sample = None
    mp3_method = None

    if isinstance(file.tags, EasyID3):
        xing = read_Xing(file_path)
        tag_type = TagType.ID3
        mp3_method = convert_bitrate_mode(file.info.bitrate_mode)
    elif isinstance(file.tags, VCFLACDict):
        tag_type = TagType.FLAC
        bits_per_sample = file.info.bits_per_sample
    elif isinstance(file.tags, EasyMP4Tags):
        tag_type = TagType.MP4

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
                 stream_info=stream_info)


def write_tags(file_path: str, track: Track) -> None:
    assert os.path.isfile(file_path)
    assert isinstance(track, Track), "A valid Track object is required"

    assert isinstance(track.date, str) or track.date is None, "'Date/Year' must be a string"
    assert isinstance(track.release_title, str) or track.release_title is None, "'Album Title' must be a string"
    assert isinstance(track.track_title, str) or track.track_title is None, "'Track Title' must be a string"

    assert isinstance(track.track_number, int) or track.track_number is None, "Track number must be a list"
    assert isinstance(track.total_tracks, int) or track.track_number is None, "Total tracks must be a list"
    assert isinstance(track.disc_number, int) or track.disc_number is None, "Disc number must be a list"
    assert isinstance(track.total_discs, int) or track.total_discs is None, "Total discs must be a list"

    # Remove duplicates, empty strings, None
    track.artists = list(dict.fromkeys([x for x in track.artists if isinstance(x, str) and x != ""]))
    track.release_artists = list(dict.fromkeys([x for x in track.release_artists if isinstance(x, str) and x != ""]))
    track.genres = list(dict.fromkeys([x for x in track.genres if isinstance(x, str) and x != ""]))

    file = mutagen.File(file_path, easy=True)

    track_number = None if not track.track_number else "{0}".format(track.track_number) if not track.total_tracks \
        else "{0}/{1}".format(track.track_number, track.total_tracks)
    disc_number = None if not track.disc_number else "{0}".format(track.disc_number) if not track.total_discs \
        else "{0}/{1}".format(track.disc_number, track.total_discs)

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

    file.save()

#tagfidelity


def read_Xing(path) -> Xing:

    stream = bitstring.ConstBitStream(filename=path)

    # look for Xing
    Xing_header = stream.find("0x58696E67", bytealigned=True)

    if Xing_header:

        xing_vbr_v = None
        xing_vbr_q = None
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
            stream.bytepos += 100 # 816
        if xing_flags & 8:
            xing_vbr_quality = stream.read("uint:32")
            xing_vbr_v = 10 - math.ceil(xing_vbr_quality/10)
            xing_vbr_q = 10 - xing_vbr_quality % 10

        # LAME versions < 3.90 do not contain encoder info, and will not be picked up by this. Treat as VBR
        lame_version = stream.read("bytes:9")
        if lame_version[0:4] == b"LAME":
            header_type = XingHeader.LAME


            lame_version = lame_version[4:].decode().strip()
            lame_tag_revision = stream.read("uint:4")
            lame_vbr_method = stream.read("uint:4") #928
            stream.bytepos += 9
            lame_nspsytune = stream.read("bool")
            lame_nssafejoint = stream.read("bool")
            lame_nogap_next = stream.read("bool")
            lame_nogap_previous = stream.read("bool")

            if lame_version[-1] == ".":
                lame_version = lame_version[:-1]

        return Xing(header_type, method, xing_vbr_v, xing_vbr_q, lame_version, lame_tag_revision, lame_vbr_method,
                    lame_nspsytune, lame_nssafejoint, lame_nogap_next, lame_nogap_previous)

    Info = stream.find("0x496E666F", bytealigned=True)
    if Info:
        return Xing(XingHeader.INFO, Mp3Method.CBR)

    VBRI = stream.find("0x56425249", bytealigned=True)
    if VBRI:
        return Xing(XingHeader.VBRI, Mp3Method.VBR)

    # Assume CBR...
    return Xing(XingHeader.NONE, Mp3Method.CBR)
