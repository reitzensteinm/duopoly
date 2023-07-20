import copy


def move_file(file_mapping, old_path, new_path):
    # Creating a copy of the dictionary
    file_mapping_copy = copy.deepcopy(file_mapping)

    if old_path in file_mapping_copy:
        # Moving the file to the new path
        file_mapping_copy[new_path] = file_mapping_copy[old_path]
        del file_mapping_copy[old_path]
    else:
        raise Exception(f"No such file: '{old_path}'")

    return file_mapping_copy
