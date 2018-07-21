#!/usr/bin/env python3

import re
from pprint import pprint

input_file = '/Users/achertolyas/git/toshl_dbs/May-June credit.txt'

# p = re.compile('^\d\d\s\D{3}\s\d{4}')
p = re.compile('^(?P<date_str>'
                    '(?P<day>\d\d)\s'
                    '(?P<month>\D{3})\s'
                    '(?P<year>\d{4})'
                ')\s+'
                '(?P<description>.+?(?=\s\s))\s+'
                '(?P<amount_str>'
                    '(?P<currency>.+?)'
                    '(?P<amount>\d+\.\d+)'
                    '(?P<flag>.*)'
                ')'
)

with open(input_file, 'r') as f:
    for x in f:
        if len(x.strip()) > 1:
            parsed=p.match(x.strip())
            if parsed:
                # print(x.strip())
                # print(len(x))
                pprint(parsed.groupdict())
