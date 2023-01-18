"""A CLI for the allocate script"""
import typer

from allocate import run_allocate


def main(course_code: str = typer.Argument(..., help="The name of the user to greet"), preferences_input_file: str = typer.Argument(..., help="The name of the user to greet"), timetable_input_file: str = typer.Argument(..., help="The name of the user to greet")):
    """Runs the allocate script"""

    course_code = course_code.lower()
    run_allocate(course_code, preferences_input_file, timetable_input_file)


if __name__ == "__main__":
    typer.run(main)
