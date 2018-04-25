#!/usr/bin/env python
# Author: 'JiaChen'

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EasyMonitor.settings")
    from utils.management import execute_from_command_line
    execute_from_command_line(sys.argv)
