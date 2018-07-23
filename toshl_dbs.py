#!/usr/bin/env python3

import re
from pprint import pprint
import yaml
import csv
import argparse
import subprocess
import sys
import os.path

def flush_tmp(file):
    """
    Remove file if exists
    :param file:
    :return:
    """
    if os.path.isfile(file): os.remove(file)

def run_pdftotext(pdf_filename, output_txt_filename):
    """
    Trying to run the pdftotext utility and pass there some parameters. It should generate the output_txt_filename file
    with the text layer of the pdf_filename file
    :param pdf_filename:
    :param output_txt_filename:
    :return: output_txt_filename file (not a return value)
    """
    # run_str = './pdftotext -simple -lineprinter -nopgbrk -eol unix {}'.format(filename.split().replace(' ', '\\ '))
    run_list = ['./pdftotext', '-simple', '-lineprinter', '-nopgbrk', '-q', '-eol', 'unix', pdf_filename, output_txt_filename]
                # '-eol', 'unix', pdf_filename.strip().replace(' ', '\\ '), output_txt_filename]
    session = subprocess.call(run_list)
    if session:
        print('Something is wrong with pdftotext, is it even here?')
        exit(1)

    return (0)  # assuming that everything went well and the output file has been created


def main():
    categories_file = 'categories.yaml'
    txt_file = 'pdftotext.tmp'
    flush_tmp(txt_file)
    csv_file = 'output.csv'

    fieldnames = '"Date","Account","Category","Tags","Expense amount","Income amount","Currency",' \
                 '"In main currency","Main currency","Description"'.split(',')
    fieldnames_dict = 'date,account,category,tags,expense_amount,income_amount,currency,' \
                      'in_main_currency,main_currency,description'.split(',')

    csv_list = []
    tmp_dict = {}

    month_convert = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06', 'jul': '07',
                     'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
    currency_convert = {'S$': 'SGD', '$': 'USD'}

    parser = argparse.ArgumentParser(description='Generate csv file for toshl from DBS pdf account details',
                                     epilog='')

    parser.add_argument('-i', '--input', type=str, help='Input pdf file')
    parser.add_argument('-o', '--output', type=str, help='Output csv file (default is {})'.format(csv_file))
    parser.add_argument('-c', '--categories', type=str, help='YAML categories dictionary file (default is {})'.format(categories_file))
    parser.add_argument('--debug', action='store_true', help='Turn debug on')

    args = parser.parse_args()

    if args.debug:
        print(args)

    if args.input:
        input_pdf_file = args.input
        # check if file exists
        pass
    else:
        print("Give me the input pdf file. For help use {} --help".format(sys.argv[0]))
        exit(1)

    if args.output: csv_file = args.output

    if os.path.isfile(csv_file):
        print("File {} exists, better not change it, exiting".format(csv_file))
        exit(1)

    if args.categories: categories_file = args.categories

    # txt_file = '/Users/achertolyas/git/toshl_dbs/May-June credit.txt'
    # categories_file = '/Users/achertolyas/git/toshl_dbs/categories.yaml'
    # csv_file = '/Users/achertolyas/git/toshl_dbs/output.csv'

    run_pdftotext(input_pdf_file, txt_file)

    p = re.compile('^(?P<date_str>'
                   '(?P<day>\d\d)\s'
                   '(?P<month>\D{3})\s'
                   '(?P<year>\d{4})'
                   ')\s+'
                   '(?P<description>.+?(?=\s\s))\s+'
                   '(?P<amount_str>'
                   '(?P<currency>.+?)'
                   '(?P<amount>\d+[.,]\d+)'
                   '(?P<flag>.*)'
                   ')'
                   )

    with open(categories_file, 'r') as f:
        categories = yaml.load(f)

    # print(categories)

    with open(txt_file, 'r', encoding='latin-1') as f:
        for x in f:  # for line in txt file
            x = x.strip()
            if args.debug: print(x)
            if len(x) > 1:
                parsed = p.match(x)
                found = False
                if parsed:
                    parsed_dict = parsed.groupdict()
                    # print(parsed_dict)
                    for y in categories['regexps']:  # matching the yaml regexp dictionary to an expense
                        pc = re.compile(y['regexp'])
                        if pc.match(parsed_dict['description']):  # matched a category
                            # print("Matched: {}, category: {}, tags: {}, account: {}".format(y['regexp'], y['category'],
                            #                                                                 y['tags'], y['account']))
                            # pprint(parsed_dict)
                            tmp_dict['category'] = y['category']
                            tmp_dict['account'] = y['account']
                            if 'description' in y:
                                tmp_dict['description'] = y['description']
                            else:
                                tmp_dict['description'] = parsed_dict['description']
                            tmp_dict['tags'] = ' '.join(y['tags'])
                            found = True
                            break

                        # else:  # no category matched
                    if not found:
                        # print("No match")
                        tmp_dict['category'] = 'default'
                        tmp_dict['account'] = 'default'
                        tmp_dict['description'] = parsed_dict['description']
                        tmp_dict['tags'] = ''

                    tmp_dict['date'] = '{}/{}/{}'.format(parsed_dict['day'],
                                                         month_convert[parsed_dict['month'].lower()],
                                                         parsed_dict['year'])
                    if parsed_dict['flag'].split() == 'cr':
                        """
                        cr means credit, if set then populating the income field
                        otherwise populating the expenses field
                        amount can be in 1,123 format, removing the comma 
                        """
                        tmp_dict['income_amount'] = tmp_dict['in_main_currency'] = \
                            parsed_dict['amount'].replace(',', '')
                        tmp_dict['expense_amount'] = '0'
                    else:
                        tmp_dict['expense_amount'] = tmp_dict['in_main_currency'] = \
                            parsed_dict['amount'].replace(',', '')
                        tmp_dict['income_amount'] = '0'

                    tmp_dict['currency'] = tmp_dict['main_currency'] = currency_convert[parsed_dict['currency']]

                    # tmp_dict['in_main_curency'] = parsed_dict['amount'].replace(',', '')
                    tmp_dict['main_cur'] = currency_convert[parsed_dict['currency']]

                    # print(tmp_dict)
                    csv_list.append(dict(tmp_dict))

    # pprint(csv_list)
    # tmp_lst = []
    with open(csv_file, 'a') as result_file:
        print(fieldnames)
        writer = csv.writer(result_file, dialect='excel')
        writer.writerow(fieldnames)
        for x in csv_list:
            tmp_lst = []
            for y in fieldnames_dict:
                # print(x[y])
                tmp_lst.append(x[y])
            # print(tmp_lst)
            # exit(0)
            writer.writerow(tmp_lst)

    flush_tmp(txt_file)
    exit(0)


if __name__ == '__main__':
    main()
    # run_pdftotext('estatement_example.pdf', 'output.txt')
