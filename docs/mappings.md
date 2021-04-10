# How DataOne Concepts Map to Knowledge Graph Concepts and Patterns

The DataOne Linked Open Data graph (D1LOD) is essentially a translation of DataOne's holdings into [RDF](http://www.w3.org/RDF/) using a variety of standard vocabularies, including [schema.org](https://schema.org) as described in [Science on schema.org](https://science-on-schema.org), OBOE, ENVO, ECSO, and other vocuabularies. i.e., there is no DataONE ontology. Originally it was mapped against the [GeoLink Ontology](http://schema.geolink.org/), but this document has moved away from using GeoLink as the base.

- **STATUS: Work in Progress**
  - This document is in a partial state of incomplete editing as we transition concepts from Geolink to other vocabularies. Changes should be made on the `feature_14_graph_pattern` branch, and will show up in the associated pull rerquest.

## Concepts

DataONE has a number of formal types that need to be mapped:

- **Objects**: Everything stored/federated in DataONE (metadata, data, etc) is an Object and has (1) a serialization on disk ("object bytes") and (2) corresponding System Metadata
- **System Metadata**: Every Object has corresponding System Metadata containing operational metadata about the Object such as its size, checksum, etc
- **Packages:** A virtual concept formed by the closure asserted by triples in an Object conforming to a variant of the OAI/ORE Resource Map data model. For every Package there is one Object describing the Package. An Object may be a member of zero, one, or many Packages
- **Accounts**: All Objects are related to Subjects in the DataONE Accounts system and Subjects can be an individual or a group. These relations are stored in the System Metadata for the Object. e.g., all Objects have a `submitter` which is a string identifying the client or person that created the Object. This is often not the same client or person that created the content in the Object. e.g., a scientist might have created a file but their data manager may have uploaded the Object
- **Nodes**: Coordinating Nodes and Member Nodes make up the federation. See Data Repositories.

At a higher level, the most important/interesting information we have in DataONE is information about:

1. "Datasets" & Data (methods, variables, measurements, space & time, funding/funders, etc)
2. Parties (People, Organizations) + their relationships to data/datasets
3. Data Repositories

The job of the mappings is to provide the link between the concepts across the two above lists.

## Datasets & Data

| DataONE Concept  | Type     | OWL Class                                                        |
| ---------------- | -------- | ---------------------------------------------------------------- |
| Object: Metadata | `1:1`    | `schema:Dataset`                                                 |
| Object: Data     | `1:1`    | `schema:DataDownload`                                            |
| Object: Portal   | n/a      | Not mapped                                                       |
| System Metadata  | n/a      | Mapped directly on to `schema:Dataset` or `schema:DataDownload`  |
| Package          | n/a      | Mapped directly on to `schema:Dataset` via `schema:distribution` |
| Accounts         | `1:many` | `schema:Person` or `schema:Organization`                         |

Packages won't be directly mapped to a first-class type but the triples contained within them will be reflected using the following linkages:

| DataONE            | RDF                                                                  |
| ------------------ | -------------------------------------------------------------------- |
| `ore:aggregates`   | `schema:Dataset` <-> `schema:distribution` <-> `schema:DataDownload` |
| Provenance         | TBD. See Notes.                                                      |
| `prov:hasLocation` | TBD. Maybe just as `prov:hasLocation`                                |
| Other triples      | Not mapped                                                           |

Notes:

- For mapping in provenance metadata, I think we want to do something simpler than ProvONE and more like what Carl Boettiger shows in [prov](https://github.com/cboettig/prov). ie, we care about derivation and usage but not really ports and all that detailed stuff

### Dataset

Note: This list is possibly not comprehensive at this point.
Note: These are loose mappings because the mappings are not as simple as XPath expressions. Also because the XPath expressions for ISO metadata are a nightmare.

| Property              | Mapped From (these aren't all real XPaths for brevity)                                                                                                                                                               |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@id`                 | `https://dataone.org/datasets/${PID}`                                                                                                                                                                                |
| `@type`               | `schema:Dataset`                                                                                                                                                                                                     |
| `identifier`          | System Metadata `identifier` (PID)                                                                                                                                                                                   |
| `isAccessibleForFree` | System Metadata `accessPolicy`                                                                                                                                                                                       |
| `url`                 | `https://dataone.org/datasets/${PID}`                                                                                                                                                                                |
| `name`                | EML: `/eml/dataset/title` <br> ISO: `//gmd:citation/gmd:title`<br>FGDC:`//idinfo/citation/citeinfo/title/` <br> Dryad: `//dcterms:title`                                                                             |
| `description`         | EML: `/eml/dataset/abstract` <br> ISO: `//gmd:identificationInfo/gmd:abstract` <br>FGDC: `//idinfo/descript/abstract` <br> Dryad: `//dcterms:description`                                                            |
| `datePublished`       | EML: `/eml/dataset/pubDate` <br> ISO: `//gmd:identificationInfo/gmd:citation/gmd:date` <br>FGDC: `//idinfo/citation/citeinfo/pubdate` <br> Dryad: n/a                                                                |
| `dateModified`        | System Metadata `dateSysMetadataUpdated`                                                                                                                                                                             |
| `keywords`            | EML: `/eml/dataset/keywordSet/keyword` <br> ISO: `//gmd:identificationInfo/gmd:descriptiveKeywords/` <br>FGDC: `//idinfo/keywords/theme/themekey`, `/idinfo/keywords/place/placekey` <br> Dryad: `//dcterms:subject` |
| `creator`             | EML: `/eml/dataset/creator` <br> ISO: `/gmd:identificationInfo/gmd:citation/gmd:CI_ResponsibleParty/` <br>FGDC: `//idinfo/citation/citeinfo/origin` <br> Dryad: `//dcterms:creator`                                  |
| `version`             | System Metadata `identifier`                                                                                                                                                                                         |
| `license`             | EML: `/eml/dataset/{licensed,intellectualRights}` <br> ISO: `//gmd:metadataConstraints/gmd:useConstraints/` <br>FGDC: n/a <br> Dryad `//dcterms:license`                                                             |
| `temporalCoverage`    | EML: `/eml/dataset/coverage/temporalCoverage` <br> ISO: `//gmd:identificationInfo/gmd:extent` <br>FGDC: `//idinfo/timeperd/timeinfo` <br> Drayd: n/a                                                                 |
| `spatialCoverage`     | EML: `/eml/dataset/coverage/spatialCoverage` <br> ISO: `//gmd:identificationInfo/gmd:extent` <br>FGDC: `//idinfo/spdom/bounding` <br> Drayd: n/a                                                                     |
| `publisher`           | EML: `/eml/dataset/publisher` <br> ISO: TBD <br>FGDC: n/a? <br> Drayd: `//dcterms:publisher` <br> Falls back to System Metadata `originMemberNode` otherwise                                                         |
| `distribution`        | Resource Map `ore:aggregates`                                                                                                                                                                                        |
| `variableMeasured`    | EML: `/eml/dataset/{entity}/attribute` <br> ISO: TODO <br>FGDC: `//attr` <br> Dryad n/a                                                                                                                              |
| `MonetaryGrant`       | EML: `/eml/dataset/project/{funding,award}/` <br> ISO: n/a <br>FGDC: n/a? <br> Dryad n/a                                                                                                                             |
| `prov:wasRevisionOf`  | System Metadata `obsoletes`                                                                                                                                                                                          |
| `schemaVersion`       | System Metadata `formatId`                                                                                                                                                                                           |
| `size`                | System Metadata `size` (summed over all members)                                                                                                                                                                     |
| `sameAs`              | The DOI if the DataONE identifier is a DOI                                                                                                                                                                           |

Extra triples:

- EML `annotation` elements will go in as-is with the subject as `https://dataone.org/datasets/${PID}[#id]` (fragment URI depending on context)

## Parties

Parties in DataONE are referenced either in system metadata or science metadata and are referenced either explicitly in the metadata or referenced by identifier in the DataONE Accounts service.

Parties exist in the graph as top-level instances so that references to them can be resolved independently and re-used across `schema:Dataset` instances.
Because parties rarely have identifiers of their own in the metadata they're referenced in, we mint opaque identifiers as needed.
When references to parties in the metadata have identifier metadata (i.e., ORCIDs), we use that instead of minting an opaque identifier.

## Data Repositories

Data repositories in DataONE are listed in the [Node list](https://cn.dataone.org/cn/v2/node) and referenced in System Metadata (`authoritativeMemberNode`, etc).
DataONE nodes (CN/MN) will are mapped to schema:ResearchProject + schema:Service following [SOSO](https://github.com/ESIPFed/science-on-schema.org/blob/master/guides/DataRepository.md).

## Example

TODO: Update for our updated graph pattern

Here's what would be added to the graph store if we just added the dataset with the PID 'doi:10.6073/AA/knb-lter-arc.376.1':

```{ttl}
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix d1landing: <https://search.dataone.org/#view/> .
@prefix pext: <http://proton.semanticweb.org/protonext#> .
@prefix psys: <http://proton.semanticweb.org/protonsys#> .
@prefix datacite: <http://purl.org/spar/datacite/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix d1org: <http://dataone.org/organization/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix geolink: <http://schema.geolink.org/base/main#> .
@prefix d1person: <http://dataone.org/person/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix d1node: <https://cn.dataone.org/cn/v1/node/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix d1dataset: <http://dataone.org/dataset/> .

<http://dataone.org/dataset/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1>
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
        geolink:isPartOf <http://dataone.org/dataset/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1> ;
        a geolink:DigitalObject
    ] ;
    geolink:hasStartDate "1991-01-01T00:00:00Z" ;
    a geolink:Dataset ;
    rdfs:label "91n1nuts.txt" .

<http://dataone.org/person/urn:uuid:78d79a39-3aef-4bad-a011-e3fd2c5466f5>
    geolink:isCreatorOf <http://dataone.org/dataset/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1> ;
    geolink:nameFamily "Miller" ;
    geolink:nameFull "Mike Miller" ;
    geolink:nameGiven "Mike" ;
    a geolink:Person .
```
