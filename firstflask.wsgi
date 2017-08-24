#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/catalog/flaskapp_menu/")

from firstflask import app as application
application.secret_key = 'aidencrestridge11545%&^'
