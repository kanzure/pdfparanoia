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

pdfparanoia is written for python2.7+ or python 3.
You will also need to manually install "pdfminer" if you do not use pip to install pdfparanoia.
For python versions prior to Python 3, use "pdfminer" from the Python Package Index (http://pypi.python.org). For recent versions of Python, use pdfminer3k instead.

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

## Supported

* AIP
* IEEE
* JSTOR
* RSC
* SPIE (sort of)

## Changelog

* 0.0.13 - RSC
* 0.0.12 - SPIE
* 0.0.11 - pdfparanoia command-line interface. Use it by either piping in pdf data, or specifying a path to a pdf in the first argv slot.
* 0.0.10 - JSTOR
* 0.0.9 - AIP: better checks for false-positives; IEEE: remove stdout garbage.
* 0.0.8 - IEEE

## License

BSD.
