from d1lod import sesamestore

import uuid

s = sesamestore.SesameStore("localhost", 8080)
r = sesamestore.SesameRepository(s, "test")
i = sesamestore.SesameInterface(r)


for i in xrange(1000000):
    identifier = str(uuid.uuid4())
    obj_string = str(uuid.uuid4())

    r.insert({'s': 'geolink:' + identifier, 'p':'rdf:type', 'o':'geolink:' + obj_string})
