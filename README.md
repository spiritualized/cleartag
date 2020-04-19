# cleartag

Audio metadata library providing a transparent interface for reading and writing MP3, FLAC, and other popular formats.

Includes support for parsing Xing/LAME/VBRI frames in MP3 files.

### Example usage
```python
from cleartag.ClearTag import read_tags

track = read_tags("/path/to/my.mp3")
print(track.release_title)

track.release_title = "A new title"
write_tags("/path/to/my.mp3", track)
```

### Reference

#### Track
```
artist.artist_name: str
artist.listener_count: int
artist.play_count: int
artist.biography: str
artist.cover_image: str
artist.tags: OrderedDict[str, int]      # tag -> weight

track.artists: List[str]
track.release_artists: List[str]
track.date: str
track.release_title: str
track.track_title: str
track.track_number: int
track.total_tracks: int
track.disc_number: int
track.total_discs: int
track.genres: List[str]
track.stream_info: StreamInfo
```

#### StreamInfo
```python
stream_info.tag_type: TagType(Enum[UNKNOWN, ID3, FLAC, MP4])
stream_info.length: float
stream_info.bitrate: int
stream_info.bits_per_sample: int
stream_info.mp3_method: Mp3Method(Enum[UNKNOWN, CBR, VBR, ABR])
stream_info.xing: Xing
```

#### Xing
```python
xing.header_type: XingHeader(Enum[NONE, XING, LAME, VBRI, INFO])
xing.method: Mp3Method(Enum[UNKNOWN, CBR, VBR, ABR])
xing.xing_vbr_v: int
xing.xing_vbr_q: int
xing.lame_version: str
xing.lame_tag_revision: int
xing.lame_vbr_method: int
xing.lame_nspsytune: bool
xing.lame_nssafejoint: bool
xing.lame_nogap_next: bool
xing.lame_nogap_previous: bool
```