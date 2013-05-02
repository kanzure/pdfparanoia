`comparediffs` provides a tools for downloading a PDF from two different sources, running pdfparanoia on the files, comparing the outputs byte-for-byte,
and reporting the results.

Typical usage is to first establish two `ssh` tunnels to hosts with access to the literature, e.g. via
`ssh -D 1080 host1` and `ssh -D 1081 host2`. You can then invoke `comparediffs` via

    ./comparediffs localhost:1080 localhost:1081 < urls

where urls is a file containing one URL per line (e.g. the example file in this directory).

`comparediffs` creates a subdirectory `pdf/`, in which is stores PDFs. It won't try to download the same PDF twice, so if you fix pdfparanoia you'll
need to clean out some or all of this subdirectory.

It's easy to see which PDFs pdfparanoia failed on, as it leaves copies of the scrubbed files with suffixes `.1.cleaned.pdf` and `.2.cleaned.pdf`.
When pdfparanoia succeeds (or isn't even needed, because the downloaded files were identical), the scrubbed files are removed.
