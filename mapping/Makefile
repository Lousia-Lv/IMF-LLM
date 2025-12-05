.PHONY: all run-geofuseki run-fuseki


JENA-version = apache-jena-4.10.0
JENA = software/$(JENA-version)
$(JENA):
	mkdir -p software
	wget https://archive.apache.org/dist/jena/binaries/$(JENA-version).zip -O $@.zip
	unzip -u $@.zip -d software

FUSEKI-version = apache-jena-fuseki-4.10.0
FUSEKI = software/$(FUSEKI-version)
$(FUSEKI):
	mkdir -p software
	wget https://archive.apache.org/dist/jena/binaries/$(FUSEKI-version).zip -O $@.zip
	unzip -u $@.zip -d software

GEOSPARQL = software/jena-fuseki-geosparql-4.9.0.jar
$(GEOSPARQL):
	mkdir -p $(@D)
	wget https://repo1.maven.org/maven2/org/apache/jena/jena-fuseki-geosparql/4.9.0/jena-fuseki-geosparql-4.9.0.jar -O $@

LUTRA = software/lutra.jar
$(LUTRA):
	mkdir -p $(@D)
	wget https://ottr.xyz/downloads/lutra/lutra-master.jar -O $@

install: \
	$(JENA) \
	$(LUTRA)


imf-model.ttl: bottr-map.ttl templates.stottr $(wildcard llm-extracted-data/*.csv)
	java -jar $(LUTRA) -f -l templates.stottr -I bottr bottr-map.ttl -o $@.temp
	$(JENA)/bin/riot --syntax TTL --formatted TTL $@.temp > $@
	rm $@.temp


# Load SPARQL endpoint RDF data into TBD (SPARQL endpoint database):
#data/%.tdb: data/.%.tdb-data.nt
#	$(JENA)/bin/tdbloader --loc=$@ $^

all: imf-model.ttl
