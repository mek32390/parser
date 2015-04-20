import sys, traceback
from bs4 import BeautifulSoup
import schemas as sch


RAISE_ERRORS = False

#List of all imported schemas
schemas = []

#Schema that the current file is using
schema = None
#List of the information that is to be extracted from this file
keywords = []
#Soup is the BeautifulSoup object associated with the open(filename)
soup = None
filename = ''

"""
Resets FileReader to its starting set, so that it is ready to parse
a new file.
"""
def clean_env():
    global keywords, schema, soup, filename

    keywords= []
    schema  = None
    soup    = None
    filename = ''

"""
Sets the parser to search for the given keywords
in the file.
@keys: List of keywords to look for. Parser will use the keyword
    contents because it is a reserved.
@f: File to parse
@errors: Raises NonExistantKey error if Keyword is not found.
         Parser is reset.
"""
def setup_parser(keys, f):
    global soup, keywords, filename
    schemaKeys = sch.keywords

    for k in keys:
        if k in schemaKeys:
            if not (sch.reservedKeyword(k)):
                keywords.append(k)
        else:
            keywords = []
            raise NonexistantKeyError(k)
    soup = BeautifulSoup(f)
    filename = f.name


"""
Checks if the set file can be parsed by the script. 
If so, it sets the module up to parse the file
with an appropriate schema.
@setter: If true, module sets appropriate schema if found
@return: True if a schema exists to parse file
"""
def can_parse(setter=True):
    global schema
    if len(keywords) == 0 or soup is None:
        print("0 length")
        return False
    s = findSchema()
    if s is None:
        return False
    elif setter:
        schema = s
        return True
    else:
        return True
    
"""
Returns the Schema that will best parse the file
"""
def findSchema():
    global schema, keywords

    mySchema = None
    bestHits = 0

    for s in schemas:
        hits = 0
        schema = getattr(sch, s)()
        try:
            if not extractData('validation', soup):
                raise InvalidHtmlForSchemaError()
            contents = extractData('contents', soup)
            hits += 1
            if len(contents) > 0:
                for k in keywords:
                    data = extractData(k, contents[0])
                    hits += 1
        except Exception as e:
            hits = 0
#For debugging, errors can be raised            
            if RAISE_ERRORS:
                raise e
        if hits > bestHits:
            bestHits = hits
            mySchema = s 
        schema = None

    if mySchema is not None:
        return getattr(sch, mySchema)()
    else:
        print("No schema for file:", filename)
        return None

"""
Parses the file that the module was set to parse.
@return: List of Entries
"""
def parse():
    global keywords, schema

    if soup is None:
        raise UnsetFileParserError()
    if schema is None:
        if not can_parse():
            raise UnparseableFileError(filename)
    entries = []
    contents = extractData('contents', soup)

    for block in contents:
        entry = {}
        for k in keywords:
            try:
                data = extractData(k, block)
                entry[k] = data
            except Exception as e:
                entry[k] = None
        if entry is not None:
            entries.append(entry)
    return entries

"""
Extracts the data associated with the key that
is parsed from the soup block. Return type is
directly dependent on the key used to extract
the data.
"""
def extractData(key, block):
    global schema

    rules = schema.get_rules()
    if rules[key] is not None:
        data = rules[key](block)
        if safeToExtract(data):
            if isinstance(data, str):
                return data.strip('\n\t ')
            else:
                return data
        elif data != None:
            return data.text.strip('\n\t ') 
    return None

def safeToExtract(data):
    if isinstance(data, str):
        return True
    elif isinstance(data, list):
        return True
    elif isinstance(data, bool):
        return True
    else:
        return False


def findSchemas():
    global schemas
    schemas = sch.getSchemaDefinitions()

#Should be used for testing purposes only, as this
#module not design to be run as the main script
def __main__():
    pass


#The following are custom exceptions raised in this module.
class EmptySchemaMapError(Exception):
    pass
class UnsetFileParserError(Exception):
    pass
class NonexistantKeyError(Exception): 
    pass
class UnparseableFileError(Exception):
    pass
class BadSchemaMatchError(Exception):
    pass
class InvalidHtmlForSchemaError(Exception):
    pass

findSchemas()

if __name__ == "__main__":
    __main__()






