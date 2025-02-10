# este código revisará una carpeta en busca de archivos JSON en formato lvltutor 
# y los procesará para convertirlos a lvltutor 2

import json
import os
import csv

# constantes
PATH = "./lvltutor1"
CSV = "./exercisesAnswers.csv"

class DoubleHash:

    # constructor
    def __init__(self):
        self.DoubleHashTable = {}

    @staticmethod
    def firstKey(key: str) -> str:
        return ''.join(c for c in key if not c.isnumeric())
    @staticmethod
    def secondKey(key: str) -> str:
        return key

    # insertar en el doble hash
    def insertHash(self, key: str, value: dict):
        fisrtHashKey = self.firstKey(key)
        secondHashKey = self.secondKey(key)

        #si no existe la primera llave, la inicializamos
        if fisrtHashKey not in self.DoubleHashTable:
            self.DoubleHashTable[fisrtHashKey] = {}
        # si ya existe la segunda llave, agregamos el objeto a la lista
        if secondHashKey in self.DoubleHashTable[fisrtHashKey]:
            self.DoubleHashTable[fisrtHashKey][secondHashKey].append(value)
        else:
            # si no, lo inicializamos dentro de una lista
            self.DoubleHashTable[fisrtHashKey][secondHashKey] = [value]
    
    # buscar en el doble hash
    def searchHash(self, key: str) -> dict:
        fisrtHashKey = self.firstKey(key)
        secondHashKey = self.secondKey(key)

        if fisrtHashKey in self.DoubleHashTable:
            if secondHashKey in self.DoubleHashTable[fisrtHashKey]:
                return self.DoubleHashTable[fisrtHashKey][secondHashKey]

        return None

class SimpleHash:

    # constructor
    def __init__(self):
        self.Table = {}

    @staticmethod
    def hashKey(key: str) -> str:
        return key

    # insertar en el hash
    def insertHash(self, key: str, value: dict):
        hashKey = self.hashKey(key)
        # si ya existe la  llave, agregamos el objeto a la lista
        if hashKey in self.Table:
            self.Table[hashKey].append(value)
        else:
            # si no, lo inicializamos con una lista con el objeto dentro
            self.Table[hashKey] = [value]
    
    # buscar en el hash
    def searchHash(self, key: str) -> dict:
        hashKey = self.hashKey(key)

        if hashKey in self.Table:
            return self.Table[hashKey]

        return None

def creatorOfDoubleHash(instanceHash: any, csvPath: str, tableHash: dict) -> dict:
    with open(csvPath, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for line in reader:
            exerciseObj = { "code": str(line[0]),
                            "step": str(line[1]),
                            "0": str(line[2])[1:-1].replace("\\\\", "\\"), #la primera es la respuesta correcta
                            "1": str(line[3])[1:-1].replace("\\\\", "\\"),
                            "hint1": str(line[4]).replace("\\\\", "\\"),
                            "2": str(line[5])[1:-1].replace("\\\\", "\\"),
                            "hint2": str(line[6]).replace("\\\\", "\\"),
                            "3": str(line[7])[1:-1].replace("\\\\", "\\"),
                            "hint3": str(line[8]).replace("\\\\", "\\")
                        }
            instanceHash.insertHash(exerciseObj["code"] ,exerciseObj)
    # mostramos el hash creado en un json
    with open("hashTable.json", "w", encoding="utf-8") as file:
        json.dump(tableHash, file, indent = 4, ensure_ascii = False)

def convertirFormato(instanceHash: any, jsonFile: dict) -> dict:

    # si no es un archivo del tipo lvltutor, simplemente lo debolvemos
    if not jsonFile.get("type") == "lvltutor":
        return jsonFile

    # creamos el diccionario
    dictLvltutor2 = jsonFile.copy()

    # no cambiamos el type
    #dictLvltutor2["type"] = "lvltutor2"

    # quitamos el campo eqc
    dictLvltutor2.pop("eqc", None)
    dictLvltutor2.pop("presentation", None)

    # buscamos el array de repuestas en el doble hash
    arrayObjAnswers = instanceHash.searchHash(jsonFile["code"])

    # agregamos el campo multipleChoice para cada step
    if arrayObjAnswers is not None:
        # agregamos las respuestas
        for step in dictLvltutor2["steps"]:
            createMultipleChoice(step, arrayObjAnswers)
        
    # agregamos el campo finalAnswer para cada ejercicio que tenga mas de un paso
    if len(dictLvltutor2["steps"]) > 1:
        dictLvltutor2["finalAnswer"] = jsonFile["steps"][-1]
        dictLvltutor2["finalAnswer"]["KCs"] = unionKCs(dictLvltutor2["steps"])

    # retornamos el diccionario
    return dictLvltutor2

def unionKCs(stepArray: list) -> list:
    # creamos el array
    kcs = []
    # recorremos los steps
    for step in stepArray:
        # recorremos los KCs
        for kc in step["KCs"]:
            if kc not in kcs:
                kcs.append(kc)
    return kcs

def createMultipleChoice(step: dict, arrayObjAnswers: list) -> dict:
    # creamos el diccionario
    multipleChoice = []
    # buscamos el objeto en el doble hash
    for obj in arrayObjAnswers:
        if int(obj["step"]) == int(step["stepId"]):
            for i in range(4):
                if obj.get(str(i)) is not """""":
                    stepChoice = {
                        "id": i,
                        #copia la respuesta correcta desde answers
                        "expression": step["answers"][0]["answer"][0] if i == 0 else obj[str(i)],
                        "correct": True if i == 0 else False
                    }
                    if i > 0 and not obj[f"hint{i}"] == '""':
                        if "@" in obj[f"hint{i}"]:
                            expressionsStr = obj[f"hint{i}"].split("@")
                            print(expressionsStr)
                            stepChoice["feedbackMsg"] = expressionsStr[0]
                            stepChoice["feedbackMsgExp"] = expressionsStr[1]
                        else:
                            print(obj[f"hint{i}"])
                            stepChoice["feedbackMsg"] = obj[f'hint{i}']
                    multipleChoice.append(stepChoice)
            break
    # agregamos las opciones
    if len(multipleChoice) > 0: 
        step["multipleChoice"] = multipleChoice

def escribeJsonNuevo(jsonFile: dict, rutaDestino: str):
    # creamos el archivo
    #print(rutaDestino)
    with open(rutaDestino, "w", encoding="utf-8") as file:
        json.dump(jsonFile, file, indent = 4, ensure_ascii = False)

def procesoCarpeta(rutaActual: str, instanceHash: any):
    # recorremos los json
    for file in os.listdir(rutaActual):
        # abrimos el archivos
        with open(rutaActual+f"/{str(file)}", "r", encoding="utf-8") as jsonFile:
            # leemos el archivo
            data = json.load(jsonFile)
            # convertimos y escribimos el archivo
            rutaDestino = rutaActual.replace("lvltutor1", "lvltutor2")+f"/{str(data["code"])}.json"
            escribeJsonNuevo(convertirFormato(instanceHash, data), rutaDestino)

def recorreCarpetas(currentPath: str, instanceHash: any):
    # recorro cada topico en la carpeta
    for element in os.listdir(currentPath):
        completePath = currentPath+f"/{element}"
        if os.path.isdir(completePath):
            # si es que estamos en una carpeta, seguimos recorriendo (recursividad)
            recorreCarpetas(completePath, instanceHash)
        else:
            # si no, procesamos la carpeta actual
            procesoCarpeta(currentPath, instanceHash)
            break

def main():
    # creamos las instancia del doble hash
    dblHash = DoubleHash()
    simpleHash = SimpleHash()
    # creamos el doble hash
    creatorOfDoubleHash(simpleHash, CSV, simpleHash.Table)
    # recorremos las carpetas
    recorreCarpetas(PATH, simpleHash)

if __name__ == "__main__":
    main()