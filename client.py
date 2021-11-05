#! /usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import sys

from firebase import ExecutionOutcome, FirebaseHelper

PROJECTS_ABBREV = [
    'moz-fenix',
    'moz-focus-android',
    'moz-reference-browser',
    'moz-android-components'
]

FILTER_NAME_ABBREV = [
    'org.mozilla.fenix.debug',
    'org.mozilla.fenix',
    'org.mozilla.focus.debug',
    'org.mozilla.focus'
]


def parse_args(cmdln_args):
    parser = argparse.ArgumentParser(
        description="Query Firebase Cloud ToolResults API for mobile test data"
    )

    parser.add_argument(
        "--project",
        help="Indicate project",
        required=True,
        choices=PROJECTS_ABBREV
    )

    parser.add_argument(
        "--filter-by-name",
        help="Indicate filter by name",
        required=True,
        choices=FILTER_NAME_ABBREV
    )

    return parser.parse_args(args=cmdln_args)


def main():
    args = parse_args(sys.argv[1:])

    FirebaseHelperClient = FirebaseHelper(args.project, args.filter_by_name)
    #FirebaseHelperClient.get_test_case_details(ExecutionOutcome.FAILURE.value)
    FirebaseHelperClient.print_test_results_by_execution_summary(
        execution_outcome_summary=ExecutionOutcome.SUCCESS.value
    )


if __name__ == '__main__':
    main()
