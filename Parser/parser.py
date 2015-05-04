"""
@Author: Brian Lovelace
@name: parser.py
Usage:  parser.py [<filename.html> | <filename.csv>]*
Usage:  parser.py -d [/HtmlDirectoryPath]^+ [/CsvDumpDirectory] 
Extracts selected data from html files and writes it to csv files
"""
import sys, os, datetime
#sys.path.append(os.getcwd())

#from Parser.Parser.fileParser import parse, can_parse, setup_parser, clean_env, NonexistantKeyError, UnparseableFileError, UnsetFileParserError
from Parser.fileParser import parse, can_parse, make_parsingPackage, NonexistantKeyError, UnparseableFileError, UnsetFileParserError
#from os.path.join(os.getcwd(), 'Parser') import parse, can_parse, setup_parser, clean_env, NonexistantKeyError, UnparseableFileError, UnsetFileParserError 
import configparser


#Variables are used when the module is being run as a 
#main script. 
_main = False
_error = ''
_parser = None
_defaultConfig = os.path.join(os.path.dirname(__file__), 'config.ini')




"""
Checks for errors in the command line for a script
usage containing the -d flag
Should only be called from __Main__
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
Should only be called from __Main__
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
Appends all new entries to the designated .csv file. If file does
not exist it is created.
@entries: A list of entry objects
"""
def _writeCSV(entries, parser, CSVfilename = None):
    header = ''
    currentLines = {}

    for i in range(len(parser.WRITTEN_KEYWORDS)):
        header += parser.WRITTEN_KEYWORDS[i]
        if i != (len(parser.WRITTEN_KEYWORDS)-1):
            header += ', '
        else:
            header += '\n'

    csvFile = _createCSVFile(entries, parser, CSVfilename)
    csvFile.seek(0,0)
    for line in csvFile:
        currentLines[line] = True
    if header not in currentLines:
        currentLines[header] = True
        csvFile.write(header)
    
    if entries is not None:
        for e in entries:
            if restricted(e, parser):
                continue
            i = 0
            newEntry = ''
            for k in parser.WRITTEN_KEYWORDS:
                if e[k] is not None:
                    newEntry += e[k]
                if i != (len(parser.WRITTEN_KEYWORDS) - 1):
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
def _createCSVFile(entries, parser, CSVfilename):
    global _error#, CsvDump

    filename = ''

    if not os.path.isdir(parser.CsvDump):
        os.makedirs(parser.CsvDump)
    filepath = parser.CsvDump
    
    try:
        if CSVfilename is None:
            if len(entries) > 0:
                check = entries[0][parser.FILENAME_BASE]
                if check is not None:
                    filename += check
                if len(filename) > 0:
                    filename += '_'
        else:
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
Checks for any restrictions
"""
def restricted(entry, parser):
    restricted = False

    for k in entry.keys():
        #Allowed values
        if k in parser.ENTRY_RESTRICTIONS.keys():
            restricted = True
            for v in parser.ENTRY_RESTRICTIONS[k]:
                if entry[k] == v:
                    restricted = False
                    break
        #Restricted Values
        if ('~' + k) in parser.ENTRY_RESTRICTIONS.keys():
            for v in parser.ENTRY_RESTRICTIONS[('~' + k)]:
                if entry[k] == v:
                    restricted = True
    return restricted

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
Should only be called from __Main__()
"""
def _handleFlags(argv):
    global _error#, Logger
    
    if len(argv) < 1:
        _error = 'No command line arguments'
        raise BadInputError()

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
            _parser.toggle_verbose()
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
            _parser.set_csv_dump(argv[i+1])
            argv.pop(i)
            argv.pop(i)
            removed = True
            c_flag = True
        elif argv[i] == '-l':
            if l_flag:
                _error = 'Log should not be set twice'
                raise BadInputError()
            elif i == (len(argv) - 1):
                _parser.Logger = None
            elif argv[i+1].split('.')[len(argv[i+1].split('.'))-1] == 'txt':
                _parser.set_logger(argv[i+1])
                argv.pop(i)
            else:
                _parser.Logger = None
            argv.pop(i)
            removed = True
            l_flag = True
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
Parses files given by the command line. Arguments are validated
and corresponding csv files are written.
Should only be called be __Main__
"""
def _parseCommandLine(argv):#, parser=_parser):
    global _error#, Csv_Dump
    #May cause issues setting a new CSVDUmp
    CsvDump = _parser.CsvDump
    message = ''
    checkCommandLineArgs(argv)
    _parser.set_csv_dump(CsvDump)    
    
    fileTypes   = getFileTypes(argv)
    htmlfiles   = fileTypes['html']
    csvfiles    = fileTypes['csv']    
    _parser.parse_files(htmlfiles, csvfiles)

"""
Parses all files in the directory, and places them in the
CsvDump.
Should only be called by __Main__
"""
def _parseDirectories(argv):
#    argv.pop(0)
    checkParseDirectoriesArgs(argv)
    directories = getFileTypes(argv)['other']
    for d in directories:
        _parser.parse_directory(os.path.abspath(d))
     
"""
Adds a message to a logger and prints it to stdio
if verbose mode is active. Newlines are added automatically.
"""
def addMessage(message, logOnly=False, parser=None):
    if parser.VERBOSE and _main and not logOnly:
        print(message)
#uses Logger
    if parser.Logger is not None:
        logFile = open(parser.Logger, 'a')
        logFile.write(message + '\n')
        logFile.close()

def parseKeywords(config, section, key):
    keywords = []
    try:
        val = config[section][key]
        for w in val.strip('\n\t ').split('\n'):
            keywords.append(w)
    except KeyError as e:
        pass
    return keywords
    

def parseRestrictions(config, section):
    restrictions = {}
    section = config[section]
    try:
        for k in section:
            words = []
            vals = section[k]
            for w in vals.strip('\n\t ').split('\n'):
                if w != '~None':
                    words.append(w.strip('\n\t '))
                else:
                    words.append(None)
            restrictions[k] = words
    except KeyError as e:
        pass
    return restrictions
    
def parseValue(config, section, key):
    val = '~None'
    try:
        val = config[section][key]
    except KeyError as e:
        pass
    if val == '~None':
        return None
    else:
        return val

def verifyDefaultValues(parser):
    global _error
    
    message = ''
    try:
        if not isinstance(parser.PARSED_KEYWORDS, list):
            message = 'parsed_keywords not properly set'
            raise BadConfigError(message)

        if not isinstance(parser.WRITTEN_KEYWORDS, list):
            message = 'parsed_keywords not properly set'
            raise BadConfigError(message)
        else:
            for w in parser.WRITTEN_KEYWORDS:
                if w not in parser.PARSED_KEYWORDS:
                    message = 'Value ' + w + ' is not parsed from the file'
                    raise BadConfigError(message)
        if not isinstance(parser.ENTRY_RESTRICTIONS, dict):
            message = 'ENTRY_RESTRICTIONS not properly set'
            raise BadConfigError(message)
        if not isinstance(parser.FILENAME_BASE, str):
            message = 'FILENAME_BASE not properly set'
            raise BadConfigError(message)
        elif parser.FILENAME_BASE not in parser.PARSED_KEYWORDS:
            message = 'FILENAME_BASE is not parsed'
            raise BadConfigError(message)
        if not isinstance(parser.CsvDump, str):
            message = 'CSV_DUMP not properly set'
            raise BadConfigError(message)

    except BadConfigError as e:
        _error = message
        raise e
"""
Returns the instance of ConfigParser that is used as the
default configuration for this parser. 
"""
def default_config():
    config = configparser.ConfigParser()
    config.read(_defaultConfig)
    return config
    
"""
Extracts a dictionary mapping keywords to parsed data
@f: An open file
@return: A list of Entries
"""
def get_entries(parsingPackage):
    global _error
    try:
        return parse(parsingPackage)
    except UnparseableFileError as e:
        _error = 'No schema available to parse ' + parsingPackage.filename
        raise e

"""
Returns the parsing package used by the fileParser module to
parse a file.
@parser: parser object
@opened: Opened file header
"""
def get_parsingPackage(parser, opened):        
    return make_parsingPackage(parser.PARSED_KEYWORDS, opened)
      
"""
A parser object. Gives user access to the public functions in 
this module
"""
class Parser():
    def __init__(self, config=_defaultConfig):
        self._currentConfig = None
        self.FILENAME_BASE = None  
        self.PARSED_KEYWORDS = []
        self.WRITTEN_KEYWORDS = []
        self.ENTRY_RESTRICTIONS = {}
        self.VERBOSE = False
        self.Logger  = None
        #ErrorLog= None
        self.CsvDump = None
        self.parsingPackage = None
		
        try:
            self.apply_config(config)
            verifyDefaultValues(parser=self)
            
        except Exception as e:
            self.close_parser()
            raise e
            
    def __setup__(self, f):
        global _error
        try:
            self.parsingPackage = get_parsingPackage(self, open(f))
        except NonexistantKeyError as e:
            _error = 'The selected keys cannot be parsed'
            raise e
        except IOError as e:
            _error = 'The selected keys cannot be parsed'
            raise e
    
    def close_parser(self):
        self.FILENAME_BASE = None  
        self.PARSED_KEYWORDS = []
        self.WRITTEN_KEYWORDS = []
        self.ENTRY_RESTRICTIONS = {}
        self.VERBOSE = False
        self.Logger  = None
        #self.ErrorLog= None
        self.CsvDump = None
        self._currentConfig = None
        self.parsingPackage = None

    def set_logger(self, logname):
        global _error

        fname = logname.split('.')
        if len(fname) > 1:
            t = fname[len(fname) - 1]
            if t != 'txt':
                _error = 'Error log should be a text file'
                raise BadInputError()
        self.Logger = logname

    def apply_config(self, configFile):
        config = None
        if isinstance(configFile, configparser.ConfigParser):
            config = configFile
        else:     
            config = configparser.ConfigParser()
            config.read(configFile)
        self._currentConfig = config
        
        self.PARSED_KEYWORDS = parseKeywords(config, 
                                            'PARSED_KEYWORDS',
                                            'parsed_keywords'
                                          )
        self.WRITTEN_KEYWORDS = parseKeywords(config,
                                          'WRITTEN_KEYWORDS',
                                          'WRITTEN_keywords'
                                          )
        self.ENTRY_RESTRICTIONS = parseRestrictions(config,
                                         'ENTRY_RESTRICTIONS')
        vTemp = parseValue(config, 'VALUES', 'VERBOSE')
        if vTemp == "True": 
            self.VERBOSE = True
        else:
            self.VERBOSE = False
        self.Logger = parseValue(config, 'VALUES', 'Logger')
        self.FILENAME_BASE = parseValue(config, 'VALUES', 'FILENAME_BASE')
        self.CsvDump = parseValue(config, 'VALUES', 'CSV_DUMP')
        
    def parse_files(self, htmlfiles, csvfiles=[]):
        i = 0
        for f in htmlfiles:
            try:
                if len(csvfiles) > i:
                    parsed = self.parse_and_write(f, csvfiles[i])
                else:
                    parsed = self.parse_and_write(f)
                if not parsed:
                    i += 1
                    raise Exception()
                i += 1
                message = str(i) + ': Parsed ' + f
                addMessage(message, parser=self)
            except Exception as e:
                message = str(i) + ': Could not parse ' + f
                addMessage(message, parser=self)
                if len(_error) == 0:
                    raise e

    def parse_and_write(self, htmlFile, CsvFile=None):       
        try:
            self.__setup__(htmlFile)
            entries = get_entries(self.parsingPackage)
            if entries is None:
                #Won't need this
#                clean_env()
                return False
            else:
                _writeCSV(entries, self, CSVfilename=CsvFile)
                #Won't need this
#                clean_env()
                return True
            
        except Exception as e:
            #won't need this anymore
#            clean_env()
            raise e
            
    def parse_directory(self, directory):
        files = os.listdir(directory)
        htmlfiles = getFileTypes(files)['html']

        i = 1
        for f in htmlfiles:
            try:
                self.parse_and_write(os.path.join(sys.path[0], directory, f))
                message = str(i) + ':\tParsed ' + f
                addMessage(message, parser=self)
            except Exception as e:
                message = str(i) + ':\tCould not parse ' + f
                addMessage(message, parser=self)
                if len(_error) == 0:
                    raise e
            i += 1
    
    def set_csv_dump(self, directory):        
        if not os.path.isabs(directory):
            directory = os.path.abspath(directory)
        self.CsvDump = directory
        
    def toggle_verbose(self):
        self.VERBOSE = not self.VERBOSE
    
    def is_verbose(self):
        return self.VERBOSE
        
    def get_config(self):
        return self._currentConfig    
        
    def is_set(self):
        return self._parserSet
        
"""
        self.close_parser   = close_parser
        self.set_logger     = set_logger
        self.apply_config   = apply_config
        self.parse_files    = parse_files
        self.parse_and_write= parse_and_write
        self.set_csv_dump   = set_csv_dump
        self.toggle_verbose = toggle_verbose
        self.is_set         = is_set
        self.get_config     = get_config
        self.is_verbose     = is_verbose
"""

"""
Main function. Only run when script is run as main program.
Main handles errors that script is designed to catch,
it allows all others to pass.
"""
def __main__():
    global _parser

    try:
        _parser = Parser(os.path.abspath(os.path.join(sys.path[0],'config.ini')))
        argv = sys.argv
        argv.pop(0)
  
        argv = _handleFlags(argv)
        message = ''   
        for i in range(25):
            message += '_'
        message += '\nNew entries added ' + str(datetime.datetime.now())
        addMessage(message, logOnly=True, parser=_parser)

        if argv[0] == '-d':
            argv.pop(0)
            _parseDirectories(argv)
        else:
            _parseCommandLine(argv)
    except Exception as e:
        if len(_error) > 0:
            sys.stderr.write("Usage: " + _error + "\n")
            sys.exit(1)
        else:
            raise e

#Custom Exception raised for bad input
class BadInputError(Exception):
    pass
class BadConfigError(Exception):
    def __init__(self, message):
        super()
        self.message = message
    def __repr__(cls):
        return cls.message + '\n'

if __name__ == "__main__":
    _main = True
    __main__()

