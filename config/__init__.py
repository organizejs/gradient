"""
This loads a configuration according to
the FLASK_CONFIG environmental variable.
For instanec, if `FLASK_CONFIG=dev`, it
load `config/dev.py` (this is the default).
In staging and production, you should set `FLASK_CONFIG=env`
so that it loads `config/env.py`, which loads configuration
variables from the environment.
"""

import os
import importlib

mod = os.environ.get('FLASK_CONFIG', 'dev')
mod = importlib.import_module('.{}'.format(mod), 'config')
Config = mod.Config
