import copy
from textwrap import dedent
from typing import List

from cleartag.StreamInfo import StreamInfo
from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.TagType import TagType
from cleartag.functions import normalize_path_chars


class Track:

    def __init__(self, artists:List[str] = None, release_artists:List[str] = None, date:str = "",
                 release_title:str = "", track_title:str = None, track_number:int = None, total_tracks:int = None,
                 disc_number:int = None, total_discs:int = None, genres:List[str] = None,
                 stream_info:StreamInfo = None) -> None:

        assert artists is None or (isinstance(artists, list) and all(x != "" for x in artists))
        assert release_artists is None or (isinstance(release_artists, list) and all(x != "" for x in release_artists))
        assert isinstance(date, str)
        assert isinstance(release_title, str)
        assert track_title is None or (isinstance(track_title, str) and track_title != "")
        assert track_number is None or (isinstance(track_number, int) and track_number > 0)
        assert total_tracks is None or (isinstance(total_tracks, int) and total_tracks > 0)
        assert disc_number is None or (isinstance(disc_number, int) and disc_number > 0)
        assert total_discs is None or (isinstance(total_discs, int) and total_discs > 0)
        assert genres is None or (isinstance(genres, list) and all(x != "" for x in genres))

        self.artists = artists or []
        self.release_artists = release_artists or []
        self.date = date
        self.release_title = release_title
        self.track_title = track_title
        self.track_number = track_number
        self.total_tracks = total_tracks
        self.disc_number = disc_number
        self.total_discs = total_discs
        self.genres = genres or []
        self.stream_info = copy.deepcopy(stream_info)

        # Remove duplicates
        self.artists = list(dict.fromkeys(self.artists))
        self.release_artists = list(dict.fromkeys(self.release_artists))
        self.genres = list(dict.fromkeys(self.genres))

    def validate(self) -> bool:
        return len(self.artists) \
               and len(self.release_artists) \
               and self.date is not None and self.date != "" \
               and self.release_title is not None and self.release_title != "" \
               and self.track_number > 0 \
               and self.track_title is not None and self.track_title != ""

    def get_codec_setting(self, short:bool=True) -> str:

        if self.stream_info.tag_type == TagType.FLAC:
            if self.stream_info.bits_per_sample != 16:
                return "{0}bit FLAC".format(self.stream_info.bits_per_sample)

            return "FLAC"

        elif self.stream_info.tag_type == TagType.MP4:
            prefix_str = "" if short else "MP4 "

            return "{0}{1}".format(prefix_str, "UNKNOWN")

        elif self.stream_info.tag_type == TagType.ID3:
            prefix_str = "" if short else "MP3 "

            if self.stream_info.xing.lame_version:

                if self.stream_info.xing.lame_vbr_method in [1, 8, None]: # [CBR, CBR 2-pass]
                    return "{0}CBR".format(prefix_str)

                elif self.stream_info.xing.lame_vbr_method == 3: # [VBR old]
                    if self.stream_info.xing.xing_vbr_v == 0:
                        return "{0}APE".format(prefix_str)
                    elif self.stream_info.xing.xing_vbr_v == 2:
                        return "{0}APS".format(prefix_str)
                    elif self.stream_info.xing.xing_vbr_v == 4:
                        return "{0}APM".format(prefix_str)
                    else:
                        return "{0}vbr-old V{1}".format(prefix_str, self.stream_info.xing.xing_vbr_v)

                elif self.stream_info.xing.lame_vbr_method in [4, 5]: # [VBR MTRH, VBR MT]
                    return "{0}V{1}".format(prefix_str, self.stream_info.xing.xing_vbr_v)
                elif self.stream_info.xing.lame_vbr_method in [2, 9]: # [ABR, ABR 2-pass]
                    return "{0}ABR".format(prefix_str, short)
                else:
                    return "{0}lame_vbr_method {1}".format(prefix_str, self.stream_info.xing.lame_vbr_method)

            elif self.stream_info.mp3_method == Mp3Method.CBR:
                return "{0}CBR".format(prefix_str)
            elif self.stream_info.mp3_method == Mp3Method.VBR:
                return "{0}VBR".format(prefix_str)
            elif self.stream_info.mp3_method == Mp3Method.ABR:
                return "{0}ABR".format(prefix_str)


    def get_filename(self, include_artist=False) -> str:
        disc_number = self.disc_number if self.total_discs and self.total_discs > 1 else ""
        ext = self.stream_info.get_ext()

        if include_artist:
            return normalize_path_chars("{disc_number}{track_number} - {artist} - {track_title}.{ext}"
                                        .format(disc_number=disc_number,
                                                track_number=str(self.track_number).zfill(2),
                                                track_title=self.track_title,
                                                ext=ext,
                                                artist=", ".join(self.artists)))

        else:
            return normalize_path_chars("{disc_number}{track_number} - {track_title}.{ext}"
                                        .format(disc_number=disc_number,
                                                track_number=str(self.track_number).zfill(2),
                                                track_title=self.track_title,
                                                ext=ext))



    def __eq__(self, other: "Track") -> bool:
        return self.artists == other.artists and self.release_artists == other.release_artists and self.date == other.date \
               and self.release_title == other.release_title and self.track_title == other.track_title \
               and self.track_number == other.track_number and self.total_tracks == other.total_tracks \
               and self.disc_number == other.disc_number and self.total_discs == other.total_discs \
               and self.genres == other.genres

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
                                    artists=("[" +", ".join(self.artists) + "]" if self.artists else None),
                                    release_artists=("[" + ", ".join(self.release_artists) + "]"
                                                   if self.release_artists else None),
                                    date="str'"+self.date+"'" if self.date else None,
                                    release_title="str'"+self.release_title if self.release_title else None,
                                    track_title="str'"+self.track_title if self.track_title else None,
                                    track_number="int'"+str(self.track_number)+"'" if self.track_number else None,
                                    total_tracks="int'"+str(self.total_tracks)+"'" if self.total_tracks else None,
                                    disc_number="int'"+str(self.disc_number)+"'" if self.disc_number else None,
                                    total_discs="int'"+str(self.total_discs)+"'",
                                    genres=("[" +", ".join(self.genres) + "]" if self.genres else None),
                                    stream_info=self.stream_info))

        stream_info_str = "Stream info: {0}".format(self.stream_info)

        return "{0}\n{1}".format(track_str, stream_info_str)


