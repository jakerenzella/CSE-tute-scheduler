"""A CLI for the allocate script"""
import typer

from allocate import run_allocate


def main(preferences_input_file: str, timetable_inpute_file: str):
    """Runs the allocate script"""
    run_allocate(preferences_input_file, timetable_inpute_file)


if __name__ == "__main__":
    typer.run(main)
