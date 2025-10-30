# examples/mosaic

https://search.dataone.org/view/doi%3A10.18739%2FA2M03XZ32

Why it's a good test:

- Has MOSAIC annotations
- Has EML 2.2.0 award info

## Abridged Output

```ttl
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix d1d: <https://dataone.org/datasets/> .
@prefix d1o: <https://dataone.org/organizations/> .
@prefix d1p: <https://dataone.org/people/> .
@prefix dataone: <https://dataone.org/> .
@prefix odo: <http://purl.dataone.org/odo/> .
@prefix odos: <https://purl.dataone.org/odo/> .
@prefix so: <http://schema.org/> .
@prefix spd: <http://spdx.org/rdf/terms#> .

d1d:doi%3a10.18739%2FA2M03XZ32 a so:Dataset ;
  so:name "Arctic sea ice thermal emission measurements from the Ultra Wideband Microwave Radiometer (UWBRAD) at the Multidisciplinary drifting Observatory for the Study of Arctic Climate (MOSAiC) Expedition in December 2019" ;
  so:award "National Science Foundation #1838401 (Monitoring Sea Ice Evolution with Ultrawideband Microwave Radiometry in the MoSAIC Campaign)" ;
  so:identifier [
    a so:PropertyValue ;
    so:propertyID "https://registry.identifiers.org/registry/doi" ;
    so:url "https://doi.org/doi%3A10.18739%2FA2M03XZ32" ;
    so:value "10.18739/A2M03XZ32" ;
  ] ;
  so:description "The Multidisciplinary drifting Observatory for the Study of Arctic Climate (MOSAiC) Expedition was conducted to investigate the Arctic processes and evolution of ocean-ice-atmosphere system in the polar region throughout a year. The campaign began in October 2019 when Polarstern moored to an ice floe measuring roughly 2.8 x 3.8 kilometers in the north of the Laptev Sea. The ice floe was estimated to have formed in the north of the New Siberian Islands at the beginning of December 2018, and survived the summer melt during its Transpolar Drift towards the central Arctic. A science camp was established on the drifting ice floe for comprehensive measurements from diverse research groups. The Ultra Wideband Microwave Radiometer (UWBRAD) was also deployed on the ice at the remote sensing site in the camp, and performed measurements over the period December 4-13, 2019. It monitored a refrozen melt pond in oblique angles to measure thermal emission signatures at frequencies 540, 900, 1380 and 1740 megahertz. The instrument was installed on a stationary telescoping mast that can be manually adjusted to different heights. The direction of antenna was controlled by a programmable rotator unit which allowed it both to monitor sea ice from a desired oblique angle and to perform periodic upward looking sky measurements for calibration. The collected data provided the opportunity to investigate the effect of ice evolution in the winter season on the measured wideband brightness temperatures so that the sea ice emission models can be improved for satellite-borne remote sensing instruments." ;

  so:creator d1p:urn%3auuid%3a6b204340-f431-4c93-bb4c-98abd4275663 ;
  so:creator d1p:urn%3auuid%3af59a8585-6209-4370-8ba9-a7a6764f72a0 ;

  so:dateModified "2021-08-26T00:19:03.335000Z" ;
  so:datePublished "2021" ;

  so:distribution d1d:urn%3auuid%3a421f76a6-c95e-4b86-8198-969e898cb185 ;

  so:isAccessibleForFree true ;

  so:keyword "MOSAiC" ;
  so:keyword "Radiometer" ;
  so:keyword "Sea ice" ;
  so:keyword "UWBRAD" ;

  so:publisher d1o:urn%3auuid%3ab75070b7-3833-41de-b237-5992ea8ea724 ;

  so:sameAs "https://doi.org/10.18739%2FA2M03XZ32" ;
  so:schemaVersion "https://eml.ecoinformatics.org/eml-2.2.0" ;
  so:byteSize 216355 ;

  so:spatialCoverage [
    a so:Place ;
    so:additionalProperty [
      a so:PropertyValue ;
      so:name "Well-Known Text (WKT) representation of geometry" ;
      so:propertyID <http://www.wikidata.org/entity/Q4018860> ;
      so:value "POLYGON ((118.2 86.59, 122 86.59, 122 86.09, 118.2 86.09, 118.2 86.59))" ;
    ] ;
    so:additionalProperty [
      a so:PropertyValue ;
      so:name "Spatial Reference System" ;
      so:propertyID <http://www.wikidata.org/entity/Q4018860> ;
      so:value "http://www.opengis.net/def/crs/OGC/1.3/CRS84" ;
    ] ;
    so:description "Arctic Ocean close to the North Pole" ;
    so:geo [
      a so:GeoShape ;
      so:box "86.59,122 86.09,118.2" ;
    ] ;
  ] ;
  so:temporalCoverage "2019-12-04/2020-06-30" ;
  so:url "https://dataone.org/datasets/doi%3A10.18739%2FA2M03XZ32" ;
  so:variableMeasured [
    a so:PropertyValue ;
    so:description "Describes the given latitude in terms of North/South" ;
    so:name "N/S" ;
  ] ;
  so:variableMeasured [
    a so:PropertyValue ;
    so:description "Height of the antenna from the ice surface in meters" ;
    so:name "Antenna Height" ;
    so:propertyID odo:ECSO%3A00001252 ;
  ] ;
  so:wasRevisionOf "https://dataone.org/datasets/doi%3A10.18739%2FA23F4KP3J" ;
  spd:checksum [
    a spd:Checksum ;
    spd:checksumValue "dd75fdcb25012e76de12171e25e4f6830c673bf3f8c3bc804bf16a9d7a4eee56" ;
  ] .

d1d:doi%3a10.18739%2FA2M03XZ32#Demir odos:MOSAIC%3A00000025 odos:MOSAIC%3A00000023 ;
  odos:MOSAIC%3A00000032 odos:MOSAIC%3A00000017 ;
  odos:MOSAIC%3A00000034 odos:MOSAIC%3A00000030 .

d1d:doi%3a10.18739%2FA2M03XZ32#table1%3Aatt1 <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl#containsMeasurementsOfType> odo:ECSO%3A00001157 .

d1d:doi%3a10.18739%2FA2M03XZ32#table1%3Aatt10 <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl#containsMeasurementsOfType> odo:ECSO%3A00002092 ;
  <http://www.w3.org/ns/prov#wasGeneratedBy> odos:MOSAIC%3A00003258 ;
  odos:MOSAIC%3A00002201 odos:MOSAIC%3A00001163 .

d1d:urn%3auuid%3a421f76a6-c95e-4b86-8198-969e898cb185 a so:DataDownload ;
  so:byteSize 167849 ;
  so:contentUrl "https://search.dataone.org/cn/v2/resolve/urn%3Auuid%3A421f76a6-c95e-4b86-8198-969e898cb185" ;
  so:dateModified "2021-06-29T19:59:49.033000Z" ;
  so:datePublished "2021-02-28T02:59:26.894000Z" ;
  so:encodingFormat "application/octet-stream" ;
  so:identifier "https://dataone.org/datasets/urn%3Auuid%3A421f76a6-c95e-4b86-8198-969e898cb185" ;
  so:name "UWBRAD_Mosaic_leg1.dat" ;
  spd:checksum [
    a spd:Checksum ;
    spd:checksumValue "ee6b5bf15290f95e0a3287a66a1523f8" ;
  ] .

d1o:urn%3auuid%3ae099fadd-9c79-4825-9c80-bc415f336a5a a so:Organization ;
  so:name "The Ohio State University" .

d1p:urn%3auuid%3a6b204340-f431-4c93-bb4c-98abd4275663 a so:Person ;
  so:affiliation d1o:urn%3auuid%3ae099fadd-9c79-4825-9c80-bc415f336a5a ;
  so:email "johnson.1374@osu.edu" ;
  so:identifier [
    a so:PropertyValue ;
    so:propertyID "https://orcid.org" ;
    so:url "https://orcid.org/0000-0002-6921-6059" ;
    so:value "0000-0002-6921-6059" ;
  ] ;
  so:name "Joel Johnson" .
```

## People

Issues:

- [ ] identifier propertyID should be a URI, should URL?

```ttl
d1d:doi%3a10.18739%2FA2M03XZ32 a so:Dataset ;
  so:creator d1p:urn%3auuid%3a6b204340-f431-4c93-bb4c-98abd4275663 ;

d1p:urn%3auuid%3a6b204340-f431-4c93-bb4c-98abd4275663 a so:Person ;
  so:name "Joel Johnson" .
  so:affiliation d1o:urn%3auuid%3ae099fadd-9c79-4825-9c80-bc415f336a5a ;
  so:email "johnson.1374@osu.edu" ;
  so:identifier [
    a so:PropertyValue ;
    so:propertyID "https://orcid.org" ;
    so:url "https://orcid.org/0000-0002-6921-6059" ;
    so:value "0000-0002-6921-6059" ;
  ] ;
```

## Organization

Issues:

- [ ] identifier triple seems wonky

```ttl
d1d:doi%3a10.18739%2FA2M03XZ32 a so:Dataset ;
  so:publisher d1o:urn%3auuid%3ab75070b7-3833-41de-b237-5992ea8ea724 ;

d1o:urn%3auuid%3ab75070b7-3833-41de-b237-5992ea8ea724 a so:Organization ;
  so:name "NSF Arctic Data Center" .
  so:email "support@arcticdata.io" ;
  so:identifier [
    a so:PropertyValue ;
    so:propertyID "https://orcid.org" ;
    so:url "https://www.wikidata.org/" ;
    so:value [];
  ] ;
```

## Files in a package

Issues

- [ ] Missing checksum algo

```ttl
d1d:doi%3a10.18739%2FA2M03XZ32 a so:Dataset ;
  so:distribution d1d:urn%3auuid%3a421f76a6-c95e-4b86-8198-969e898cb185 ;

d1d:urn%3auuid%3a421f76a6-c95e-4b86-8198-969e898cb185 a so:DataDownload ;
  so:byteSize 167849 ;
  so:contentUrl "https://search.dataone.org/cn/v2/resolve/urn%3Auuid%3A421f76a6-c95e-4b86-8198-969e898cb185" ;
  so:dateModified "2021-06-29T19:59:49.033000Z" ;
  so:datePublished "2021-02-28T02:59:26.894000Z" ;
  so:encodingFormat "application/octet-stream" ;
  so:identifier "https://dataone.org/datasets/urn%3Auuid%3A421f76a6-c95e-4b86-8198-969e898cb185" ;
  so:name "UWBRAD_Mosaic_leg1.dat" ;
  spd:checksum [
    a spd:Checksum ;
    spd:checksumValue "ee6b5bf15290f95e0a3287a66a1523f8" ;
  ] .
```
