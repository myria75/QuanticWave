import csv
import numpy as np

remove_first_columns_Metrics = 6
remove_last_columns_Metrics = 4
remove_first_columns_Patterns = 40
circuit_position = 6
delimiter = ";"
file_path = "./src/presentation/frontend/app/dataset_openqasm_qiskit.csv"
path_position = 5
all_paths = "*"

def getTableHeaderMetrics():
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        line_count = 0

        for row in csv_reader:
            if remove_first_columns_Metrics > 0:
                del row[:remove_first_columns_Metrics]
            
            if remove_last_columns_Metrics > 0:
                del row[-remove_last_columns_Metrics:]
            
            for i in range(0, len(row)):
                if row[i].startswith("m."):
                    row[i] = row[i].replace("m.", "", 1)

            if line_count == 0:
                return row

def getTableHeaderPatterns():
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        line_count = 0

        for row in csv_reader:
            if remove_first_columns_Patterns > 0:
                del row[(circuit_position+1):remove_first_columns_Patterns]
            
            del row[0:(circuit_position)]
            
            for i in range(0, len(row)):
                if row[i].startswith("p."):
                    row[i] = row[i].replace("p.", "", 1)

            if line_count == 0:
                return row
            
def getTableContentMetrics(path):
    rows = []
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        line_count = 0
        
        for row in csv_reader:
            if (line_count == 0) or (path != all_paths and row[path_position] != path):
                line_count += 1
                continue
            else:
                if remove_first_columns_Metrics > 0:
                    del row[:remove_first_columns_Metrics]
                
                if remove_last_columns_Metrics > 0:
                    del row[-remove_last_columns_Metrics:]

                for i in range(len(row)):
                    try:
                        row[i]= int(float(row[i]))
                    except ValueError:
                        pass
                
                rows.append(row)
                line_count += 1
    return rows

def getTableContentPatterns(path):
    rows = []
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        line_count = 0
        
        for row in csv_reader:
            if (line_count == 0) or (path != all_paths and row[path_position] != path):
                line_count += 1
                continue
            else:
                if remove_first_columns_Patterns > 0:
                    del row[(circuit_position+1):remove_first_columns_Patterns]
                
                del row[0:(circuit_position)]
                
                rows.append(row)
                line_count += 1
    return rows

def getAllPaths():
    all_paths = []

    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        line_count = 0
        
        for row in csv_reader:
            if line_count != 0:
                all_paths.append(row[path_position])
            line_count+=1
    
    return list(set(all_paths))

def getStatisticsQiskit():
    pattern_data = getTableContentPatterns(all_paths)
    initialization_data = [row[1] for row in pattern_data]
    superposition_data = [row[2] for row in pattern_data]
    oracle_data = [row[3] for row in pattern_data]
    entanglement_data = [row[4] for row in pattern_data]
    
    initialization_value = initialization_data.count("True")
    superposition_value = superposition_data.count("True")
    oracle_value= oracle_data.count("True")
    entanglement_value= entanglement_data.count("True")

    return [initialization_value, superposition_value, oracle_value,  entanglement_value]

def getMinimum():
    metrics: list = getTableContentMetrics(all_paths)
    metrics = [subarray[1:] for subarray in metrics]
    metrics = [[round(float(value), 3) for value in row] for row in metrics]
    
    metricsArray = np.array(metrics)

    minimums = []

    for col in range(metricsArray.shape[1]):
        column = metricsArray[:, col]
        minimums.append(np.min(column))
    
    return minimums

def getMaximun():
    metrics: list = getTableContentMetrics(all_paths)
    metrics = [subarray[1:] for subarray in metrics]
    metrics = [[round(float(value), 3) for value in row] for row in metrics]
    
    metricsArray = np.array(metrics)

    maximuns = []

    for col in range(metricsArray.shape[1]):
        column = metricsArray[:, col]
        maximuns.append(np.max(column))
        
    return maximuns

def getAverage():
    metrics: list = getTableContentMetrics(all_paths)
    metrics = [subarray[1:] for subarray in metrics]
    metrics = [[round(float(value), 3) for value in row] for row in metrics]
    metricsArray = np.array(metrics)

    averages = []

    for col in range(metricsArray.shape[1]):
        column = metricsArray[:, col]
        #averages.append(round(np.mean(column), 3))
        average = np.mean(column)
        averages.append(average)
        # averages.append(round(np.mean(column), 3))
    
    return averages



def getStandardDeviation():
    metrics: list = getTableContentMetrics(all_paths)
    metrics = [subarray[1:] for subarray in metrics]
    metrics = [[round(float(value), 3) for value in row] for row in metrics]
    
    metricsArray = np.array(metrics)

    standardDeviations = []

    for col in range(metricsArray.shape[1]):
        column = metricsArray[:, col]
        standardDeviation = np.std(column)

        standardDeviations.append(standardDeviation)
        #standardDeviations.append(round(np.std(column), 3))     
    
    return standardDeviations

#print(getAverage())