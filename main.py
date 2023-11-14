import json
import multiprocessing
from time import sleep
from concurrent import futures
import grpc
import os
import example_pb2_grpc
from Branch import Branch
from Customer import Customer

def file_reader(input_file_path):
    with open(input_file_path, 'r') as file:
        data = json.load(file)
    return data

def customerprocess_init(customers, customerProcessList, branch_stubs):
    for customer in customers:
        customer_process = multiprocessing.Process(target=customerProcessing, args=(customer,branch_stubs))
        customerProcessList.append(customer_process)
        customer_process.start()
        sleep(0.4)


def finish_branch_processes(branchProcessList):
    [branch_process.terminate() for branch_process in branchProcessList]

def customer_process_data(customerProcessList):
    [customer_process.join() for customer_process in customerProcessList]

def BranchServerInit(branch):
    branch.createStubs()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    example_pb2_grpc.add_BranchServicer_to_server(branch, server)
    server.add_insecure_port("localhost:" + str(60000 + branch.id))
    server.start()

    sleep(0.5 * branch.id)
    output = ({"id": branch.id, "type":"branch","events": branch.output()})
    Output2_generator(output)
    sleep(1)
    server.wait_for_termination()


def customerProcessing(customer, branch_stubs):
    customer.createStub()
    customer.processor_events()
    combined_output = customer.output()
    # Write to output files
    Output1_generator(combined_output[0])
    sleep(2)
def processes_creator(processes):
    branch_data = []
    branchIds = []
    branchProcess_data = []
    branch_stubs = []

    branch_customer_mapping = {}
    for entry in processes:
        if entry["type"] == "customer":
            customer_id = entry["id"]
            request_ids = [req["customer-request-id"] for req in entry["customer-requests"]]
            branch_customer_mapping[customer_id] = request_ids
    for process in processes:
        if process["type"] == "branch":
            branch = Branch(process["id"], process["balance"], branchIds)
            branch_data.append(branch)
            branchIds.append(branch.id)
    for branch in branch_data:
        branch_process = multiprocessing.Process(target=BranchServerInit, args=(branch,))
        branchProcess_data.append(branch_process)
        branch_process.start()

    # Allow branch processes to start
    sleep(0.25)

    branch_stubs = branch.getStubs()
    customerProcessList = []

    customers = [
        Customer(process["id"], process["customer-requests"], branch_customer_mapping)
        for process in processes
        if process["type"] == "customer"
    ]

    customerprocess_init(customers, customerProcessList, branch_stubs)
    customer_process_data(customerProcessList)
    finish_branch_processes(branchProcess_data)


def Output1_generator(output):
    output_file_path = "output1.json"

    with open(output_file_path, "a") as output_file:
        if os.path.getsize(output_file_path) > 0:
            output_file.write(",\n")
        else:
            output_file.write("[\n")

        output_file.write(json.dumps(output, indent=2))

def Output2_generator(output):
    output_file_path = "output2.json"

    with open(output_file_path, "a") as output_file:
        if os.path.getsize(output_file_path) > 0:
            output_file.write(",\n")
        else:
            output_file.write("[\n")

        formatted_output = json.dumps(output, indent=2)
        output_file.write(formatted_output)


def Output3_generator(customer_events, branch_events):
    output3 = []

    # Process customer events
    for customer_event in customer_events:
        # Add output3 events
        for event in customer_event['events']:
            customer_request_id = event['customer-request-id']
            output3.append({
                'id': customer_event['id'],
                'customer-request-id': event['customer-request-id'],
                'type': 'customer',
                'logical_clock': event['logical_clock'],
                'interface': event['interface'],
                'comment': event['comment']
            })
            for branch_event in branch_events:
                for event in branch_event['events']:
                    if event['customer-request-id'] == customer_request_id:
                        output3.append({
                            'id': branch_event['id'],
                            'customer-request-id': event['customer-request-id'],
                            'type': 'branch',
                            'logical_clock': event['logical_clock'],
                            'interface': event['interface'],
                            'comment': event['comment']
                        })
    return output3

def close_output_file(output_filename):
    with open(output_filename, "a") as output_file:
        output_file.write("\n]")


def request_handler():
    data = file_reader('input.json')
    open("output1.json", "w").close()
    open("output2.json", "w").close()
    processes_creator(data)

    close_output_file("output1.json")
    close_output_file("output2.json")

    sleep(2)
    with open('output1.json', 'r') as file:
        output_json = json.load(file)

    with open('output2.json', 'r') as file:
        output2_json = json.load(file)

        # Generate output3
        output3_json = Output3_generator(output_json, output2_json)

    with open('output3.json', 'w') as file:
        json.dump(output3_json, file, indent=2)

if __name__ == "__main__":
    request_handler()


