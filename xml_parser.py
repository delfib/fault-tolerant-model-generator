from typing import Dict, List
import xml.etree.ElementTree as ET

class Fault:
    def __init__(self, fault_id, type, variable, value=None):
        self.fault_id = fault_id  
        self.type = type
        self.variable = variable
        self.value = value

    def __repr__(self):
        return f"Fault(id={self.fault_id}, type={self.type}, variable={self.variable}, value={self.value})"

class Property:
    def __init__(self, id, comment, spec):
        self.id = id
        self.comment = comment
        self.spec = spec

    def __repr__(self):
        return f"Property(id={self.id})"


class ModuleConfig:
    def __init__(self, name, redundancy, faults):
        self.name = name
        self.redundancy = redundancy
        self.faults = faults

    def __repr__(self):
        return (
            f"ModuleConfig("
            f"name={self.name}, "
            f"redundancy={self.redundancy}, "
            f"faults={self.faults})"
        )


class FaultModel:
    def __init__(self, model_file, protocol_type, modules, properties=None):
        self.model_file = model_file
        self.protocol_type = protocol_type
        self.modules = modules
        self.properties = properties or []

    def __repr__(self):
        return (
            f"FaultModel("
            f"model_file={self.model_file}, "
            f"protocol_type={self.protocol_type}, "
            f"modules={self.modules}, "
            f"properties={self.properties})"
        )


def parse_fault_model(xml_path: str) -> FaultModel:
    """Loads, validates, and processes input XML file"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError, PermissionError) as err:
        raise ValueError(f"XML Parse Failure: {err}") from err

    # Parse and verify <model> reference
    model_file = root.findtext("model")
    if model_file is None:
        raise ValueError("Missing required <model> in XML")

    model_file = model_file.strip()

    # Parse and verify <protocol-type> reference
    protocol_type = root.findtext("protocol-type")

    if protocol_type is None:
        raise ValueError("Missing required <protocol-type> in XML")

    protocol_type = protocol_type.strip().upper()

    if protocol_type not in ("R", "RR", "RRA"):
        raise ValueError(f"Unsupported <protocol-type>: '{protocol_type}'. Expected: R, RR, or RRA.")

    # Parse <modules> references
    modules = {}
    modules_elem = root.find("modules")

    if modules_elem is None:
        raise ValueError("Missing tag element: <modules>")

    for module_elem in modules_elem.findall("module"):
        module_name = module_elem.attrib.get("name")
        if module_name not in ("Client", "Server"):
            raise ValueError(f"Invalid module name: '{module_name}'. Expected: Client or Server.")

        redundancy = 1
        redundancy_elem = module_elem.find("redundancy")

        if redundancy_elem is not None:
            try:
                redundancy = int(redundancy_elem.attrib.get("count", "1"))
            except ValueError as err:
                raise ValueError(f"Redundancy count attribute for '{module_name}' must be an integer value.") from err

        if redundancy < 1:
            raise ValueError(f"Redundancy limits for '{module_name}' must be >= 1. Evaluated: {redundancy}")

        faults = []
        faults_elem = module_elem.find("faults")

        if faults_elem is not None:
            for f in faults_elem.findall("fault"):
                fault_id = f.attrib.get("id", "")
                fault_type = f.findtext("type")
                variable = f.findtext("variable")
                value = f.findtext("value")

                if fault_type is None or variable is None or variable.strip() == "":
                    raise ValueError(f"Fault reference '{fault_id}' must supply <type> and <variable> parameters.")

                fault_type = fault_type.strip()
                variable = variable.strip()

                if fault_type == "stuck-at":
                    if value is None or value.strip() == "":
                        raise ValueError(f"Stuck-at fault reference '{fault_id}' missing parameter label <value>.")
                    faults.append(Fault(fault_id, fault_type, variable, value.strip()))

                elif fault_type == "byzantine":
                    faults.append(Fault(fault_id, fault_type, variable, value.strip() if value else None))

                else:
                    raise ValueError(f"Unknown fault type: '{fault_type}' in fault reference '{fault_id}'.")

        variable_fault_types = {} 
        tracked_fault_signatures = set()

        # A variable may only have one fault.
        for fault in faults:
            # A variable can only be assigned to ONE type of fault
            previous_type = variable_fault_types.get(fault.variable)
            if previous_type is None:
                variable_fault_types[fault.variable] = fault.type
            elif previous_type != fault.type:
                raise ValueError(
                    f"Variable '{fault.variable}' in module '{module_name}' has multiple fault types "
                    f"('{previous_type}' and '{fault.type}'). Only one fault definition per variable is allowed."
                )

            # Detect duplicates (same variable and same target value)
            fault_signature = (fault.variable, fault.value)
            if fault_signature in tracked_fault_signatures:
                value_str = f" with value '{fault.value}'" if fault.value else ""
                raise ValueError(
                    f"Duplicate fault definition found for variable '{fault.variable}'"
                    f"{value_str} in module '{module_name}'."
                )
            tracked_fault_signatures.add(fault_signature)

        modules[module_name] = ModuleConfig(name=module_name, redundancy=redundancy, faults=faults)

    # Extract verification <properties> 
    properties = []
    properties_elem = root.find("properties")

    if properties_elem is not None:
        for p in properties_elem.findall("property"):
            prop_id = p.attrib.get("id", "")
            comment = p.findtext("comment", default="").strip()
            spec = p.findtext("spec")

            if spec is None or spec.strip() == "" :
                raise ValueError(f"Property '{prop_id}' missing block <spec>.")
            properties.append(Property(prop_id, comment, spec.strip()))

    return FaultModel(
        model_file=model_file,
        protocol_type=protocol_type,
        modules=modules,
        properties=properties
    )