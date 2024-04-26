#! /usr/bin/env python3
"""Converts a timetable CSV to a .lp format for use with the solver
"""

from itertools import chain
import pathlib
import logging
import sys
import re
import time
from fact_builder import fact_builder, save_lp, csv_to_dict, clear_file
import clingo

WORKING_DIR = pathlib.Path(__file__).parent.parent.absolute()
DATA_DIR = WORKING_DIR / 'data'
FACTS_DIR = WORKING_DIR / 'facts'
OUTPUT_DIR = WORKING_DIR / 'output'
LATENCY = 1

DAYS = ["M", "T", "W", "H", "F"]
TIMES = ["08", "09", "10", "11", "12", "13",
         "14", "15", "16", "17", "18", "19", "20"]
DAY_TIMES = [(x, y) for x in DAYS for y in TIMES]

KEY_TO_PREF = {
    '0': ('impossible', 0, 'onlineOnly'),
    '0.1': ('impossible', 0, 'onlineOrPerson'),
    '1': ('dislike', 1, 'onlineOnly'),
    '1.1': ('dislike', 1, 'onlineOrPerson'),
    '2': ('possible', 2, 'onlineOnly'),
    '2.1': ('possible', 2, 'onlineOrPerson'),
    '3': ('preferred', 3, 'onlineOnly'),
    '3.1': ('preferred', 3, 'onlineOrPerson'),
    'impossible': ('impossible', 0, 'onlineOrPerson'),
    'impossible-online-only': ('impossible', 0, 'onlineOnly'),
    'dislike': ('dislike', 1, 'onlineOrPerson'),
    'dislike-online-only': ('dislike', 1, 'onlineOnly'),
    'possible': ('possible', 2, 'onlineOrPerson'),
    'possible-online-only': ('possible', 2, 'onlineOnly'),
    'preferred': ('preferred', 3, 'onlineOrPerson'),
    'preferred-online-only': ('preferred', 3, 'onlineOnly'),
}


def preference_entry_to_lps(preference_entry: dict) -> list[str]:
    """Converts a single preference entry to a .lp format

    Args:
        preference_entry (dict): The preference entry to convert

    Returns:
        str: the lp format of the preference entry
    """

    # validate the preference entry

    z_id = preference_entry['zid']
    tt_max = preference_entry['TT'] if 'TT' in preference_entry else 0
    at_max = preference_entry['AT'] if 'AT' in preference_entry else 0

    result = []
    result.append(fact_builder('teacher', preference_entry['zid']))
    # This is a bit of a hack. Need to do something better some day.
    previous_experiences = [course.strip().lower(
    ) for course in preference_entry['previous_experience'].split('|')]
    previous_experiences = [(course[0:8], 'admin' in course)
                            for course in previous_experiences]
    for (course, admin) in previous_experiences:
        result.append(fact_builder('experience', z_id, f'involved({course})'))
        if admin:
            result.append(fact_builder('experience', z_id, f'admin({course})'))
    # if "1511" in preference_entry['previous_experience']:
    #    result.append(fact_builder('experience', z_id, 'tute'))
    #    result.append(fact_builder('experience', z_id, 'asst'))

    # Go through each day and time
    # (M09) and then extract the preference
    for (day, daytime_time) in DAY_TIMES:
        # key = [day, daytime_time]
        # pref = preference_entry[key[0] + key[1]]
        try:
            # Turn the preference entry (1.1) into a tuple (dislike, True)
            pref = KEY_TO_PREF[preference_entry[day+daytime_time]]
        except KeyError:
            # Seems as though there are more times available in CASTLE than the tutors complete,
            # so some preferences are not available. In this case return impossible
            pref = ('impossible', 0, False)
        if pref[0] != 'impossible':
            if pref[2] == 'onlineOrPerson':
                result.append(fact_builder(
                    'available', z_id, 'online', day, int(daytime_time)))
                result.append(fact_builder('available', z_id,
                              'inPerson', day, int(daytime_time)))
            else:
                assert pref[2] == 'onlineOnly'
                result.append(fact_builder(
                    'available', z_id, 'online', day, int(daytime_time)))
        result.append(fact_builder('desire', z_id,
                      pref[1], day, int(daytime_time)))
        # result.append(fact_builder('preference', z_id, *key, *pref))

    result.append(fact_builder('capacity', z_id, 'tute', tt_max))
    result.append(fact_builder('capacity', z_id, 'asst', at_max))
    # These are just stubbed for now
    result.append(fact_builder('preferredRole', z_id, 'tute'))
    return result


def preferences_dict_to_lp(preferences: list) -> list:
    """Iterates through the list of preferences and converts them to .lp format

    Args:
        preferences (list): the list of preferences

    Returns:
        list: the list of .lp formatted preferences
    """
    # Unpacking the list of preferences per tutor as we go
    return list(chain.from_iterable([preference_entry_to_lps(x) for x in preferences]))


def timetable_entry_to_lps(timetable_entry: dict) -> list[str]:
    """Converts a single timetable entry to a .lp format

    Args:
        timetable_entry (dict): The timetable entry to convert

    Returns:
        str: the lp format of the timetable entry
    """
    slot = timetable_entry['Class Desc']
    mode = 'inPerson' if timetable_entry['In Person'] == 'TRUE' else 'online'
    day = timetable_entry['Day'].lower()
    time_entry = timetable_entry['Time']

    result = []
    result.append(fact_builder('class', slot))
    result.append(fact_builder('mode', slot, mode))
    result.append(fact_builder('day', slot, day))
    result.append(fact_builder('startTime', slot, int(time_entry)))
    return result
#    keys_to_extract = ['Class Desc', 'In Person',
#                       'Room', 'Day', 'Time']

#    fact_builder_args = [timetable_entry[x].lower() for x in keys_to_extract]
#    return fact_builder('class', *fact_builder_args)


def timetable_dict_to_lp(timetable: list) -> list:
    """Iterates through the list of timetable entries and converts them to .lp format

    Args:
        timetable (list): the list of timetable entries

    Returns:
        list: the list of .lp formatted timetable entries
    """
    return list(chain.from_iterable([timetable_entry_to_lps(x) for x in timetable]))
#    return [timetable_entry_to_lp(x) for x in timetable]


def clingo_patient_optimisation(handle, total_timeout):
    """Generated iterative clingo optimisation for the model

    Args:
        handle (_type_): The handle to the clingo process
        total_timeout (_type_): the max time to wait

    Returns:
        (model, boolean): the model and True if optimal
    """
    start_time = time.time()
    deadline = time.time()+total_timeout
    best_model = None
    while True:
        handle.resume()
        timeout = deadline-time.time()
        logging.debug('time spent so far {}, time left available {}.'.format(time.time()-start_time, timeout))
        found = handle.wait(timeout)
        if not found:
            print("best model not found")
            print(best_model)
            return (best_model, False)
        model = handle.model()
        if model:
            best_model = model
            print(best_model)
        else:
            # print(best_model.number,best_model.cost,best_model.optimality_proven)
            print("best model found")
            return (best_model, True)
        # print(time.time()-start_time,found)
        # print(search,model.number,best_model.cost,best_model.optimality_proven)


def run_solver():
    """Runs clingo on the generated lp files
    """

    ctrl = clingo.Control()

    # load all the .lp files and save to array
    ctrl.load(str(WORKING_DIR / 'facts' / 'solve.lp'))
    ctrl.load(str(WORKING_DIR / 'output' / 'cse_facts.lp'))

    for file in FACTS_DIR.glob('*.lp'):
        logging.debug("Load file %s", file)
        ctrl.load(str(file))

    for file in OUTPUT_DIR.glob('*.lp'):
        logging.debug("Load file %s", file)
        ctrl.load(str(file))

    ctrl.ground([('base', [])])

    timeout = 60 # 3 minutes in seconds
    start_time = time.time()

    with ctrl.solve(yield_=True, async_=True) as hnd:
        best_model = None
        while True:
            (model, opt) = clingo_patient_optimisation(hnd, LATENCY)
            if model:
                best_model = model
                logging.debug('Model {} found. Cost {}. {}'.format(best_model.number, best_model.cost, best_model))
            else:
                logging.debug('no improvement found')
            if opt:
                break
            if time.time() - start_time > timeout:
                break

        # this is strange but necessary
        with open(str(OUTPUT_DIR / 'solution.txt'), 'w', encoding='utf-8') as output_file:
            print(best_model, file=output_file)
        format_output(str(OUTPUT_DIR / 'solution.txt'))

def create_cse_facts(course_code):
    """Creates the cse_facts.lp file

    Args:
        course_code (str): the course code to generate facts for
    """
    with open( WORKING_DIR / 'facts' / 'cse_facts.tpl', 'r', encoding='utf-8') as cse_facts_template_file:
        # read the file and replace all occurance of COURSE_CODE
        cse_facts = cse_facts_template_file.read().replace('{COURSE_CODE}', course_code)

        # create file in output dir if it doesn't exist

        with open(OUTPUT_DIR / 'cse_facts.lp', 'w', encoding='utf-8') as cse_facts_file:
            cse_facts_file.write(cse_facts)
            logging.debug("Created cse_facts.lp file")

def run_allocate(course_code, preferences_file, timetable_file):
    """ Runs the allocate algorithm on the given files
    """
    logging.debug("Clearing existing .lp files")
    clear_file(OUTPUT_DIR, 'preferences.lp')
    clear_file(OUTPUT_DIR, 'cse_facts.lp')
    clear_file(OUTPUT_DIR, 'timetable.lp')

    logging.debug("Converting timetable to .lp format")
    timetable_lps = timetable_dict_to_lp(
        csv_to_dict(timetable_file))

    logging.debug("Converting preferences to .lp format")
    preferences_lps = preferences_dict_to_lp(
        csv_to_dict(preferences_file))

    logging.debug("Creating cse_facts.lp file")
    create_cse_facts(course_code)

    logging.debug("Saving .lp files to %s", {OUTPUT_DIR / 'timetable.lp'})
    save_lp(timetable_lps, OUTPUT_DIR, 'timetable.lp')

    logging.debug("Saving .lp files to %s", {OUTPUT_DIR / 'preferences.lp'})
    save_lp(preferences_lps, OUTPUT_DIR, 'preferences.lp')

    run_solver()


def format_output(output_file_name):
    """Formats the output of the solver into a list csv
    """
    with open(output_file_name, 'r', encoding='utf-8') as output_file:
        # read string from file into variable
        output = output_file.read()

        regex = re.compile(r'assign\((.*?)\)')
        # find all matches of regex in output
        matches = regex.findall(output)

        # create csv from array and save
        with open(str(OUTPUT_DIR / 'solution.csv'), 'w', encoding='utf-8') as csvfile:
            data = 'zid, code, type\n'
            data += '\n'.join(matches)
            print(data)
            csvfile.write(data)


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "--load":
        logging.debug("Executing solve.lp with any lp files in input_data dir")
        run_solver()
        exit()

    run_allocate(DATA_DIR / 'preferences.csv', DATA_DIR / 'timetable.csv')
