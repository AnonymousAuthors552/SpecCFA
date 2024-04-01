# SpecCFA Repository

This repository contains the prototype for SpecCFA: Enhancing Control Flow Attestation and Auditing via Application-Aware Sub-Path Speculation

This work is currently under peer-review.

## Abstract
At the edge of modern cyber-physical systems, Micro-Controller Units (MCUs) are responsible for safety-critical sensing/actuation. However, MCU cost constraints typically rule out the usual security mechanisms available in general-purpose computers. Thus, various low-cost security architectures have been proposed for remote verification of their software state via integrity proofs. These proofs vary in terms of expressiveness, with simpler ones confirming correct binary presence, while more expressive ones, e.g., Control Flow Attestation (CFA), enable a Verifier (Vrf) to remotely assess the run-time behavior of a prover MCU (Prv), generating an authenticated log (CFLog) of all of Prv control flow transfers. Further, Control Flow Auditing augments best-effort CFA by guaranteeing that this evidence is reliably delivered to Vrf. Unfortunately, a common limitation of existing CFA lies in the cost to store and transmit CFLog, as even simple MCU software may generate a large number of CFLog entries. While prior work has proposed static optimizations to reduce CFLog, we note that prior approaches are context-insensitive, i.e., they do not support configurable program-specific optimizations.

In this work, we note that components of a particular program may produce predictable control flow sub-paths and argue that this program-specific predictability could be leveraged to dynamically optimize CFA, while retaining all of its security guarantees. Based on this premise, we propose SpecCFA: an architecture for dynamic sub-path speculation in CFA. SpecCFA allows Vrf to dynamically speculate on likely control flow sub-paths for each attested program/function. At run-time, when a sub-path in CFLog matches a pre-defined speculation, the entire sub-path is replaced by a reserved symbol of reduced size, resulting in significant savings. SpecCFA is agnostic to the underlying CFA method and can support simultaneous speculation on multiple variable-length control flow sub-paths. To demonstrate SpecCFA feasibility we implement it atop two open-source CFA architectures: one based on a clean-slate CFA hardware design and one based on a commodity Trusted Execution Environment (ARM TrustZone-M).

## Dependencies

### SpecCFA in HW

Vivado IDE: https://www.xilinx.com/support/download.html

### SpecCFA in TZ
STM32CubeIDE: https://www.st.com/en/development-tools/stm32cubeide.html
