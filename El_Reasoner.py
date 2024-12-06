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

    print(f"Loading ontology from file: {ontology_file}")
    gateway = JavaGateway()  # Connect to the Java gateway of dl4python

    try:
        parser = gateway.getOWLParser()  # Get a parser for OWL files
        formatter = gateway.getSimpleDLFormatter()  # Get a formatter for DL concepts
        ontology = parser.parseFile(ontology_file)  # Load the ontology file
        print("Ontology successfully loaded.")
    except Exception as e:
        print(f"Error loading ontology file {ontology_file}: {e}")
        sys.exit(1)

    print("Converting conjunctions to binary format...")
    try:
        gateway.convertToBinaryConjunctions(ontology)
        print("Conjunctions converted.")
    except Exception as e:
        print(f"Error converting conjunctions: {e}")
        sys.exit(1)

    # Debugging: Print all TBox axioms in the ontology
    print("\nAll TBox axioms in the ontology:")
    tbox = ontology.tbox()
    for axiom in tbox.getAxioms():
        print(formatter.format(axiom))

    # Debugging: Check available classes in the ontology
    print("\nAvailable classes in the ontology:")
    for concept in ontology.getConceptNames():
        print(" -", formatter.format(concept))

    # Get the target class
    elFactory = gateway.getELFactory()
    try:
        target_class = elFactory.getConceptName(class_name)
        print(f"\nClass '{class_name}' found. Proceeding with reasoning...")
    except Exception as e:
        print(f"Error finding class {class_name} in ontology: {e}")
        sys.exit(1)

    # Debugging: Print parent relationships for the target class
    print(f"\nParent classes for the class '{class_name}':")
    for axiom in tbox.getAxioms():
        if axiom.getClass().getSimpleName() == "GeneralConceptInclusion":
            lhs = formatter.format(axiom.lhs())
            rhs = formatter.format(axiom.rhs())
            if lhs == class_name:
                print(f" - {rhs}")

    # Use the ELK reasoner to compute subsumers
    elk = gateway.getELKReasoner()
    try:
        elk.setOntology(ontology)
        print("\nOntology set in the reasoner. Computing subsumers...")
        subsumers = elk.getSubsumers(target_class)
    except Exception as e:
        print(f"Error reasoning with ELK: {e}")
        sys.exit(1)

    # Output all subsumers
    print(f"\nSubsumers for the class '{class_name}':")
    if not subsumers:
        print(f"No subsumers found for the class '{class_name}'.")
    else:
        for concept in subsumers:
            print(" -", formatter.format(concept))

    # Debugging: Print classification results
    print("\nDebugging: Classification results (if available):")
    try:
        classification_result = elk.classify()
        for key, value in classification_result.items():
            print(f"{formatter.format(key)} -> {[formatter.format(v) for v in value]}")
    except Exception as e:
        print(f"Error during classification: {e}")


if __name__ == "__main__":
    main()