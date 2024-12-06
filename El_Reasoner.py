#! /usr/bin/python

import sys
from py4j.java_gateway import JavaGateway, GatewayParameters

def main():
    # Check command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python el_reasoner.py ONTOLOGY_FILE CLASS_NAME")
        sys.exit(1)

    ontology_file = sys.argv[1]
    class_name = sys.argv[2]

    print(f"Loading ontology from file: {ontology_file}")

    # Connect to the Java gateway
    gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_field=True))

    try:
        # Get ontology parser and formatter
        parser = gateway.getOWLParser()
        formatter = gateway.getSimpleDLFormatter()

        # Load ontology
        ontology = parser.parseFile(ontology_file)
        print("Ontology successfully loaded.")
    except Exception as e:
        print(f"Error loading ontology: {e}")
        sys.exit(1)

    print("\nConverting conjunctions to binary format...")
    try:
        gateway.convertToBinaryConjunctions(ontology)
        print("Conjunctions converted.")
    except Exception as e:
        print(f"Error converting conjunctions: {e}")
        sys.exit(1)

    print("\nAll TBox axioms in the ontology:")
    tbox = ontology.tbox()
    for axiom in tbox.getAxioms():
        print(formatter.format(axiom))

    print("\nAvailable classes in the ontology:")
    for concept in ontology.getConceptNames():
        print(" -", formatter.format(concept))

    # Fetch the target class
    elFactory = gateway.getELFactory()
    try:
        target_class = elFactory.getConceptName(class_name)
        print(f"\nClass '{class_name}' found. Proceeding with reasoning...")
    except Exception as e:
        print(f"Error finding class '{class_name}' in ontology: {e}")
        sys.exit(1)

    print(f"\nParent classes for the class '{class_name}':")
    for axiom in tbox.getAxioms():
        if axiom.getClass().getSimpleName() == "GeneralConceptInclusion":
            lhs = formatter.format(axiom.lhs())
            rhs = formatter.format(axiom.rhs())
            if lhs == class_name:
                print(f" - {rhs}")

    # Use ELK reasoner
    elk = gateway.getELKReasoner()
    try:
        elk.setOntology(ontology)
        print("\nOntology set in the reasoner. Computing subsumers...")
        subsumers = elk.getSubsumers(target_class)

        print(f"\nSubsumers for the class '{class_name}':")
        if not subsumers:
            print(f"No subsumers found for the class '{class_name}'.")
        else:
            for concept in subsumers:
                print(" -", formatter.format(concept))
    except Exception as e:
        print(f"Error reasoning with ELK: {e}")
        sys.exit(1)

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