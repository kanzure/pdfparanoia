# pdfparanoia

pdfparanoia is a PDF watermark remover library for academic papers.

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

## Changelog

* 0.0.1 - initial commit

## License

BSD.
