#! /usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A script to pull recent test results summary"""

from __future__ import absolute_import

import sys
from enum import Enum

from lib.firebase_conn import FirebaseConn


class ExecutionOutcome(Enum):
    FAILURE = 'failure'
    SUCCESS = 'success'
    INCONCLUSIVE = 'inconclusive'
    SKIPPED = 'skipped'


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

    def get_executions(self, history_id: str) -> dict:
        """Get a list of (default: 25) executions for a given project """
        executions = self.projects_client.projects().histories().executions().list(
            projectId=self.projectId,
            historyId=history_id,
            pageSize=int(40)
        ).execute()
        return executions

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

    def get_environment(self, history_id: str, execution_id: int) -> dict:
        """Get the environment for a given execution"""
        environment = self.projects_client.projects().histories().executions().environments().list(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id,
        ).execute()
        return environment


class FirebaseHelper:
    def __init__(self, project_id: str, filter_by_name: str) -> None:
        self.firebase = Firebase(project_id, filter_by_name)

    def get_histories(self) -> dict:
        """Get a list of all test histories"""
        return self.firebase.get_histories()

    def get_executions(self, history_id: str) -> dict:
        """Get a list of all test executions"""
        return self.firebase.get_executions(history_id)

    def get_steps(self, history_id: str, execution_id: int, page_size: int) -> dict:
        """Get a list of all test steps"""
        return self.firebase.get_steps(history_id, execution_id, page_size)

    def get_test_cases(self, history_id: str, execution_id: int, step_id: str, page_size: int) -> dict:
        """Get a list of test cases attached to a Step"""
        return self.firebase.get_test_cases(history_id, execution_id, step_id, page_size)

    def get_environment(self, history_id: str, execution_id: int) -> dict:
        """Get the environment for a given execution"""
        return self.firebase.get_environment(history_id, execution_id)

    def get_test_case_results(self, history_id: str, execution_id: int, step_id: str, page_size: int) -> dict:
        """Get a list of test case results attached to a Step"""
        test_case_results = self.firebase.get_test_cases(history_id, execution_id, step_id, page_size)
        return test_case_results

    def get_test_case_details(self, execution_outcome_summary: str) -> dict:
        """Get test cases with provided execution outcome summary"""
        results = []
        histories = self.get_histories()
        for history in histories.values():
            for id in history:
                executions = self.get_executions(
                    history_id=id['historyId']
                )
                for execution in executions['executions']:
                    """Filter on complete executions"""
                    if 'complete' in execution.values():
                        if execution['outcome']['summary'] == execution_outcome_summary:
                            steps = self.get_steps(
                                history_id=id['historyId'],
                                execution_id=int(execution['executionId']),
                                page_size=int(200)
                            )
                            for k, v in steps.items():
                                if k == 'steps':
                                    for step in v:
                                        if step['outcome']['summary'] == 'failure':
                                            cases = self.get_test_cases(
                                                history_id=id['historyId'],
                                                execution_id=int(execution['executionId']),
                                                step_id=step['stepId'],
                                                page_size=int(200)
                                            )
                                            # TODO: Decide on which data to capture
                                            results.append( {
                                                'testCase': [case['testCaseReference'] for case in cases['testCases']],
                                                'result': [case['status'] for case in cases['testCases']],
                                                'matrix': execution['testExecutionMatrixId']
                                            })
        print(results)
   
    def get_test_case_results_by_execution_summary(self, execution_outcome_summary: str) -> dict:
        """Get test case results for executions with a provided outcome summary"""
        results = []
        histories = self.get_histories()
        for history in histories.values():
            for id in history:
                executions = self.get_executions(
                    history_id=id['historyId']
                )
                for execution in executions['executions']:
                    """Filter on complete executions"""
                    if 'complete' in execution.values():
                        if execution['outcome']['summary'] == execution_outcome_summary:
                            steps = self.get_steps(
                                history_id=id['historyId'],
                                execution_id=int(execution['executionId']),
                                page_size=int(200)
                            )
                            for k, v in steps.items():
                                if k == 'steps':
                                    for step in v:
                                        if step['outcome']['summary'] == 'failure':
                                            cases = self.get_test_cases(
                                                history_id=id['historyId'],
                                                execution_id=int(execution['executionId']),
                                                step_id=step['stepId'],
                                                page_size=int(200)
                                            )
                                            for k, v in cases.items():
                                                if k == 'testCases':
                                                    for case in v:
                                                        if case['status'] == 'failed':
                                                            results.append(
                                                                case['testCaseReference']
                                                            )
        return results

    def print_test_results_by_execution_summary(self, execution_outcome_summary: str) -> None:
        results = self.get_test_case_results_by_execution_summary(execution_outcome_summary)
        if results:
            for result in results:
                print(result)
        else:
            print("No results found")
