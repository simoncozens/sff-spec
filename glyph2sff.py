from fontTools.ttLib import TTFont
import sys
import argparse
import struct


parser = argparse.ArgumentParser("Test SFF streaming")
parser.add_argument('file', metavar='TTF',
                    help='font file')
parser.add_argument('-s', dest='statistics', action="store_true",
                    help='don\'t output records, just output statistics')

args = parser.parse_args()

font = TTFont(args.file)
if "glyf" not in font:
	print("Not yet")
	sys.exit(1)

def tablelen(table):
	return len(font[table].compile(font))

if args.statistics:
	cmap_l, glyf_l, hmtx_l = tablelen("cmap"), tablelen("glyf"), tablelen("hmtx")
	loca_l, maxp_l = tablelen("loca"), tablelen("maxp")
	print(f'cmap({cmap_l}) + glyf({glyf_l}) + hmtx({hmtx_l}) = {cmap_l+glyf_l+hmtx_l} bytes')
	print(f'loca({loca_l}) + maxp({maxp_l}) = {loca_l+maxp_l}\n')

output = b''
codepoints = font["cmap"].buildReversed()

lastGid = -999
lastUnicode = -999

for gid, g in enumerate(font.getGlyphOrder()):
	flags = 0
	gidcomponent = b''
	unicodescomponent = b''
	metricscomponent = b''
	pointscomponent = b''
	componentscomponent = b''
	variationscomponent = b''

	if gid == lastGid + 1:
		flags = flags & 0x1
	else:
		gidcomponent = struct.pack(">I", gid)
	lastGid = gid

	if g in codepoints and len(codepoints[g]) == 1 and list(sorted(codepoints[g]))[0] == lastUnicode + 1:
		flags = flags & 0x2
	elif g in codepoints:
		unicodescomponent = struct.pack(">B", len(codepoints[g]))
		for codepoint in codepoints[g]:
			unicodescomponent = unicodescomponent + chr(codepoint).encode('utf-8')
			lastUnicode = codepoint
	else:
		unicodescomponent = struct.pack(">B", 0)

	glyf = font["glyf"][g]
	if glyf.numberOfContours == 0:
		metricscomponent = struct.pack(">hhhhhh", 0,0,0,0,0,0)
		flags = flags & 0x40
	elif glyf.numberOfContours == -1:
		flags = flags & 0x40
		componentscomponent = glyf.compileComponents(font["glyf"])
	else:
		flags = flags & 0x80
		metricscomponent = struct.pack(">hhhhhh", *font["hmtx"][g], glyf.xMin, glyf.yMin, glyf.xMax, glyf.yMax)
		pointscomponent = struct.pack(">H", glyf.numberOfContours)
		pointscomponent = pointscomponent + glyf.compileCoordinates()


	header = struct.pack(">BB", 0x1, flags)
	output += header + gidcomponent + unicodescomponent + metricscomponent + pointscomponent + componentscomponent + variationscomponent

if args.statistics:
	print("SFF equivalent = %i bytes" % len(output))
else:
	print(output)
