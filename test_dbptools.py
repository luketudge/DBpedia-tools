import pytest

import dbptools


VERBOSE = True

NAMES = [
    ('', ''),
    ('angela', 'Angela'),
    ('Angela Merkel', 'Angela_Merkel'),
]


@pytest.mark.parametrize('raw, formatted', NAMES)
def test_format_name(raw, formatted):
    
    assert dbptools.format_name(raw) == formatted


def test_init():
    
    entity = dbptools.DBPEntity('Angela Merkel', verbose=VERBOSE)
    
    assert entity.resolved_name == 'Angela_Merkel'


def test_redirect():
    
    entity = dbptools.DBPEntity('Angie Merkel', verbose=VERBOSE)
    
    assert entity.resolved_name == 'Angela_Merkel'


def test_not_exists():
    
    with pytest.raises(dbptools.NotInDBPediaError):
        dbptools.DBPEntity('Nonexistent_person', verbose=VERBOSE)


IS_PERSON_NAMES = [
    ('Angela Merkel', True),
    ('candiru', False),
    ('Sherlock Holmes', False),
]

@pytest.mark.parametrize('name, answer', IS_PERSON_NAMES)
def test_is_person(name, answer):
    
    entity = dbptools.DBPEntity(name, verbose=VERBOSE)
    
    assert entity.is_person() == answer


IS_POLITICIAN_NAMES = [
    ('Angela Merkel', True),
    ('Nicki Minaj', False),
]

@pytest.mark.parametrize('name, answer', IS_POLITICIAN_NAMES)
def test_is_politician(name, answer):
    
    entity = dbptools.DBPEntity(name, verbose=VERBOSE)
    
    assert entity.is_politician() == answer


IS_DEAD_NAMES = [
    ('Angela Merkel', False),
    ('Otto von Bismarck', True),
]

@pytest.mark.parametrize('name, answer', IS_DEAD_NAMES)
def test_is_dead(name, answer):
    
    entity = dbptools.DBPEntity(name, verbose=VERBOSE)
    
    assert entity.is_dead() == answer


PERSON_METHODS = [
    dbptools.DBPEntity.is_politician,
    dbptools.DBPEntity.is_dead,
]

@pytest.mark.parametrize('method', PERSON_METHODS)
def test_not_person(method):
    
    with pytest.raises(dbptools.NotAPersonError):
        entity = dbptools.DBPEntity('candiru', verbose=VERBOSE)
        method(entity)
