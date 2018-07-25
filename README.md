# DBS to Toshl

Parser for DBS account statements in PDF format. Converts the statements to .csv file edible by Toshl.

Uses `pdftotext` binary from `xpdf-tools` packet for pdf-2-text conversion. Put the `pdftotext` executable in the same folder with the script. The download link is in the `Links` section.

## Categories dictionary

Used for assigning account/categories/tags/description parameters to the output csv file.

Pretty self-descriptive:

```yaml
  - regexp: '^GO.SKYPE.COM'
    account: 'main'
    category: 'subscriptions'
    description: 'Skype subscription'
    tags:
      - 'skype'
      - 'subscription'
  - regexp: '^GRAB'
    account: 'main'
    category: 'transport'
    description: 'GRAB taxi payment'
    tags:
      - 'taxi'
      - 'grab'
      - 'transport'
```

## ToDo

1. Remove `account` from the categories dictionary (or better make it optional) and take it from the command line arguments.
1. Add command line arguments for default `category` value

## Links
1. http://www.xpdfreader.com/download.html
