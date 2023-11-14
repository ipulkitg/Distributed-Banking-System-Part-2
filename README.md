# Distributed-Banking-System-Part-2
Setup
Relevant Technologies used in the setup are : S.No Name
1. Python (3.9)
2. JSON
3. Multiprocessing
4. Grpcio (1.59)
5. Grpcio-tools (1.59)
6. Protobuf (4.24.4)
7. Future (0.18.3)
8. os

Implementation Processes
The following important files are included in this project:
• main.py: Main program to be executed from the command line with: python main.py input.json
• input.json: Input file containing a list of branch processes and customer processes with transaction events
• Output1.json: The output file containing list of all the events taken place on each customer & sorted by clock value. (This file will be overwritten each time the program is ran).
• Output2.json: The output file containing List all the events taken place on each branch.
• Output3.json: The output file containing List all the events (along with their logical times)
triggered by each customer Deposit/Withdraw request
• branch.proto: Protocol buffer file defining RPC messages & services. This file has
already been compiled to produce the branch_pb2.py & branch_pb2_grpc.py files.
• Branch.py: Branch class served as a gRPC server to process customer transactions and
propagate them to other branches.
• Customer.py: Customer class with gRPC client branch stub to send transaction requests
to its corresponding bank branch.
