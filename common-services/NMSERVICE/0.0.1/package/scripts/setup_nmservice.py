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
import fileinput
import shutil
import os
from resource_management import *
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management.core.logger import Logger
from resource_management.core import shell
from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions import StackFeature

def setup_nmservice(env, type, upgrade_type = None, action = None):
  import params

  Directory([params.nmservice_pid_dir, params.nmservice_log_dir],
            owner=params.nmservice_user,
            group=params.user_group,
            mode=0775,
            create_parents = True
  )
  if type == 'server' and action == 'config':
    params.HdfsResource(params.nmservice_hdfs_user_dir,
                       type="directory",
                       action="create_on_execute",
                       owner=params.nmservice_user,
                       mode=0775
    )
    params.HdfsResource(None, action="execute")

  PropertiesFile(format("{nmservice_conf}/nmservice-defaults.conf"),
    properties = params.config['configurations']['nmservice2-defaults'],
    key_value_delimiter = " ",
    owner=params.nmservice_user,
    group=params.nmservice_group,
    mode=0644
  )

  # create nmservice-env.sh in etc/conf dir
  File(os.path.join(params.nmservice_conf, 'nmservice-env.sh'),
       owner=params.nmservice_user,
       group=params.nmservice_group,
       content=InlineTemplate(params.nmservice_env_sh),
       mode=0644,
  )

  #create log4j.properties in etc/conf dir
  File(os.path.join(params.nmservice_conf, 'log4j.properties'),
       owner=params.nmservice_user,
       group=params.nmservice_group,
       content=params.nmservice_log4j_properties,
       mode=0644,
  )

  #create metrics.properties in etc/conf dir
  File(os.path.join(params.nmservice_conf, 'metrics.properties'),
       owner=params.nmservice_user,
       group=params.nmservice_group,
       content=InlineTemplate(params.nmservice_metrics_properties),
       mode=0644
  )

  effective_version = params.version if upgrade_type is not None else params.stack_version_formatted
  if effective_version:
    effective_version = format_stack_version(effective_version)
