import sys
from bs4 import BeautifulSoup
#import Parser.Parser.schemas as sch
import Parser.schemas as sch


RAISE_ERRORS = False#True
SCHEMAS = []

class ParsingPackage():
    def __init__(self, f, keywords):
        self.schema = None
        self.filename = f.name
        self.keywords = keywords
        self.soup = BeautifulSoup(f)

"""
Returns an instance of ParsingPackage the fileParser module
can use to parse.
@keys: List of keywords to look for. Parser will use the keyword
    contents because it is a reserved.
@f: File to parse
@errors: Raises NonExistantKey error if Keyword is not found.
         Parser is reset.
"""
def make_parsingPackage(keys, f):
    schemaKeys  = sch.keywords
    keywords    = []
    for k in keys:
        if k in schemaKeys:
            if not (sch.reservedKeyword(k)):
                keywords.append(k)
        else:
            raise NonexistantKeyError(k)
    return ParsingPackage(f, keys) 

"""
Checks if the set file can be parsed by the script. 
If so, it sets the module up to parse the file
with an appropriate schema.
@setter: If true, module sets appropriate schema if found
@return: True if a schema exists to parse file
"""
def can_parse(package, setter=False):
    if len(package.keywords) == 0 or package.soup is None:
        return False
    s = findSchema(package)
    if s is None:
        return False
    elif setter:
        package.schema = s
        return True
    else:
        return True
    
"""
Returns the Schema that will best parse the file
"""
def findSchema(package):
    mySchema = None
    bestHits = 0

    for s in schemas:
        hits = 0
        package.schema = getattr(sch, s)()
        try:
            if not extractData('validation', package.soup, package.schema):
                raise InvalidHtmlForSchemaError()
            contents = extractData('contents', package.soup, package.schema)
            hits += 1
            if len(contents) > 0:
                for k in package.keywords:
                    try:
                        data = extractData(k, contents[0], package.schema)
                        if data != None:
                            hits += 1                     
                    except Exception as e:
                        pass
        #Ignore schema if validation/contents don't work
        except Exception as e:
            hits = 0
            if RAISE_ERRORS:#For debugging, errors can be raised
                raise e
        if hits > bestHits:
            bestHits = hits
            mySchema = s 
        package.schema = None

    if mySchema is not None:
        return getattr(sch, mySchema)()
    else:
        return None

"""
Parses the file that the module was set to parse.
@return: List of Entries
"""
def parse(package):
    if package.soup is None:
        raise UnsetFileParserError()
    if package.schema is None:
        if not can_parse(package, setter=True):
            raise UnparseableFileError(package.filename)
    entries = []
    contents = extractData('contents', package.soup, package.schema)

    for block in contents:
        entry = {}
        for k in package.keywords:
            try:
                data = extractData(k, block, package.schema)
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
def extractData(key, block, schema):  
    data = None
    rules = schema.get_rules()
    
    if rules[key] is not None:
        data = rules[key](block)
        if safeToExtract(data):
            if isinstance(data, str):
                data = data.strip('\n\t- ')
                return data
            else:
                return data
        elif data != None:
            data = data.text.strip('\n\t- ')
            return data
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






