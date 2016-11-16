#!/usr/bin/python
import os
import sys
import logging
logging.basicConfig(stream=sys.stderr)


sys.path.insert(0, '/var/www/demo/')
os.chdir("/var/www/demo")

from manage import app as application


if __name__ == "__main__":
    application.run(host='0.0.0.0')
