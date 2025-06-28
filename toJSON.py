def parse_input_to_json(input_text):
    """
    Parse input text in format 'product/units/weekly_usage' into list of JSON objects
    
    Args:
        input_text (str): Multi-line string with format:
                         product/units/weekly_usage
                         Example: "milk/litres/7\nrice/gms/2100"
    
    Returns:
        list: List of dictionaries with keys: name, unit, weekly_usage
              Example: [{"name": "milk", "unit": "litres", "weekly_usage": "7"}]
    """
    json_objects = []
    
    # Split input by lines and process each line
    lines = input_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line:  # Skip empty lines
            parts = line.split('/')
            if len(parts) == 3:
                product, units, weekly_usage = parts
                json_obj = {
                    "name": product.strip(),
                    "unit": units.strip(),
                    "weekly_usage": weekly_usage.strip()
                }
                json_objects.append(json_obj)
    
    return json_objects
