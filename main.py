from lib.get_infor import AbaqusModelManager
from lib.get_infor import find_coordinate_from_group
from lib.get_infor import group_nodes_by_distance
from lib.create_adx import create_adx_file
from lib.get_result import NodeTemperature
from lib.insert_to_excel import insert_values_to_excel

# if __name__ == "__main__":
#     # Specify the file path for the .inp file
#     inp_file_path = r"C:\Users\TechnoStar\Documents\macro\read_model\Job_1.inp"
#     adx_file_path = r"C:\Users\TechnoStar\Documents\macro\read_model\Local_temperature_result.adx"
#     groups = ["group1"]
#     for group in groups:
#         print(group)
#         model_manager, node_ids_of_faces = find_coordinate_from_group(inp_file_path, group)
#         print("_"*100)
#         create_adx_file(node_ids_of_faces, adx_file_path, "group_1_result")

if __name__ == "__main__":
    # Specify the file path for the .inp file
    inp_file_path = r"C:\Users\TechnoStar\Documents\macro\read_model\Job_1.inp"
    csv_file_path = r"C:\Users\TechnoStar\Documents\macro\read_model\group_1_result.csv"
    groups = ["group1"]

    for group in groups:
        print(group)
        model_manager, list_node_id, list_coordinate = find_coordinate_from_group(inp_file_path, group)
            # print(f"Coordinates of Node ID {node_ids_of_face}: {coordinates}")
        print("_"*50)

        tolerance = 10
        group_coordinate = group_nodes_by_distance(list_node_id, list_coordinate, tolerance)

        for i, group in enumerate(group_coordinate):
            print(f"Group {i + 1}: {group}")

        # node_temp = NodeTemperature()
        # node_temp.load_from_csv(csv_file_path)
        # for node in list_node_id:
        #         print(f"Temperature of node {node}: {node_temp.get_temperature(node)}°C")


# if __name__ == "__main__":
#         file_path = r"C:\Users\TechnoStar\Documents\macro\read_model\New Microsoft Excel Worksheet.xlsx"
#         sheet_name = "温度評価"

#         insert_values_to_excel(file_path, sheet_name, 45000001, 100.0)