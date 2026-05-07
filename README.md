# pdfparanoia

pdfparanoia is a PDF watermark removal library for academic papers. Some
publishers include private information like institution names, personal names,
ip addresses, timestamps and other identifying information in watermarks on
each page.

pdfparanoia это библиотека для удаления водяных знаков из PDF файлов научных
статей. Некоторые издатели включают личную информацию, такую как названия
институтов, имена, IP-адреса, время и дату и другую информацию в водяные знаки
содержащиеся на каждой странице.

## Installing

Simple.

``` bash
sudo pip install pdfparanoia
```

or,

``` bash
sudo python setup.py install
```

pdfparanoia is written for Python 2.7+ or Python 3.
Dependencies are installed automatically by pip: **pdfminer.six** (publisher
watermark plugins) and **pikepdf** (custom string + metadata scrubbing).

## Usage

``` python
import pdfparanoia

pdf = pdfparanoia.scrub(open("nmat91417.pdf", "rb"))

with open("output.pdf", "wb") as file_handler:
    file_handler.write(pdf)
```

or from the shell,

``` bash
pdfparanoia --verbose input.pdf -o output.pdf
```

and,

``` bash
cat input.pdf | pdfparanoia > output.pdf
```

To remove a specific string from all page content streams *and* metadata:

``` bash
pdfparanoia input.pdf -s "Downloaded by user@example.com" -o output.pdf
```

To remove a string from metadata only (leaving page text untouched):

``` bash
pdfparanoia input.pdf -s "My Institution" --only-scrub-metadata -o output.pdf
```

Multiple `-s` flags can be combined, and matching is case-insensitive by default
(pass `--case-sensitive` to opt out).  The `-o` flag is safe to use with the
same path as the input file.

## Supported

* AIP
* IEEE
* JSTOR
* RSC
* SPIE (sort of)

## Changelog

* 0.0.18 - pikepdf-based CustomStrings plugin: TJ-kerning-aware content-stream scrubbing, XMP and DocInfo metadata scrubbing, `--scrub-strings` / `--only-scrub-metadata` CLI flags, safe in-place `-o` output.
* 0.0.13 - RSC
* 0.0.12 - SPIE
* 0.0.11 - pdfparanoia command-line interface. Use it by either piping in pdf data, or specifying a path to a pdf in the first argv slot.
* 0.0.10 - JSTOR
* 0.0.9 - AIP: better checks for false-positives; IEEE: remove stdout garbage.
* 0.0.8 - IEEE

## License

BSD.
