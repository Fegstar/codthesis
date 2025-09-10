import sys
import math
import numpy as np
from odbAccess import *
from abaqus import *
from abaqusConstants import *
from scipy.interpolate import UnivariateSpline
from scipy.spatial import distance 
from scipy.spatial.distance import cdist

def extraction_evf_void(odb_path):
    odb = openOdb(odb_path)
    element_set = odb.rootAssembly.instances['MASSIF-1'].elementSets['SET-MASSIF']
    step_name = list(odb.steps.keys())[0]
    step = odb.steps[step_name]
    frame = step.frames[-1]
    field_output = frame.fieldOutputs['EVF_VOID']
    filtered_results = []
    for element in element_set.elements:
        element_values = field_output.getSubset(region=element).values
        for value in element_values:
            filtered_results.append("{}, {}, {}".format(element.label, value.integrationPoint, value.data))
    with open('evf_void_by_element.txt', 'w') as file:
        file.write("Element Label, Integration Point, EVF_VOID\n")
        file.write("\n".join(filtered_results)) 

def detect_elements_isolated(input_file, output_file):
    with open(input_file, "r") as file:
        lines = [line.strip().split(",") for line in file.readlines()[1:]]    
    data = [{'element_label': int(line[0].strip()), 'integration_point': int(line[1].strip()), 'evf_void': float(line[2].strip())} for line in lines]
    isolated_elements = []    
    with open(output_file, "w") as out:
        i = 1
        while i < len(data) - 1:
            if (0.25 < data[i]['evf_void'] < 0.999 and data[i-1]['evf_void'] in [0.0, 1.0] and data[i+1]['evf_void'] in [0.0, 1.0]):
                isolated_elements.append(data[i]['element_label'])
            if (i < len(data) - 2 and 0.25 < data[i]['evf_void'] < 0.99 and 0.25 < data[i+1]['evf_void'] < 0.99 and data[i-1]['evf_void'] in [0.0, 1.0] and data[i+2]['evf_void'] in [0.0, 1.0]):
                isolated_elements.extend([data[i]['element_label'], data[i+1]['element_label']])
                i += 1
            i += 1        
        for label in isolated_elements:
            out.write(f"{label}\n")
        if not isolated_elements:
            out.write("⚠️ Aucun élément trouvé selon les critères.\n")
            print("⚠️ Aucun élément isolé détecté selon les critères définis.")
        else:
            print(f"✅ {len(isolated_elements)} éléments isolés détectés et enregistrés dans {output_file}")

def lire_elements(input_file):
    with open(input_file, "r") as file:
        return [int(line.strip()) for line in file.readlines() if line.strip().isdigit()] 

def get_node_coordinates(odb, element_labels):
    coordinates = []
    part = odb.rootAssembly.instances['MASSIF-1']
    for element_label in element_labels:
        try:
            element = part.getElementFromLabel(element_label)
            for conn_label in element.connectivity:
                node = part.getNodeFromLabel(conn_label)
                coordinates.append((element_label, node.label, node.coordinates))
        except KeyError:
            print(f"Élément {element_label} non trouvé.")
    return coordinates 

def distance_point_droite(p, p1, p2):
    """Calcule la distance d'un point p à la droite définie par p1 et p2."""
    p, p1, p2 = np.array(p), np.array(p1), np.array(p2)
    num = np.linalg.norm(np.cross(p2 - p1, p1 - p))
    den = np.linalg.norm(p2 - p1)
    return num / den if den != 0 else float('inf')

def extraire_coordonnees_odb(odb_path, input_file, output_file):
    odb = openOdb(odb_path)
    instance = odb.rootAssembly.instances['MASSIF-1']    
    element_labels = lire_elements(input_file)
    coordinates = []
    for element_label in element_labels:
        try:
            element = instance.getElementFromLabel(element_label)
            for conn_label in element.connectivity:
                node = instance.getNodeFromLabel(conn_label)
                coordinates.append((element_label, node.label, node.coordinates))
        except KeyError:
            print(f"Élément {element_label} non trouvé.")
    
    # Points de référence pour la droite
    p1 = np.array([ -1.67599e-02, -5.80584e-04,  1.00000e-02])
    p2 = np.array([-1.02747e-02,  4.16034e-02,  1.00000e-02])
    # Classer les points en courbure 1 ou courbure 2
    courbure1 = []
    courbure2 = []
    for element_label, node_label, coords in coordinates:
        distance = distance_point_droite(coords, p1, p2)
        if distance < 0.08:
            courbure1.append((element_label, node_label, coords))
        else:
            courbure2.append((element_label, node_label, coords))
    
    # Écriture des résultats dans un fichier
    with open(output_file, 'w') as file:
        file.write("courbure1\n")
        for element_label, node_label, coords in courbure1:
            file.write(f"{element_label}, {node_label}, {coords}\n")
        file.write("courbure2\n")
        for element_label, node_label, coords in courbure2:
            file.write(f"{element_label}, {node_label}, {coords}\n")
    
    print(f"✅ Coordonnées extraites et enregistrées dans {output_file}") 


def calculer_distances_min(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    courbure1, courbure2 = {}, {}
    current_courbure = None
    for line in lines:
        line = line.strip()
        if line == "courbure1":
            current_courbure = courbure1
        elif line == "courbure2":
            current_courbure = courbure2
        elif line:
            parts = line.split(',', maxsplit=2)
            if len(parts) < 3:
                continue
            try:
                element_label = int(parts[0])
                node_label = int(parts[1])
                coords = np.array([float(x) for x in re.findall(r"[-+]?[0-9]*\.?[0-9]+", parts[2])])
                if element_label not in current_courbure:
                    current_courbure[element_label] = []
                current_courbure[element_label].append((node_label, coords))
            except (ValueError, SyntaxError):
                continue
    def extraire_max_points(courbure):
        if not courbure:
            return []
        return [max(nodes, key=lambda x: (x[1][0], x[1][1], x[1][2])) for nodes in courbure.values()]
    points_max_c1 = extraire_max_points(courbure1)
    points_max_c2 = extraire_max_points(courbure2)
    if not points_max_c1 or not points_max_c2:
        return None
    distances_min = []
    for node2, coords_courbure2 in points_max_c2:
        coords_courbure2 = np.array(coords_courbure2)
        distances = {node1: np.linalg.norm(coords_courbure2 - np.array(coords_courbure1)) for node1, coords_courbure1 in points_max_c1}
        closest_node1 = min(distances, key=distances.get)
        min_dist = distances[closest_node1]
        coords_courbure1 = [coords for node, coords in points_max_c1 if node == closest_node1][0]
        distances_min.append((node2, coords_courbure2, closest_node1, coords_courbure1, min_dist))
    if distances_min:
        min_distance_tuple = min(distances_min, key=lambda x: x[-1])
        node_courbure2, coords_courbure2, node_courbure1, coords_courbure1, min_distance = min_distance_tuple
        print(f"Entre Node {node_courbure2} (courbure2) {coords_courbure2} et Node {node_courbure1} (courbure1) {coords_courbure1}, Distance Minimale: {min_distance}")
        return min_distance_tuple
    return None 

###############calcul de Lc############ 
def load_courbure2(filename):
    """Charge uniquement la partie 'courbure2' du fichier."""
    with open(filename, 'r') as file:
        lines = file.readlines()
    start_idx = lines.index("courbure2\n") + 1  # Trouver le début de la courbure 2
    data = []
    for line in lines[start_idx:]:
        parts = line.strip().split(", ")
        if len(parts) == 3:
            elem_label = int(parts[0])
            node_label = int(parts[1])
            coords = np.array(np.fromstring(parts[2].strip("[]"), sep=" "))  # Convertit la chaîne en array numpy
            data.append((elem_label, node_label, coords))
    return data


def select_minminmax_nodes(data):
    """
    Sélectionne un seul nœud par élément ayant les coordonnées (xmin, ymin, zmax).
    data: liste de tuples (elem_label, node_label, coords), 
          où coords est un np.array([x, y, z])
    """
    elem_dict = {}
    for elem_label, node_label, coords in data:
        if elem_label not in elem_dict:
            elem_dict[elem_label] = (node_label, coords)
        else:
            current_coords = elem_dict[elem_label][1]
            # Comparaison selon xmin, puis ymin, puis zmax
            if (
                coords[0] < current_coords[0] or
                (coords[0] == current_coords[0] and coords[1] < current_coords[1]) or
                (coords[0] == current_coords[0] and coords[1] == current_coords[1] and coords[2] > current_coords[2])
            ):
                elem_dict[elem_label] = (node_label, coords)
    return [coords for _, coords in elem_dict.values()]

def distance_point_droite(p, p1, p2):
    """Calcule la distance d'un point p à la droite définie par p1 et p2."""
    p, p1, p2 = np.array(p), np.array(p1), np.array(p2)
    num = np.linalg.norm(np.cross(p2 - p1, p1 - p))
    den = np.linalg.norm(p2 - p1)
    return num / den if den != 0 else float('inf')

def main(filename, p1, p2):
    data = load_courbure2(filename)
    selected_points = select_minminmax_nodes(data) 
    print(selected_points)
    
    # Ajouter p1 explicitement à la liste des points valides
    valid_points = [p1]
    
    # Filtrer les points ayant y > y_p1
    selected_points = [p for p in selected_points if p[1] > p1[1]]
    
    # Vérifier la distance à la droite pour les autres points (distance < 0.005)(mesh_size)
    valid_points.extend([p for p in selected_points if distance_point_droite(p, p1, p2) < 0.005])
    
    if len(valid_points) < 2:
        print("Pas assez de points valides pour calculer une distance.")
        return None
    
    # Récupérer les labels des nœuds correspondants
    node_labels = [node_label for _, node_label, _ in data if np.array_equal(_, valid_points[0]) or np.array_equal(_, valid_points[-1])]
    
    # Distance entre le premier et le dernier point retenu
    dist = np.linalg.norm(valid_points[-1] - valid_points[0])
    
    # Afficher les labels des nœuds et la distance
    print(f"Distance entre le premier et le dernier point sélectionné : {dist:.6f}")
    print(f"Labels des nœuds entre lesquels la distance est calculée : {node_labels[0]} et {node_labels[-1]}")


# Utilisation des fonctions  


filepath = "element_coordinates_with_labels.txt"
odb_path = 'C:\\Users\\Ougbine\\BChipInp.odb'
input_file = "evf_void_by_element.txt"
output_file = "isolated_elements.txt"
isolated_elements_file = 'isolated_elements.txt'
extraction_evf_void(odb_path)
detect_elements_isolated(input_file, output_file)
nodes = lire_elements(output_file)
extraire_coordonnees_odb(odb_path, 'isolated_elements.txt', 'element_coordinates_with_labels.txt')
odb = openOdb(odb_path)
coordinates = get_node_coordinates(odb, nodes) 
distances_min = calculer_distances_min(filepath)  

########## calcul de longueur de contact############
def load_courbure2(filename):
    """Charge uniquement la partie 'courbure2' du fichier."""
    with open(filename, 'r') as file:
        lines = file.readlines()
    start_idx = lines.index("courbure1\n") + 1  # Trouver le début de la courbure 2
    data = []
    for line in lines[start_idx:]:
        parts = line.strip().split(", ")
        if len(parts) == 3:
            elem_label = int(parts[0])
            node_label = int(parts[1])
            coords = np.array(np.fromstring(parts[2].strip("[]"), sep=" "))  # Convertit la chaîne en array numpy
            data.append((elem_label, node_label, coords))
    return data




def distance_point_droite(p, p1, p2):
    """Calcule la distance d'un point p à la droite définie par p1 et p2."""
    p, p1, p2 = np.array(p), np.array(p1), np.array(p2)
    num = np.linalg.norm(np.cross(p2 - p1, p1 - p))
    den = np.linalg.norm(p2 - p1)
    return num / den if den != 0 else float('inf')


# Exemple d'utilisation avec les points P1 et P2 donnés
p1 = np.array([-1.90702e-02,  1.00937e-01,  5.00000e-03])
p2 = np.array([-2.99156e-02, -2.24936e-03,  5.00000e-03])


distances_min = calculer_distances_min(filepath)

main("element_coordinates_with_labels.txt", p1, p2)