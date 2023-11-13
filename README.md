
# 🕒 Distributed Banking System with Lamport Logical Clocks (gRPC)

## 🧩 Problem Statement

To enable secure deposit and withdrawal transactions across multiple branches while ensuring synchronized and consistent data replication. Each customer interacts with a specific branch, and the system ensures consistency using Lamport’s logical clocks.

---

## 🎯 Project Goal

Build upon the gRPC-based distributed banking system (Part 1) by implementing **Lamport’s Logical Clock algorithm** to coordinate events across distributed processes. This ensures a correct “happens-before” relationship between events across branches and customers in the system.

---

## ✅ Key Objectives

- Integrate **logical clock tracking** into both customer and branch processes.
- Implement **Lamport's clock synchronization rules** across all communication layers.
- Maintain **causality and event ordering** across gRPC-based RPC calls.
- Generate multiple structured output files reflecting logical timestamps:
  - Customer-side event order
  - Branch-side propagation history
  - Combined trace for all propagated events

---

## ⚙️ Technologies Used

| Tool/Library       | Version  |
|--------------------|----------|
| Python             | 3.9      |
| gRPC (grpcio)      | 1.59     |
| grpcio-tools       | 1.59     |
| Protobuf           | 4.24.4   |
| Multiprocessing    | Stdlib   |
| JSON, OS, Future   | Various  |

---

## 🚀 Implementation Highlights

- **Logical Clock Integration:**  
  Every process (customer/branch) maintains its own logical clock. Events update local clocks based on the Lamport algorithm before sending and after receiving messages.

- **Event Propagation:**  
  All deposit and withdraw requests are tagged with a unique `customer-request-id`, and logical time is carried throughout the event lifecycle across all processes.

- **Clock Coordination:**  
  - Clock increment before sending events  
  - Clock sync on receiving an event (max of local and received + 1)

- **gRPC Services Extended:**  
  Existing service interfaces (`Deposit`, `Withdraw`, `Propagate`) were extended to carry logical timestamps.

---

## 🧪 Output Results

Three structured JSON output files are produced:

1. **Output1.json:**  
   Lists all events initiated by customers, ordered by logical time.

2. **Output2.json:**  
   Logs all branch-side operations including propagation and reception of events.

3. **Output3.json:**  
   Full trace of all events (with timestamps) triggered by each customer request, showing causal chains.

✅ Sample evaluation results:
- `Checker_part_1`: 20/20 correct
- `Checker_part_2`: 360/360 correct
- `Checker_part_3`: 400/400 correct

---
