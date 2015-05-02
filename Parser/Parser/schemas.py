"""

"""
import sys
SCHEMA_DEF = 'SchemaDefinition_'

#Set to the unique id of a Schema definition to debug
#only that definition. Should always be set to None for
#actual actual usage.
DEBUG = None

keywords =  [   #Each keyword maps to a list which leads to text data
    'validation',#Lists of Lists that check if the html should be used  
    'contents', #Leads to the blocks of html where the data is store
                #Content can't be requested by user
    'first',    #Leads to first name of user in content block
    'last',     #Leads to last name of the entry in content block
    'username', #Leads to username of the entry in content block
    'email',    #Leads to email of the entry in content block
    'course',    #Leads to course of the entry in content block
    'instructor',#
    'TA',
    'role'
            ]
"""
Returns true if keyword that the user should not request
for parsing
"""
def reservedKeyword(key):
    if key == 'validation' or key == 'contents':
        return True
    else:
        return False


"""
Class extended by the Schema implementations returned in the
SchemaDefinition_<name> functions.
"""
class Schema():
    def __init__(self, custom):
        self.lookup = {}
        self.rules  = {}
        for word in keywords:
            if word in custom:
                self.rules[word] = custom[word]
            else:
                self.rules[word] = None
        if (self.rules['contents'] is None) or (self.rules['validation'] is None):
            raise BadSchemaError()

    def get_rules(cls):
        return cls.rules
        
"""
Returns a list of the names of each schema definition function in this
module
"""
def getSchemaDefinitions():
    schemas = []
    for i in globals().keys():
        if str.find(i, SCHEMA_DEF) != -1:
            if not DEBUG:
                schemas.append(i)
            else:
                if i == (SCHEMA_DEF + DEBUG):
                    schemas.append(i)
    return schemas

"""
Returns true if every schema in this module is valid. 
Does not check for parsing ability.
"""
def validateSchemas():
    schemas = getSchemaDefinitions()
    for s in schemas:
        schema = globals()[s]()
        for key in keywords:
            if key not in schema.get_rules():
                return False
    return True

def createSchema(functions, ancestor=None):
    schemaDefs = {}

    for k in keywords:
        funcName = ('_'+ k)
        if funcName in functions.keys():
            schemaDefs[k] = functions[funcName]
        elif ancestor is not None:
            if ancestor.rules[k] is not None:
                schemaDefs[k] = ancestor.rules[k]
    return Schema(schemaDefs)

def getSchemaCreator(locs, ancestor=None):
    def schemaMaker():
        functions = {}
        for f in locs:
            if str.find(f, '_') != -1:
                functions[f] = locs[f]
        schema = createSchema(functions, ancestor)
        return schema
    return schemaMaker
    
##FIX ERROR CHECKING HERE -------------------------------------------
##
###########################################
#############Schema Definitions############
###########################################
###########################################
#Schema definitions define all _<keyword> functions that they
#implement, and then return the schema created by the
#createSchema() functioned defined above.
"""
Defines the schema used to parse varients of the Moodle CMS
"""
def SchemaDefinition_MoodleVarient():
    schema = None

    def _validation(soup):
        if not test1(soup):
            return False
        elif not test2(soup):
            return False
        else:
            return True
        
    def test1(soup):
        v = soup.find('option', {'value':'1','selected':'selected'})
        if v.text.strip('\n\t ') == 'User details':
            return True
        else:
            return False

    def test2(soup):
        v = soup.find('option', {'value':'5','selected':'selected'})
        if v.text.strip('\t\n ') == 'Student':
            return True
        else:
            return False
##
    def _username(block):
        return block.find('div', {'class': 'username'}).text
##

    def _contents(soup):
        return soup.find_all('td', {'class': 'content cell c1'})

##
    def _email(block):
        email = block.find('div', {'class': 'info'})
        return email.find('a').text
##    
    def _first(block):
        return extractFirst(block.find('div', {'class': 'username'}))

    def extractFirst(username):
        if username is None:
            return None
        names = username.text.split()
        if len(names) < 1:
            return ''
        else:
            return names[0]
##    
    def _last(block):
        return extractLast(block.find('div', {'class': 'username'}))

    def extractLast(username):
        if username is None:
            return None
        names = username.text.split()
        if len(names) < 2:
            return ''
        else:
            return names[1]
##
    def _course(block):
        return extractCourse(block)

    def extractCourse(block):
        key = 'course'
        title = None
        course = ''
        if key in schema.lookup.keys():
            return schema.lookup[key]

        for parent in block.parents:
            if parent is not None:
                if parent.name == 'html':
                    title = parent.find('title')
                    break
        if title is not None:
            words = title.text.split(': ')
            if len(words) > 0:
                schema.lookup[key] = words[0]
                return words[0]
        schema.lookup[key] = None
        return None
    schema = getSchemaCreator(locals())()
    return schema
######
"""
Defines the schema used to parse Syracuse's varient of the 
BlackBoard CMS
"""
def SchemaDefinition_SyracuseBlackBoard():    
    def _validation(soup):
        if not test1(soup):
            return False
        else:
            return True

    def test1(soup):
        tag = soup.find('title').text
        words = tag.split('-')
        words1 = tag.split('–')
        if (words1[0].strip('\t\n ') or words[0].strip('\t\n ')) == 'Select Users':
            return True
        else:
            
            return False    
##
    def _contents(soup):
        return soup.find_all('option')

##
    def _course(block):
        key = 'course'
        course = ''
        if key in schema.lookup.keys():
            return schema.lookup[key]

        for parent in block.parents:
            if parent is None:
                continue
            if parent.name == 'html':
                words = parent.find ('span', 
                                    {'class': 'courseName'})
                if words is None:
                    return None
                words = words.text.split('.')
                if len(words) > 3:
                    i = 0
                    while i < 4:
                        course += words[i]
                        if i != 3:
                            course += '-'
                        i += 1
        schema.lookup[key] = course
        return course
##
    def _first(name):
        name = name.text
        if name is None:
            return None
        words = name.split(', ')
        if len(words) > 1:
            return words[1]
        else:
            return ''
##
    def _last(name):
        if name is None:
            return None
        name = name.text
        if name is None:
            return None
        words = name.split(', ')
        if len(words) > 0:
            return words[0]
        else:
            return ''
    schema = getSchemaCreator(locals())()
    return schema

######
"""
Defines the schema used to parse the University of Arizona's
varient of the D2L CMS.
"""
def SchemaDefinition_UofAD2L():   
    def _validation(soup):
        return True
##
    def _contents(soup):
        block = soup.find('table', {'class': 'd_g d_gl'})
        contents = block.find_all('tr')
        contents.pop(0)
        contents.pop(0)
        return contents

    def _email(block):
        return block.find('td', {'class': 'd_gn'})
##
    def _first(block):
        name = block.find('th', {'class': 'd_ich', 'scope': 'row'})
        return getFirst(name)

    def getFirst(soup):
        if soup is None:
            return None
        words = soup.text
        if words is not None:
            words = words.split(', ')
            if len(words) > 1:
                word = words[1].split()
                return word[0]
        return None
##
    def _last(block):
        name = block.find('th', {'class': 'd_ich', 'scope': 'row'})
        return getLast(name)

    def getLast(soup):
        if soup is None:
            return None
        words = soup.text
        if words is not None:
            words = words.split(', ')
            if len(words) > 0:
                return words[0]
        return None
##
    def _course(block):
        key = 'course'
        if key in schema.lookup.keys():
            return schema.lookup[key]

        for parent in block.parents:
            if parent is not None:
                if parent.name == 'html':
                    title = parent.find('title')
                    break
        if title is not None:
            words = title.text.split()
            i = len(words) - 6
            course = ''
            while i < (len(words) - 2):
                course += words[i]
                if i != (len(words) - 3):
                    course+= '-'
                i += 1
            schema.lookup[key] = course
            return course
        schema.lookup[key] = None
        return None
## 
    def _instructor(soup):
        key = 'instructor'

        if key in schema.lookup.keys():
            return schema.lookup[key]

        if soup is not None:
            siblings = soup.parent.find_all('tr')
            for s in siblings:
                children = s.find_all('td')
                name = s.find('th', {'class': 'd_ich',
                            'scope': 'row'})
                for child in children:
                    try:
                        child = child.find('label').text
                        child = child.strip('\n\t ')
                        if child == 'Instructor':
                            instr = getLast(name)
                            schema.lookup[key] = instr
                            return instr
                    except Exception as e:
                        pass
        schema.lookup[key] = None
        return None
##
    def _role(block):
        children = block.find_all('label')
        for c in children:
            if len(c.text.split('@')) == 1:
                return c.text

    schema = getSchemaCreator(locals())()
    return schema
##
"""
Defines the schema used to parse the University of Arizona's
varient of the Blackboard CMS.
"""

def SchemaDefinition_UofABlackBoard():
    schema = SchemaDefinition_SyracuseBlackBoard()
#    def _validation(soup):
#        if not test1(soup):
#            return False
#        return True
    
#    def test1(soup):
#        tag = soup.find('title').text.strip('\t\n ')
#        words = tag.split(' - ')
#        if 
#        if tag == 'Select Users – Basic Operations Mgmt (Spring - 2015)':
#            return True
#        else:
#            return False
##    
    def _contents(soup):
        block = soup.find('select', {'id': 'USERS_AVAIL'})
        return block.find_all('option')
##    
    def _first(block):
        name = block.text
        return getFirst(name)

    def getFirst(name):
        firstAndMid = name.split(',')[1]
        first = firstAndMid.split()[0]
        return first.strip('\t\n ')
##
    def _course(block):
        key = 'course'
        if key in schema.lookup.keys():
            return schema.lookup[key]

        for parent in block.parents:
            if parent is not None:
                if parent.name == 'html':
                    title = parent.find('title')
                    break
        if title is not None:
            words = title.text.split()
            i = len(words) - 6
            course = ''
            while i < (len(words) - 3):
                course += words[i]
                if i != (len(words) - 4):
                    course+= '-'
                i += 1
            schema.lookup[key] = course
            return course
        schema.lookup[key] = None
        return None        
##
    schema = getSchemaCreator(locals(), schema)()
    return schema

class BadSchemaError(Exception):
    pass

#Raises error if Schema defintions define invalid schema
if not validateSchemas():
    raise BadSchemaError()

#from bs4 import BeautifulSoup

def __main__():
    pass
#    soup = BeautifulSoup(open(sys.argv[1]))
#    schema = SchemaDefinition_MoodleVarient()
#    print(schema.rules['validation'](soup))
#    contents = schema.rules['contents'](soup)
#    print(contents)
#    print(len(contents))
#    for c in contents:
#        course = schema.get_rules()['course'](c)
#        first = schema.get_rules()['first'](c)
#        last = schema.get_rules()['last'](c)
#        email = schema.get_rules()['email'](c)
#        print(first," ", last, " ", course)
#    print(schema.get_rules()['course'](contents[0]))
#    print(schema.get_rules()['validation'])

if __name__ == '__main__':
    __main__()



