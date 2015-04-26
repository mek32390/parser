# parser
Parser is a python3 script that parses information from 
html files into csv files. It reads a default config.ini
file to initialize its starting settings. From there, 
command line flags or calls to the public apply_config
function.

Below is a description of the script usage:

Flags: 
    -v toggles verbose mode. Can be placed anywhere in the 
       command line arguments.
    
    -l [file.txt] sets a logger file to store verbose messages.
       Can be placed anywhere in the command line arguments.
        
    -c [directory] Sets parser to dump csv files
       into the specified directory. Can be placed anywhere
       in the command line argument.
        
    -d [directories[]] Sets parser to search for html files
       in the specified directories. Must be placed before and
       arguments.
        
Command Line Usage: python3 parser.py [arguments[.html|.csv]
    Arguments and can be given in any order. 
    Data parsed form html files will be written into the next
    given csv file, or one will created based on the config file.

External Application Usage:
    Call parser.Parser(config) constrcutor. 
    Parser public methods:
        close_parser: Cleans the parser environment
        set_logger: Sets the parser's logger
        apply_config: Applies a new configuration file to the parser
        parse_files: Parses the html files given
        parse_and_write: Parses and html and writes it to a csv file
        set_csv_dump: sets the directory that parser will place csv files
        toggle_verbose: Toggles verbose mode
        is_set: Checks if a the parser is set up for use
        default_config: Gets a copy of the default and working config object

Config.ini file:
    The parser sets its default settings based on the given config.ini file.
    When using a .ini to initialize the parser, if certain values are not
    set the parser will not allow the user to continue.

    Required Fields:
        CSV_DUMP in  [VALUES]
            Path to the directory where created csv files should be placed
        FILENAME_BASE in [VALUES]
            The parsed keyword to base the name of the csv file on.
        parsed_keywords in [PARSED_KEYWORDS] 
            Determined the keywords to be parsed
        written_keywords in [WRITTEN_KEYWORDS]
            Determines the keywords and their order to be written to the csv files
        [ENTRY_RESTRICTIONS] must be defined
            Determines any restrictions that should be made when adding a row to a
            csv file. A key with a "~" will restrict an row from having the listed 
            values. A key without it will restrict rows without any of the listed
            values.
            Format:
                <keyword>:  <allowed val>
                            <allowed val>
                ~<keyword>: <disallowed val>
                            <disallowed val>
                            
    Optional fields:
        VERBOSE in [VALUES]
            Sets the default status of verbose mode.
        LOGGER in [VALUES]
            Sets the name of the verbosity logger. A value
            of "~None" will disable the logger.
        ERROR_LOG in [VALUES]
            Not yet implemented.
        
    




