import json

with open('config.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

connection_parameters = data['connection_parameters']
engineers = data['engineers']
machines = data['machines']
statuses = data['statuses']
operation_types = data['operation_types']
engineers.sort()
machines.sort()

