"""A CLI for the allocate script"""
import typer

from allocate import run_allocate


def main(course_code: str = typer.Argument(..., help="The course code (comp1531"), preferences_input_file: str = typer.Argument(..., help="The path to the preferences csv file"), timetable_input_file: str = typer.Argument(..., help="The path to the timetable csv file")):
    """Runs the allocate script"""

    run_allocate(course_code.lower(), preferences_input_file, timetable_input_file)


if __name__ == "__main__":
    typer.run(main)
