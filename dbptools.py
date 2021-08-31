"""Some example tools for querying the DBpedia SPARQL endpoint:
http://dbpedia.org/sparql

These rely on the SPARQLWrapper package:
https://github.com/RDFLib/sparqlwrapper
"""

from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper import JSON


# One query session is re-used throughout the module.
SPARQL = SPARQLWrapper('http://dbpedia.org/sparql')

# JSON is probably the most Python-friendly format, so let's stick with that.
SPARQL.setReturnFormat(JSON)

# Prefix query terms as definitions from the DBpedia ontology.
# These include things like 'Person', 'Politician' and 'deathYear'.
QUERY_PREFIXES = """
PREFIX dbpedia: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
"""

# From: https://dbpedia.org/ontology/Person
DEATH_PROPERTIES = [
    'deathPlace',
    'deathDate',
    'deathCause',
    'bodyDiscovered',
    'placeOfBurial',
    'deathYear',
    'causeOfDeath',
    'dateOfBurial',
    'deadInFightDate',
    'deadInFightPlace',
    'deathAge',
]


# %% Exceptions

class DBPError(Exception):
    """Base class for exceptions.
    """

    pass


class NotInDBPediaError(DBPError):
    """Raised when attempting to query an entry that does not exist at:
    http://dbpedia.org/resource
    """

    pass


class NotAPersonError(DBPError):
    """Raised when attempting to query Person-specific properties of an entity that is not of class 'Person':
    http://dbpedia.org/ontology/Person
    """

    pass


# %% Helper functions

def format_name(name):
    """Convert a name to wikipedia entry format.

    Initial letter is capitalized and spaces are represented by underscores.
    """

    if name:
        name = name.strip()
        name = name[0].upper() + name[1:]
        name = name.replace(' ', '_')

    return name


def submit_query(query_text, verbose=False):
    """Submit a SPARQL query to DBpedia.

    The prefixes for the dbpedia ontology are added.
    
    boolean argument verbose toggles printing query text
    returns JSON-format query result
    """

    query = QUERY_PREFIXES + query_text

    if verbose:
        print(query)

    SPARQL.setQuery(query)

    return SPARQL.query().convert()


# %% Main class

class DBPEntity():
    """Class for querying information about an entity in DBPedia.
    """
    
    def __init__(self, name, verbose=False):
        """name is the name of an entity to query
        verbose is boolean passed on to submit_query()
        """
        
        self.requested_name = name
        self.verbose = verbose
        
        self.person = None
        self.politician = None
        self.dead = None
        
        # Check if requested entry is in DBpedia.
        
        formatted_name = format_name(self.requested_name)
        
        query_text = (
            'ASK WHERE { dbpedia:' +
             formatted_name +
            ' a owl:Thing }'
        )
        result = submit_query(query_text, verbose=self.verbose)
        
        if result['boolean']:
            
            self.resolved_name = formatted_name
        
        # Otherwise check whether it redirects.
        
        else:
            
            query_text = (
                'SELECT ?entity WHERE {dbpedia:' +
                formatted_name +
                ' dbo:wikiPageRedirects ?entity} LIMIT 1'
            )
            result = submit_query(query_text, verbose=self.verbose)
            result = result['results']
            
            if result['bindings']:
                uri = result['bindings'][0]['entity']['value']
                self.resolved_name = uri.split('/')[-1]
            else:
                raise NotInDBPediaError(formatted_name, 'not in DBPedia.')
    
    def is_person(self):
        """Ask whether entity is a person.
        
        returns bool
        """
        
        if self.person is None:
    
            query_text = (
                'ASK WHERE { dbpedia:' +
                self.resolved_name +
                ' a dbo:Person }'
            )
            result = submit_query(query_text)
        
            self.person = result['boolean']
        
        return self.person

    def is_politician(self):
        """Ask whether a entity is a politician.
        
        'Politician' is a definition from the DBpedia ontology.
        
        raises NotAPersonError if entity is not of class 'Person'.
        returns bool
        """
        
        if not self.is_person():
            raise NotAPersonError(self.resolved_name, 'not a person.')

        if self.politician is None:
            
            query_text = (
                'ASK WHERE { dbpedia:' +
                self.resolved_name +
                ' a dbo:Politician }'
            )
            result = submit_query(query_text)
    
            self.politician = result['boolean']
        
        return self.politician

    def is_dead(self):
        """Ask whether entity is dead.
        
        This relies on checking whether any of various death-related properties is set.
        
        raises NotAPersonError if entity exists but is not of class 'Person'.
        returns bool
        """
        
        if not self.is_person():
            raise NotAPersonError(self.resolved_name, 'not a person.')
        
        if self.dead is None:
            
            query_text = (
                'ASK WHERE { dbpedia:' +
                self.resolved_name +
                ' ' +
                '|'.join('dbo:' + x for x in DEATH_PROPERTIES) +
                ' ?value }'
            )
            result = submit_query(query_text)
    
            self.dead = result['boolean']
        
        return self.dead
