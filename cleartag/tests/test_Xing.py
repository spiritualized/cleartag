import unittest

from cleartag.Xing import Xing
from cleartag.enums.Mp3Method import Mp3Method
from cleartag.enums.XingHeader import XingHeader


class TestStreamHeader(unittest.TestCase):

    def test_init(self):
        xing = create_xing()

        assert xing.header_type == XingHeader.LAME

    def test_eq(self):
        xing1 = create_xing()

        xing2 = create_xing()

        assert xing1 == xing2

        xing2.method = "CBR"

        assert xing1 != xing2


    def test_repr(self):
        xing = create_xing()

        assert "LAME" in xing.__repr__()


def create_xing():
    return Xing(header_type = XingHeader.LAME, method = Mp3Method.VBR, xing_vbr_v = 2, xing_vbr_q = 2,
                lame_version = "CUSTOM1", lame_tag_revision = 0, lame_vbr_method = 3,
                lame_nspsytune = False, lame_nssafejoint = False, lame_nogap_next = False,
                lame_nogap_previous = True)