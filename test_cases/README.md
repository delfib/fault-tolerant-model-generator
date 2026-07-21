# Test Cases

This directory contains the NuSMV models used as test cases for this project.
Each test case is provided as a standalone `.smv` model.

## Requirements

To execute the test cases, the following software is required:

- **NuSMV** (version 2.7 or compatible)

Make sure the `NuSMV` executable is available in your system's `PATH`, or invoke it using its full path.

## Running a Test Case

Start NuSMV in interactive Bounded Model Checking (BMC) mode:

```bash
NuSMV -int -bmc <test_case>.smv
```

For example:

```bash
NuSMV -int -bmc RR_Stuck_At_2S.smv
```

Once the NuSMV prompt appears, initialize the BMC environment:

```text
NuSMV > go_bmc
```

Then verify the LTL specification using the desired bound `k`:

```text
NuSMV > check_ltlspec_bmc -k <k>
```

For example, using a bound of 10:

```text
NuSMV > check_ltlspec_bmc -k 10
```

## Notes

- The value of `k` may be chosen according to the verification scenario.
- Any of the `.smv` files included in this directory can be executed using the same procedure.
- If a property is violated within the specified bound, NuSMV will report a counterexample.