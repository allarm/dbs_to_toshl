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
    # return
    if os.path.isfile(file): os.remove(file)


def return_input_file_type(input_file):
    """
    Simple file format check
    Transaction history document contains: "View Transaction History"
    Consolidated statement contains: "CONSOLIDATED STATEMENT"
    :return:
    """

    formats = {'View Transaction History': 'transaction_history', 'CONSOLIDATED STATEMENT': 'consolidated_statement'}

    with open(input_file, 'r', encoding='latin-1') as f:
        for line in f:
            for y in formats.keys():
                if y in line:
                    return formats[y]
    return 'unknown'


def run_pdftotext(pdf_filename, output_txt_filename):
    """
    Trying to run the pdftotext utility and pass there some parameters. It should generate the output_txt_filename file
    with the text layer of the pdf_filename file
    :param pdf_filename:
    :param output_txt_filename:
    :return: output_txt_filename file (not a return value)
    """
    run_list = ['./pdftotext', '-simple', '-lineprinter', '-nopgbrk', '-q', '-eol', 'unix', pdf_filename,
                output_txt_filename]
    session = subprocess.call(run_list)
    if session:
        print('Something is wrong with pdftotext, is it even here?')
        exit(1)

    return 0  # assuming that everything went well and the output file has been created


def main():
    categories_file = 'categories.yaml'
    txt_file = 'pdftotext.tmp'
    flush_tmp(txt_file)
    csv_file = 'output.csv'
    default_category = 'default'
    default_account = 'default'

    fieldnames = '"Date","Account","Category","Tags","Expense amount","Income amount","Currency",' \
                 '"In main currency","Main currency","Description"'.split(',')
    fieldnames_dict = 'date,account,category,tags,expense_amount,income_amount,currency,' \
                      'in_main_currency,main_currency,description'.split(',')

    csv_list = []
    tmp_dict = {}

    month_convert = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06', 'jul': '07',
        'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
    currency_convert = {'S$': 'SGD', '$': 'USD'}

    parser = argparse.ArgumentParser(description='Generate csv file for toshl from DBS pdf account details',
                                     epilog='')

    parser.add_argument('-i', '--input', type=str, help='Input pdf file')
    parser.add_argument('-o', '--output', type=str, help='Output csv file (default is {})'.format(csv_file))
    parser.add_argument('-d', '--dictionary', type=str,
                        help='YAML categories dictionary file (default is {})'.format(categories_file))
    parser.add_argument('-c', '--category', type=str, help='Default Toshl category name')
    parser.add_argument('-a', '--account', type=str, help='Default Toshl account name')
    parser.add_argument('--debug', action='store_true', help='Turn debug on')

    args = parser.parse_args()

    if args.debug:
        print(args)

    if args.category:
        default_category = args.category

    if args.account:
        default_account = args.account

    if args.input:
        input_pdf_file = args.input
        # check if file exists
        if not os.path.isfile(input_pdf_file):
            print("{} does not exist, exiting".format(input_pdf_file))
            exit(1)
    else:
        print("Give me the input pdf file. For help use {} --help".format(sys.argv[0]))
        exit(1)

    if args.output: csv_file = args.output

    if os.path.isfile(csv_file):
        print("File {} exists, better not change it, exiting".format(csv_file))
        exit(1)

    if args.dictionary: categories_file = args.dictionary

    run_pdftotext(input_pdf_file, txt_file)

    input_file_format = return_input_file_type(txt_file)

    if input_file_format == 'consolidated_statement':
        print("Can't parse consolidated statement yet, use transaction history instead.")
        flush_tmp(txt_file)
        exit(1)
    if input_file_format == 'unknown':
        print("Unknown file format")
        flush_tmp(txt_file)
        exit(1)

    # @formatter:off
    # p = re.compile('^(?P<date_str>'
    #                '(?P<day>\d\d)\s'
    #                '(?P<month>\D{3})\s'
    #                '(?P<year>\d{4})'
    #                ')\s+'
    #                '(?P<description>.+?(?=\s\s))\s+'
    #                '(?P<amount_str>'
    #                '(?P<currency>.+?)'
    #                '(?P<amount>\d+[.,]\d+)'
    #                '(?P<flag>.*)'
    #                ')'
    #                )
    p = re.compile('^(?P<date_str>(?P<day>\d\d)\s(?P<month>\D{3})\s(?P<year>\d{4}))\s+(?P<description>.+?(?=\s\s))\s+'
                   '(?P<amount_str>(?P<currency>.+?)(?P<amount>\d+[.,]\d+([.]\d+)?)(?P<flag>.*))')
    # @formatter:on

    with open(categories_file, 'r') as f:
        categories = yaml.load(f)

    with open(txt_file, 'r', encoding='latin-1') as f:
        for x in f:  # for line in txt file
            x = x.strip()
            if args.debug: print(x)
            if len(x) > 1:
                parsed = p.match(x)
                found = False
                if parsed:
                    parsed_dict = parsed.groupdict()
                    for y in categories['regexps']:  # matching the yaml regexp dictionary to an expense
                        pc = re.compile(y['regexp'])
                        if pc.match(parsed_dict['description']):  # matched a category
                            tmp_dict['category'] = y['category']
                            tmp_dict['account'] = y['account']
                            if 'description' in y:
                                tmp_dict['description'] = y['description']
                            else:
                                tmp_dict['description'] = parsed_dict['description']
                            tmp_dict['tags'] = ' '.join(y['tags'])
                            found = True
                            break

                    if not found:
                        tmp_dict['category'] = default_category
                        tmp_dict['account'] = default_account
                        tmp_dict['description'] = parsed_dict['description']
                        tmp_dict['tags'] = ''

                    if args.debug: print(parsed_dict)

                    tmp_dict['date'] = '{}/{}/{}'.format(parsed_dict['day'],
                                                         month_convert[parsed_dict['month'].lower()],
                                                         parsed_dict['year'])
                    if parsed_dict['flag'].strip() == 'cr':
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

                    tmp_dict['main_cur'] = currency_convert[parsed_dict['currency']]

                    csv_list.append(dict(tmp_dict))

    with open(csv_file, 'a') as result_file:
        print(fieldnames)
        writer = csv.writer(result_file, dialect='excel')
        writer.writerow(fieldnames)
        for x in csv_list:
            tmp_lst = []
            for y in fieldnames_dict:
                tmp_lst.append(x[y])
            writer.writerow(tmp_lst)

    flush_tmp(txt_file)
    exit(0)


if __name__ == '__main__':
    main()
