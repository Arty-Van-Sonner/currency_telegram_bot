import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], 'classes/exceptions'))

from error_connection_sqlite import ErrorConnectionSQLite
from error_in_string_from_userer import ErrorInStringFromUser
