def transform(intermediate_data, config):
    base_url = config["base_url"]

    # Process links into a dictionary
    links = {}
    for link_item in config["links"]:
        # Ensure each link_item is a dictionary and contains a single key-value pair
        if isinstance(link_item, dict) and len(link_item) == 1:
            links.update(link_item)
        else:
            raise ValueError(
                f"Invalid link item format: {link_item}. Each item in 'links' should be a dictionary with a single key-value pair."
            )

    structure = config["structure"]

    def process_structure(structure, data_list):
        if isinstance(structure, dict):
            result = {}
            for key_template, value_template in structure.items():
                # Check for field placeholders in the key
                if "{field:" in key_template:
                    field_name = key_template[
                        key_template.find("{field:") + 7 : key_template.find("}")
                    ]
                    # Group data by the field_name
                    groups = {}
                    for data in data_list:
                        key_value = data.get(field_name, "")
                        groups.setdefault(key_value, []).append(data)

                    for key_value, group_data in groups.items():
                        new_key = key_template.replace(
                            f"{{field:{field_name}}}", key_value
                        )
                        new_value = process_structure(value_template, group_data)
                        result[new_key] = new_value
                else:
                    new_key = key_template
                    new_value = process_structure(value_template, data_list)
                    result[new_key] = new_value
            return result
        elif isinstance(structure, list):
            result = {}
            for item in structure:
                item_result = process_structure(item, data_list)
                for key, value in item_result.items():
                    if key in result and isinstance(value, dict):
                        if isinstance(result[key], dict):
                            result[key].update(value)
                        else:
                            result[key] = value
                    else:
                        result[key] = value
            return result
        elif isinstance(structure, str):
            # Process placeholders in the string
            s = structure
            # Replace field placeholders
            if "{field:" in s:
                field_name = s[s.find("{field:") + 7 : s.find("}")]
                field_value = data_list[0].get(field_name, "")
                s = s.replace(f"{{field:{field_name}}}", field_value)
            # Replace link placeholders
            if "{link:" in s:
                link_name = s[s.find("{link:") + 6 : s.find("}")]
                link_template = links.get(link_name, "")
                url = base_url + link_template.format(**data_list[0])
                s = s.replace(f"{{link:{link_name}}}", url)
            return s
        else:
            return structure

    output = process_structure(structure, intermediate_data)
    return output
