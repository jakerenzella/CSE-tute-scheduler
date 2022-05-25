"""Converts a timetable CSV to a .lp format for use with the solver
"""

import csv
import pathlib

WORKING_DIR = pathlib.Path(__file__).parent.parent.absolute()
DATA_DIR = WORKING_DIR / 'sample_data'
OUTPUT_DIR = WORKING_DIR / 'data'


def load_timetable() -> list:
    """Loads the timetable CSV into a dictionary

    Returns:
        List: A dictionary containing the CSV data
    """
    results = []
    with open(pathlib.Path(DATA_DIR / 'timetable.csv'), encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)

        for row in reader:
            results.append(dict(row))  # pull in each row as a key-value pair
    return results


def save_lp(lp_list: list):
    """Generates the .lp file from the timetable CSV, and saves it to a file
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(pathlib.Path(OUTPUT_DIR / 'timetable.lp'), 'w', encoding='utf-8') as lpfile:
        lpfile.write('\n'.join(lp_list))


def timetable_entry_to_lp(timetable_entry: dict) -> str:
    """Converts a single timetable entry to a .lp format

    Args:
        timetable_entry (dict): The timetable entry to convert

    Returns:
        str: the lp format of the timetable entry
    """
    keys_to_extract = ['Class Desc', 'In Person',
                       'Room', 'Day', 'Time', 'Code']

    return f"class({', '.join((timetable_entry[key].lower()) for key in keys_to_extract)})."


def timetable_dict_to_lp(timetable: list) -> list:
    """Iterates through the list of timetable entries and converts them to .lp format

    Args:
        timetable (list): the list of timetable entries

    Returns:
        list: the list of .lp formatted timetable entries
    """
    return [timetable_entry_to_lp(x) for x in timetable]


if __name__ == '__main__':
    lp_data = timetable_dict_to_lp(load_timetable())
    save_lp(lp_data)
