import json
import codecs
import base64
import itertools
from types import SimpleNamespace as Namespace

from pprint import pprint

class Config:
	version = "0.1.0"
	fontRevision = 0.0100
	vendor = "Nowar Typeface"
	vendorId = "NOWR"
	vendorUrl = "https://github.com/nowar-fonts"
	copyright = "Copyright © 2019—2020 Cyano Hao and Nowar Typeface. Portions Copyright 2015 Google Inc. Portions © 2014-2019 Adobe (http://www.adobe.com/)."
	designer = "Cyano Hao (character set definition, autohinting & modification for web font); Monotype Design Team (Latin, Greek & Cyrillic); Ryoko NISHIZUKA 西塚涼子 (kana, bopomofo & ideographs); Sandoll Communications 산돌커뮤니케이션, Soo-young JANG 장수영 & Joo-yeon KANG 강주연 (hangul elements, letters & syllables); Dr. Ken Lunde (project architect, glyph set definition & overall production); Masataka HATTORI 服部正貴 (production & ideograph elements)"
	designerUrl = "https://github.com/CyanoHao"
	license = "This Font Software is licensed under the SIL Open Font License, Version 1.1. This Font Software is distributed on an \"AS IS\" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the SIL Open Font License for the specific language, permissions and limitations governing your use of this Font Software."
	licenseUrl = "https://scripts.sil.org/OFL"

	fontInstanceWeight = [ 400 ]
	fontInstanceWidth = [ 5 ]

config = Config()

weightMap = {
	100: "Thin",
	200: "ExtraLight",
	300: "Light",
	400: "Regular",
	500: "Medium",
	600: "SemiBold",
	700: "Bold",
	800: "ExtraBold",
	900: "Black",
}

widthMap = {
	3: "Condensed",
	4: "SemiCondensed",
	5: None,
	7: "Extended",
}

notoWidthMap = {
	3: 3,
	5: 4,
	7: 5,
}

def GenerateFamily(p):
	return {
		0x0409: "War C²",
		0x0804: "战·锐方",
		0x0404: "戰·銳方",
		0x0C04: "戰·鋭方",
		0x0411: "戦・鋭方",
		0x0412: "전 예방",
	}


def GenerateSubfamily(p):
	width = widthMap[p.width]
	weight = weightMap[p.weight]
	if hasattr(p, "italic") and p.italic:
		if p.weight == 400:
			return width + " Italic" if width else "Italic"
		else:
			return ("{} {}".format(width, weight) if width else weight) + " Italic"
	else:
		if p.weight == 400:
			return width if width else "Regular"
		else:
			return "{} {}".format(width, weight) if width else weight

def GenerateFriendlyFamily(p):
	return { k: "{} {}".format(v, GenerateSubfamily(p)) for k, v in GenerateFamily(p).items() }

def GenerateLegacySubfamily(p):
	width = widthMap[p.width]
	weight = weightMap[p.weight]
	if hasattr(p, "italic") and p.italic:
		if p.weight == 400:
			return width or "", "Italic"
		elif p.weight == 700:
			return width or "", "Bold Italic"
		else:
			return "{} {}".format(width, weight) if width else weight, "Italic"
	else:
		if p.weight == 400 or p.weight == 700:
			return width or "", weight
		else:
			return "{} {}".format(width, weight) if width else weight, "Regular"

def GenerateFilename(p):
	familyName = {
		"Sans": "WarCnC",
		"Noto": "NotoSans",
		"Source": "SourceHanSansSC",
	}
	return familyName[p.family] + "-" + GenerateSubfamily(p).replace(" ", "")

def ResolveDependency(p):
	return {
		"Latin": Namespace(
			family = "Noto",
			width = notoWidthMap[p.width],
			weight = p.weight
		),
		"CJK": Namespace(
			family = "Source",
			weight = p.weight,
			width = 5,
		),
	}

def ParamToArgument(param):
	js = json.dumps(param.__dict__, separators=(',',':'))
	b64 = base64.b64encode(js.encode())
	return b64.decode()

def ParamFromArgument(arg):
	js = base64.b64decode(arg).decode()
	return Namespace(**json.loads(js))

if __name__ == "__main__":

	fontInstance = [ Namespace(family = "Sans", weight = w, width = wd) for w in config.fontInstanceWeight for wd in config.fontInstanceWidth ]
	fontFilename = [ GenerateFilename(i) for i in fontInstance ]
	hintGroup = { k: list(w) for k, w in itertools.groupby(fontInstance, lambda p: p.weight) }

	makefile = {
		"variable": {
			"VERSION": config.version,
			"IDH_JOBS?": 1,
		},
		"rule": {
			".PHONY": {
				"depend": [ "all", "hint2" ] + [ "hint2-{}".format(w) for w in hintGroup ],
			},
			"all": {
				"depend": [ "woff", "woff2" ],
			},
			"woff": {
				"depend": [ "out/woff/{}.woff".format(f) for f in fontFilename ],
			},
			"woff2": {
				"depend": [ "out/woff2/{}.woff2".format(f) for f in fontFilename ],
			},
			"hint2": {
				"depend": [ "hint2-{}".format(w) for w in hintGroup ],
			},
			"clean": {
				"command": [
					"-rm -rf build/",
				],
			},
		},
	}

	makefile["rule"].update({
		"out/{0}/{1}.{0}".format(fl, f): {
			"depend": [ "build/nowar/{}.ttx".format(f) ],
			"command": [
				"mkdir -p out/{}/".format(fl),
				"ttx --flavor {} -o $@ $<".format(fl),
			],
		} for f in fontFilename for fl in [ "woff", "woff2" ]
	})

	makefile["rule"].update({
		"build/nowar/{}.ttx".format(f): {
			"depend": [ "build/nowar/{}.ttf".format(f) ],
			"command": [ "ttx -o $@ $<" ],
		} for f in fontFilename
	})

	makefile["rule"].update({
		"build/nowar/{}.ttf".format(f): {
			"depend": [ "build/nowar/{}.otd".format(f) ],
			"command": [ "otfccbuild --quiet -O3 -o $@ $<" ],
		} for f in fontFilename
	})

	makefile["rule"].update({
		"build/nowar/{}.otd".format(GenerateFilename(p)): {
			"depend": [ "build/hint2/{}.instr.gz".format(GenerateFilename(p)) ],
			"command": [
				"mkdir -p build/nowar/",
				"node node_modules/@chlorophytum/cli/bin/_startup integrate -c source/idh/{0}.json build/hint2/{1}.instr.gz build/hint2/{1}.otd build/nowar/{1}.otd".format(w, GenerateFilename(p)),
			],
		} for w in hintGroup for p in hintGroup[w]
	})

	makefile["rule"].update({
		"build/hint2/{}.instr.gz".format(GenerateFilename(p)): {
			"depend": [ "build/hint2/{}.hint.gz".format(GenerateFilename(p)) ],
			"command": [ "node node_modules/@chlorophytum/cli/bin/_startup instruct -c source/idh/{0}.json build/hint2/{1}.otd build/hint2/{1}.hint.gz build/hint2/{1}.instr.gz".format(w, GenerateFilename(p)) ],
		} for w in hintGroup for p in hintGroup[w]
	})

	makefile["rule"].update({
		"build/hint2/{}.hint.gz".format(f): {
			"depend": [ "hint2" ],
		} for f in fontFilename
	})

	makefile["rule"].update({
		"hint2-{}".format(w): {
			"depend": [ "build/hint2/{}.otd".format(GenerateFilename(p)) for p in hintGroup[w] ],
			"command": [
				"mkdir -p cache/",
				"node node_modules/@chlorophytum/cli/bin/_startup hint -c source/idh/{0}.json -h cache/idh-{0}.gz -j ${{IDH_JOBS}} ".format(w) +
				" ".join([ "build/hint2/{0}.otd build/hint2/{0}.hint.gz".format(GenerateFilename(p)) for p in hintGroup[w] ]),
			],
		} for w in hintGroup
	})

	makefile["rule"].update({
		"build/hint2/{}.otd".format(f): {
			"depend": [ "build/hint1/{}.ttf".format(f) ],
			"command": [
				"mkdir -p build/hint2/",
				"otfccdump $< -o $@",
			],
		} for f in fontFilename
	})

	makefile["rule"].update({
		"build/hint1/{}.ttf".format(f): {
			"depend": [ "build/unhinted/{}.ttf".format(f) ],
			"command": [
				"mkdir -p build/hint1/",
				"ttfautohint -a qqq -c -D latn -f latn -G 0 -l 7 -r 48 -n -x 0 -v $< $@",
			],
		} for f in fontFilename
	})

	for p in fontInstance:
		makefile["rule"]["build/unhinted/{}.ttf".format(GenerateFilename(p))] = {
			"depend": ["build/unhinted/{}.otd".format(GenerateFilename(p))],
			"command": [ "otfccbuild --quiet -O3 $< -o $@" ]
		}
		dep = ResolveDependency(p)
		makefile["rule"]["build/unhinted/{}.otd".format(GenerateFilename(p))] = {
			"depend": [
				"build/noto/{}.otd".format(GenerateFilename(dep["Latin"])),
				"build/shs/{}.otd".format(GenerateFilename(dep["CJK"])),
			],
			"command": [ 
				"mkdir -p build/unhinted/",
				"python merge.py {}".format(ParamToArgument(p)),
			]
		}
		makefile["rule"]["build/noto/{}.otd".format(GenerateFilename(dep["Latin"]))] = {
			"depend": [ "source/noto/{}.ttf".format(GenerateFilename(dep["Latin"])) ],
			"command": [
				"mkdir -p build/noto/",
				"otfccdump --ignore-hints --glyph-name-prefix latn $< -o $@",
			]
		}
		makefile["rule"]["build/shs/{}.otd".format(GenerateFilename(dep["CJK"]))] = {
			"depend": [ "source/shs/{}.ttf".format(GenerateFilename(dep["CJK"])) ],
			"command": [
				"mkdir -p build/shs/",
				"otfccdump --ignore-hints --glyph-name-prefix hani $< -o $@",
			],
		}

	# dump `makefile` dict to actual “GNU Makefile”
	makedump = ""

	for var, val in makefile["variable"].items():
		makedump += "{}={}\n".format(var, val)

	for tar, recipe in makefile["rule"].items():
		dep = recipe["depend"] if "depend" in recipe else []
		makedump += "{}: {}\n".format(tar, " ".join(dep))
		com = recipe["command"] if "command" in recipe else []
		for c in com:
			makedump += "\t{}\n".format(c)

	with codecs.open("Makefile", 'w', 'UTF-8') as mf:
		mf.write(makedump)
