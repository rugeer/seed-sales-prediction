#!python3
# -*- coding: utf-8 -*-
import os
from os.path import expanduser

home = expanduser("~")

sqlite_path = os.path.join(home, "seed-predictions.db")

DATABASE = f"sqlite:///{sqlite_path}"
DEBUG = False
EXPECTED_MONTHLY_SALES_VARIANCE = 40  # TODO: check with Fanda to find optimal value
