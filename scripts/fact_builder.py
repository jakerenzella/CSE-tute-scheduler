"""Some helpers to read the CSV data into a dictionary, write lp files"""

import pathlib
import csv


def clear_file(output_dir: str, filename: str):
    """Clears a given file

    Args:
        output_dir (str): The output directory
        filename (str): The output path
    """
    with open(pathlib.Path(output_dir / filename), 'a', encoding='utf-8') as lpfile:
        lpfile.truncate(0)  # clear file


def csv_to_dict(input_path: str, filename: str) -> list[dict]:
    """Loads the timetable CSV into a dictionary

    Returns:
        List: A dictionary containing the CSV data
    """
    results = []
    with open(pathlib.Path(input_path / filename), encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        # ignore the headers
        next(reader)

        for row in reader:
            results.append(dict(row))  # pull in each row as a key-value pair
    return results


def fact_builder(functor: str, *args: list) -> str:
    """Builds the fact statement for the solver from a list of strings

    Args:
        args (list): The arguments to the fact statement

    Returns:
        str: The fact statement
    """
    args = [str(x).lower() for x in args]
    return f"{functor}({', '.join(args)})."


def save_lp(lp_list: list[str], output_dir: str, filename: str) -> None:
    """Generates the .lp file from the timetable CSV, and saves it to a file
    """
    output_dir.mkdir(exist_ok=True)
    with open(pathlib.Path(output_dir / filename), 'a', encoding='utf-8') as lpfile:
        lpfile.write('\n'.join(lp_list))
