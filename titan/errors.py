from enum import Enum

class TitanErrors(Enum):

    PARSE_BAD_OPTION = "unknown option"
    PARSE_OPTION_FAILURE = "unable to parse option" 
    NON_EXISTENT_FILE = "file does not exist or could not be found"
