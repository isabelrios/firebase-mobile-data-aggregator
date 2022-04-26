#! /usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import os
from enum import Enum

import googleapiclient.discovery
from google.oauth2 import service_account


class FirebaseProjects(Enum):
    """
    Enum for the Firebase projects.
    """
    MOZ_FENIX = "moz-fenix"
    MOZ_FOCUS_ANDROID = "moz-focus-android"
    MOZ_ANDROID_COMPONENTS = "moz-android-components"


class FirebaseConn:

    def get_projects_client(self):
        return self.projects_client

    def set_project(self, credentials):
        self.projects_client = googleapiclient.discovery.build(
            'toolresults', 'v1beta3', credentials=self.credentials)

    def __init__(self, project) -> None:
        try:
            if project == FirebaseProjects.MOZ_FENIX.value:
                gcloud_auth_moz_fenix = os.environ['GCLOUD_AUTH_MOZ_FENIX']
                self.JSON_CREDENTIAL = json.loads(gcloud_auth_moz_fenix)
            elif project == FirebaseProjects.MOZ_FOCUS_ANDROID.value:
                gcloud_auth_moz_focus_android = os.environ['GCLOUD_AUTH_MOZ_FOCUS_ANDROID']
                self.JSON_CREDENTIAL = json.loads(
                    gcloud_auth_moz_focus_android)
            elif project == FirebaseProjects.MOZ_ANDROID_COMPONENTS.value:
                gcloud_auth_moz_android_components = os.environ['GCLOUD_AUTH_MOZ_ANDROID_COMPONENTS']
                self.JSON_CREDENTIAL = json.loads(
                    gcloud_auth_moz_android_components)
        except KeyError:
            raise Exception("Please set the GCLOUD_AUTH_MOZ_<project> auth environment variable.")

        """Authenticate with Google API"""
        self.credentials = service_account.Credentials.from_service_account_info(
            self.JSON_CREDENTIAL)

        self.set_project(self.credentials)
