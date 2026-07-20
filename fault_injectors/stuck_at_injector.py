import re
from fault_injectors.base_injector import BaseInjector

class StuckAtInjector(BaseInjector):
    """Injects stuck at faults into target variables"""

    def inject(self, module_text: str, module_name: str) -> str:
        if not self.faults:
            return module_text

        # Collect all fault configurations 
        fault_ids = [f.fault_id for f in self.faults]
        
        module_text = self._add_fault_mode_infrastructure(module_text, fault_ids, "stuck_at")

        for fault in self.faults:
            target_var = fault.variable
            fault_case = f"        fault_mode_stuck_at = {fault.fault_id} : {fault.value};"

            pattern = rf"(next\({target_var}\)\s*:=\s*case\n)"
            if not re.search(pattern, module_text):
                raise ValueError(f"Stuck-At Injector Error: No 'next({target_var})' assignment block found.")
                
            module_text = re.sub(pattern, rf"\1{fault_case}\n", module_text)

        # In RRA Server guard the TRUE branch inside next(request_received)
        if module_name == "Server" and "reply_ack_received" in module_text:
            # Check which guards are active to build an accurate guard string
            guards = ["fault_mode_stuck_at = none"]
            if "fault_mode_byzantine" in module_text:
                guards.append("fault_mode_byzantine = none")
            guard_string = " & ".join(guards) + " &"

            pattern = r"(next\(request_received\)\s*:=\s*case\s*\n.*?)(server_request_state\s*=\s*receiving.*?:\s*TRUE;)"
            module_text = re.sub(pattern, rf"\1{guard_string}\n        \2", module_text, flags=re.DOTALL)

        # Avoid side effects on counters and interface toggles
        potential_side_effects = ["request_toggle", "num_requests_sent", "num_requests_received", "request_sent"]

        fault_targets = [f.variable for f in self.faults]
        potential_side_effects = [v for v in potential_side_effects if v not in fault_targets]
        active_side_effects = [v for v in potential_side_effects if f"next({v})" in module_text]
        
        return self._suppress_side_effects(module_text, active_side_effects)