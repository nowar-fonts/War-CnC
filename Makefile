VERSION=0.1.0
IDH_JOBS?=1
.PHONY: all hint2 hint2-400
all: woff woff2
woff: out/woff/WarCnC-Regular.woff
woff2: out/woff2/WarCnC-Regular.woff2
hint2: hint2-400
clean: 
	-rm -rf build/
out/woff/WarCnC-Regular.woff: build/nowar/WarCnC-Regular.ttx
	mkdir -p out/woff/
	ttx --flavor woff -o $@ $<
out/woff2/WarCnC-Regular.woff2: build/nowar/WarCnC-Regular.ttx
	mkdir -p out/woff2/
	ttx --flavor woff2 -o $@ $<
build/nowar/WarCnC-Regular.ttx: build/nowar/WarCnC-Regular.ttf
	ttx -o $@ $<
build/nowar/WarCnC-Regular.ttf: build/nowar/WarCnC-Regular.otd
	otfccbuild --quiet -O3 -o $@ $<
build/nowar/WarCnC-Regular.otd: build/hint2/WarCnC-Regular.instr.gz
	mkdir -p build/nowar/
	node node_modules/@chlorophytum/cli/bin/_startup integrate -c source/idh/400.json build/hint2/WarCnC-Regular.instr.gz build/hint2/WarCnC-Regular.otd build/nowar/WarCnC-Regular.otd
build/hint2/WarCnC-Regular.instr.gz: build/hint2/WarCnC-Regular.hint.gz
	node node_modules/@chlorophytum/cli/bin/_startup instruct -c source/idh/400.json build/hint2/WarCnC-Regular.otd build/hint2/WarCnC-Regular.hint.gz build/hint2/WarCnC-Regular.instr.gz
build/hint2/WarCnC-Regular.hint.gz: hint2
hint2-400: build/hint2/WarCnC-Regular.otd
	mkdir -p cache/
	node node_modules/@chlorophytum/cli/bin/_startup hint -c source/idh/400.json -h cache/idh-400.gz -j ${IDH_JOBS} build/hint2/WarCnC-Regular.otd build/hint2/WarCnC-Regular.hint.gz
build/hint2/WarCnC-Regular.otd: build/hint1/WarCnC-Regular.ttf
	mkdir -p build/hint2/
	otfccdump $< -o $@
build/hint1/WarCnC-Regular.ttf: build/unhinted/WarCnC-Regular.ttf
	mkdir -p build/hint1/
	ttfautohint -a qqq -c -D latn -f latn -G 0 -l 7 -r 48 -n -x 0 -v $< $@
build/unhinted/WarCnC-Regular.ttf: build/unhinted/WarCnC-Regular.otd
	otfccbuild --quiet -O3 $< -o $@
build/unhinted/WarCnC-Regular.otd: build/noto/NotoSans-SemiCondensed.otd build/shs/SourceHanSansSC-Regular.otd
	mkdir -p build/unhinted/
	python merge.py eyJmYW1pbHkiOiJTYW5zIiwid2VpZ2h0Ijo0MDAsIndpZHRoIjo1fQ==
build/noto/NotoSans-SemiCondensed.otd: source/noto/NotoSans-SemiCondensed.ttf
	mkdir -p build/noto/
	otfccdump --ignore-hints --glyph-name-prefix latn $< -o $@
build/shs/SourceHanSansSC-Regular.otd: source/shs/SourceHanSansSC-Regular.ttf
	mkdir -p build/shs/
	otfccdump --ignore-hints --glyph-name-prefix hani $< -o $@
