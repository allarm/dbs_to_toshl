# DBS to Toshl

Parser for DBS account statements in PDF format. Converts the statements to .csv file edible by Toshl.

Uses `pdftotext` binary from `xpdf-tools` packet for pdf-2-text conversion. Put the `pdftotext` executable in the same folder with the script. The download link is in the `Links` section.

## Changelog

- Changed the `yaml` dictionary structure.

## Categories dictionary

Used for assigning account/categories/tags/description parameters to the output csv file.

Pretty self-descriptive:

```yaml
categories:
  -
    r:
     - '^PAYMENT - DBS INTERNET/WIRELESS'
    exclude: True
  -
    category: 'transport'
    r:
      - '^CALTRAIN'
      - '^UBER TRIP.*'
      - '^GRAB'
    account: 'main'
    tags:
      - 'transport'
  -
    category: 'eatery'
    r:
      - '^GUARDIAN'
      - '^WATSON'
      - '^LITTLE FARMS'
      - '^COLD STORAGE'
    account: 'main'
    tags:
      - 'food'
  -
    category: 'medical'
    r:
      - '^GENTLE DENTAL'
    account: 'main'
    tags:
      - 'dental'
```


## Links
1. http://www.xpdfreader.com/download.html
