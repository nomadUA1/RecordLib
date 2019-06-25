from RecordLib import ruledefs
from RecordLib.common import Sentence
from datetime import date
import pytest
import types

def test_rule_expunge_over_70(example_crecord):
    example_crecord.person.date_of_birth = date(1920, 1, 1)
    example_crecord.cases[0].arrest_date = date(1970, 1, 1)
    example_crecord.cases[0].charges[0].sentences = [Sentence(
        sentence_date = date.today(),
        sentence_type = "Confinement",
        sentence_period = "90 days",
        sentence_length = "90 days"
    )]
    modified_record, analysis = ruledefs.expunge_over_70(example_crecord)
    assert analysis["age_over_70_expungements"]["conclusion"] == "No expungements possible"

    example_crecord.cases[0].charges[0].sentences[0] = Sentence(
        sentence_date = date(1980, 1, 1),
        sentence_type = "Confinement",
        sentence_period = "90 days",
        sentence_length = "90 days"
    )
    modified_record, analysis = ruledefs.expunge_over_70(example_crecord)
    assert analysis["age_over_70_expungements"]["conclusion"] == "Expunge cases"
