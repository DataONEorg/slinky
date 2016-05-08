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

## Example

An example will solidify what I've said above. Here's what would be added to the graph store if we just added the dataset with the PID 'doi:10.6073/AA/knb-lter-arc.376.1':

```{ttl}
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix d1landing: <https://search.dataone.org/#view/> .
@prefix pext: <http://proton.semanticweb.org/protonext#> .
@prefix psys: <http://proton.semanticweb.org/protonsys#> .
@prefix datacite: <http://purl.org/spar/datacite/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix d1org: <http://lod.dataone.org/organization/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix geolink: <http://schema.geolink.org/base/main#> .
@prefix d1person: <http://lod.dataone.org/person/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix d1node: <https://cn.dataone.org/cn/v1/node/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix d1dataset: <http://lod.dataone.org/dataset/> .

<http://lod.dataone.org/dataset/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1>
    geolink:description "phosphorus, nitrate, ammonia, and particulate phosphorus for lake N1 in 1991." ;
    geolink:hasEndDate "1991-01-01T00:00:00Z" ;
    geolink:hasGeometryAsWktLiteral "POLYGON ((-149.75 68.8, -149.0433 68.8, -149.0433 68.5, -149.75, 68.5))" ;
    geolink:hasIdentifier [
        geolink:hasIdentifierScheme datacite:doi ;
        geolink:hasIdentifierValue "doi:10.6073/AA/knb-lter-arc.376.1" ;
        a geolink:Identifier ;
        rdfs:label "doi:10.6073/AA/knb-lter-arc.376.1"
    ] ;
    geolink:hasLandingPage <https://search.dataone.org/#view/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1> ;
    geolink:hasPart [
        geolink:dateUploaded "2005-07-27T23:00:00.000+00:00" ;
        geolink:hasAuthoritativeDigitalRepository <https://cn.dataone.org/cn/v1/node/urn:node:LTER> ;
        geolink:hasByteLength "7093" ;
        geolink:hasChecksum "22bd46629eaf8d71e686f63395a12a56" ;
        geolink:hasChecksumAlgorithm "MD5" ;
        geolink:hasFormat <http://schema.geolink.org/dev/voc/dataone/format#002> ;
        geolink:hasIdentifier [
            geolink:hasIdentifierScheme datacite:doi ;
            geolink:hasIdentifierValue "doi:10.6073/AA/knb-lter-arc.376.1" ;
            a geolink:Identifier ;
            rdfs:label "doi:10.6073/AA/knb-lter-arc.376.1"
        ] ;
        geolink:hasOriginDigitalRepository <https://cn.dataone.org/cn/v1/node/urn:node:LTER> ;
        geolink:hasReplicaDigitalRepository <https://cn.dataone.org/cn/v1/node/urn:node:CN>, <https://cn.dataone.org/cn/v1/node/urn:node:LTER> ;
        geolink:isPartOf <http://lod.dataone.org/dataset/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1> ;
        a geolink:DigitalObject
    ] ;
    geolink:hasStartDate "1991-01-01T00:00:00Z" ;
    a geolink:Dataset ;
    rdfs:label "91n1nuts.txt" .

<http://lod.dataone.org/person/urn:uuid:78d79a39-3aef-4bad-a011-e3fd2c5466f5>
    geolink:isCreatorOf <http://lod.dataone.org/dataset/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1> ;
    geolink:nameFamily "Miller" ;
    geolink:nameFull "Mike Miller" ;
    geolink:nameGiven "Mike" ;
    a geolink:Person .
```
