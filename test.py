import json
import ast

options = ["comp1", "comp2"]

compDict = {}

for option in options:
    compDict[option] = 0

print(compDict, type(compDict))

compDict = json.dumps(compDict)
print(compDict, type(compDict))

compDict = ast.literal_eval(compDict)
print(compDict, type(compDict))
print(compDict["comp1"])