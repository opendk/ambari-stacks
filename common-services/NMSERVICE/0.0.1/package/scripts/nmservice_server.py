#!/usr/bin/python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import sys
import os

from resource_management.libraries.script.script import Script
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions.copy_tarball import copy_to_hdfs
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions import StackFeature
from resource_management.core.logger import Logger
from resource_management.core import shell
from setup_nmservice import *
from nmservice_service import nmservice_service


class NMServiceServer(Script):

  def install(self, env):
    import params
    env.set_params(params)

    self.install_packages(env)

  def configure(self, env, upgrade_type=None, config_dir=None):
    import params
    env.set_params(params)

    setup_nmservice(env, 'server', upgrade_type=upgrade_type, action = 'config')

  def start(self, env, upgrade_type=None):
    import params
    env.set_params(params)

    self.configure(env)
    nmservice_service('nmservice', upgrade_type=upgrade_type, action='start')

  def stop(self, env, upgrade_type=None):
    import params
    env.set_params(params)

    nmservice_service('nmservice', upgrade_type=upgrade_type, action='stop')

  def status(self, env):
    import status_params
    env.set_params(status_params)

    check_process_status(status_params.nmservice_history_server_pid_file)


  def get_component_name(self):
    return "nmservice-server"

  def pre_upgrade_restart(self, env, upgrade_type=None):
    import params

    env.set_params(params)
    if params.version and check_stack_feature(StackFeature.ROLLING_UPGRADE, params.version):
      Logger.info("Executing NMService Server Stack Upgrade pre-restart")
      conf_select.select(params.stack_name, "nmservice", params.version)
      stack_select.select("nmservice-server", params.version)

  def get_log_folder(self):
    import params
    return params.nmservice_log_dir

  def get_user(self):
    import params
    return params.nmservice_user

if __name__ == "__main__":
  NMServiceServer().execute()
