import re
import numpy as np

class AbaqusModelManager:
    def __init__(self, file_path):
        """Initialize the manager with the file path of the .inp file"""
        self.file_path = file_path
        self.nodes = {}         # Dictionary to store nodes as {node_id: (x, y, z)}
        self.elements = {}      # Dictionary to store elements as {elset_name: {element_id: [node_ids]}}
        self.surfaces = {}      # Dictionary to store surfaces as {surface_name: [(element_id, surface)]}
        self.nsets = {}         # Dictionary to store NSETs as {nset_name: [node_ids]}
        self.read_inp_file()

    def read_inp_file(self):
        """Reads the .inp file from the given file path and processes the data"""
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            return
        
        node_section = False
        element_section = False
        surface_section = False
        nset_section = False
        current_surface = None
        current_nset = None
        nset_buffer = []  # Buffer to accumulate node IDs for multi-line NSETs
        current_elset = None
        
        for line in lines:
            line = line.strip()

            # Ignore comment lines or empty lines
            if line.startswith("**") or not line:
                continue

            # Detect the start of node section
            if line.startswith("*NODE"):
                node_section = True
                element_section = False
                surface_section = False
                nset_section = False
                continue

            # Detect the start of element section
            elif line.startswith("*ELEMENT"):
                node_section = False
                element_section = True
                surface_section = False
                nset_section = False
                current_elset = re.search(r'ELSET\s*=\s*(\w+)', line).group(1)
                self.elements[current_elset] = {}
                continue

            # Detect the start of surface section
            elif line.startswith("*SURFACE"):
                node_section = False
                element_section = False
                surface_section = True
                nset_section = False
                current_surface = re.search(r'NAME\s*=\s*(\w+)', line).group(1)
                self.surfaces[current_surface] = []
                continue

            # Detect the start of NSET section
            elif line.startswith("*NSET"):
                node_section = False
                element_section = False
                surface_section = False
                nset_section = True

                # If there was a previous NSET, flush the buffer for it
                if current_nset and nset_buffer:
                    self.nsets[current_nset].extend(nset_buffer)
                    nset_buffer = []  # Reset buffer

                current_nset = re.search(r'NSET\s*=\s*(\w+)', line).group(1)
                self.nsets[current_nset] = []
                continue

            # Processing nodes
            if node_section and line:
                try:
                    node_data = line.split(',')
                    node_id = int(node_data[0].strip())
                    coordinates = tuple(map(float, node_data[1:]))
                    self.nodes[node_id] = coordinates
                except ValueError:
                    print(f"Skipping invalid node data: {line}")
                    continue

            # Processing elements
            elif element_section and line:
                try:
                    element_data = line.split(',')
                    element_id = int(element_data[0].strip())
                    node_ids = list(map(int, element_data[1:]))
                    # Add element to the current ELSET
                    self.elements[current_elset][element_id] = node_ids
                except ValueError:
                    print(f"Skipping invalid element data: {line}")
                    continue

            # Processing surfaces
            elif surface_section and line:
                try:
                    surface_data = line.split(',')
                    element_id = int(surface_data[0].strip())
                    surface_name = surface_data[1].strip()
                    self.surfaces[current_surface].append((element_id, surface_name))
                except ValueError:
                    print(f"Skipping invalid surface data: {line}")
                    continue

            # Processing NSETs (handle multi-line NSET node IDs)
            elif nset_section and line:
                try:
                    # Remove extra spaces, split by commas, and accumulate node IDs
                    cleaned_line = re.sub(r'\s+', '', line)  # Remove spaces
                    node_ids = list(map(int, cleaned_line.split(',')))  # Split and convert to integers
                    nset_buffer.extend(node_ids)
                except ValueError:
                    line = line[0:-1]
                    # Remove extra spaces, split by commas, and accumulate node IDs
                    cleaned_line = re.sub(r'\s+', '', line)  # Remove spaces
                    node_ids = list(map(int, cleaned_line.split(',')))  # Split and convert to integers
                    nset_buffer.extend(node_ids)
                    # print(f"Skipping invalid NSET data: {line}")
                    continue

        # At the end of the file, flush the NSET buffer if there's any unprocessed data
        if current_nset and nset_buffer:
            self.nsets[current_nset].extend(nset_buffer)

    def get_node_coordinates(self, node_id):
        """Returns the coordinates of a given node ID"""
        return self.nodes.get(node_id, None)

    def get_element_nodes(self, elset_name, element_id):
        """Returns the nodes associated with an element ID in a given ELSET"""
        elset = self.elements.get(elset_name, {})
        return elset.get(element_id, None)

    def get_nset(self, nset_name):
        """Returns the node IDs in a given NSET"""
        return self.nsets.get(nset_name, None)

    def get_surface(self, surface_name):
        """Returns the element IDs and surface sides in a given surface"""
        return self.surfaces.get(surface_name, None)

    def print_all_nsets(self):
        """Prints all NSETs and their node IDs"""
        print("All NSETs:")
        for nset_name, node_ids in self.nsets.items():
            print(f"NSET: {nset_name}")
            print(f"Node IDs: {node_ids}")
            print("-" * 30)

    def print_all_surfaces(self):
        """Prints all surfaces and their element IDs with surface names"""
        print("All Surfaces:")
        for surface_name, elements in self.surfaces.items():
            print(f"Surface: {surface_name}")
            for element_id, surface_side in elements:
                print(f"  Element ID: {element_id}, Surface Side: {surface_side}")
            print("-" * 30)

    def print_all_nodes(self):
        """Prints all nodes and their coordinates"""
        print("All Nodes:")
        for node_id, coordinates in self.nodes.items():
            print(f"Node ID: {node_id}, Coordinates: {coordinates}")
        print("-" * 30)

    def print_all_elements(self):
        """Prints all elements, their ELSETs, and their associated node IDs"""
        print("All Elements:")
        for elset_name, elements in self.elements.items():
            print(f"ELSET: {elset_name}")
            for element_id, node_ids in elements.items():
                print(f"  Element ID: {element_id}, Node IDs: {node_ids}")
            print("-" * 30)
    def get_element_ids_from_surface(self, surface_name):
        """
        Returns all Element IDs associated with the given surface name.
        """
        if surface_name in self.surfaces:
            element_ids = [elem_id for elem_id, _ in self.surfaces[surface_name]]
            return element_ids
        else:
            print(f"Error: Surface {surface_name} not found.")
            return None
    def get_surface_side(self, element_id):
        """
        Returns the surface side(s) associated with a given element ID.
        """
        surfaces_with_element = []
        for surface_name, elements in self.surfaces.items():
            for elem_id, surface_side in elements:
                if elem_id == element_id:
                    surfaces_with_element.append((surface_name, surface_side))

        if surfaces_with_element:
            return surfaces_with_element
        else:
            print(f"Error: Element ID {element_id} not found in any surface.")
            return None
    def get_element_node_ids(self, element_id):
        """
        Returns the node IDs associated with a given element ID.
        Searches through all ELSETs and elements to find the element.
        """
        for elset_name, elements in self.elements.items():
            if element_id in elements:
                return elements[element_id]
        print(f"Error: Element ID {element_id} not found.")
        return None
    def get_node_coordinates(self, node_id):
        """
        Returns the coordinates (x, y, z) associated with a given node ID.
        """
        coordinates = self.nodes.get(node_id)
        if coordinates:
            return coordinates
        else:
            print(f"Error: Node ID {node_id} not found.")
            return None

def reorder_values(values, order_str):
    # Define the order mapping based on the input string
    order_mapping = {
        "S1": [0, 1, 2, 4, 5, 6],  # Corresponds to indices 1, 2, 3, 5, 6, 7
        "S2": [0, 1, 3, 4, 8, 7],  # Corresponds to indices 1, 2, 4, 5, 9, 8
        "S3": [1, 2, 3, 4, 9, 6],  # Corresponds to indices 2, 3, 4, 5, 10, 7
        "S4": [2, 0, 3, 6, 7, 9],  # Corresponds to indices 3, 1, 4, 7, 8, 10
    }
    
    # Get the appropriate order for the input string
    if order_str in order_mapping:
        order_indices = order_mapping[order_str]
        # Return the reordered values
        return [values[i] for i in order_indices]
    else:
        return "Invalid input string!"


def remove_duplicates(input_list):
    seen = set()
    output_list = []
    
    for item in input_list:
        if item not in seen:
            output_list.append(item)
            seen.add(item)
    
    return output_list
def find_coordinate_from_group(file_path, group):
    # Specify the file path for the .inp file
    # file_path = r"C:\Users\TechnoStar\Documents\macro\read_model\Job_1.inp"

    # Create an instance of AbaqusModelManager with the given file path
    model_manager = AbaqusModelManager(file_path)
    list_node_id = []
    list_coordinate = []
    list_node_ids_of_faces = []
    list_node_id_remove_duplicates = []
    list_coordinate_remove_duplicates = [] 

    # # Print all NSETs
    # model_manager.print_all_nsets()

    # Print all surfaces
    # model_manager.print_all_surfaces()

    # # Print all elements
    # model_manager.print_all_elements()

    # # Print all nodes
    # model_manager.print_all_nodes()

    # Get Element IDs from Surface s_cap_preten_01

    # surface_name = "group2"
    element_ids = model_manager.get_element_ids_from_surface(group)
    for element_id in element_ids:
        surface_sides = model_manager.get_surface_side(element_id)
        # print(surface_sides[0][1])
        node_ids = model_manager.get_element_node_ids(element_id)
        list_node_id.append(node_ids)
        # print(node_ids)
        node_ids_of_faces = reorder_values(node_ids, surface_sides[0][1])
        list_node_ids_of_faces = list_node_ids_of_faces + node_ids_of_faces
        # print(node_ids_of_faces)
    print(list_node_ids_of_faces)
    list_node_ids_of_faces_remove_duplicates = remove_duplicates(list_node_ids_of_faces)

    for id in list_node_ids_of_faces_remove_duplicates:
        coordinates = model_manager.get_node_coordinates(id)
        
        if coordinates:
            list_node_id_remove_duplicates.append(id)
            list_coordinate_remove_duplicates.append(coordinates)
            print(f"Coordinates of Node ID {id}: {coordinates}")
    return model_manager, list_node_id_remove_duplicates, list_coordinate_remove_duplicates

def calculate_distance(coord1, coord2):
    return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2 + (coord1[2] - coord2[2])**2)

def group_nodes_by_distance(node_list, coord_list, tolerance):

    groups = []
    visited = set()
    
    for i, node_id in enumerate(node_list):
        if node_id in visited:
            continue
        
        # Create a new group and add the current node
        group = [node_id]
        visited.add(node_id)
        
        # Get the coordinates of the current node
        coord = coord_list[i]
        
        # Compare the current node with all other nodes
        for j, other_node_id in enumerate(node_list):
            if other_node_id != node_id and other_node_id not in visited:
                other_coord = coord_list[j]
                distance = calculate_distance(coord, other_coord)
                if distance <= tolerance:
                    group.append(other_node_id)
                    visited.add(other_node_id)
        
        groups.append(group)
    
    return groups