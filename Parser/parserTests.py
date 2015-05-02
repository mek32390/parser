import sys, os
import parser
import unittest
import configparser


"""
p = parser.Parser()
c = p.get_config()
c.add_section("New section")
c["New section"] = {'key': "asdfasdfsdfasdfasdfasdfasdf"}
p.apply_config(c)
print("Get config sections: ", p.get_config().sections())
print("Is verbose: ", p.is_verbose())
c['VALUES']['VERBOSE'] = 'False'
print("c verbose val: ", c['VALUES']['VERBOSE'])
p.apply_config(c)
print("Is verbose: ", p.is_verbose())
print("get config verbose: ", p.get_config()['VALUES']['VERBOSE'])
p.close_parser()
c = p.get_config()
print("c is: ", c)
"""

"""
Tests to make sure that the fundemental functions in the parser
module are working.
"""
class TestParserFunctions(unittest.TestCase):
#class TestParserFunctions():
    def setUp(self):
        self.configfile = os.path.abspath('testConfig.ini')
    def tearDown(self):
        parser.close_parser()
    """
    Test that default_config it returns a config object 
    with all of the correct sections and section names
    """
    def test_default_config(self):
        config = parser.default_config()
        self.assertIsInstance(config, configparser.ConfigParser, msg='defualt_config does not return instance of ConfigParser')
        req_sections =  {
                        'VALUES':               ['CSV_DUMP', 'FILENAME_BASE'], 
                        'WRITTEN_KEYWORDS':     ['written_keywords'],
                        'PARSED_KEYWORDS':      ['parsed_keywords'], 
                        'ENTRY_RESTRICTIONS':   [] 
                        }
        for member in config.sections():
            self.assertIn(member, req_sections.keys(), msg='default_config does not have the required sections')
        for k in req_sections.keys():
            for w in req_sections[k]:
                try:
                    config[k][w]
                except KeyError as e:
                    fail(msg=w +' is not located in ' + k)

    """
    Tests that user can instanciate a Parser object 
    with and without a .ini file/ConfigParser object.
    Makes sure it raises and error if you try to
    instanciate it with bad input. 
    """
    def test_parser_creation(self):
        p = parser.Parser()
        self.assertIsInstance(p, parser.Parser, msg='Parser constructor does not create a Parser object when ' +
                                                'not given any input')
        p = None
        p = parser.Parser(self.configfile)
        self.assertIsInstance(p, parser.Parser, msg='Parser constructor does not create a Parser object when ' +
                                                'given a .ini file name')
        p = None
        c = configparser.ConfigParser()
        c.read(self.configfile)
        p = parser.Parser(c)
        self.assertIsInstance(p, parser.Parser, msg='Parser constructor does not create a Parser object when ' +
                                                'given a ConfigParser argument')
        
        

"""
Tests the functionality of the methods in a Parser object. These
these tests should only be run if all tests in TestParserFunctions 
pass. This is because the setup method depends on the functionality
tested in TestParserFunctions working correctly. 
"""
#class TestParserMethods(unittest.TestCase):
class TestParserMethods():
    def setup(self):
        self.p = parser.Parser()
        self.config = parser.default_config()
        
    def teardown(self):
        self.p = None

    """
    Tests apply_config with a good ini files,
    bad ini files, good ConfigParsers and bad
    ConfigParsers. Makes sure get_config returns the
    correct ConfigParsers.
    """
    def test_apply_config():
        pass

    """
    Tests that user can change the logger and that it 
    logs appropriately. Makes sure setting it to None
    disables logging. Makes sure that you can control
    the name of the logger with the config file.
    """
    def test_logger():
        pass

    """
    Tests that parse_and_write can parse an html file
    to the default CSV_DUMP. That you you can change where
    it parses to. That you can control the name of the 
    CSV file or let it default. 
    """
    def test_parse_and_write():
        pass
        
    """
    Test that parser can parse a list of html files.
    """
    def test_parse_files():
        pass
        
    """
    Test that parser can control the default name of
    the csv files by changing the FILENAME_BASE in the
    config file. Also ensures that a bad FILENAME_NAME
    base will yield a csv file called <htmlFileName>.csv
    """
    def test_filename_base():
        pass

    """
    Tests that parser can control the type of entries
    that are written to the csv files by changing the 
    restrictions in the config file.
    """
    def test_entry_restrictions():
        pass 

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestParserFunctions)

    return suite
   
def __main__():
#    unittest.main(TestParserFunctions)
    unittest.main()
    
if __name__ == '__main__':
    __main__()




    
