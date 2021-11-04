#! /usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A script to pull recent test results summary"""

from __future__ import absolute_import

import sys

from lib.firebase_conn import FirebaseConn


class Firebase:

    def __init__(self, project_id: str, filter_by_name: str) -> None:
        try:
            self.connection = FirebaseConn(project_id)
            self.projects_client = self.connection.get_projects_client()
            self.histories = self.projects_client.projects().histories().list(
                projectId=project_id,
                filterByName=filter_by_name
            )
            self.projectId = project_id
            self.filterByName = filter_by_name
        except KeyError:
            print("Firebase connection failed")
            sys.exit(1)

    def get_histories(self) -> list:
        """Get a list of (default: 20) histories sorted by modification time in descending order"""
        histories = self.histories.execute()
        return histories

    def get_executions(self, history_id: str) -> list:
        """Get a list of (default: 25) executions for a given project """
        executions = self.projects_client.projects().histories().executions().list(
            projectId=self.projectId,
            historyId=history_id
        ).execute()
        return executions

    def get_steps(self, history_id: str, execution_id: int, page_size: int) -> list:
        """Get a list of all steps (default: 25) for a given execution sorted by creation time in descending order"""
        steps = self.projects_client.projects().histories().executions().steps().list(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id,
            pageSize=page_size
        ).execute()
        return steps
    
    def get_test_cases(self, history_id: str, execution_id: int, step_id: str, page_size: int) -> list:
        """Get a list of test cases attached to a Step"""
        test_cases = self.projects_client.projects().histories().executions().steps().testCases().list(
            projectId=self.projectId,
            historyId=history_id,
            executionId=execution_id,
            stepId=step_id,
            pageSize=page_size
        ).execute()
        return test_cases


class FirebaseHelper:
    def __init__(self, project_id: str, filter_by_name: str) -> None:
        self.firebase = Firebase(project_id, filter_by_name)

    def get_histories(self) -> list:
        """Get a list of all test histories"""
        return self.firebase.get_histories()

    def get_executions(self, history_id: str) -> list:
        """Get a list of all test executions"""
        return self.firebase.get_executions(history_id)

    def get_steps(self, history_id: str, execution_id: int, page_size: int) -> list:
        """Get a list of all test steps"""
        return self.firebase.get_steps(history_id, execution_id, page_size)

    def get_test_cases(self, history_id: str, execution_id: int, step_id: str, page_size: int) -> list:
        """Get a list of test cases attached to a Step"""
        return self.firebase.get_test_cases(history_id, execution_id, step_id, page_size)
     
    def print_outcome_summaries(self) -> None:
        histories = self.get_histories()
        for history in histories.values():
            for id in history:
                executions = self.get_executions(history_id=id['historyId'])
                for k, v in executions.items():
                    if k == 'executions':
                        for execution in v:
                            if 'outcome' in execution:
                                if execution['outcome']['summary'] == 'failure':
                                    steps = self.get_steps(
                                        history_id=id['historyId'],
                                        execution_id=int(execution['executionId']),
                                        page_size=int(200))
                                    for k, v in steps.items():
                                        if k == 'steps':
                                            for step in v:
                                                if step['outcome']['summary'] == 'failure':
                                                    if 'testExecutionStep' in step and 'dimensionValue' in step:
                                                        for k, v in step['testExecutionStep'].items():
                                                            if k == 'toolExecution':
                                                                for details in v['toolOutputs']:
                                                                    if 'testCase' in details:
                                                                        print(
                                                                            f"Test: {details['testCase']['name']} "
                                                                            f"Matrix: {execution['testExecutionMatrixId']} "
                                                                            f"Outcome: {step['outcome']['summary']}"
                                                                        )
                                if execution['outcome']['summary'] == 'success':
                                    steps = self.get_steps(
                                        history_id=id['historyId'],
                                        execution_id=int(execution['executionId']),
                                        page_size=int(200))
                                    for k, v in steps.items():
                                        if k == 'steps':
                                            for step in v:
                                                if step['outcome']['summary'] == 'failure':
                                                    if 'testExecutionStep' in step and 'dimensionValue' in step:
                                                        for k, v in step['testExecutionStep'].items():
                                                            if k == 'toolExecution':
                                                                for details in v['toolOutputs']:
                                                                    if 'testCase' in details:
                                                                        print(
                                                                            f"Flaky Test: {details['testCase']['name']}"
                                                                            f"Matrix: {execution['testExecutionMatrixId']}"
                                                                            f"Outcome: {step['outcome']['summary']}"
                                                                        )
