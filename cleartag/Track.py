import copy
from textwrap import dedent
from typing import List, Optional, Tuple

from cleartag.StreamInfo import StreamInfo
from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.TagType import TagType
from cleartag.functions import normalize_path_chars


class Track:

    def __init__(self, artists:List[str] = None, release_artists:List[str] = None, date:str = "",
                 release_title:str = "", track_title:str = None, track_number:int = None, total_tracks:int = None,
                 disc_number:int = None, total_discs:int = None, genres:List[str] = None, comment: str = None,
                 always_write: bool = False, stream_info:StreamInfo = None) -> None:

        assert artists is None or (isinstance(artists, list) and all(x != "" for x in artists))
        assert release_artists is None or (isinstance(release_artists, list) and all(x != "" for x in release_artists))
        assert date is None or isinstance(date, str)
        assert release_title is None or isinstance(release_title, str)
        assert track_title is None or (isinstance(track_title, str) and track_title != "")
        assert track_number is None or isinstance(track_number, int)
        assert total_tracks is None or (isinstance(total_tracks, int) and total_tracks > 0)
        assert disc_number is None or (isinstance(disc_number, int) and disc_number > 0)
        assert total_discs is None or (isinstance(total_discs, int) and total_discs > 0)
        assert genres is None or (isinstance(genres, list) and all(x != "" for x in genres))
        assert comment is None or isinstance(comment, str)
        assert isinstance(always_write, bool)

        self.artists = artists or []
        self.release_artists = release_artists or []
        self.date = date
        self.release_title = release_title
        self.track_title = track_title
        self.track_number = track_number if isinstance(track_number, int) and track_number > 0 else None
        self.total_tracks = total_tracks if isinstance(total_discs, int) and total_discs > 0 else None
        self.disc_number = disc_number if isinstance(disc_number, int) and disc_number > 0 else None
        self.total_discs = total_discs if isinstance(total_discs, int) and total_discs > 0 else None
        self.genres = genres or []
        self.comment = comment
        self.always_write = always_write
        self.stream_info = copy.deepcopy(stream_info)

        # Remove duplicates
        self.artists = list(dict.fromkeys(self.artists))
        self.release_artists = list(dict.fromkeys(self.release_artists))
        self.genres = list(dict.fromkeys(self.genres))

    def __lt__(self, other) -> bool:
        if self.disc_number and other.disc_number and self.disc_number < other.disc_number:
            return True
        elif self.disc_number and other.disc_number and self.disc_number > other.disc_number:
            return False
        elif not self.disc_number and other.disc_number:
            return True
        elif self.disc_number and not other.disc_number:
            return False
        elif not self.disc_number and not other.disc_number:
            return False

        # at this point, both have a disc number set and they are equal
        if self.track_number and other.track_number:
            return self.track_number < other.track_number
        elif not self.track_number and other.track_number:
            return False
        elif self.track_number and not other.track_number:
            return True

    def validate(self) -> bool:
        return len(self.artists) \
               and len(self.release_artists) \
               and self.date is not None and self.date != "" \
               and self.release_title is not None and self.release_title != "" \
               and self.track_number is not None and self.track_number > 0 \
               and self.track_title is not None and self.track_title != ""

    def get_codec(self) -> str:
        codec_setting = self.get_codec_setting()

        if codec_setting[0] == "FLAC" and codec_setting[1]:
            return "{0} {1}".format(codec_setting[1], codec_setting[0])
        return codec_setting[0]

    def get_codec_setting_str(self, short: bool=True) -> str:
        """Return a the codec format/setting as a string"""
        codec_setting = self.get_codec_setting()

        if codec_setting[0] == "FLAC":
            if codec_setting[1]:
                return "{0} {1}".format(codec_setting[1], codec_setting[0])
            return codec_setting[0]

        if short:
            return codec_setting[1]

        return "{0} {1}".format(codec_setting[0], codec_setting[1])

    def get_codec_setting(self) -> Tuple[str, Optional[str]]:
        """Return a tuple of format, setting"""

        if self.stream_info.tag_type == TagType.FLAC:
            if self.stream_info.bits_per_sample != 16:
                return "FLAC", "{0}bit".format(self.stream_info.bits_per_sample)

            return "FLAC", None

        elif self.stream_info.tag_type == TagType.MP4:
            return "MP4", "UNKNOWN"

        elif self.stream_info.tag_type == TagType.ID3:

            if self.stream_info.xing.lame_version:

                if self.stream_info.xing.lame_vbr_method is None:
                    return "MP3", "VBR"

                if self.stream_info.xing.lame_vbr_method == 1:  # [CBR]
                    return "MP3", "CBR"

                # CBR 2-pass
                elif self.stream_info.xing.lame_vbr_method == 8:
                    """Prior to LAME 3.94, the VBR header was only written in VBR files"""
                    if self.stream_info.xing.lame_version_major and self.stream_info.xing.lame_version_minor and \
                            (self.stream_info.xing.lame_version_major, self.stream_info.xing.lame_version_minor) \
                            < (3, 94):
                        return "MP3", "VBR"
                    else:
                        return "MP3", "CBR"

                elif self.stream_info.xing.lame_vbr_method == 3:  # [VBR old]
                    if self.stream_info.xing.xing_vbr_v == 0:
                        return "MP3", "APE"
                    elif self.stream_info.xing.xing_vbr_v == 2:
                        return "MP3", "APS"
                    elif self.stream_info.xing.xing_vbr_v == 4:
                        return "MP3", "APM"
                    else:
                        return "MP3", "vbr-old V{0}".format(self.stream_info.xing.xing_vbr_v)

                elif self.stream_info.xing.lame_vbr_method in [4, 5]:  # [VBR MTRH, VBR MT]
                    return "MP3", "V{0}".format(self.stream_info.xing.xing_vbr_v)
                elif self.stream_info.xing.lame_vbr_method in [2, 9]:  # [ABR, ABR 2-pass]
                    return "MP3", "ABR"
                else:
                    return "MP3", "lame_vbr_method {0}".format(self.stream_info.xing.lame_vbr_method)

            elif self.stream_info.mp3_method == Mp3Method.CBR:
                return "MP3", "CBR"
            elif self.stream_info.mp3_method == Mp3Method.VBR:
                return "MP3", "VBR"
            elif self.stream_info.mp3_method == Mp3Method.ABR:
                return "MP3", "ABR"

    def get_filename(self, include_artist=False) -> Optional[str]:
        disc_number = self.disc_number
        if not self.total_discs or self.total_discs <= 1:
            disc_number = ""
        elif self.total_discs and self.total_discs > 9:
            disc_number = str(disc_number).zfill(2)

        ext = self.stream_info.get_ext()

        if self.disc_number is None or self.disc_number == 0 \
                or self.track_number is None or self.track_number == 0 or self.artists == [] \
                or self.track_title is None or self.track_title == "" or (include_artist and not len(self.artists)):
            return None

        disc_track_prefix = "{disc_number}{track_number} - ".format(disc_number=disc_number,
                                                                    track_number=str(self.track_number).zfill(2))
        if self.disc_number == 1 and self.total_discs == 1 and self.track_number == 1 and self.total_tracks == 1:
            disc_track_prefix = ""

        if include_artist:
            return normalize_path_chars("{disc_track_prefix}{artist} - {track_title}.{ext}"
                                        .format(disc_track_prefix=disc_track_prefix,
                                                track_title=self.track_title,
                                                ext=ext,
                                                artist=", ".join(self.artists)))

        else:
            return normalize_path_chars("{disc_track_prefix}{track_title}.{ext}"
                                        .format(disc_track_prefix=disc_track_prefix,
                                                track_title=self.track_title,
                                                ext=ext))

    def __eq__(self, other: "Track") -> bool:
        return self.artists == other.artists and self.release_artists == other.release_artists \
               and self.date == other.date and self.release_title == other.release_title \
               and self.track_title == other.track_title and self.track_number == other.track_number \
               and self.total_tracks == other.total_tracks and self.disc_number == other.disc_number \
               and self.total_discs == other.total_discs and self.genres == other.genres \
               and self.comment == other.comment

    def __ne__(self, other: "Track") -> bool:
        return not self == other

    def __repr__(self) -> str:
        track_str = dedent("""\
                Artists:            {artists}
                Release Artists:    {release_artists}
                Date:               {date}
                Release Title:      {release_title}
                Track Title:        {track_title}
                Track Number:       {track_number}
                Total Tracks:       {total_tracks}
                Disc Number:        {disc_number}
                Total Discs:        {total_discs}
                Genres:             {genres}""".format(
                                    artists=("[" + ", ".join(self.artists) + "]" if self.artists else None),
                                    release_artists=("[" + ", ".join(self.release_artists) + "]"
                                                     if self.release_artists else None),
                                    date="str'"+self.date+"'" if self.date else None,
                                    release_title="str'"+self.release_title if self.release_title else None,
                                    track_title="str'"+self.track_title if self.track_title else None,
                                    track_number="int'"+str(self.track_number)+"'" if self.track_number else None,
                                    total_tracks="int'"+str(self.total_tracks)+"'" if self.total_tracks else None,
                                    disc_number="int'"+str(self.disc_number)+"'" if self.disc_number else None,
                                    total_discs="int'"+str(self.total_discs)+"'",
                                    genres=("[" + ", ".join(self.genres) + "]" if self.genres else None),
                                    stream_info=self.stream_info))

        stream_info_str = "Stream info: {0}".format(self.stream_info)

        return "{0}\n{1}".format(track_str, stream_info_str)
