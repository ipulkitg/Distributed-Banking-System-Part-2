import grpc
import example_pb2_grpc
import example_pb2
from time import sleep

class Branch(example_pb2_grpc.BranchServicer):
    def __init__(self, id, balance, branches):
        self.id = id
        self.balance = balance
        self.branches = branches
        self.stubList = list()
        self.recvMsg = list()
        self.events = list()
        self.logical_clock = 1
        self.branch_id_map = {}
    # Setup gRPC channel & client stub for each branch
    def createStubs(self):

        self.stubList = [
            example_pb2_grpc.BranchStub(grpc.insecure_channel(f"localhost:{60000 + branchId}"))
            for branchId in self.branches if branchId != self.id
        ]


    def getStubs(self):
        return self.stubList

    def Withdraw_Propogation(self, request, logical_clock):
        for x in range(1,len(self.branches) + 1):
            if x != self.id:
                self.logical_clock += 1
                msg = {
                    "customer-request-id": self.branch_id_map[x][1],
                    "logical_clock": self.logical_clock,
                    "interface": "propogate_" + request.interface,
                    "comment": f"event_recv by branch {x}",
                }
                self.events.append(msg)

        for stub in self.stubList:
            stub.MsgPropagation(example_pb2.MsgRequest(id=request.id, interface="withdraw",
                                                       customer_request_id = request.customer_request_id,
                                                       logical_clock=logical_clock))


    def Deposit_Propogation(self, request, logical_clock):
        for x in range(1,len(self.branches) + 1):
            if x != self.id:
                self.logical_clock += 1
                msg = {
                    "customer-request-id": self.branch_id_map[x][0],
                    "logical_clock": self.logical_clock,
                    "interface": "propogate_" + request.interface,
                    "comment": f"event_recv by branch {x}",
                }
                self.events.append(msg)
            for stub in self.stubList:
                stub.MsgPropagation(example_pb2.MsgRequest(id=request.id, interface="deposit",
                                                           customer_request_id = request.customer_request_id,
                                                           logical_clock=logical_clock))


    def constructmessageforprop(self, request, propagate):
        logical_clock = self.logical_clock
        if request.interface == "deposit":
            self.logical_clock += 1
            if propagate == 1:
                for x in range(1, len(self.branches) + 1):
                    if x != self.id:
                        self.logical_clock += 1
                        msg = {
                            "customer-request-id": request.customer_request_id,
                            "logical_clock": self.logical_clock,
                            "interface": "propagate_" + request.interface,
                            "comment": f"event_sent to branch {x}",
                        }
                        self.events.append(msg)
                self.Deposit_Propogation(request, self.logical_clock)
        elif request.interface == "withdraw":
            self.logical_clock += 1
            if propagate == 1:
                for x in range(1, len(self.branches) + 1):
                    if x != self.id:
                        self.logical_clock += 1
                        msg = {
                            "customer-request-id": request.customer_request_id,
                            "logical_clock": self.logical_clock,
                            "interface": "propogate_" + request.interface,
                            "comment": f"event_sent to branch {x}",
                        }
                        self.events.append(msg)
                self.Withdraw_Propogation(request, self.logical_clock)

        msg = {
            "customer-request-id": request.customer_request_id,
            "logical_clock": logical_clock,
            "interface": request.interface,
            "comment": f"event_sent to branch {self.id}" if propagate else f"event_recv from branch {request.id}",
        }
        self.recvMsg.append(msg)
        return example_pb2.MsgResponse(
            interface=request.interface,
            customer_request_id=request.customer_request_id,
            logical_clock=self.logical_clock,
        )

    def BranchMap(self, request):
        for customer_request_map in request.request_and_id_map:
            branch_id = customer_request_map.branch_id
            corresponding_customer_request_ids = customer_request_map.cr_id

            # Check if the branch_id is already a key in the map
            if branch_id in self.branch_id_map:
                self.branch_id_map[branch_id].extend(corresponding_customer_request_ids)
            else:
                self.branch_id_map[branch_id] = corresponding_customer_request_ids

    def MsgDelivery(self, request, context):
        if not self.branch_id_map:
            self.BranchMap(request)
        self.logical_clock = request.logical_clock
        comment = f"event_recv from customer {request.id}"
        self.events.append({"customer-request-id": request.customer_request_id, "logical_clock": self.logical_clock, "interface": request.interface, "comment": comment})
        return self.constructmessageforprop(request, True)

    def MsgPropagation(self, request, context):
        self.logical_clock = max(self.logical_clock, request.logical_clock) + 1
        return self.constructmessageforprop(request, False)

    def output(self):
        return self.events

