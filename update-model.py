# %%
# notebook for testing 

from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
import argparse

# %%
def get_points(graph):
    
    points = dict()
    
    points['observables'] = []
    points['actuatables'] = []
    points['just_quantifiables'] = []

    for subject, _, obj in graph.triples((None, RDF.type, S223.QuantifiableObservableProperty)):
        points['observables'].append(subject)

    for subject, _, obj in graph.triples((None, RDF.type, S223.QuantifiableActuatableProperty)):
        points['actuatables'].append(subject)

    for subject, _, obj in graph.triples((None, RDF.type, S223.QuantifiableProperty)):
        points['just_quantifiables'].append(subject)

    return points

# %%
def increase_by_one():
    number = 0
    while True: 
        yield number
        number += 1

# %%
def add_bacnet_ref(model, graph, id_counter, point, bacnet_type):
    
    # graph and model separate just for debugging

    # could do this based on label alternatively to uri 
    point_name = point.rsplit('/')[-1]

    ref_name = point_name + '_bacnet'
    graph.add((BLDG[ref_name], RDF.type, REF.BACnetReference))
    graph.add((BLDG[ref_name], BACNET['object-type'], Literal(bacnet_type)))
    
    id_num = next(id_counter)
    graph.add((BLDG[ref_name], BACNET['object-identifier'], Literal(f"{bacnet_type},{id_num}")))
    graph.add((BLDG[ref_name], BACNET['object-name'], Literal(point_name)))
    graph.add((BLDG[ref_name], BACNET['objectOf'], BLDG['boptest-proxy']))

    # Not necessary
    # unit = model.value(point, QUDT.hasUnit)
    # unit_name = unit.rsplit('/')[-1]

    # graph.add((BLDG[ref_name], BACNET['units'],Literal(unit_name)))

    graph.add((point, REF.hasExternalReference, BLDG[ref_name]))

# %%
def add_bacnet_device(graph, device_id):
    graph.add((BLDG['boptest-proxy'], RDF.type, BACNET.BACnetDevice))
    graph.add((BLDG['boptest-proxy'], BACNET['device-instance'], Literal(599)))

# %%
graph = Graph()

BLDG = Namespace("urn:bldg/")
graph.bind("bldg", BLDG)

REF = Namespace("https://brickschema.org/schema/Brick/ref#")
graph.bind("ref", REF)

BACNET = Namespace("http://data.ashrae.org/bacnet/2020#")
graph.bind("bacnet", BACNET)

S223 = Namespace("http://data.ashrae.org/standard223#")
graph.bind("s223", S223)

QUDT = Namespace("http://qudt.org/schema/qudt/")
graph.bind("qudt", QUDT)

# %%

def main():
 
    parser = argparse.ArgumentParser(description="update a 223P model with BACnet references")

    parser.add_argument('model_file', type=str, help='223P model that defines the site, a ttl file')
    parser.add_argument('out_file', type=str, help="output file name")
    parser.add_argument('--device_id', type=int, default=599, help="device ID for bacnet device")

    # TODO: add other addressing information? 
    
    args = parser.parse_args()

    model = Graph()

    model.parse(args.model_file, format = "ttl")
    points = get_points(model)

    id_counter = increase_by_one()

    add_bacnet_device(model, args.device_id)

    for point in points['actuatables']:
        add_bacnet_ref(model, model, id_counter, point, "analog-output")

    for point in points['observables']:
        add_bacnet_ref(model, model, id_counter, point, "analog-input")

    for point in points['just_quantifiables']:
        add_bacnet_ref(model, model, id_counter, point, "analog-value")

    # model.serialize(args.model_file.replace('.ttl', '_bacnet.ttl'))
    model.serialize(args.out_file, format = 'ttl')

if __name__ == "__main__":
    main()




# %%
