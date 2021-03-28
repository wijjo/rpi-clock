#!/usr/bin/env python3

import os
import sys
import shlex
from argparse import ArgumentParser
from dataclasses import dataclass
from subprocess import run
from typing import Callable, Dict, List

# Assume this script is in an immediate sub-folder of the base folder.

BASE_FOLDER = os.path.dirname(os.path.dirname(__file__))
DIST_FOLDER = os.path.join(BASE_FOLDER, 'dist')
DIST_FILTERS = [
    '- /__pycache__/**',
    '- **/__pycache__/**',
    '+ /app',
    '+ /app/**',
    '+ /bin',
    '+ /bin/**',
    '+ /fonts',
    '+ /fonts/**',
    '+ /rpiclock',
    '+ /rpiclock/**',
    '+ *.py',
    '+ *.json',
    '- /**',
]


class Arg:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


@dataclass
class Task:
    name: str
    description: str
    arguments: List[Arg]
    function: Callable


TASKS: Dict[str, Task] = {}


def task(*arguments: Arg):
    """Task function decorator."""
    def inner(task_function: Callable):
        TASKS[task_function.__name__] = Task(task_function.__name__,
                                             task_function.__doc__,
                                             list(arguments),
                                             task_function)
        return task_function
    return inner


@task()
def dist(args):
    """populate distribution folder"""
    task_heading('Populating distribution folder.')
    rsync(BASE_FOLDER + '/',
          DIST_FOLDER + '/',
          filters=DIST_FILTERS,
          delete=True,
          dry_run=args.dry_run,
          verbose=args.verbose)


@task(Arg('target', help='rsync target specification'))
def deploy(args):
    """deploy distribution"""
    dist(args)
    task_heading('Deploying distribution.')
    # This does not delete target files corresponding to deleted source files,
    # because the program runs as root and leaves .pyc files owned by root.
    rsync(DIST_FOLDER + '/', args.target + '/', dry_run=args.dry_run, verbose=args.verbose)


def task_heading(text: str):
    print('')
    print(f'=== {text} ===')
    print('')


def rsync(source_folder: str,
          target_folder: str,
          filters: list = None,
          delete: bool = False,
          dry_run: bool = False,
          verbose: bool = False):
    """
    Synchronize folders and files using rsync.

    Excludes all by default if includes are provided.

    :param source_folder: full source folder path
    :param target_folder: full target folder path
    :param filters: include/exclude rsync filter specs
    :param delete: delete extra target files if True
    :param dry_run: perform a dry-run without affecting any files or folders
    :param verbose: display more detailed messages
    """
    rsync_command = ['rsync']
    if dry_run:
        rsync_command.append('--dry-run')
    rsync_command.append('-a')
    if verbose:
        rsync_command.append('-v')
    if delete:
        rsync_command.append('--delete')
    if filters is not None:
        for filter_spec in filters:
            rsync_command.append('--filter')
            rsync_command.append(filter_spec)
    rsync_command.append(source_folder)
    rsync_command.append(target_folder)
    if verbose:
        print(' '.join([shlex.quote(s) for s in rsync_command]))
    proc = run(rsync_command)
    if proc.returncode != 0:
        sys.exit(proc.returncode)


def main():
    parser = ArgumentParser(description='RPI-Clock Builder')
    parser.add_argument('-n', '--dry-run',
                        dest='dry_run',
                        action='store_true',
                        help='perform a dry run')
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        help='display more detailed messages, when possible')
    task_subparsers = parser.add_subparsers(dest='task',
                                            metavar='task',
                                            required=True)
    for task_name, task_spec in TASKS.items():
        task_parser = task_subparsers.add_parser(task_spec.name, help=task_spec.description)
        for argument in task_spec.arguments:
            task_parser.add_argument(*argument.args, **argument.kwargs)
    args = parser.parse_args()
    TASKS[args.task].function(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write(os.linesep)
        sys.exit(1)
