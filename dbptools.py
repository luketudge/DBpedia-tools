"""Some example tools for querying the DBpedia SPARQL endpoint:
http://dbpedia.org/sparql

These rely on the SPARQLWrapper package:
https://github.com/RDFLib/sparqlwrapper
"""

import functools

from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper import JSON


VERBOSE = False

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


# %% Exceptions

class DBPError(Exception):
    """Base class for exceptions.
    """

    pass


class NotInDBPediaError(DBPError):
    """Raised when attempting to query an entry that does not exist at:
    http://dbpedia.org/resource/
    """

    pass


class NotaPersonError(DBPError):
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


def submit_query(query_text):
    """Submit a SPARQL query to DBpedia.

    The prefixes for the dbpedia ontology are added.

    returns JSON-format query result
    """

    query = QUERY_PREFIXES + query_text

    if VERBOSE:
        print(query)

    SPARQL.setQuery(query)

    return SPARQL.query().convert()


def entry_exists(entity):
    """Ask whether an entry exists in DBpedia.

    Checks whether the entry is an instance of the base class 'Thing'.
    Important, because queries on non-existent entities will otherwise just return False.

    returns bool
    """

    query_text = (
        'ASK WHERE { dbpedia:' +
        format_name(entity) +
        ' a owl:Thing }'
    )

    result = submit_query(query_text)

    return result['boolean']


def check_exists(func):
    """Decorator for functions whose first argument is a wikipedia entity.
    Adds a check that the entity exists in DBPedia.

    Raises NotInDBPediaError if not.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        entity = format_name(args[0])
        if not entry_exists(entity):
            raise NotInDBPediaError("'" + entity + "' not in DBpedia.")
        return func(*args, **kwargs)

    return wrapper


# %% Example functions

def is_person(entity):
    """Ask whether a wikipedia entity is a person.

    returns bool
    """

    query_text = (
        'ASK WHERE { dbpedia:' +
        format_name(entity) +
        ' a dbo:Person }'
    )

    result = submit_query(query_text)

    return result['boolean']


@check_exists
def is_politician(entity):
    """Ask whether a wikipedia entity is a politician.

    'Politician' is a definition from the DBpedia ontology.

    raises NotaPersonError if entity is not of class 'Person'.

    returns bool
    """

    entity = format_name(entity)

    if not is_person(entity):
        raise NotaPersonError("'" + entity + "' is not a person.")

    query_text = (
        'ASK WHERE { dbpedia:' +
        entity +
        ' a dbo:Politician }'
    )

    result = submit_query(query_text)

    return result['boolean']


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


@check_exists
def is_dead(entity):
    """Ask whether a wikipedia entity is dead.

    This relies on checking whether any of various death-related properties is set.

    raises NotaPersonError if entity exists but is not of class 'Person'.

    returns bool
    """

    entity = format_name(entity)

    if not is_person(entity):
        raise NotaPersonError("'" + entity + "' is not a person.")

    query_text = (
        'ASK WHERE { dbpedia:' +
        entity +
        ' dbo:' +
        '|dbo:'.join(DEATH_PROPERTIES) +
        ' ?value }'
    )

    result = submit_query(query_text)

    return result['boolean']


# %% Demo

if __name__ == '__main__':

    examples = [
        'Angela Merkel',
        'Angela Murkle',
        'Ronald Reagan',
        'Nicki Minaj',
        'Elvis Presley',
        'Baked Alaska',
        'Sherlock Holmes',
    ]

    for person in examples:

        try:

            if is_dead(person):
                status = 'dead'
            else:
                status = 'living'

            if is_politician(person):
                profession = 'politician'
            else:
                profession = 'non-politician'

            print(person, ':', status, profession)

        except NotInDBPediaError:

            print(person, ': not found')

        except NotaPersonError:

            print(person, ': not a person')
