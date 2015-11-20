# How DataOne Concepts Map to GeoLink Concepts

The DataOne Linked Open Data graph (D1LOD) is essentially a translation of DataOne's holdings into [RDF](http://www.w3.org/RDF/) using the [GeoLink Ontology](http://schema.geolink.org/).
In order to do this translation, concepts that exist in DataOne (e.g., [Data Packages](https://releases.dataone.org/online/api-documentation-v1.2.0/design/DataPackage.html), [System Metadata](https://releases.dataone.org/online/api-documentation-v1.2.0/design/SystemMetadata.html), etc.) must be mapped onto suitable concepts from the [GeoLink Ontology](http://schema.geolink.org/).
This document describes how concepts from DataOne have been mapped onto GeoLink's ontology with the hope that others may provide feedback or spot issues and/or errors with the mappings.

Note: The prefix `gl` is used throughout this document and is meant to refer to the GeoLink Base Ontology ([HTML](http://www.essepuntato.it/lode/http://schema.geolink.org/dev/view.owl), [OWL](http://schema.geolink.org/dev/view.owl))

## `gl:Dataset`

DataOne has the concept of a [Data Package](https://releases.dataone.org/online/api-documentation-v1.2.0/design/DataPackage.html) which is a set of digital objects and is composed of a Science Metadata object, at least one Data object, all of which are described by a Resource Map (another type of object).
All three elements of the Data Package are objects, which is the common currency on DataOne.
While it is the goal that data are part of a Data Package, it is possible for a Science Metadata object to exist on DataOne that is not part of a Data Package and does not have a corresponding set of Data objects.

**To capture the greatest amount of information from DataOne, the mapping for `gl:Dataset` is a Science Metadata object.**
This choice captures data that exists within a Data Package but also covers the aforementioned case where Science Metadata exist without being part of a Data Package.
An important result of this choice is that any Data objects that exist in the DataOne network that are not part of a Resource Map -- and thus cannot be linked to a Science Metadata object -- will not exist in the D1LOD graph.
The latter scenario is understood to be rare and, regardless of its rarity, a Data object without Science Metadata contains too little information to be useful in the D1LOD graph.

## `gl:DigitalObject`

Science Metadata objects and Data objects are both mapped onto `gl:DigitalObject`.
Each `gl:Dataset` will thus have at least one `gl:DigitalObject` which is a Science Metadata object.
In the case of a Science Metadata object that is part of a Resource Map (part of a Data Package), a `gl:DigitalObject` will be created for the one Science Metadata object and for each object in the Resource Map that is the object (in the RDF sense) of a [`ore:describes`](http://www.openarchives.org/ore/1.0/vocabulary#ore-describes) statement.
The latter set of described objects is not limited to the Data objects described by the Science Metadata and thus a `gl:Dataset` may include objects without a related Science Metadata object.
Note: The relationship used to link `gl:Dataset` resources to `gl:DigitalObject` resources is `gl:isPartOf`.
Note: Because of the above choices, the `gl:Dataset` resource will also be typed as a `gl:DigitalObject`.

##`gl:Identifier`

Data objects, Science Metadata objects, and Resource Maps all have [Persistent Identifiers](http://jenkins-1.dataone.org/jenkins/job/API%20Documentation%20-%20trunk/ws/api-documentation/build/html/design/PIDs.html) within DataOne.
Because `glDataset` maps to the Science Metadata object (see above), a `gl:Dataset` and the corresponding `gl:DigitalObject` for the Science Metadata have the same DataOne PID and therefore will share a `gl:Identifier` resource.
