#!/usr/bin/env python3
# Copyright (c) 2014 Pawel Rozlach
# Copyright (c) 2014 Zadane.pl sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import shlex
import sys
import subprocess
import platform
import os

UNKNW = 3
CRIT = 2
WARN = 1
OK = 0

CRM_RESOURCE_LOCATE = "/usr/bin/sudo " + \
                      "/usr/sbin/crm_resource --quiet --locate --resource {0}"


def verify_binary(path):
    if not os.path.isfile(path):
        print("CMR location script cannot access path {0}.".format(path))
        sys.exit(UNKNW)
    if not os.access(path, os.X_OK):
        print("Binary {0} is not executable.".format(path))
        sys.exit(UNKNW)
    # All OK

if len(sys.argv) < 3:
    print("Unsuficcient number of arguments provided.")
    print("Usage:", file=sys.stderr)
    print(sys.argv[0] + " <crm resource name to follow> "
          "<nagios check with its args>", file=sys.stderr)
    sys.exit(UNKNW)

locate_cmd = shlex.split(CRM_RESOURCE_LOCATE.format(sys.argv[1]))

# Verify sudo:
verify_binary(locate_cmd[0])

# Verify crm_resource:
verify_binary(locate_cmd[1])

# Verify nagios check path:
verify_binary(sys.argv[2])

try:
    location = subprocess.check_output(locate_cmd,
                                       shell=False,
                                       universal_newlines=True,
                                       stderr=subprocess.STDOUT)
except subprocess.CalledProcessError as e:
    print("crm_resource command exited with status {0} and text: {1}".format(
        e.returncode, e.output))
    sys.exit(UNKNW)

location = location.rstrip()

if location != platform.node():
    print("Resource is on node {0}, skipping nagios check execution".format(
        location))
    sys.exit(OK)

# we own the resource, we have to check it

try:
    output = subprocess.check_output(sys.argv[2:],
                                     shell=False,
                                     universal_newlines=True,
                                     stderr=subprocess.STDOUT)
except subprocess.CalledProcessError as e:
    print(e.output)
    sys.exit(e.returncode)

print(output)
sys.exit(0)
