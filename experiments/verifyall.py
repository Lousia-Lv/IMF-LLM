import os, json
from rdflib import Graph

path_rdfref = '2-modified\initialmodification.rdf.ttl'
path_rdftarget = '1-generated rdfs\generated.rdf.ttl'
# path_rdfref = 'codes\0-ground truth\TennesseeEastmanProcess_attributes.rdf.ttl'
# path_rdftarget = 'codes\1-generated rdfs\20250522imf-model.ttl'

# %%
def read_rdf(path_rdf,verbose=1):
    if verbose:
        print(f'Reading rdf: {path_rdf}')
    g = Graph()
    g.parse(path_rdf, format='turtle')
    return g

def calculate_metrics(ref, target, verbose=0):
    true_positive = ref & target   # elements that match in both graphs.
    false_positive = target - ref   # elements only in the target graph.
    false_negative = ref - target   # elements only in the reference graph.

    # Calculate evaluation metrics.
    TP = len(true_positive)
    FP = len(false_positive)
    FN = len(false_negative)
    num_blockstarget = len(target)

    # Define accuracy as the ratio of correctly predicted blocks over all target blocks
    accuracy = TP / num_blockstarget if num_blockstarget > 0 else 0
    # Compute precision and recall.
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    # Compute F1 score.
    F1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"True Positives (present in both): {TP}, False Positives (only in target): {FP}, False Negatives (only in reference): {FN}")
    # print("False Positives (present only in target):", len(false_positive))
    # print("False Negatives (present only in reference):", len(false_negative))
    # Print the evaluation metrics.
    print("Evaluation Metrics:")
    print(f"Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1 score: {F1}")
    # print("Precision:", precision,)
    # print("Recall:", recall,)
    # print("F1 score:", F1)

    if verbose:
        # Optionally, print the actual matching details:
        print("\nDetails:")
        print("True Positives:", true_positive)
        print("False Positives:", false_positive)
        print("False Negatives:", false_negative)
    return accuracy, precision, recall, F1

def verify_block(gref,gtarget,aspect='',match_aspect=1,verbose=0):
    if aspect:
        print(f"\n*** Verifying blocks of {aspect} ***")
        cquery = f"""
        SELECT ?x ?a ?l
        WHERE {{
            ?x rdf:type imf:Block .
            ?x imf:hasAspect imf:{aspect} .
            ?x skos:prefLabel ?l .
        }}
        """
    else:
        print(f"\n*** Verifying blocks of all aspects ***")
        cquery = """
        SELECT ?x ?a ?l
        WHERE {
            ?x rdf:type imf:Block .
            ?x imf:hasAspect ?a .
            ?x skos:prefLabel ?l .
        }
        """
    ref_results = gref.query(cquery)
    target_results = gtarget.query(cquery)

    if match_aspect:        # When matching both, use a tuple of (block label, aspect).
        ref_blocks = {(str(row.l), str(row.a)) for row in ref_results}
        target_blocks = {(str(row.l), str(row.a)) for row in target_results}
    else:         # Otherwise, only compare block labels.
        ref_blocks = {str(row.l) for row in ref_results}
        target_blocks = {str(row.l) for row in target_results}

    # Print out the results.
    if match_aspect:
        print("Comparing both block name and aspect:")
    else:
        print("Comparing only block name:")

    calculate_metrics(ref_blocks, target_blocks, verbose=0)
    return ref_blocks, target_blocks

def verify_relation(gref,gtarget,relation='',aspect='',verbose=0):
    if aspect:
        print(f"\n*** Verifying the relation {relation} of {aspect} ***")
        cquery = f"""
        SELECT ?hl ?tl
        WHERE {{
            ?h imf:{relation} ?t .
            ?h imf:hasAspect imf:{aspect} .
            ?h skos:prefLabel ?hl . 
            ?t skos:prefLabel ?tl . 
        }}
        """
    else:
        print(f"\n*** Verifying the relation {relation} of all aspects ***")
        cquery = f"""
        SELECT ?hl ?tl
        WHERE {{
            ?h imf:{relation} ?t .
            ?h skos:prefLabel ?hl . 
            ?t skos:prefLabel ?tl . 
        }}
        """
    ref_results = gref.query(cquery)
    target_results = gtarget.query(cquery)

    ref_edge = {(str(row.hl), f'imf:{relation}', str(row.tl)) for row in ref_results}
    target_edge = {(str(row.hl), f'imf:{relation}', str(row.tl)) for row in target_results}
    calculate_metrics(ref_edge, target_edge)
    return ref_edge, target_edge

def verify_parameter(gref,gtarget,verbose=0):
    print("\n*** Verifying attributes of product blocks ***")
    cquery = """
    SELECT ?blocklabel ?attr ?predicate
    WHERE {
        ?block rdf:type imf:Block .
        ?block imf:hasAspect imf:productAspect .
        ?block imf:hasAttribute ?attr .
        ?block skos:prefLabel ?blocklabel . 
        ?attr rdf:type imf:Attribute .
        ?attr imf:predicate ?predicate
    }
    """
    ref_results = gref.query(cquery)
    target_results = gtarget.query(cquery)
    ref_results = gref.query(cquery)
    target_results = gtarget.query(cquery)

    ref_attr = {(str(row.blocklabel), str(row.predicate)) for row in ref_results}
    target_attr = {(str(row.blocklabel), str(row.predicate)) for row in target_results}
    calculate_metrics(ref_attr, target_attr, verbose=verbose)
    return ref_attr, target_attr

gref = read_rdf(path_rdfref)
gtarget = read_rdf(path_rdftarget)

# %% verify everything

# verify blocks
aspectf = 'functionAspect'
aspectp = 'productAspect'
ref_blocks, target_blocks = verify_block(gref,gtarget,aspect=aspectf,match_aspect=1,verbose=0)
ref_blocks, target_blocks = verify_block(gref,gtarget,aspect=aspectp,match_aspect=1,verbose=0)
ref_blocks, target_blocks = verify_block(gref,gtarget,aspect='',match_aspect=1,verbose=0)

# verify parameters
ref_attr, target_attr = verify_parameter(gref,gtarget)

# verify relations
relationf = 'fulfilledBy'
relationc = 'connectedTo'
relationp = 'partOf'
ref_edgef, target_edgef = verify_relation(gref,gtarget,relation=relationf,aspect='',verbose=0) # fulfilledBy
ref_edgec, target_edgec = verify_relation(gref,gtarget,relation=relationc,aspect='',verbose=0) # connected±To
ref_edgepf, target_edgepf = verify_relation(gref,gtarget,relation=relationp,aspect=aspectf,verbose=0) # subfunction
ref_edgepp, target_edgepp = verify_relation(gref,gtarget,relation=relationp,aspect=aspectp,verbose=0) # subproduct
print("\n*** Verifying all relations ***")
ref_edgemerge = ref_edgef.union(ref_edgec, ref_edgepf, ref_edgepp)
target_edgemerge = target_edgef.union(target_edgec, target_edgepf, target_edgepp)
calculate_metrics(ref_edgemerge,target_edgemerge)
