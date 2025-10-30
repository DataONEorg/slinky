# examples/sasap

https://search.dataone.org/view/doi%3A10.5063%2F154FGN

Why it's a good test:

- Has annotations SASAP pattern
- Package with sorta more files than usual

```ttl
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix d1d: <https://dataone.org/datasets/> .
@prefix d1o: <https://dataone.org/organizations/> .
@prefix d1p: <https://dataone.org/people/> .
@prefix dataone: <https://dataone.org/> .
@prefix odo: <http://purl.dataone.org/odo/> .
@prefix so: <http://schema.org/> .
@prefix spd: <http://spdx.org/rdf/terms#> .

d1d:doi%3A10.5063%2F154FGN a so:Dataset ;
  so:name "North Pacific salmon abundance, 1925-2015" ;
  so:description """Abundance estimates of wild and hatchery Pacific salmon Oncorhynchus spp. are important for evaluation of stock status and density-dependent interactions at sea. This data package includes total abundances of pink, chum, and sockeye salmon, reconstructed from catch and spawning abundance data for both Asia and North America. These data are in two main categories of salmon abundance estimates: (1) return (catch plus escapement) estimates of natural-origin and enhanced-origin salmon (numerical and biomass) by species and region, and (2) Total biomass estimates of mature and younger salmon by species and region (natural-origin and hatchery-origin combined). Most of the tables cover the period from 1952-2015. Longterm tables begin at 1925. The .csv files are plain text versions of the tables found in the original excel file. The excel file also contains additional information on how the datasets can be used.
       These data are described further in: Ruggerone, G.T., Peterman, R.M., Dorner, B., Myers, K.W. (2010). Magnitude and trends in abundance of hatchery and wild pink salmon, chum salmon, and sockeye salmon in the North Pacific Ocean. Marine and Coastal Fisheries: Dynamics, Management, and Ecosystem Science 2:306–328 (available at http://www.bioone.org/doi/full/10.1577/C09-054.1). They are also included as Supporting Information in Ruggerone, G.T. &amp;amp;amp; Irvine, J.R. (2018). Numbers and Biomass of Natural- and Hatchery-Origin Pink Salmon, Chum Salmon, and Sockeye Salmon in the North Pacific Ocean, 1925–2015. Marine and Coastal Fisheries: Dynamics, Management, and Ecosystem Science 10:152–168 (available at https://onlinelibrary.wiley.com/doi/full/10.1002/mcf2.10023). The dataset here is the same version as in the SI of Ruggerone &amp;amp;amp; Irvine 2018, in the form of extracted .csv's.""" ;
  so:url "https://dataone.org/datasets/doi%3A10.5063%2F154FGN" ;

  so:identifier [
    a so:PropertyValue ;
    so:propertyID "https://registry.identifiers.org/registry/doi" ;
    so:url "https://doi.org/doi%3A10.5063%2F154FGN" ;
    so:value "10.5063/154FGN" ;
  ] ;
  so:sameAs "https://doi.org/10.5063%2F154FGN" ;

  so:award """State of Alaska's Salmon and People (Gordon and Betty Moore Foundation Award 5124)
         Data Task Forces for Better Synthesis Studies (Gordon and Betty Moore Foundation Award 5451)""" ;

  so:creator d1p:urn%3Auuid%3A29675ce3-45fa-4179-a34f-f045cd209166 ;
  so:creator d1p:urn%3Auuid%3Aa14ee844-3b17-4353-be71-5491f0fe3677 ;

  so:dateModified "2021-08-23T03:26:07.117000Z" ;
  so:datePublished "2018-03-26" ;

  so:distribution d1d:urn%3Auuid%3A19bedae0-6591-460b-9617-f4bcd14aa469 ;
  so:distribution d1d:urn%3Auuid%3A69bd6a26-213a-407c-bc91-55384a60bbe1 ;
  so:distribution d1d:urn%3Auuid%3A6dc1b447-8f85-469e-8980-00e405f81524 ;
  so:distribution d1d:urn%3Auuid%3A9d62b615-636a-4ce2-a424-04103dc04d79 ;
  so:distribution d1d:urn%3Auuid%3Aaf2dc8a5-d39b-4487-aea6-6cb6cd336231 ;
  so:distribution d1d:urn%3Auuid%3Ab7ea45ef-45a7-4f98-a739-3f3330d71a3e ;
  so:distribution d1d:urn%3Auuid%3Ac4307fe3-d42a-4013-b519-9e3d46fcb6b6 ;
  so:distribution d1d:urn%3Auuid%3Afd192190-47fc-454e-8ac3-452581e5825a ;
  so:distribution d1d:urn%3Auuid%3Afdf90e56-fbb0-4675-8622-d5ca4c23765d ;

  so:keyword "featured" ;
  so:keyword "ocean climate" ;
  so:keyword "ocean distribution" ;

  so:spatialCoverage [
    a so:Place ;
    so:additionalProperty [
      a so:PropertyValue ;
      so:name "Spatial Reference System" ;
      so:propertyID <http://www.wikidata.org/entity/Q4018860> ;
      so:value "http://www.opengis.net/def/crs/OGC/1.3/CRS84" ;
    ] ;
    so:additionalProperty [
      a so:PropertyValue ;
      so:name "Well-Known Text (WKT) representation of geometry" ;
      so:propertyID <http://www.wikidata.org/entity/Q4018860> ;
      so:value "POLYGON ((130.0000 40.0000, -120.0000 40.0000, -120.0000 65.0000, 130.0000 65.0000, 130.0000 40.0000))" ;
    ] ;
    so:description "Northern Pacific Ocean" ;
    so:geo [
      a so:GeoShape ;
      so:box "40.0000,-120.0000 65.0000,130.0000" ;
    ] ;
  ] ;
  so:temporalCoverage "1925/2015" ;


  so:variableMeasured [
    a so:PropertyValue ;
    so:description "Year that abundance data are from" ;
    so:name "Year" ;
    so:propertyID odo:ECSO_00002050 ;
  ] ;

  so:byteSize 580266 ;
  so:wasRevisionOf "https://dataone.org/datasets/doi%3A10.5063%2FF1Z899P0" ;
  so:schemaVersion "https://eml.ecoinformatics.org/eml-2.2.0" ;
  so:isAccessibleForFree true ;
  spd:checksum [
    a spd:Checksum ;
    spd:checksumValue "dada440cc2f8e712aef75b47fd14d271303224cf" ;
  ] .

d1d:doi%3A10.5063%2F154FGN%23dataTable10_spp odo:salmon_000828 odo:salmon_000241 .

d1d:doi%3A10.5063%2F154FGN%23dataTable11_spp odo:salmon_000828 odo:salmon_000242 .

d1d:doi%3A10.5063%2F154FGN%23dataTable12_spp odo:salmon_000828 odo:salmon_000240 ;
  odo:salmon_000828 odo:salmon_000241 ;
  odo:salmon_000828 odo:salmon_000242 .

d1d:doi%3A10.5063%2F154FGN%23dataTable13_spp odo:salmon_000828 odo:salmon_000240 .

d1d:doi%3A10.5063%2F154FGN%23dataTable14_spp odo:salmon_000828 odo:salmon_000241 .

d1d:doi%3A10.5063%2F154FGN%23dataTable15_spp odo:salmon_000828 odo:salmon_000242 .

d1d:doi%3A10.5063%2F154FGN%23dataTable16_spp odo:salmon_000828 odo:salmon_000240 ;
  odo:salmon_000828 odo:salmon_000241 ;
  odo:salmon_000828 odo:salmon_000242 .

d1d:doi%3A10.5063%2F154FGN%23dataTable17_spp odo:salmon_000828 odo:salmon_000240 .

d1d:doi%3A10.5063%2F154FGN%23entity10_attribute_CI <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl%23containsMeasurementsOfType> odo:salmon_000504 .

d1d:doi%3A10.5063%2F154FGN%23entity10_attribute_EKam <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl%23containsMeasurementsOfType> odo:salmon_000504 .

d1d:doi%3A10.5063%2F154FGN%23entity10_attribute_Japan <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl%23containsMeasurementsOfType> odo:salmon_000504 .

d1d:doi%3A10.5063%2F154FGN%23entity10_attribute_Kod <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl%23containsMeasurementsOfType> odo:salmon_000504 .

d1d:doi%3A10.5063%2F154FGN%23entity10_attribute_Korea <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl%23containsMeasurementsOfType> odo:salmon_000504 .

d1d:doi%3A10.5063%2F154FGN%23entity10_attribute_M%26I <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl%23containsMeasurementsOfType> odo:salmon_000504 .

d1d:doi%3A10.5063%2F154FGN%23entity10_attribute_NBC <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl%23containsMeasurementsOfType> odo:salmon_000504 .

d1d:doi%3A10.5063%2F154FGN%23entity10_attribute_PWS <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl%23containsMeasurementsOfType> odo:salmon_000504 .

d1d:doi%3A10.5063%2F154FGN%23entity10_attribute_SBC <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl#containsMeasurementsOfType> odo:salmon_000504 .

d1d:urn%3Auuid%3A19bedae0-6591-460b-9617-f4bcd14aa469 a so:DataDownload ;
  so:byteSize 4722 ;
  so:contentUrl "https://search.dataone.org/cn/v2/resolve/urn%3Auuid%3A19bedae0-6591-460b-9617-f4bcd14aa469" ;
  so:dateModified "2018-03-29T19:00:02.049000Z" ;
  so:datePublished "2018-03-26T19:49:23.018000Z" ;
  so:encodingFormat "text/csv" ;
  so:identifier "https://dataone.org/datasets/urn%3Auuid%3A19bedae0-6591-460b-9617-f4bcd14aa469" ;
  so:name "Nat-origin-ret_pink.csv" ;
  spd:checksum [
    a spd:Checksum ;
    spd:checksumValue "2ec43b7d48e0c017f8066521c71d4e3fa8a5c6b6" ;
  ] .

d1o:urn%3Auuid%3A32a33943-e126-4847-b04a-e3b232656ca4 a so:Organization ;
  so:name "Natural Resources Consultants, Inc." .

d1o:urn%3Auuid%3Ad52f9bac-2c78-46b1-9c6c-c774d479d657 a so:Organization ;
  so:name "Fisheries and Oceans Canada" .

d1p:urn%3Auuid%3A29675ce3-45fa-4179-a34f-f045cd209166 a so:Person ;
  so:affiliation d1o:urn%3Auuid%3Ad52f9bac-2c78-46b1-9c6c-c774d479d657 ;
  so:name "Jim Irvine" .

d1p:urn%3Auuid%3Aa14ee844-3b17-4353-be71-5491f0fe3677 a so:Person ;
  so:affiliation d1o:urn%3Auuid%3A32a33943-e126-4847-b04a-e3b232656ca4 ;
  so:name "Greg Ruggerone" .
```
