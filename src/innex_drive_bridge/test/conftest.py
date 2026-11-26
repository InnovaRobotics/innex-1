"""Keep ROS tests in a process-specific domain away from normal rover traffic."""

import os

os.environ['ROS_DOMAIN_ID'] = str(201 + os.getpid() % 20)
