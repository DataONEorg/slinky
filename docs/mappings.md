# How DataOne Concepts Map to GeoLink Concepts

The DataOne Linked Open Data graph (D1LOD) is essentially a translation of DataOne's holdings into [RDF](http://www.w3.org/RDF/) using the [GeoLink Ontology](http://schema.geolink.org/).
In order to do this translation, concepts that exist in DataOne (e.g., [Data Packages](https://releases.dataone.org/online/api-documentation-v1.2.0/design/DataPackage.html), [System Metadata](https://releases.dataone.org/online/api-documentation-v1.2.0/design/SystemMetadata.html), etc.) must be mapped onto suitable concepts from the [GeoLink Ontology](http://schema.geolink.org/).
This document describes how concepts from DataOne have been mapped onto GeoLink's ontology with the hope that others may provide feedback or spot issues and/or errors with the mappings.

Note: The prefix `gl` is used throughout this document and is meant to refer to the GeoLink Base Ontology ([HTML](http://www.essepuntato.it/lode/http://schema.geolink.org/dev/view.owl), [OWL](http://schema.geolink.org/dev/view.owl))

## `gl:Dataset`

DataOne has the concept of a [Data Package](https://releases.dataone.org/online/api-documentation-v1.2.0/design/DataPackage.html) which is a set of digital objects and is composed of a Science Metadata object, at least one Data object, all of which are described by a Resource Map (another type of object). All three elements of the Data Package are objects, which is the common currency on DataOne.

`gl:Dataset`s have take on the PID of the Science Metadata object and have properties that are drawn from the Solr index which is mainly fields that were extracted from the Science Metadata object during ingestion of the Data Package. For `gl:Dataset`s with a Resource Map, the `gl:Dataset` then contains a set of `gl:DigitalObject`s, which may be either Science Metadata (e.g., EML, FGDC) or Science Data (e.g., CSV, XLS, etc.).

Notes:

- Each `gl:Dataset` enters the graph as a resource with a URI of the form `<http://lod.dataone.org/dataset/{PID}`.

## `gl:DigitalObject`

Science Metadata objects and Data objects are both mapped onto `gl:DigitalObject`. Each `gl:Dataset` will thus have at least one `gl:DigitalObject` which is a Science Metadata object. In the case of a Science Metadata object that is part of a Resource Map (part of a Data Package), a `gl:DigitalObject` will be created for the one Science Metadata object and for each object in the Resource Map that is the object (in the RDF sense) of a [`ore:aggregates`](http://www.openarchives.org/ore/1.0/vocabulary#ore-aggregates) statement. The latter set of described objects is not limited to the Data objects described by the Science Metadata and thus a `gl:Dataset` may include objects without a related Science Metadata object. Note: The relationship used to link `gl:Dataset` resources to `gl:DigitalObject` resources is `gl:isPartOf`.

Notes:

- Resource maps are not in the graph.
- Each `gl:DigitalObject` enters the graph as a blank node.

## `gl:Identifier`

Data objects, Science Metadata objects, and Resource Maps all have [Persistent Identifiers](http://jenkins-1.dataone.org/jenkins/job/API%20Documentation%20-%20trunk/ws/api-documentation/build/html/design/PIDs.html) (PIDs) within DataOne. For the D1 LOD graph, only Science Metadata and Data Objects get `gl:Identifier`s.

Notes:

- Each `gl:Identifier` enters the graph as a blank node.
