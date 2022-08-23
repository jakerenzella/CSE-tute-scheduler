#! /usr/bin/env python3
"""Converts a timetable CSV to a .lp format for use with the solver
"""

from itertools import chain
import pathlib
import sys, time
from fact_builder import fact_builder, save_lp, csv_to_dict, clear_file
import clingo

WORKING_DIR = pathlib.Path(__file__).parent.parent.absolute()
DATA_DIR = WORKING_DIR / 'data_1511'
#DATA_DIR = WORKING_DIR / 'data_sample'
OUTPUT_DIR = WORKING_DIR / 'data'
LATENCY = 1

DAYS = ["M", "T", "W", "H", "F"]
TIMES = ["08", "09", "10", "11", "12", "13",
         "14", "15", "16", "17", "18", "19", "20"]
DAY_TIMES = [(x, y) for x in DAYS for y in TIMES]

KEY_TO_PREF = {
    '0': ('impossible', 0, 'onlineOrPerson'),
    '0.1': ('impossible', 0, 'onlineOnly'),
    '1': ('dislike', 1, 'onlineOrPerson'),
    '1.1': ('dislike', 1, 'onlineOnly'),
    '2': ('possible', 2, 'onlineOrPerson'),
    '2.1': ('possible', 2, 'onlineOnly'),
    '3': ('preferred', 3, 'onlineOrPerson'),
    '3.1': ('preferred', 3, 'onlineOnly'),
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

    z_id = preference_entry['zid']
    tt_max = preference_entry['TT'] if 'TT' in preference_entry else 4
    at_max = preference_entry['AT'] if 'AT' in preference_entry else 4

    result = []
    result.append(fact_builder('teacher', preference_entry['zid']))
    previous_experiences = [course.strip().lower() for course in preference_entry['previous_experience'].split('|')] # This is a bit of a hack. Need to do something better some day.
    previous_experiences = [(course[0:8], 'admin' in course) for course in previous_experiences]
    for (course, admin) in previous_experiences:
        result.append(fact_builder('experience', z_id, f'involved({course})'))
        if admin:
            result.append(fact_builder('experience', z_id, f'admin({course})'))
    #if "1511" in preference_entry['previous_experience']:
    #    result.append(fact_builder('experience', z_id, 'tute'))
    #    result.append(fact_builder('experience', z_id, 'asst'))

    # Go through each day and time
    # (M09) and then extract the preference
    for (day, time) in DAY_TIMES:
        # key = [day, time]
        # pref = preference_entry[key[0] + key[1]]
        try:
            # Turn the preference entry (1.1) into a tuple (dislike, True)
            pref = KEY_TO_PREF[preference_entry[day+time]]
        except KeyError:
            # Seems as though there are more times available in CASTLE than the tutors complete,
            # so some preferences are not available. In this case return impossible
            pref = ('impossible', 0, False)
        if pref[0] != 'impossible':
            if pref[2] == 'onlineOrPerson':
                result.append(fact_builder('available', z_id, 'online', day, int(time)))
                result.append(fact_builder('available', z_id, 'inPerson', day, int(time)))
            else:
                assert pref[2] == 'onlineOnly'
                result.append(fact_builder('available', z_id, 'online', day, int(time)))
        result.append(fact_builder('desire', z_id, pref[1], day, int(time)))
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
    time = timetable_entry['Time']

    result = []
    result.append(fact_builder('class', slot))
    result.append(fact_builder('mode', slot, mode))
    result.append(fact_builder('day', slot, day))
    result.append(fact_builder('startTime', slot, int(time)))
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

def clingoPatientOptimization(handle,total_timeout):
    starttime = time.time()
    deadline = time.time()+total_timeout
    bestModel = None
    while True:
        handle.resume()
        timeout = deadline-time.time()
        #print(timeout,time.time()-starttime)
        found = handle.wait(timeout)
        if not found:
            return (bestModel, False)
        model = handle.model()
        if model:
            bestModel = model
        else:
            #print(bestModel.number,bestModel.cost,bestModel.optimality_proven)
            return (bestModel, True)
        #print(time.time()-starttime,found)
        #print(search,model.number,bestModel.cost,bestModel.optimality_proven)

def run_solver():
    """Runs clingo on the generated lp files
    """

    ctrl = clingo.Control()

    # load all the .lp files and save to array
    ctrl.load(str(WORKING_DIR / 'solve.lp'))

    for file in OUTPUT_DIR.glob('*.lp'):
        print(file)
        ctrl.load(str(file))

    ctrl.ground([('base', [])])

    with ctrl.solve(yield_=True, async_=True) as hnd:
        bestModel = None
        while True:
            (model,opt) = clingoPatientOptimization(hnd,LATENCY)
            if model:
                bestModel = model
                #print(bestModel.number,bestModel.cost)
                print(bestModel,bestModel.number,bestModel.cost)
            else:
                print('no improvement found')
            if opt:
                break
        print(hnd.get())
        print(bestModel)
    #result = ctrl.solve(on_model=print)

    #print(result)


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "--load":
        print("Executing solve.lp with any lp files in input_data dir")
        run_solver()
        exit()

    print("Converting timetable to .lp format")
    timetable_lps = timetable_dict_to_lp(csv_to_dict(DATA_DIR, f'timetable.csv'))

    print("Converting preferences to .lp format")
    preferences_lps = preferences_dict_to_lp(csv_to_dict(DATA_DIR, f'preferences.csv'))

    print("Clearing existing .lp files")
    clear_file(OUTPUT_DIR, 'preferences.lp')
    clear_file(OUTPUT_DIR, 'timetable.lp')

    print(f"Saving .lp files to {OUTPUT_DIR / 'timetable.lp'}")
    save_lp(timetable_lps, OUTPUT_DIR, 'timetable.lp')

    print(f"Saving .lp files to {OUTPUT_DIR / 'preferences.lp'}")
    save_lp(preferences_lps, OUTPUT_DIR, 'preferences.lp')

    run_solver()
