"""Converts a timetable CSV to a .lp format for use with the solver
"""

from itertools import chain
import pathlib
from fact_builder import fact_builder, save_lp, csv_to_dict, clear_file

WORKING_DIR = pathlib.Path(__file__).parent.parent.absolute()
DATA_DIR = WORKING_DIR / 'sample_data'
OUTPUT_DIR = WORKING_DIR / 'data'

DAYS = ["M", "T", "W", "H", "F"]
TIMES = ["08", "09", "10", "11", "12", "13",
         "14", "15", "16", "17", "18", "19", "20"]
DAY_TIMES = [(x, y) for x in DAYS for y in TIMES]

KEY_TO_PREF = {
    '0': ('impossible', 'onlineOrPerson'),
    '0.1': ('impossible', 'onlineOnly'),
    '1': ('dislike', 'onlineOrPerson'),
    '1.1': ('dislike', 'onlineOnly'),
    '2': ('possible', 'onlineOrPerson'),
    '2.1': ('possible', 'onlineOnly'),
    '3': ('preferred', 'onlineOrPerson'),
    '3.1': ('preferred', 'onlineOnly'),
}


def preference_entry_to_lps(preference_entry: dict) -> list[str]:
    """Converts a single preference entry to a .lp format

    Args:
        preference_entry (dict): The preference entry to convert

    Returns:
        str: the lp format of the preference entry
    """

    z_id = preference_entry['zid']

    result = []
    result.append(fact_builder('teacher', preference_entry['zid']))
    if "1511" in preference_entry['previous_experience']:
        result.append(fact_builder('experience', z_id, 'tute'))
        result.append(fact_builder('experience', z_id, 'asst'))

    # Go through each day and time
    # (M09) and then extract the preference
    for (day,time) in DAY_TIMES:
        key = [day, time]
        #pref = preference_entry[key[0] + key[1]]
        try:
            # Turn the preference entry (1.1) into a tuple (dislike, True)
            pref = KEY_TO_PREF[preference_entry[day+time]]
        except KeyError:
            # Seems as though there are more times available in CASTLE than the tutors complete,
            # so some preferences are not available. In this case return impossible
            pref = ('impossible', False)
        if pref[0] != 'impossible':
            result.append(fact_builder('available', z_id, 'online', day, int(time)))
            if pref[1] == 'onlineOrPerson':
                result.append(fact_builder('available', z_id, 'inPerson', day, int(time)))
            result.append(fact_builder('desire', z_id, pref[0], day, int(time)))
        #result.append(fact_builder('preference', z_id, *key, *pref))

    # These are just stubbed for now
    result.append(fact_builder('capacity', z_id, 'tute', 4))
    result.append(fact_builder('capacity', z_id, 'asst', 4))
    result.append(fact_builder('prefer', z_id, 'tute'))
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
    day  = timetable_entry['Day'].lower()
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


if __name__ == '__main__':
    print("Converting timetable to .lp format")
    timetable_lps = timetable_dict_to_lp(
        csv_to_dict(DATA_DIR, 'timetable.csv'))

    print("Converting preferences to .lp format")
    preferences_lps = preferences_dict_to_lp(
        csv_to_dict(DATA_DIR, 'preferences_castle.csv'))

    print("Clearing existing .lp files")
    clear_file(OUTPUT_DIR, 'preferences.lp')
    clear_file(OUTPUT_DIR, 'timetable.lp')

    print(f"Saving .lp files to {OUTPUT_DIR / 'timetable.lp'}")
    save_lp(timetable_lps, OUTPUT_DIR, 'timetable.lp')
    print(f"Saving .lp files to {OUTPUT_DIR / 'preferences.lp'}")
    save_lp(preferences_lps, OUTPUT_DIR, 'preferences.lp')
