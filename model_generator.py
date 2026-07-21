from typing import Dict
from protocol_extenders.extender_factory import create_extender
from fault_injectors.injector_factory import create_injector
from smv_utils import get_module_text, strip_main_module
from xml_parser import FaultModel, ModuleConfig


class ModelGenerator:
    """
    Coordinates the complete model generation pipeline.
        1. Extract nominal modules.
        2. Extend the protocol according to redundancy.
        3. Inject faults into the requested modules.
        4. Assemble the final SMV model.
    """    
    def __init__(self, fault_model: FaultModel) -> None:
        self.fault_model: FaultModel = fault_model


    def generate(self, smv_content: str) -> str:
        """Receives the nominal SMV model and returns the generated extended model."""

        modules = self._extract_modules(smv_content)
        extender = create_extender(self.fault_model.protocol_type)
        modules = extender.extend(modules, self.fault_model)
        modules = self._inject_faults(modules)

        return self._assemble_model(smv_content, modules)


    def _extract_modules(self, smv_content: str) -> Dict[str, str]:
        """Extract all nominal modules from the nominal SMV file."""
        try:
            return {
                "queue": get_module_text(smv_content, "Queue"),
                "client": get_module_text(smv_content, "Client"),
                "server": get_module_text(smv_content, "Server"),
                "wrapper": get_module_text(smv_content, "Nominal")
            }
        except ValueError as err:
            raise ValueError(f"Failed to extract base modules from input SMV. Details: {err}") from err


    def _inject_faults(self, modules: Dict[str, str]) -> Dict[str, str]:
        """Inject faults into ClientExtended and/or ServerExtended when requested."""
        client_cfg = self.fault_model.modules.get("Client")
        server_cfg = self.fault_model.modules.get("Server")

        if client_cfg and client_cfg.faults:
            modules["client"] = self._inject_module_faults(modules["client"], "Client", client_cfg)

        if server_cfg and server_cfg.faults:
            modules["server"] = self._inject_module_faults(modules["server"], "Server", server_cfg)

        return modules


    def _inject_module_faults(self, module_text: str, module_name: str, module_cfg: ModuleConfig) -> str:
        """
        Apply all fault injectors required by a module.
        Faults are grouped by type and each injector is applied once.
        """
        fault_groups = {}

        for fault in module_cfg.faults:
            fault_groups.setdefault(fault.type, []).append(fault)

        for faults in fault_groups.values():
            injector = create_injector(faults)
            module_text = injector.inject(module_text=module_text, module_name=module_name)

        return module_text


    def _assemble_model(self, original_smv: str, modules: Dict[str, str]) -> str:
        """Assemble the final generated extended SMV model"""
        nominal_base = strip_main_module(original_smv)

        # Build the LTLSPEC section from the parsed properties
        properties_blocks = []
        for prop in self.fault_model.properties:
            clean_spec = "\n".join(f"    {line.strip()}" for line in prop.spec.strip().split("\n"))
            
            ltlspec_text = ""
            if prop.comment:
                ltlspec_text += f"-- {prop.comment}\n"
            
            ltlspec_text += f"LTLSPEC G (\n{clean_spec}\n)"
            
            properties_blocks.append(ltlspec_text)

        # Combine all if there are multiple properties parsed from XML
        properties_section = "\n\n".join(properties_blocks)

        parts = [
            nominal_base,
            modules["queue"].rstrip(),
            modules["client"].rstrip(),
            modules["server"].rstrip(),
            modules["wrapper"].rstrip(),
            modules["sync"].rstrip()
        ]

        if properties_section:
            parts.append(properties_section)

        parts.append(modules["main"].rstrip())

        return "\n\n\n".join(parts)