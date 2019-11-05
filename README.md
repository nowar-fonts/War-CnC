# War C² (Nowar Sans for Web)

## Features

### Hinted OpenType/TT

* Be clear and crisp on Windows.
* Be smooth on macOS and mobile OSes.
* Adapt to user preference on Linux.

### Distributed in WOFF and WOFF2 Format

* All modern browsers (and Internet Explorer 11) support WOFF.
* Recent releases of modern browsers support WOFF2. (~30% smaller!)

### Character Set

* Adobe Latin 3
* Adobe Cyrillic 1
* Adobe Greek 1
* GBK
* Big-5
* Adobe-Japan1-1
* 通用规范汉字表
* Unicode block: CJK Unified Ideographs
* Unicode script: Hangul

### Localized Forms: Miltiple Languages in One Font

NOTE: Safari (and thus ALL browsers on iOS) DOES NOT support OpenType `locl` feature, as of 2019.

![Sample from CJK Type Blog](https://blogsimages.adobe.com/CCJKType/files/2018/11/shsans-66-compare.gif)
(from [CJK Type Blog](https://blogs.adobe.com/CCJKType/2018/11/shsans-v2-technical-tidbits.html))

## Use War C² on Web Pages

Use CSS `@font-face` to introduce War C²:

```html
<style>
    @font-face {
        font-family: "Nowar Sans";
        font-weight: 400;
        src: url("/font/WarCnC-Regular.woff2") format("woff2"),
             url("/font/WarCnC-Regular.woff") format("woff");
    }
    element {
        font-family: "Nowar Sans", sans-serif;
    }
</style>
```

Then add proper language tag to the element:

```html
<p lang="en">“Hello——Is it not delightful to have friends coming from distant quarters?”</p>
<p lang="zh-CN">“Hello——有朋自遠方來，不亦樂乎”</p>
<p lang="zh-TW">「Hello——有朋自遠方來，不亦樂乎」</p>
<p lang="zh-HK">「Hello——有朋自遠方來，不亦樂乎」</p>
<p lang="ja">「ハロー——有朋自遠方來，不亦楽乎」</p>
```

### Recommendations

* Explicitly enable at least one OpenType layout feature.
  - For Internet Explorer 11. 
  - Whichever feature is explicitly enabled does not matter. `ccmp` is generally okay.

```html
<style>
    body {
        font-feature-settings: "ccmp";
    }
</style>
```

## How to Build

### Dependencies

* Basic Unix utils;
* [Python 3](https://www.python.org/),
  + run `git submodule update --init --recursive` to fetch additional modules;;
* [otfcc](https://github.com/caryll/otfcc);
* [ttfautohint](https://www.freetype.org/ttfautohint/);
* [Node.js](https://nodejs.org/), 
  + run `npm install` to fetch additional modules.

To build, run

```
python configure.py
make -j<threads>
```

## Credit

Latin, Greek and Cyrillic characters are from [Noto Sans](https://github.com/googlei18n/noto-fonts) by Google.

CJK Ideographs, Kana and Hangul are from [Source Han Sans](https://github.com/adobe-fonts/source-han-sans) by Adobe.

Ideograph is autohinted with [Chlorophytum](https://github.com/chlorophytum/Chlorophytum).
