import re

def format_output(input_dict, exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec):

    
    sections_to_show = []

    # If the user chose to show all sections
    if all_sec is True:
        sections_to_show = list(input_dict.keys())
    else:
        # Otherwise, build the list based on specific flags
        if exec_sec:
            sections_to_show.append("executable")
        if slib_sec:
            print(f"Format output function shared libs sections var: {slib_sec}")
            sections_to_show.append("shared_libs")
        if he_sec:
            sections_to_show.append("heap")
        if st_sec:
            sections_to_show.append("stack")
        if vvar_sec:
            sections_to_show.append("vvar")
        if vsys_sec:
            sections_to_show.append("vsyscall")
        if vdso_sec:
            sections_to_show.append("vdso")
        if none_sec:
            sections_to_show.append("none")
        

    for category_name in sections_to_show:
        # Access the list of sections for the current category
        sections_list = input_dict.get(category_name, [])

        if not sections_list:
            print(f"\n--- {category_name.upper()} SECTIONS (No entries) ---\n")
            continue
            
        print(f"\n--- {category_name.upper()} SECTIONS ---\n")
        
        for line_num, section in enumerate(sections_list, 1):
            print(f"{line_num}: {section}")


def process_lines(line):
    match = re.match(r"(\w{0,16}+-\w{0,16})\s+(.{4})\s+(\w{8})\s+(\d{2}+:\d{2})\s+(\d[0-9]{0,8})\s*(.+)", line)
    if not match: 
            print(f"No match for: {line.strip()}")
            return None 

    address, permissions, offsets, maj_min_id, inode, file_path= match.groups()

    return {
            "address": address,
            "permissions": permissions,
            "offsets": offsets,
            "maj_min_id": maj_min_id,
            "inode": inode,
            "file_path": file_path
            }


def group_regions(file, exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec):
    '''
    This dictionary contains the sections of data that match a certain condition.
    For example if the section has the stack label it's metadata (addresses, etc.) 
    would be stored in the stack list.
    '''

    section_categories = {
        "executable": [],
        "shared_libs": [],
        "heap":[], 
        "stack": [],
        "vvar": [],
        "vsyscall": [],
        "vdso": [],
        "none": []
    }

    f_path_target_char = "/"
    h_target_char = "[heap]"
    s_target_char = "[stack]"
    vvar_target_char = "[vvar]"
    vsyscall_target_char = "[vsyscall]"


    vdso_target_char = "[vdso]"

    for line_number, line in enumerate(file, 1):
        result = process_lines(line)

        # Check if a match was successfully made
        if result:
            file_path = result.get("file_path", "")

            # Check for specific identifiers
            if h_target_char in file_path:
                section_categories["heap"].append(result)
            elif s_target_char in file_path:
                section_categories["stack"].append(result)
            elif vvar_target_char in file_path:
                section_categories["vvar"].append(result)
            elif vsyscall_target_char in file_path:
                section_categories["vsyscall"].append(result)
            elif vdso_target_char in file_path:
                section_categories["vdso"].append(result)
            elif file_path and f_path_target_char in file_path:
                # Distinguish between shared libraries (.so) and other files.
                if file_path.endswith(".so"):
                    section_categories["shared_libs"].append(result)
                else:
                    section_categories["executable"].append(result)
            else:
                section_categories["none"].append(result)


    #Display results in a clean manner
    format_output(section_categories, exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec)

    return section_categories
