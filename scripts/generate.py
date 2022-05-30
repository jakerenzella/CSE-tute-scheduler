import click

from castle_to_lps import generate
from subprocess import Popen, PIPE


@click.command()
@click.argument('coursecode')
@click.argument('timetable', type=click.Path(exists=True))
@click.argument('preferences', type=click.Path(exists=True))
@click.argument('output', type=click.File('wb'))
def launch_solving(coursecode, timetable, preferences, output):
    """Simple program that greets NAME for a total of COUNT times."""
    generate(coursecode, timetable, preferences)

    p = Popen(['clingo', 'solve.lp', 'data/timetable.lp', 'data/preferences.lp',
              'data/cse_facts.lp'], stdout=PIPE, stderr=PIPE, stdin=PIPE)

    output = p.stdout.read()
    p.stdin.write(input)

    # os.system(
        # 'clingo solve.lp data/timetable.lp data/preferences.lp data/cse_facts.lp')


def main():
    launch_solving(prog_name="CSE tute solver")


if __name__ == '__main__':
    main()
