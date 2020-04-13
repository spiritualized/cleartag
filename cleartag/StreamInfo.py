from cleartag.Xing import Xing
from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.TagType import TagType


class StreamInfo:

    def __init__(self, tag_type: TagType, length: float, bitrate: int, bits_per_sample: int = None,
                 mp3_method: Mp3Method = None, xing: Xing = None) -> None:

        assert isinstance(tag_type, TagType)
        assert isinstance(length, float) and length > 0, "Invalid track length"
        assert isinstance(bitrate, int) and bitrate > 0, "Invalid bitrate"
        assert mp3_method != Mp3Method.UNKNOWN, "Unknown mp3 method"
        assert tag_type != TagType.UNKNOWN, "Unknown tag type '{0}'".format(tag_type)

        self.tag_type = tag_type
        self.length = length
        self.bitrate = bitrate
        self.bits_per_sample = bits_per_sample
        self.mp3_method = mp3_method
        self.xing = xing

    def get_ext(self):
        if self.tag_type == TagType.FLAC:
            return "flac"
        if self.tag_type == TagType.ID3:
            return "mp3"
        if self.tag_type == TagType.MP4:
            return "mp4"

    def __eq__(self, other: "StreamInfo") -> bool:
        return self.tag_type == other.tag_type \
               and self.bits_per_sample == other.bits_per_sample \
               and self.xing == other.xing

    def __ne__(self, other: "StreamInfo") -> bool:
        return not self == other

    def __repr__(self) -> str:
        return ("""
                Tag type:    {tag_type}
                Length:      {length} sec
                Bitrate:     {bitrate}
                Bits:        {bits_per_sample}
                Mp3 method:  {mp3_method}
                Xing:        {xing}""".format(tag_type=self.tag_type, length=self.length, bitrate=self.bitrate,
                                              bits_per_sample=self.bits_per_sample, mp3_method=self.mp3_method,
                                              xing=self.xing))
