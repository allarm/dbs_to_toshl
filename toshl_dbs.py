#!/usr/bin/env python3

import re
from pprint import pprint
import yaml

input_file = '/Users/achertolyas/git/toshl_dbs/May-June credit.txt'
categories_file = '/Users/achertolyas/git/toshl_dbs/categories.yaml'

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

with open(categories_file, 'r') as f:
    categories = yaml.load(f)

with open(input_file, 'r') as f:
    for x in f:
        x = x.strip()
        if len(x) > 1:
            parsed = p.match(x)
            if parsed:
                for y in categories['regexps']:
                    pc = re.compile(y['regexp'])
                    if pc.match(parsed.groupdict()['description']):
                        print("Matched: {}, category: {}, tags: {}".format(y['regexp'], y['category'], y['tags']))
                        pprint(parsed.groupdict())
                    else:
                        print("No match")
                    # pprint(parsed.groupdict())
