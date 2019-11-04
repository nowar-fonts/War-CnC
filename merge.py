import sys
import json
import codecs
from libotd.merge import MergeBelow
from libotd.pkana import ApplyPalt, NowarApplyPaltMultiplied
from libotd.transform import Transform, ChangeAdvanceWidth
from libotd.gc import Gc, RemoveFeature
from libotd.instruct import SetHintFlag
import configure

langIdList = [ 0x0409, 0x0804, 0x0404, 0x0C04, 0x0411, 0x0412 ]

def NameFont(param, font):
	family = configure.GenerateFamily(param)
	subfamily = configure.GenerateSubfamily(param)
	friendly = configure.GenerateFriendlyFamily(param)
	legacyf, legacysubf = configure.GenerateLegacySubfamily(param)

	font['head']['fontRevision'] = configure.config.fontRevision
	font['OS_2']['achVendID'] = configure.config.vendorId
	font['OS_2']['usWeightClass'] = param.weight
	font['OS_2']['usWidthClass'] = param.width
	font['name'] = [
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 0,
			"nameString": configure.config.copyright
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 2,
			"nameString": legacysubf
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 3,
			"nameString": "{} {}".format(friendly[1033], configure.config.version)
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 5,
			"nameString": configure.config.version
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 6,
			"nameString": friendly[1033].replace(" ", "-").replace("C²", "C&C")
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 8,
			"nameString": configure.config.vendor
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 9,
			"nameString": configure.config.designer
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 11,
			"nameString": configure.config.vendorUrl
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 12,
			"nameString": configure.config.designerUrl
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 13,
			"nameString": configure.config.license
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 14,
			"nameString": configure.config.licenseUrl
		},
		{
			"platformID": 3,
			"encodingID": 1,
			"languageID": 1033,
			"nameID": 17,
			"nameString": subfamily
		},
	] + sum(
		[[
			{
				"platformID": 3,
				"encodingID": 1,
				"languageID": langId,
				"nameID": 1,
				"nameString": "{} {}".format(family[langId], legacyf).strip()
			},
			{
				"platformID": 3,
				"encodingID": 1,
				"languageID": langId,
				"nameID": 4,
				"nameString": friendly[langId]
			},
			{
				"platformID": 3,
				"encodingID": 1,
				"languageID": langId,
				"nameID": 16,
				"nameString": family[langId]
			},
		] for langId in langIdList],
		[]
	)

	if 'CFF_' in font:
		cff = font['CFF_']
		cff['version'] = configure.config.version
		if 'notice' in cff:
			del cff['notice']
		cff['copyright'] = configure.config.copyright
		cff['fontName'] = friendly[1033].replace(" ", "-")
		cff['fullName'] = friendly[1033]
		cff['familyName'] = family[1033]
		cff['weight'] = subfamily

def AdditionalCcmp(font):
	cmap_ = font['cmap']
	u2014 = cmap_[str(0x2014)] # EM DASH
	u2015 = cmap_[str(0x2015)] # HORIZONTAL BAR
	u2E3A = cmap_[str(0x2E3A)] # TWO-EM DASH
	u2E3B = cmap_[str(0x2E3B)] # THREE-EM DASH

	gsub_ = font['GSUB']
	gsub_['lookups']['lookup_ccmp_1000'] = {
		'type': 'gsub_ligature',
		'flags': {},
		'subtables': [
			{
				'substitutions': [
					{ 'from': [ u2014, u2014, u2014 ], 'to': u2E3B },
					{ 'from': [ u2014, u2014 ], 'to': u2E3A },
					{ 'from': [ u2015, u2015, u2015 ], 'to': u2E3B },
					{ 'from': [ u2015, u2015 ], 'to': u2E3A },
				]
			}
		]
	}
	for f in gsub_['features']:
		if f[0:4] != 'ccmp':
			continue
		gsub_['features'][f].append('lookup_ccmp_1000')
	gsub_['lookupOrder'].append('lookup_ccmp_1000')

def TransfontLoclFeature(asianFont, baseFont):
	asianSymbol = [
		0x00B7, # MIDDLE DOT
		0x2014, # EM DASH
		0x2015, # HORIZONTAL BAR
		0x2018, # LEFT SINGLE QUOTATION MARK
		0x2019, # RIGHT SINGLE QUOTATION MARK
		0x201C, # LEFT DOUBLE QUOTATION MARK
		0x201D, # RIGHT DOUBLE QUOTATION MARK
		0x2026, # HORIZONTAL ELLIPSIS
		0x2027, # HYPHENATION POINT
		0x2E3A, # TWO-EM DASH
		0x2E3B, # THREE-EM DASH
	]

	# Apply ZHS `locl`, ensure asian symbol
	gsub_ = asianFont['GSUB']
	for f in gsub_['languages']['hani_ZHS ']['features']:
		if 'locl' in f:
			break
	else:
		return
	lookup = gsub_['features'][f][0]
	lut = gsub_['lookups'][lookup]
	substitution = {}
	for st in lut['subtables']:
		substitution.update(st)
	for k, v in asianFont['cmap'].items():
		if v in substitution:
			asianFont['cmap'][k] = substitution[v]

	# Rewrite this table
	st = {}
	for u in asianSymbol:
		u = str(u)
		if u in baseFont['cmap'] and u in asianFont['cmap']:
			st[baseFont['cmap'][u]] = asianFont['cmap'][u]
	lut['subtables'] = [ st ]

if __name__ == '__main__':
	param = configure.ParamFromArgument(sys.argv[1])
	dep = configure.ResolveDependency(param)

	with open("build/noto/{}.otd".format(configure.GenerateFilename(dep['Latin'])), 'rb') as baseFile:
		baseFont = json.loads(baseFile.read().decode('UTF-8', errors='replace'))
	NameFont(param, baseFont)
	SetHintFlag(baseFont)

	baseFont['hhea']['ascender'] = 880
	baseFont['hhea']['descender'] = -120
	baseFont['hhea']['lineGap'] = 200
	baseFont['OS_2']['sTypoAscender'] = 880
	baseFont['OS_2']['sTypoDescender'] = -120
	baseFont['OS_2']['sTypoLineGap'] = 200
	baseFont['OS_2']['fsSelection']['useTypoMetrics'] = True
	baseFont['OS_2']['usWinAscent'] = 1050
	baseFont['OS_2']['usWinDescent'] = 300

	with open("build/shs/{}.otd".format(configure.GenerateFilename(dep['CJK'])), 'rb') as asianFile:
		asianFont = json.loads(asianFile.read().decode('UTF-8', errors = 'replace'))

	NowarApplyPaltMultiplied(asianFont, 0.4)
	TransfontLoclFeature(asianFont, baseFont)

	AdditionalCcmp(baseFont)
	RemoveFeature(asianFont['GSUB'], [ 'pwid', 'fwid', 'hwid', 'twid', 'qwid', 'vert', 'vrt2', 'aalt' ])
	RemoveFeature(asianFont['GPOS'], [ 'palt', 'halt', 'vert', 'vpal', 'vhal', 'vkrn' ])
	Gc(asianFont)
	MergeBelow(baseFont, asianFont)

	outStr = json.dumps(baseFont, ensure_ascii=False)
	with codecs.open("build/unhinted/{}.otd".format(configure.GenerateFilename(param)), 'w', 'UTF-8') as outFile:
		outFile.write(outStr)
