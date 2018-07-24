# DBS to Toshl

Parser for DBS account statements in PDF format. Converts the statements to .csv file edible by Toshl.

Uses xpdfreader for pdf-2-text conversion. Put the 'pdftotext' executable in the same folder.

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

## Links
1. http://www.xpdfreader.com/download.html