# pdfparanoia

pdfparanoia is a PDF watermark removal library for academic papers.

## Installing

Simple.

``` bash
sudo pip install pdfparanoia
```

or,

``` bash
sudo python setup.py install
```

## Usage

``` python
import pdfparanoia

pdf = pdfparanoia.scrub(open("nmat91417.pdf", "rb"))

file_handler = open("output.pdf", "wb")
file_handler.write(pdf)
file_handler.close()
```

or from the shell,

``` bash
pdfparanoia input.pdf > output.pdf
```

and,

``` bash
cat input.pdf | pdfparanoia > output.pdf
```

## Supported

* AIP
* IEEE
* JSTOR
* SPIE (sort of)

## Changelog

* 0.0.12 - SPIE
* 0.0.11 - pdfparanoia command-line interface. Use it by either piping in pdf data, or specifying a path to a pdf in the first argv slot.
* 0.0.10 - JSTOR
* 0.0.9 - AIP: better checks for false-positives; IEEE: remove stdout garbage.
* 0.0.8 - IEEE

## License

BSD.
