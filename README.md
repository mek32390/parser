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
        
Command line Usage: python3 parser.py [arguments[.html|.csv|.txt]]

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

