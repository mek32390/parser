# parser

Parser is an html script that can be used to parse html
files from directories or from the command line into 
customoizable csv files. At the moment, current features
can be reviewed at the Trello project tracking board.

Below is a description of the script usage:

Flags: 
    -v toggles verbose mode
    
    -l [file.txt] sets a logger file to store
    
        verbose messages
        
    -c [directory] Sets parser to dump csv files
    
        into the specified directory
        
    -d [directories[]] Sets parser to search for html files
    
        in the specified directories.
        

Usage: python3 parser.py [arguments[.html|.csv|.txt]]

Note:

This is an initial commit so that the parser can be used in
the following week. There may still be quite a few bugs, as
the command line parsing features were just updated and are
not thoroughly tested. Please contact me with any issues 
that are discovered through regular usage.

Thank you.
