# Fault-Tolerant Model Generator

This repository contains a framework for the automatic generation of fault-tolerant NuSMV models from nominal client-server protocol specifications. The framework supports the R, RR, and RRA communication protocols, extending their models with configurable redundancy and fault injection mechanisms to produce models ready for formal verification through model checking.

---
## Requirements

- Python 3

No external Python dependencies are required.

---

## Usage

Run the framework by providing:

Run the framework by providing:

1. One of the supported nominal NuSMV protocol models (`.smv`) from the `protocols/` directory (`R_Protocol.smv`, `RR_Protocol.smv`, or `RRA_Protocol.smv`).
2. An XML configuration file describing the redundancy, fault model, and verification properties.

```bash
./run.sh <input_nominal.smv> <faults.xml>
```

Example:

```bash
./run.sh protocols/R_Protocol.smv faults.xml
```

The generated extended model will be written to:

```text
output/ExtendedModel.smv
```