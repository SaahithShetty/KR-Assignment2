#! /usr/bin/python

import sys
from py4j.java_gateway import JavaGateway

def load_ontology(gateway, ontology_file):
    """Load the ontology using the dl4python parser."""
    parser = gateway.getOWLParser()
    try:
        ontology = parser.parseFile(ontology_file)
        print(f"Ontology '{ontology_file}' loaded successfully.")
        return ontology
    except Exception as e:
        print(f"Error loading ontology: {e}")
        sys.exit(1)

def compute_subsumers(gateway, ontology, class_name):
    """Compute all subsumers for the given class name."""
    elk = gateway.getELKReasoner()
    elk.setOntology(ontology)
    
    elFactory = gateway.getELFactory()
    formatter = gateway.getSimpleDLFormatter()

    try:
        target_class = elFactory.getConceptName(class_name)
        subsumers = elk.getSubsumers(target_class)
        return [formatter.format(subsumer) for subsumer in subsumers]
    except Exception as e:
        print(f"Error computing subsumers for '{class_name}': {e}")
        sys.exit(1)

def main():
    # Validate command-line arguments
    if len(sys.argv) != 3:
        print("Usage: PROGRAM_NAME ONTOLOGY_FILE CLASS_NAME")
        sys.exit(1)

    ontology_file = sys.argv[1]
    class_name = sys.argv[2]

    # Connect to the Java gateway
    try:
        gateway = JavaGateway()
    except Exception as e:
        print(f"Error connecting to Java gateway: {e}")
        sys.exit(1)

    # Load ontology
    ontology = load_ontology(gateway, ontology_file)

    # Compute subsumers
    subsumers = compute_subsumers(gateway, ontology, class_name)

    # Output each subsumer on a new line
    for subsumer in subsumers:
        print(subsumer)

if __name__ == "__main__":
    main()