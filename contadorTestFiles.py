
"""Main executable of the project
"""

__author__ = "Miriam Fernández Osuna"
__version__ = "1.0"

import ast
import configparser
from datetime import datetime
import time
from src.business.controller.Qiskit_QCSR_Conversor.EmptyCircuitException import EmptyCircuitException
from src.business.controller.Qiskit_QCSR_Conversor.VariableNotCalculatedException import VariableNotCalculatedException
from src.business.controller.Qiskit_QCSR_Conversor.OperationNotFoundException import OperationNotFoundException
import src.business.controller.Qiskit_QCSR_Conversor.Qiskit_QCSR_Conversor as conversor
import src.business.controller.QmetricsAPI.qmetrics_functions as qmetrics
import src.business.controller.QCPDTool.views as qcpdtool
import os
import json
import logging
import traceback

configuration_file = os.path.join("resources", "config", "properties.ini")
config = configparser.ConfigParser()
config.read(configuration_file)

logging.root.handlers=[]
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(eval(config.get('log', 'file')))
        #,logging.StreamHandler()
    ],
    encoding="UTF-8"
)
logging.info("--EXCUTION STARTED")
logging.info("--INGEST STARTED")
#Searches in GitHub and ingest the data
#import src.persistency.Mongo_Ingest_Data_Dealing.languages_ingest_with_dates

logging.info("--ANTLR4, QCSR CIRCUIT, METRICS AND PATTERNS CREATION")
#Searches in db for codes in qiskit language
from pymongo import MongoClient
from pymongo import cursor

db_link = eval(config.get('MongoDB', 'db_link'))
db_name = eval(config.get('MongoDB', 'db_name'))
db_coll = eval(config.get('MongoDB', 'db_coll_accepted'))
connection = MongoClient(db_link, socketTimeoutMS=None)
dbGithub = connection[db_name]
collRepo = dbGithub[db_coll]
n_generated_trees = 0
n_generated_circuits = 0
n_blank_circuits = 0

query = {"language": "Python"}
documents: cursor.Cursor = collRepo.find(query, no_cursor_timeout=True)
refreshTime = 600 #10 minutes
startQueryTime = time.time()

contadorTestInName=0
contadorLessThan2Gates=0

for document in documents:
    nowQueryTime = time.time()
    if nowQueryTime - startQueryTime >= refreshTime:
        documents.close()
        documents = collRepo.find(query, no_cursor_timeout=True)
        startQueryTime = nowQueryTime

    #print(document["path"])
    #antlr4 of the codes and conversion from python qiskit to QCSR
    circuitsJsons = {}
    tree = ""
    try:
        tree = conversor.generateTree(document["content"], document["language"])
    except (IndentationError, Exception):
        continue

    n_generated_trees+=1
    errorsFoundAtParse = False
    errorMsg = ""

    try:
        circuitsJsons = conversor.visitTree(tree, document["language"])
        n_generated_circuits+=1
    except EmptyCircuitException as e:
        #print("Empty array error because QuantumRegister isn't called")
        logging.warning(f"{document['language']}.{document['extension']}, {document['author']}/{document['name']} | {document['path']} Empty array error because QuantumRegister isn't called")
        errorsFoundAtParse = True
        errorMsg = "The tree couldn't be generated. Empty array error because QuantumRegister isn't called"
        n_generated_circuits+=1
        n_blank_circuits+=1
    except VariableNotCalculatedException as e:
        #print("A variable during the QCSR circuit conversion couldn't be obtained")
        logging.warning(f"{document['language']}.{document['extension']}, {document['author']}/{document['name']} | {document['path']} A variable during the QCSR circuit conversion couldn't be obtained")
        errorsFoundAtParse = True
        errorMsg = f"The ast tree couldn't be generated. A variable during the QCSR circuit conversion couldn't be obtained"
    except ValueError as e:
        #print("Translator can't read variables when reading gates/circuit, the code is incompatible")
        logging.warning(f"{document['language']}.{document['extension']}, {document['author']}/{document['name']} | {document['path']} Translator can't read variables when reading gates/circuit, the code is incompatible")
        errorsFoundAtParse = True
        errorMsg = f"The antlr4 tree couldn't be generated. Translator can't read variables when reading gates/circuit, the code is incompatible\n{traceback.format_exc()}"
    except (AttributeError, KeyError, IndexError, TypeError, OperationNotFoundException, ZeroDivisionError, Exception) as e: 
        #print("-------Throws an error----------")
        #print(f"{e.__str__()} {document['path']}")
        logging.warning(f"{document['language']}.{document['extension']}, {document['author']}/{document['name']} | {document['path']} throws an error")
        errorsFoundAtParse = True
        errorMsg = f"The tree couldn't be generated. The circuit isn't converted\n{traceback.format_exc()}"

    #TODO: insert general error

    circuitsMadeToTest = 0

    if "test" in document["path"]:
        contadorTestInName+=1

    for circuit_id, circuit in circuitsJsons.items():
        
        #TO COUNT TEST FILES
        circuitCounter=0
        circuitArray = ast.literal_eval(circuit) #[[H, H], [H], []]
        for i in circuitArray: #[H, H]
            circuitCounter+=len(i)
            
        if circuitCounter <=2:
            circuitsMadeToTest+=1
    
    if circuitsMadeToTest >= 1:
        contadorLessThan2Gates+=1

connection.close()

print(f"Number of codes with test in document path: {contadorTestInName}")
print(f"Number of codes with at least a circuit with less than 2 gates: {contadorLessThan2Gates}")
