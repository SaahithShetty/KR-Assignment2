#! /usr/bin/python

import sys
from py4j.java_gateway import JavaGateway

def main():
    # Check command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python el_reasoner.py ONTOLOGY_FILE CLASS_NAME")
        sys.exit(1)

    ontology_file = sys.argv[1]
    class_name = sys.argv[2]

    # Connect to the Java gateway of dl4python
    gateway = JavaGateway()

    # Get a parser from OWL files to DL ontologies
    parser = gateway.getOWLParser()

    # Get a formatter for DL concepts
    formatter = gateway.getSimpleDLFormatter()

    # Load the ontology
    try:
        ontology = parser.parseFile(ontology_file)
    except Exception as e:
        print(f"Error loading ontology file {ontology_file}: {e}")
        sys.exit(1)

    # Convert conjunctions to binary format
    gateway.convertToBinaryConjunctions(ontology)

    # Create EL concepts and use the ELK reasoner
    elk = gateway.getELKReasoner()
    elFactory = gateway.getELFactory()

    try:
        target_class = elFactory.getConceptName(class_name)
    except Exception as e:
        print(f"Error finding class {class_name} in ontology: {e}")
        sys.exit(1)

    try:
        elk.setOntology(ontology)
        subsumers = elk.getSubsumers(target_class)
    except Exception as e:
        print(f"Error reasoning with ELK: {e}")
        sys.exit(1)

    # Output subsumers, one class name per line
    for concept in subsumers:
        print(formatter.format(concept))

if __name__ == "__main__":
    main()