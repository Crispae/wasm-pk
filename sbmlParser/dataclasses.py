# -*- coding: utf-8 -*-
"""
Created on Sun May 12 20:14:31 2019

@author: Steve
"""
# The purpose of this script is to define SBML classes used by the functions for parsing
# SBML files and generating python versions of the models. These classes serve little
# more than namespaces

import json


class ModelData:
    """
    This class contains a dictionary for each type of SBML model component.

    Each dictionary uses the Id of each model component (a str) as a key, and each
    value is of the appropriate class for that component.

    Attributes
    ----------
    assignmentRules : dict
        Each value is an instance of AssignmentRuleData
    compartments : dict
        Each value is an instance of CompartmentData
    functions : dict
        Each value is an instance of FunctionData
    initialAssignments : dict
        Each value is an instance of InitialAssignmentData
    parameters : dict
        Each value is an instance of ParameterData
    rateRules : dict
        Each value is an instance of RateRuleData
    reactions : dict
        Each value is an instance of ReactionData
    species : dict
        Each value is an instance of SpeciesData


    Methods
    -------
    DumpToJSON(filePath)
    LoadFromJSON(filePath)
        These methods are used for creating a JSON file and for creating an instance of ModelData from a JSON file, respectively.
        Note that LoadFromJSON is a class method that creates a new instance of ModelData.


    """

    def __init__(self):
        self.parameters = {}
        self.compartments = {}
        self.species = {}
        self.reactions = {}
        self.functions = {}

        self.assignmentRules = {}
        self.rateRules = {}

        self.initialAssignments = {}
        self.events = {}

    def DumpToJSON(self, filePath):
        fileObject = open(filePath, "w")

        modelDictionary = {
            "parameters": {},
            "compartments": {},
            "species": {},
            "reactions": {},
            "functions": {},
            "assignmentRules": {},
            "rateRules": {},
            "initialAssignments": {},
            "events": {},
        }

        for key, component in self.parameters.items():
            modelDictionary["parameters"][key] = component.ToDictionary()

        for key, component in self.compartments.items():
            modelDictionary["compartments"][key] = component.ToDictionary()

        for key, component in self.species.items():
            modelDictionary["species"][key] = component.ToDictionary()

        for key, component in self.reactions.items():
            modelDictionary["reactions"][key] = component.ToDictionary()

        for key, component in self.functions.items():
            modelDictionary["functions"][key] = component.ToDictionary()

        for key, component in self.assignmentRules.items():
            modelDictionary["assignmentRules"][key] = component.ToDictionary()

        for key, component in self.rateRules.items():
            modelDictionary["rateRules"][key] = component.ToDictionary()

        for key, component in self.initialAssignments.items():
            modelDictionary["initialAssignments"][key] = component.ToDictionary()

        for key, component in self.events.items():
            modelDictionary["events"][key] = component.ToDictionary()

        json.dump(modelDictionary, fileObject, indent="\t")
        fileObject.close()

    @classmethod
    def LoadFromJSON(cls, filePath):
        file = open(filePath, "r")
        modelData = json.load(file)
        file.close()

        newModel = cls()

        for key, componentDict in modelData["parameters"].items():
            newModel.parameters[key] = ParameterData.ConstructFromDict(componentDict)

        for key, componentDict in modelData["compartments"].items():
            newModel.compartments[key] = CompartmentData.ConstructFromDict(
                componentDict
            )

        for key, componentDict in modelData["species"].items():
            newModel.species[key] = SpeciesData.ConstructFromDict(componentDict)

        for key, componentDict in modelData["reactions"].items():
            newModel.reactions[key] = ReactionData.ConstructFromDict(componentDict)

        for key, componentDict in modelData["functions"].items():
            newModel.functions[key] = FunctionData.ConstructFromDict(componentDict)

        for key, componentDict in modelData["assignmentRules"].items():
            newModel.assignmentRules[key] = AssignmentRuleData.ConstructFromDict(
                componentDict
            )

        for key, componentDict in modelData["rateRules"].items():
            newModel.rateRules[key] = RateRuleData.ConstructFromDict(componentDict)

        for key, componentDict in modelData["initialAssignments"].items():
            newModel.initialAssignments[key] = InitialAssignmentData.ConstructFromDict(
                componentDict
            )

        for key, componentDict in modelData.get("events", {}).items():
            newModel.events[key] = EventData.ConstructFromDict(componentDict)

        return newModel


class ParameterData:
    """
    This class holds all of the necessary data from an SBML model for a parameter.

    Attributes
    ----------
    Id : str
    isConstant : str
    name : str
    value : str
    """

    def __init__(self):
        self.Id = None
        self.value = None
        self.isConstant = None
        self.name = None

    def ToDictionary(self):
        # This function turns this class into a dictionary to prep dumping to JSON
        returnDict = {
            "Id": self.Id,
            "name": self.name,
            "value": self.value,
            "isConstant": self.isConstant,
        }
        return returnDict

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()

        newComponent.Id = dataDict["Id"]
        newComponent.name = dataDict["name"]
        newComponent.value = dataDict["value"]
        newComponent.isConstant = dataDict["isConstant"]

        return newComponent


class RateRuleData:
    """
    This class holds all of the necessary data from an SBML model for a rate rule.

    Attributes
    ----------
    Id : str
    math : str
    name : str
    variable : str
    """

    def __init__(self):
        self.Id = None
        self.variable = None
        self.math = None
        self.name = None

    def ToDictionary(self):
        # This function turns this class into a dictionary to prep dumping to JSON
        returnDict = {
            "Id": self.Id,
            "name": self.name,
            "variable": self.variable,
            "math": self.math,
        }
        return returnDict

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()

        newComponent.Id = dataDict["Id"]
        newComponent.name = dataDict["name"]
        newComponent.variable = dataDict["variable"]
        newComponent.math = dataDict["math"]

        return newComponent


class AssignmentRuleData:
    """
    This class holds all of the necessary data from an SBML model for an assignement rule.

    Attributes
    ----------
    Id : str
    math : str
    name : str
    variable : str
    """

    def __init__(self):
        self.Id = None
        self.variable = None
        self.math = None
        self.name = None

    def ToDictionary(self):
        # This function turns this class into a dictionary to prep dumping to JSON
        returnDict = {
            "Id": self.Id,
            "name": self.name,
            "variable": self.variable,
            "math": self.math,
        }
        return returnDict

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()

        newComponent.Id = dataDict["Id"]
        newComponent.name = dataDict["name"]
        newComponent.variable = dataDict["variable"]
        newComponent.math = dataDict["math"]

        return newComponent


class CompartmentData:
    """
    This class holds all of the necessary data from an SBML model for a compartment.

    Attributes
    ----------
    dimensionality : str
    Id : str
    isConstant : str
    name : str
    size : str
    """

    def __init__(self):
        self.Id = None
        self.size = None
        self.dimensionality = None
        self.name = None
        self.isConstant = None

    def ToDictionary(self):
        # This function turns this class into a dictionary to prep dumping to JSON
        returnDict = {
            "Id": self.Id,
            "name": self.name,
            "size": self.size,
            "dimensionality": self.dimensionality,
            "isConstant": self.isConstant,
        }
        return returnDict

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()

        newComponent.Id = dataDict["Id"]
        newComponent.name = dataDict["name"]
        newComponent.size = dataDict["size"]
        newComponent.dimensionality = dataDict["dimensionality"]
        newComponent.isConstant = dataDict["isConstant"]

        return newComponent


class SpeciesData:
    """
    This class holds all of the necessary data from an SBML model for a species.

    Attributes
    ----------
    compartment : str
    Id : str
    isBoudarySpecies : str
    isConstant : str
    hasOnlySubstanceUnits : str
    name : str
    value : str
    valueType : str
    """

    def __init__(self):
        self.Id = None
        self.valueType = None
        self.hasOnlySubstanceUnits = None
        self.compartment = None
        self.value = None
        self.isConstant = None
        self.isBoudarySpecies = None
        self.name = None

    def ToDictionary(self):
        # This function turns this class into a dictionary to prep dumping to JSON
        returnDict = {
            "Id": self.Id,
            "name": self.name,
            "value": self.value,
            "valueType": self.valueType,
            "compartment": self.compartment,
            "isConstant": self.isConstant,
            "isBoundarySpecies": self.isBoudarySpecies,
            "hasOnlySubstanceUnits": self.hasOnlySubstanceUnits,
        }
        return returnDict

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()

        newComponent.Id = dataDict["Id"]
        newComponent.name = dataDict["name"]
        newComponent.value = dataDict["value"]
        newComponent.valueType = dataDict["valueType"]
        newComponent.compartment = dataDict["compartment"]
        newComponent.isConstant = dataDict["isConstant"]
        newComponent.isBoundarySpecies = dataDict["isBoundarySpecies"]
        newComponent.hasOnlySubstanceUnits = dataDict["hasOnlySubstanceUnits"]

        return newComponent


class ReactionData:
    """
    This class holds all of the necessary data from an SBML model for a reaction.

    Attributes
    ----------
    Id : str
    name : str
    rateLaw : str
    reactants : str
    reactionIndex : str
    rxnParameters : str
    """

    def __init__(self):
        self.Id = None
        self.reactionIndex = None  # used in the logic for setting up stoichCoeffMat
        self.reactants = None  # reactants only
        self.products = None  # products in separate list
        self.rateLaw = None
        self.rxnParameters = None
        self.name = None

    def ToDictionary(self):
        # This function turns this class into a dictionary to prep dumping to JSON
        returnDict = {
            "Id": self.Id,
            "name": self.name,
            "reactants": self.reactants,
            "products": self.products,
            "rxnParameters": self.rxnParameters,
            "rateLaw": self.rateLaw,
        }
        return returnDict

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()

        newComponent.Id = dataDict["Id"]
        newComponent.name = dataDict["name"]
        newComponent.reactants = dataDict["reactants"]
        newComponent.products = dataDict.get("products", [])
        newComponent.rxnParameters = dataDict["rxnParameters"]
        newComponent.rateLaw = dataDict["rateLaw"]

        return newComponent


class FunctionData:
    """
    This class holds all of the necessary data from an SBML model for a function definition.

    Attributes
    ----------
    arguments : str
    Id : str
    mathString : str
    name : str
    """

    def __init__(self):
        self.Id = None
        self.arguments = None
        self.mathString = None
        self.name = None

    def ToDictionary(self):
        # This function turns this class into a dictionary to prep dumping to JSON
        returnDict = {
            "Id": self.Id,
            "name": self.name,
            "arguments": self.arguments,
            "mathString": self.mathString,
        }
        return returnDict

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()

        newComponent.Id = dataDict["Id"]
        newComponent.name = dataDict["name"]
        newComponent.arguments = dataDict["arguments"]
        newComponent.mathString = dataDict["mathString"]

        return newComponent


class InitialAssignmentData:
    """
    This class holds all of the necessary data from an SBML model for an initial assignment.

    Attributes
    ----------
    Id : str
    math : str
    name : str
    variable : str
    """

    def __init__(self):
        self.Id = None
        self.variable = None
        self.math = None
        self.name = None

    def ToDictionary(self):
        # This function turns this class into a dictionary to prep dumping to JSON
        returnDict = {
            "Id": self.Id,
            "name": self.name,
            "variable": self.variable,
            "math": self.math,
        }
        return returnDict

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()

        newComponent.Id = dataDict["Id"]
        newComponent.name = dataDict["name"]
        newComponent.variable = dataDict["variable"]
        newComponent.math = dataDict["math"]

        return newComponent
# -*- coding: utf-8 -*-
"""
Event-related data classes for SBML events
"""


class EventAssignmentData:
    """
    This class holds data for an SBML event assignment.

    Attributes
    ----------
    variable : str
        The variable (species/parameter) being modified
    math : str
        MathML expression for the assignment value
    """

    def __init__(self):
        self.variable = None
        self.math = None

    def ToDictionary(self):
        return {
            "variable": self.variable,
            "math": self.math,
        }

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()
        newComponent.variable = dataDict["variable"]
        newComponent.math = dataDict["math"]
        return newComponent


class EventData:
    """
    This class holds all necessary data from an SBML model for an event.

    Attributes
    ----------
    Id : str
    name : str
    trigger : str
        MathML expression for the trigger condition
    delay : str
        MathML expression for delay (optional)
    useValuesFromTriggerTime : bool
    eventAssignments : list of EventAssignmentData
    """

    def __init__(self):
        self.Id = None
        self.name = None
        self.trigger = None
        self.delay = None
        self.useValuesFromTriggerTime = True
        self.eventAssignments = []

    def ToDictionary(self):
        return {
            "Id": self.Id,
            "name": self.name,
            "trigger": self.trigger,
            "delay": self.delay,
            "useValuesFromTriggerTime": self.useValuesFromTriggerTime,
            "eventAssignments": [ea.ToDictionary() for ea in self.eventAssignments],
        }

    @classmethod
    def ConstructFromDict(cls, dataDict):
        newComponent = cls()
        newComponent.Id = dataDict["Id"]
        newComponent.name = dataDict.get("name")
        newComponent.trigger = dataDict["trigger"]
        newComponent.delay = dataDict.get("delay")
        newComponent.useValuesFromTriggerTime = dataDict.get("useValuesFromTriggerTime", True)
        newComponent.eventAssignments = [
            EventAssignmentData.ConstructFromDict(ea)
            for ea in dataDict.get("eventAssignments", [])
        ]
        return newComponent
