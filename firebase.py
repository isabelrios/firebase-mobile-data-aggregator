#! /usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A small Firebase CloudToolsResults API client"""

from __future__ import absolute_import

import sys
from enum import Enum

from lib.firebase_conn import FirebaseConn


class ExecutionOutcome(Enum):
    FAILURE = 'failure'
    SUCCESS = 'success'
    INCONCLUSIVE = 'inconclusive'
    SKIPPED = 'skipped'

EXECUTIONS_PAGE_SIZE = 60
STEPS_PAGE_SIZE = 200
CASES_PAGE_SIZE = 200

class Firebase:

    def __init__(self, project_id: str, filter_by_name: str) -> None:
        try:
            self.connection = FirebaseConn(project_id)
            self.projects_client = self.connection.get_projects_client()
            self.projectId = project_id
            self.filterByName = filter_by_name
        except KeyError:
            print("Firebase connection failed")
            sys.exit(1)

    def get_histories(self) -> dict:
        """Get a list of (default: 20) histories sorted by modification time in descending order"""
        histories = self.projects_client.projects().histories().list(
            projectId=self.projectId,
            filterByName=self.filterByName
        ).execute()
        return histories

    def get_executions(self, history_id: str, page_token: str = None) -> dict:
        """Get a list of (default: 25) executions for a given project """
        executions = self.projects_client.projects().histories().executions().list(
            projectId=self.projectId,
            historyId=history_id,
            pageSize=int(EXECUTIONS_PAGE_SIZE),
            pageToken=page_token
        ).execute()
        return executions

    def get_execution(self, history_id: str, execution_id: int) -> dict:
        """Get a single execution"""
        execution = self.projects_client.projects().histories().executions().get(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id
        ).execute()
        return execution

    def get_steps(self, history_id: str, execution_id: int, page_size: int) -> dict:
        """Get a list of all steps (default: 25) for a given execution
        sorted by creation time in descending order"""
        steps = self.projects_client.projects().histories().executions().steps().list(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id,
            pageSize=page_size
        ).execute()
        return steps

    def get_step(self, history_id: str, execution_id: int, step_id: str) -> dict:
        """Get a single step"""
        step = self.projects_client.projects().histories().executions().steps().get(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id,
            stepId=step_id
        ).execute()
        return step

    def get_test_cases(self, history_id: str, execution_id: int, step_id: str, page_size: int) -> dict:
        """Get a list of test cases attached to a Step"""
        test_cases = self.projects_client.projects().histories().executions().steps().testCases().list(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id,
            stepId=step_id,
            pageSize=page_size
        ).execute()
        return test_cases

    def get_test_case(self, history_id: str, execution_id: int, step_id: str, test_case_id: str) -> dict:
        """Get a single test case"""
        test_case = self.projects_client.projects().histories().executions().steps().testCases().get(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id,
            stepId=step_id,
            testCaseId=test_case_id
        ).execute()
        return test_case

    def get_environments(self, history_id: str, execution_id: int) -> dict:
        """Get the environments for a given execution"""
        environments = self.projects_client.projects().histories().executions().environments().list(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id,
        ).execute()
        return environments

    def get_environment(self, history_id: str, execution_id: int, environment_id: int) -> dict:
        environment = self.projects_client.projects().histories().executions().environments().get(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id,
            environmentId=environment_id
        ).execute()
        return environment


class FirebaseHelper:
    def __init__(self, project_id: str, filter_by_name: str) -> None:
        self.firebase = Firebase(project_id, filter_by_name)

    def get_histories(self) -> dict:
        """Get a list of all test histories"""
        return self.firebase.get_histories()

    def get_executions(self, history_id: str, page_token: str) -> dict:
        """Get a list of all test executions"""
        return self.firebase.get_executions(history_id, page_token)

    def get_execution(self, history_id: str, execution_id: int) -> dict:
        """Get a single execution"""
        return self.firebase.get_execution(history_id, execution_id)

    def get_steps(self, history_id: str, execution_id: int, page_size: int) -> dict:
        """Get a list of all test steps"""
        return self.firebase.get_steps(history_id, execution_id, page_size)

    def get_step(self, history_id: str, execution_id: int, step_id: str) -> dict:
        """Get a single step"""
        return self.firebase.get_step(history_id, execution_id, step_id)

    def get_test_cases(self, history_id: str, execution_id: int, step_id: str, page_size: int) -> dict:
        """Get a list of test cases attached to a Step"""
        return self.firebase.get_test_cases(history_id, execution_id, step_id, page_size)

    def get_test_case(self, history_id: str, execution_id: int, step_id: str, test_case_id: str) -> dict:
        """Get a single test case"""
        return self.firebase.get_test_case(history_id, execution_id, step_id, test_case_id)

    def get_environments(self, history_id: str, execution_id: int) -> dict:
        """Get the environments for a given execution"""
        return self.firebase.get_environments(history_id, execution_id)

    def get_environment(self, history_id: str, execution_id: int, environment_id: int) -> dict:
        """Get a single environment"""
        return self.firebase.get_environment(history_id, execution_id, environment_id)

    def get_test_case_details(self, execution_outcome_summary: str) -> dict:
        """Get test case details with provided execution outcome summary"""
        history = next(iter([x for y in self.get_histories().values() for x in y]))
        executions = self.get_executions(
            history_id=history['historyId'],
            page_token=None
        )
        results = []

        for execution in executions['executions']:
            """Filter on complete executions"""
            if 'complete' in execution.values():
                if execution['outcome']['summary'] == execution_outcome_summary:
                    steps = self.get_steps(
                        history_id=history['historyId'],
                        execution_id=int(execution['executionId']),
                        page_size=int(STEPS_PAGE_SIZE)
                    )
                    for k, v in steps.items():
                        if k == 'steps':
                            for step in v:
                                if step['outcome']['summary'] == 'failure':
                                    cases = self.get_test_cases(
                                        history_id=history['historyId'],
                                        execution_id=int(execution['executionId']),
                                        step_id=step['stepId'],
                                        page_size=int(CASES_PAGE_SIZE)
                                    )
                                    # TODO: Decide on which data to capture
                                    results.append({
                                        'testCase': [case['testCaseReference'] for case in cases['testCases']],
                                        'result': [case['status'] for case in cases['testCases']],
                                        'matrix': execution['testExecutionMatrixId']
                                    })
        print(f"{results}")

    def get_test_case_results_by_execution_summary(self, execution_outcome_summary: str) -> dict:
        from datetime import datetime

        """Get test case results from executions with a provided outcome summary"""
        history = next(iter([x for y in self.get_histories().values() for x in y]))
        executions = self.get_executions(
            history_id=history['historyId'],
            page_token=None
        )
        results = []

        for execution in executions['executions']:
            """Filter on complete executions"""
            if 'complete' in execution.values():
                """Executions with flaky tests (of multiple attempts) are treated as successful"""
                if execution['outcome']['summary'] == execution_outcome_summary:
                    steps = self.get_steps(
                        history_id=history['historyId'],
                        execution_id=int(execution['executionId']),
                        page_size=int(STEPS_PAGE_SIZE)
                    )
                    environments = self.get_environments(
                        history_id=history['historyId'],
                        execution_id=int(execution['executionId'])
                    )
                    for k, v in steps.items():
                        if k == 'steps':
                            for step in v:
                                if step['outcome']['summary'] == 'failure':
                                    cases = self.get_test_cases(
                                        history_id=history['historyId'],
                                        execution_id=int(execution['executionId']),
                                        step_id=step['stepId'],
                                        page_size=int(CASES_PAGE_SIZE)
                                    )
                                    for k, v in cases.items():
                                        if k == 'testCases':
                                            for case in v:
                                                if case['status'] == 'failed':
                                                    results.append({
                                                            'testCase': [case['testCaseReference'] for case in cases['testCases']],
                                                            'testCaseResult': [case['status'] for case in cases['testCases']],
                                                            'matrix': execution['testExecutionMatrixId'],
                                                            'environmentSummary': [environment['environmentResult']['outcome']['summary'] for environment in environments['environments']],
                                                            'creationTime': str(
                                                                datetime.fromtimestamp(
                                                                    int(execution['creationTime']['seconds'])
                                                                ).strftime('%Y-%m-%d')
                                                            ),
                                                        }
                                                    )
        return results

    def print_test_results_by_execution_summary(self, execution_outcome_summary: str) -> None:
        results = self.get_test_case_results_by_execution_summary(execution_outcome_summary)
        if results:
            for result in results:
                print(f"{result}")
        else:
            print("No results found")

    def display_execution_timestamp(self, execution_outcome_summary: str) -> None:
        from datetime import datetime

        history = next(iter([x for y in self.get_histories().values() for x in y]))
        executions = self.get_executions(
            history_id=history['historyId'],
            page_token=None
        )
        for execution in executions['executions']:
            """Filter on complete executions"""
            if 'complete' in execution.values():
                if execution['outcome']['summary'] == execution_outcome_summary:
                    for k, v in execution['creationTime'].items():
                        if k == 'seconds':
                            dt_obj = datetime.fromtimestamp(
                                int(v)
                            )
                            print(f"{dt_obj.strftime('%Y-%m-%d')} - {execution['testExecutionMatrixId']}")
