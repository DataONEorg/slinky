from d1lod import sesamestore

import uuid

s = sesamestore.SesameStore("virtuoso", 8890)
r = sesamestore.SesameRepository("virtuoso", 8890, "geolink_test")
i = sesamestore.SesameInterface(r)


for i in range(1000000):
    identifier = str(uuid.uuid4())
    obj_string = str(uuid.uuid4())

    r.insert({'s': 'schema:' + identifier, 'p':'rdf:type', 'o':'schema:' + obj_string})
