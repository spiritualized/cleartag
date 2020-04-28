from textwrap import dedent

from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.XingHeader import XingHeader


class Xing:

    def __init__(self, header_type:XingHeader = None, method:Mp3Method = None, xing_vbr_v:int = None, xing_vbr_q:int = None,
                 lame_version:str = None, lame_tag_revision:int = None, lame_vbr_method:int = None,
                 lame_nspsytune:bool = None, lame_nssafejoint:bool = None, lame_nogap_next:bool = None,
                 lame_nogap_previous:bool = None) -> None:
        self.header_type = header_type
        self.method = method
        self.xing_vbr_v = xing_vbr_v
        self.xing_vbr_q = xing_vbr_q
        self.lame_version = lame_version
        self.lame_version_major = 0
        self.lame_version_minor = 0
        self.lame_tag_revision = lame_tag_revision
        self.lame_vbr_method = lame_vbr_method
        self.lame_nspsytune = lame_nspsytune
        self.lame_nssafejoint = lame_nssafejoint
        self.lame_nogap_next = lame_nogap_next
        self.lame_nogap_previous = lame_nogap_previous

        if lame_version:
            if lame_version.split(".")[0].isdigit():
                self.lame_version_major = int(lame_version.split(".")[0])
            if len(lame_version.split(".")) == 2:
                lame_version_minor = lame_version.split(".")[1]
                if len(lame_version_minor) >= 2 and lame_version_minor[0:2].isdigit():
                    self.lame_version_minor = int(lame_version_minor[0:2])


    def __eq__(self, other: "Xing") -> bool:
        return self.header_type == other.header_type and self.method == other.method \
                and self.xing_vbr_v == other.xing_vbr_v and self.xing_vbr_q == other.xing_vbr_q \
                and self.lame_version == other.lame_version and self.lame_tag_revision == other.lame_tag_revision \
                and self.lame_vbr_method == other.lame_vbr_method and self.lame_nspsytune == other.lame_nspsytune \
                and self.lame_nssafejoint == other.lame_nssafejoint and self.lame_nogap_next == other.lame_nogap_next \
                and self.lame_nogap_previous == other.lame_nogap_previous

    def __ne__(self, other: "Xing") -> bool:
        return not self == other

    def __repr__(self) -> str:
        xing_str = ""

        if self.header_type in [XingHeader.XING, XingHeader.LAME]:
            xing_str = """
                             xing_vbr_v:          {vbr_v}
                             xing_vbr_q:          {vbr_q}
            """.format(vbr_v=self.xing_vbr_v, vbr_q=self.xing_vbr_q)

        lame_str = ""

        if self.header_type == XingHeader.LAME:
            lame_str = """
                             lame_version:        {lame_version}
                             lame_tag_revision:   {lame_tag_revision}
                             lame_vbr_method:     {lame_vbr_method}
                             lame_nspsytune:      {lame_nspsytune}
                             lame_nssafejoint:    {lame_nssafejoint}
                             lame_nogap_next:     {lame_nogap_next}
                             lame_nogap_previous: {lame_nogap_previous}
            """.format(lame_version=self.lame_version, lame_tag_revision=self.lame_tag_revision,
                       lame_vbr_method=self.lame_vbr_method, lame_nspsytune=self.lame_nspsytune,
                       lame_nssafejoint=self.lame_nssafejoint, lame_nogap_next=self.lame_nssafejoint,
                       lame_nogap_previous=self.lame_nogap_previous)

        return """
                             Header type:         {header_type}
                             Method:              {method}{xing_str}{lame_str}""".format(header_type=self.header_type,
                                                                                         method=self.method,
                                                                                         xing_str=xing_str,
                                                                                         lame_str=lame_str)
