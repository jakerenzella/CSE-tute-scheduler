"""Converts a timetable CSV to a .lp format for use with the solver
"""

import csv
import pathlib

WORKING_DIR = pathlib.Path(__file__).parent.absolute().parent.absolute()
DATA_DIR = WORKING_DIR / 'sample_data'
OUTPUT_DIR = WORKING_DIR / 'data'


def load_timetable():
    results = []
    with open(pathlib.Path(DATA_DIR / 'timetable.csv'), encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)

        for row in reader:
            results.append(dict(row))  # pull in each row as a key-value pair
    return results


def timetable_entry_to_lp(timetable_entry):
    keys_to_extract = ['Class Desc', 'In Person',
                       'Room', 'Day', 'Time', 'Code']

    return f"class({', '.join((timetable_entry[key].lower()) for key in keys_to_extract)})."


def timetable_dict_to_lp(timetable_dict):
    return [timetable_entry_to_lp(x) for x in timetable_dict]


def timetable_lp_to_file():
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(pathlib.Path(OUTPUT_DIR / 'timetable.lp'), 'w', encoding='utf-8') as lpfile:
        lpfile.write('\n'.join(timetable_dict_to_lp(load_timetable())))


timetable_lp_to_file()
