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
