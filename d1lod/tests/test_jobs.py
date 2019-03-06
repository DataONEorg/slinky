"""test_jobs.py

Test aspects of the job module.
"""

import RDF

from d1lod import jobs


def test_can_create_a_void_model():
    to_string = "2015-12-10"

    m = jobs.createVoIDModel(to_string)

    assert isinstance(m, RDF.Model)
    assert m.size() == 4


def test_fails_to_create_a_void_model_with_bad_input():
    assert not isinstance(jobs.createVoIDModel(""), RDF.Model)
    assert not isinstance(jobs.createVoIDModel(5), RDF.Model)
