from RecordLib.person import Person
from dataclasses import asdict
from datetime import date
from RecordLib.serializers import to_serializable
from cleanslate.serializers import PersonSerializer
import json

def test_person():
    per = Person("John", "Smeth", date(2010, 1, 1), date_of_death = date(2020, 1, 1))
    assert per.first_name == "John"
    assert per.last_name == "Smeth"
    assert per.date_of_birth.year == 2010
    assert per.date_of_death.year == 2020
    assert per.aliases is None

def test_person_age():
    per = Person("John", "Smeth", date(2000, 1, 1))
    assert per.age() > 17


def test_person_years_dead(example_person):
    example_person.date_of_death = None
    assert example_person.years_dead() == float("-Inf")
    example_person.date_of_death = date.today()
    assert example_person.years_dead() == 0
    example_person.date_of_death = date(2000,1,1)
    assert example_person.years_dead() > 10


def test_person_todict():
    per = Person("John", "Smeth", date(2010, 1, 1), aliases=["JJ", "Smelly"])
    assert asdict(per) == {
        "first_name": "John",
        "last_name": "Smeth",
        "date_of_birth": date(2010, 1, 1),
        "date_of_death": None,
        "aliases": ["JJ", "Smelly"]
    }

def test_serializing_person(example_person):
    ser = to_serializable(example_person)
    assert ser["first_name"] == example_person.first_name
    assert ser["aliases"] == example_person.aliases

    deser = PersonSerializer(data=ser)
    breakpoint()
    assert deser.is_valid(), deser.error_messages
    deser = deser.validated_data
    deser = Person.from_dict(deser)
    assert isinstance(deser, Person)
    assert deser == example_person