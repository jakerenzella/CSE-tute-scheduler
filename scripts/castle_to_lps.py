"""Converts a timetable CSV to a .lp format for use with the solver
"""

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
    '0': ('impossible', False),
    '0.1': ('impossible', True),
    '1': ('dislike', False),
    '1.1': ('dislike', True),
    '2': ('possible', False),
    '2.1': ('possible', True),
    '3': ('preferred', False),
    '3.1': ('preferred', True),
}


def preferences_dict_to_lp(preferences: list) -> list:
    """Iterates through the list of preferences and converts them to .lp format

    Args:
        preferences (list): the list of preferences

    Returns:
        list: the list of .lp formatted preferences
    """
    return [preference_entry_to_lps(x) for x in preferences]


def preference_entry_to_lps(preference_entry: dict) -> list[str]:
    """Converts a single preference entry to a .lp format

    Args:
        preference_entry (dict): The preference entry to convert

    Returns:
        str: the lp format of the preference entry
    """

    z_id = preference_entry['zid'].lower()

    result = []
    result.append(fact_builder('teacher', preference_entry['zid'].lower()))
    result.append(fact_builder('previousTuteExperience',
                  z_id, "1511" in preference_entry['previous_experience']))

    # Go through each day and time
    # (M09) and then extract the preference
    for key in DAY_TIMES:
        pref = preference_entry[key[0] + key[1]]
        try:
            # Turn the preference entry (1.1) into a tuple (dislike, True)
            pref = KEY_TO_PREF[preference_entry[''.join(key)]]
        except KeyError:
            # Seems as though there are more times available in CASTLE than the tutors complete,
            # so some preferences are not available. In this case return impossible
            pref = ['impossible', False]
        result.append(fact_builder('preference', z_id, *key, *pref))

    # These are just stubbed for now
    result.append(fact_builder('capacityTute', z_id, 1))
    result.append(fact_builder('capacityAsst', z_id, 1))
    result.append(fact_builder('preferTutorial', z_id, 1))
    return result


def timetable_entry_to_lp(timetable_entry: dict) -> str:
    """Converts a single timetable entry to a .lp format

    Args:
        timetable_entry (dict): The timetable entry to convert

    Returns:
        str: the lp format of the timetable entry
    """
    keys_to_extract = ['Class Desc', 'In Person',
                       'Room', 'Day', 'Time']

    fact_builder_args = [timetable_entry[x].lower() for x in keys_to_extract]
    return fact_builder('class', *fact_builder_args)


def timetable_dict_to_lp(timetable: list) -> list:
    """Iterates through the list of timetable entries and converts them to .lp format

    Args:
        timetable (list): the list of timetable entries

    Returns:
        list: the list of .lp formatted timetable entries
    """
    return [timetable_entry_to_lp(x) for x in timetable]


if __name__ == '__main__':
    timetable_lps = timetable_dict_to_lp(
        csv_to_dict(DATA_DIR, 'timetable.csv'))
    preferences_lps = preferences_dict_to_lp(
        csv_to_dict(DATA_DIR, 'preferences_castle.csv'))
    preferences_lps = [item for sublist in preferences_lps for item in sublist]

    clear_file(OUTPUT_DIR, 'preferences.lp')
    clear_file(OUTPUT_DIR, 'timetable.lp')

    save_lp(timetable_lps, OUTPUT_DIR, 'timetable.lp')
    save_lp(preferences_lps, OUTPUT_DIR, 'preferences.lp')
