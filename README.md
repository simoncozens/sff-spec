Streaming Font Format
=====================

SFF is a wire transport format for font data, designed for efficient
transfer, incremental delivery, and trivial subsetting.

To see the rendered specification, go [here](https://simoncozens.github.io/sff-spec/)

`glyph2sff.py` is a simple Python script to convert a TrueType-contour
OpenType font to SFF, and optionally report on byte statistics:

```
$ python3 glyph2sff.py -s NotoSans-Regular.ttf
cmap(1640) + glyf(133689) + hmtx(9662) = 144991 bytes
loca(9668) + maxp(32) = 9700

SFF equivalent = 137687 bytes
```
