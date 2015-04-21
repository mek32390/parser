"""
@Author: Brian Lovelace
@name: parser.py
Usage:  parser.py [<filename.html> | <filename.csv>]*
Usage:  parser.py -d [/HtmlDirectoryPath]^+ [/CsvDumpDirectory] 
Extracts selected data from html files and writes it to csv files
"""
import sys, os.path, datetime
sys.path.append(os.path.join(sys.path[0] + '/Parser'))
from Parser.fileParser import parse, can_parse, setup_parser, clean_env, NonexistantKeyError, UnparseableFileError, UnsetFileParserError

#True if script is Main
_main = False
_error = ''

#if no csv file is given, one will be created based on the mapping of
#FILENAME_BASE on the first parsed entry. If FILENAME_BASE maps to 
#None, the file will be names "class_list.csv".
FILENAME_BASE = 'course'   

DEFAULT_KEYWORDS = ['first', 'email', 'last', 'course', 'instructor']
currentKeywords = DEFAULT_KEYWORDS


VERBOSE = False
Logger  = 'Logger.txt'
ErrorLog= 'Errors.txt'
CsvDump = 'Csv_Dump'


"""
Checks for errors in the command line for a script
usage containing the -d flag
"""
def checkParseDirectoriesArgs(argv):
    global _error
    
    htmlfiles   = []
    csvfiles    = []
    textfiles   = []
    directories = []
    fileTypes   = getFileTypes(argv)    
    htmlfiles   = fileTypes['html']
    csvfiles    = fileTypes['csv']
    textfiles   = fileTypes['txt']
    directories = fileTypes['other']
    if len(directories) < 1:
        _error = 'No directories to parse'
        raise BadInputError()
    if len(htmlfiles) > 0:
        _error = 'Cannot parse individual html files with -d flag'
        raise BadInputError()
    if len(csvfiles) > 0:
        _error = 'Cannot specify csv files to write to with -d flag'
        raise BadInputError()
    if len(textfiles) > 0:
        _error = 'Cannot yet specify csv files to write to with -d flag'
        raise BadInputError()
    for d in directories:
        if not os.path.isdir(d):
            _error = 'Cannot find directory ' + d
            raise BadInputError()

"""
Checks for errors in the arguments sent to the script
@args argv: Arguments sent to the script.
"""
def checkCommandLineArgs(argv):
    global _error

    htmlfiles   = []
    csvfiles    = []
    textfiles   = []
    directories = []
    if len(argv) < 1:
        _error = 'Incorrect number of arguments'
        raise BadInputError()

    fileTypes = getFileTypes(argv)
    htmlfiles   = fileTypes['html']
    csvfiles    = fileTypes['csv']
    textfiles  = fileTypes['txt']
    directories = fileTypes['other']

    if len(csvfiles) > len(htmlfiles):
        _error = 'Too many .csv files'
        raise BadInputError()
    if len(textfiles) > 1:
        _error = 'Only one file can be set as the parser\'s log'
        raise BadInputError()
    if len(directories) > 0:
#        _error = 'Parser can only dump csv files into a single directory'
        _error = 'Use -c flag to specify a csv dump directory'
        raise BadInputError()

    fil = None
    try: 
        for f in htmlfiles:
            fil = f
            open(f)
    except IOError as e:
        _error = 'Cannot open file ' + fil
        raise e
    except Exception as e:
        _error = 'An unexpected error occurred: ' + e
        raise e
    return True

"""
Sets up the parser module to parse the file
@arg f: a file
"""
def setup(f):
    global _error
    try:
        opened = open(f)
        setup_parser(currentKeywords, opened)
        return opened
    except NonexistantKeyError as e:
        _error = 'The selected keys cannot be parsed'
        raise e
    except IOError as e:
        _error = 'The selected keys cannot be parsed'
        raise e
    

"""
Extracts a dicitonary mapping keywords to parsed data
@f: An open file
@return: A list of Entries
"""
def getEntries(f):
    global _error
    try:
        entries = parse()
        return entries
    except UnparseableFileError as e:
        _error = 'No schema available to parse ' + f.name
        raise e

"""
Appends all new entries to the designated .csv file. If file does
not exist it is created.
@entries: A list of entry objects
"""
def writeCSV(entries, CSVfilename = None):
    header = ''
    currentLines = {}

    for i in range(len(currentKeywords)):
        header += currentKeywords[i]
        if i != (len(currentKeywords)-1):
            header += ', '
        else:
            header += '\n'

    csvFile = createCSVFile(entries, CSVfilename)
    csvFile.seek(0,0)
    for line in csvFile:
        currentLines[line] = True
    if header not in currentLines:
        currentLines[header] = True
        csvFile.write(header)
    
    if entries is not None:
        for e in entries:
            i = 0
            newEntry = ''
            for k in currentKeywords:
                if e[k] is not None:
                    newEntry += e[k]
                if i != (len(currentKeywords) - 1):
                    newEntry += ', '
                else:
                    newEntry += '\n'
                i += 1
            if newEntry not in currentLines:
                currentLines[newEntry] = True
                csvFile.write(newEntry)
        
"""
Creates a file with the correct name for the parsed html file.
"""
def createCSVFile(entries, CSVfilename):
    global _error, CsvDump

    filename = ''
    if not os.path.isdir(os.path.join(sys.path[0], CsvDump)):
        os.makedirs(os.path.join(sys.path[0], CsvDump))
    filepath = os.path.join(sys.path[0], CsvDump)
    

    try:
        if CSVfilename is None:
            if len(entries) > 0:
                check = entries[0][FILENAME_BASE]
                if check is not None:
                    filename += check
                if len(filename) > 0:
                    filename += '_'
        else:
#            filepath = os.path.join(filepath, CSVfilename)
            filename = CSVfilename           
    except KeyError as e:
        _error = 'FILENAME_BASE must be listed as a keyword'
        raise e
    filepath = os.path.join(filepath, filename)

    if CSVfilename is not None:
        return open(filepath, 'a+')
    else:
        filepath += 'class_list.csv'
        return open(filepath, 'w+')

"""
Seperates the given file names into lists of html, csv,
and other file types.
@arg files: List of file names
@return Dictionary mapping file types to lists of files
        of that type. Dictionary keys are: 'html', 'csv',
        'directory', and 'other'.
"""
def getFileTypes(files):
    htmlfiles   = []
    csvfiles    = []
#    directories = []
    textfiles   = []
    other       = []

    i = 0    
    while i < len(files):
        parts = files[i].split('.')
        if parts[len(parts)-1] == 'html':
            htmlfiles.append(files[i])
        elif parts[len(parts)-1] == 'csv':
            csvfiles.append(files[i])
        elif parts[len(parts)-1] == 'txt':
            textfiles.append(files[i])   
 #       elif os.path.isdir(files[i]):
 #           directories.append(files[i])
        else:
            other.append(files[i])
        i += 1
    
    return  {
            'html': htmlfiles,
            'csv': csvfiles,
#            'directory': directories,
            'txt': textfiles, 
            'other': other
            }

"""
Scans the arguments and looks for flags and their
corresponding variables. Most flags are handled 
and removed from argv. If -d is present, it will
become the first element of argv. 
"""
def handleFlags(argv):
    global _error

    v_flag = False
    l_flag = False
    d_flag = False
    c_flag = False
    others = False
    i = 0
    while i < len(argv):
        removed = False
        if argv[i] == '-v':
            if v_flag:
                _error = 'Verbose should not be set twice'
                raise BadInputError()
            toggle_verbose()
            argv.pop(i)
            removed = True
            v_flag = True
        elif argv[i] == '-c':
            if c_flag:
                _error = 'Csv files can only be dumped into one directory'
                raise BadInputError()
            elif i == (len(argv) - 1):
                _error = 'No Csv dump directory given'
            elif os.path.exists(argv[i+1]):
                if not os.path.isdir(argv[i+1]):
                    _error = 'Csv dump is not a directory'
                    raise BadInputError()
            set_csv_dump(argv[i+1])
            argv.pop(i)
            argv.pop(i)
            removed = True
            c_flag = True
        elif argv[i] == '-l':
            if l_flag:
                _error = 'Log should not be set twice'
                raise BadInputError()
            elif i == (len(argv) - 1):
                Logger = None
#                _error = 'No log file name given'
#                raise BadInputError()
            elif argv[i+1].split('.')[len(argv)-1] == 'txt':
                if not os.path.isfile(argv[i+1]):
                    _error = 'Log is not a file'
                    raise BadInputError()
                else:
                    set_error_log(argv[i+1])
                    argv.pop(i)
            else:
                Logger = None
            argv.pop(i)
            removed = True
            l_flag = True
        """Sets error log
         elif argv[i] == '-e':
            if l_flag:
                _error = 'Log should not be set twice'
                raise BadInputError()
            elif i == (len(argv) - 1):
                Logger = None
#                _error = 'No log file name given'
#                raise BadInputError()
            elif argv[i+1].split('.')[len(argv)-1] == 'txt':
                if not os.path.isfile(argv[i+1]):
                    _error = 'Log is not a file'
                    raise BadInputError()
                else:
                    set_error_log(argv[i+1])
                    argv.pop(i)
            else:
                Logger = None
            argv.pop(i)
            removed = True
            l_flag = True
        """
        elif argv[i] == '-d':
            if d_flag:
                _error = 'Directory parsing mode should not be set twice'
                raise BadInputError()
            if others:
                _error = 'Directory parsing flag should come before any parser arguments'
                raise BadInputError()
            d_flag = True
        else:
            others = True
        if not removed:
            i += 1
    return argv

"""
Toggles the parser's verbose setting
"""
def toggle_verbose():
    global VERBOSE
    VERBOSE = not VERBOSE


"""
Sets a .txt file to be the parser's error log
"""
def set_error_log(errorLog):
    global _error, Log

    fname = errorLog.split('.')
    if len(fname) > 1:
        t = fname[len(fname) - 1]
        if t != 'txt':
            _error = 'Error log should be a text file'
            raise BadInputError()
    Log = errorLog

"""
Sets the given directory to be the directory that
the parser places all parsed .csv files into.
"""
def set_csv_dump(directory):
    global CsvDump
    
    if not os.path.isabs(directory):
        directory = os.path.abspath(directory)
    CsvDump = directory
    if not os.path.isdir(os.path.join(sys.path[0], CsvDump)):
        os.makedirs(os.path.join(sys.path[0], CsvDump))    
    
"""
Parses the files and writes them to csv files
@argv Arguments to parse.
"""
def parse_and_write(htmlFile, CsvFile=None):       
    try:
        opened = setup(htmlFile)
        entries = getEntries(opened)
        if entries is None:
            clean_env()
            return False
        else:
            writeCSV(entries, CsvFile)
            clean_env()
            return True
        
    except Exception as e:
        clean_env()
        raise e


"""
Parses files given by the command line. Arguments are validated
and corresponding csv files are written.
"""
def parseCommandLine(argv):
    global _error, CsvDump

    checkCommandLineArgs(argv)
    set_csv_dump(CsvDump)    
    
    fileTypes   = getFileTypes(argv)
    htmlfiles   = fileTypes['html']
    csvfiles    = fileTypes['csv']    
    verbLog     = None        
    logFile     = None

    if len(fileTypes['other']) > 0:
        verbLog = os.path.join(sys.path[0], CsvDump, fileTypes['other'][0])

    if verbLog is not None:
        if os.path.isfile(verbLog):        
            logFile = open(verbLog, 'a')
        else:
            logFile = open(verbLog)
            
        for i in range(25):
            logFile.write("_")        
        logFile.write('\nNew entries added ' + str(datetime.datetime.now()) + '\n')           
    parse_files(htmlfiles, csvfiles, logFile)


"""
Parses all files in the directory, and places them in the
CsvDump. 
"""
def parseDirectories(argv):
#    argv.pop(0)    
    checkParseDirectoriesArgs(argv)
    directories = getFileTypes(argv)['other']
    for d in directories:
        parse_directory(os.path.abspath(d))

        
def parse_directory(directory, logFile=None):
    files = os.listdir(directory)
    htmlfiles = getFileTypes(files)['html']
#    parse_files(htmlfiles, logFile=logFile)
    i = 1
    for f in htmlfiles:
        try:
            parse_and_write(os.path.join(sys.path[0], directory, f))
            message = str(i) + ': Parsed ' + f
            addMessage(message, logFile)
        except Exception as e:
            message = str(i) + ': Could not parse ' + f
            addMessage(message, logFile)
            if len(_error) == 0:
                raise e
        i += 1

"""
Parses a list of htmlfiles, adding them to their corresponding
csv file if given.
"""
def parse_files(htmlfiles, csvfiles=[], logFile=None):
    i = 0
    for f in htmlfiles:
        try:
            if len(csvfiles) > i:
                parsed = parse_and_write(f, csvfiles[i])
            else:
                parsed = parse_and_write(f)
            if not parsed:
                i += 1
                raise Exception()
            i += 1
            message = str(i) + ': Parsed ' + f
            addMessage(message, logFile)
        except Exception as e:
            message = str(i) + ': Could not parse ' + f
            addMessage(message, logFile)
            if len(_error) == 0:
                raise e

"""
Adds a message to a logger and prints it to stdio
if verbose mode is active. Newlines are added automatically.
"""
def addMessage(message, logFile=None):
    if logFile is not None:
        logFile.write(message + '\n')
    if VERBOSE and _main:
        print(message)

"""
Main function. Only run when script is run as main program.
Main handles errors that script is designed to catch,
it allows all others to pass.
"""
def __main__():
    global _error

    argv = sys.argv
    argv.pop(0)
    try:
        argv = handleFlags(argv)
        if argv[0] == '-d':
            argv.pop(0)
            parseDirectories(argv)
        else:
            parseCommandLine(argv)
    except Exception as e:
        if len(_error) > 0:
            sys.stderr.write("Usage: " + _error + "\n")
            sys.exit(1)
        else:
            raise e

#Costum Exception raised for bad input
class BadInputError(Exception):
    pass

if __name__ == "__main__":
    _main = True
    __main__()

