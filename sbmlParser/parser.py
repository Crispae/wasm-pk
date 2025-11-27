# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 12:12:05 2018

@author: Steve
"""

import libsbml
import re
import sys
from sbmlParser import dataclasses


def ParseParameterAssignment(parameterIndex, parameter):
    # if parameter.isSetValue() and parameter.isSetId():

    #    if parameter.isSetName():
    #        parameterName = parameter.getName()
    #        parameterValue = parameter.getValue()
    #        #print("Parameter," + str(parameterIndex + 1) + "\n" + str(parameterId) + "\nValue\n" + str(parameterValue))
    #        outputFile.write(str(parameterName) + ";" + str(parameterValue) + "\n")
    #        return
    newParameter = dataclasses.ParameterData()
    if parameter.isSetName():
        newParameter.name = parameter.getName()
    else:
        newParameter.name = ""

    if parameter.isSetId():
        newParameter.Id = parameter.getId()
        if parameter.isSetValue():
            newParameter.value = parameter.getValue()
        else:
            newParameter.value = None

        if parameter.isSetConstant():
            newParameter.isConstant = parameter.getConstant()
        else:
            newParameter.isConstant = False
        # print("Parameter," + str(parameterIndex + 1) + "\n" + str(parameterId) + "\nValue\n" + str(parameterValue))
    #        outputFile.write(str(parameterId) + "; " + str(parameterValue) + "; " + str(parameterConst) + "; " + parameterName + "\n")
    else:
        raise Exception("Parameter with no Id")

    return newParameter


def ParseRule(ruleIndex, rule):
    if rule.isAlgebraic():
        raise Exception("Algebraic rules are currently not supported")

    #        outputFile.write("Rule; " + ruleId + "; Algebraic; " + ruleName + "\n")
    if rule.isAssignment():
        newRule = dataclasses.AssignmentRuleData()
    #        outputFile.write("Rule; " + ruleId + "; Assignment; " + ruleName + "\n")
    if rule.isRate():
        newRule = dataclasses.RateRuleData()
    #        outputFile.write("Rule; " + ruleId + "; Rate; " + ruleName + "\n")

    if rule.isSetName():
        newRule.name = str(rule.getName())
    else:
        newRule.name = ""

    if rule.isSetIdAttribute():
        newRule.Id = str(rule.getIdAttribute())
    else:
        newRule.Id = str(ruleIndex + 1)

    newRule.variable = rule.getVariable()
    newRule.math = libsbml.formulaToString(rule.getMath())
    ## We used here formulaTostring, istead of L3string, because dimenstions is not important for calulation

    if rule.getVariable() == "":
        raise Exception("Algebraic rules are currently not supported")

    else:
        return newRule


#        outputFile.write(rule.getVariable() + ";" + formulaToString(rule.getMath()) + "\n")


def ParseSpecies(speciesIndex, species):
    newSpecies = dataclasses.SpeciesData()

    if species.isSetName():
        newSpecies.name = species.getName()
    else:
        newSpecies.name = ""

    #    outputFile.write("Species; " + str(speciesIndex + 1) + "; " + speciesName + "\n" )

    newSpecies.Id = species.getId()
    newSpecies.compartment = species.getCompartment()
    newSpecies.isConstant = species.getConstant()
    newSpecies.isBoundarySpecies = species.getBoundaryCondition()
    newSpecies.hasOnlySubstanceUnits = species.getHasOnlySubstanceUnits()
    if species.isSetInitialAmount():
        newSpecies.valueType = "Amount"
        newSpecies.value = species.getInitialAmount()
    # assert(species.isSetInitialAmount())

    elif species.isSetInitialConcentration():
        newSpecies.valueType = "Concentration"
        newSpecies.value = species.getInitialConcentration()
    # assert(species.isSetInitialConcentration())
    else:
        newSpecies.valueType = "Amount"
        newSpecies.value = None
    return newSpecies


# outputFile.write(species.getId() + "; " + valueType + "; " + speciesCompartment + '; ' + str(value) + '; ' + str(speciesConstant) + '; ' + str(speciesBoundary) + '; ' + str(speciesFormulaUnits) + '\n')


def ParseReaction(reactionIndex, reaction):
    newReaction = dataclasses.ReactionData()
    if reaction.isSetIdAttribute():
        newReaction.Id = reaction.getIdAttribute()
    else:
        newReaction.Id = str(ruleIndex + 1)

    if reaction.isSetName():
        newReaction.name = reaction.getName()
    else:
        newReaction.name = ""

    #    outputFile.write("Reaction; " + reactionId + "; " + reactionName + "\n")

    numReactants = reaction.getListOfReactants().size()
    numProducts = reaction.getListOfProducts().size()

    newReaction.reactants = []
    newReaction.products = []
    i = 0
    for i in range(numReactants):
        reactantStoich = float(reaction.getListOfReactants().get(i).getStoichiometry())
        reactantSpecies = reaction.getListOfReactants().get(i).getSpecies()

        newReaction.reactants.append([reactantStoich, reactantSpecies])

    i = 0
    for i in range(numProducts):
        productStoich = float(reaction.getListOfProducts().get(i).getStoichiometry())
        #        productsString += " , "
        productSpecies = reaction.getListOfProducts().get(i).getSpecies()

        newReaction.products.append([productStoich, productSpecies])

    rateLawObject = reaction.getKineticLaw()

    if rateLawObject.getMath() != None:
        newReaction.rateLaw = libsbml.formulaToString(rateLawObject.getMath())
    #        outputFile.write(formulaToString(rateLaw.getMath()) + "\n")
    else:
        raise Exception("Rate law defined by plugin that is not currently supported")
    #        outputFile.write("None\n")

    numRateLawParams = rateLawObject.getNumParameters()

    if numRateLawParams > 0:
        newReaction.rxnParameters = []
        for i in range(numRateLawParams):
            param = rateLawObject.getParameter(i)
            #            paramsString += param.getId() + "; " + str(param.getValue())
            newReaction.rxnParameters.append([param.getId(), param.getValue()])

    else:
        newReaction.rxnParameters = []

    return newReaction


#    outputFile.write(paramsString + "\n")


def ParseCompartment(compartmentIndex, compartment):
    newCompartment = dataclasses.CompartmentData()

    newCompartment.Id = compartment.getId()

    if compartment.isSetName():
        newCompartment.name = compartment.getName()
    else:
        newCompartment.name = ""

    if compartment.isSetSize():
        newCompartment.size = compartment.getSize()
    else:
        newCompartment.size = None

    if compartment.isSetSpatialDimensions():
        newCompartment.dimensionality = compartment.getSpatialDimensions()
    else:
        newCompartment.dimensionality = None

    if compartment.isSetConstant():
        newCompartment.isConstant = compartment.getConstant()
    else:
        newCompartment.isConstant = False

    #    outputFile.write("Compartment; " + str(compartmentIndex + 1) + "\nSize; " + str(size) + "\nDimensionality; " + str(dimensions) + "\n")
    #    outputFile.write("Compartment; " + compartment.getId() + "; " + compartmentName + "\nSize; " + str(size) + "\nDimensionality; " + str(dimensions) + "\n")
    return newCompartment


def ParseFunction(functionIndex, function):
    newFunction = dataclasses.FunctionData()
    #    outputFile.write("Function; " + str(functionIndex + 1) + "\n")

    if function.isSetName():
        newFunction.name = function.getName()
    else:
        newFunction.name = ""

    #    outputFile.write(function.getId() + ";" + functionName + "\n")
    newFunction.Id = function.getId()
    newFunction.mathString = libsbml.formulaToString(function.getMath())
    numArguments = function.getNumArguments()
    funcStringIter = re.finditer(",", newFunction.mathString)
    newFunction.arguments = []
    for i in range(numArguments):
        match = next(funcStringIter)
        newFunction.arguments.append(libsbml.formulaToString(function.getArgument(i)))

    newFunction.mathString = newFunction.mathString[match.end() + 1 : -1]

    #    functionMath = formulaToString(function.getMath())
    #    numArguments = function.getNumArguments()
    #    funcStringIter = re.finditer(",", functionMath)
    #    argumentString = ""
    #    for i in range(numArguments):
    #        match = next(funcStringIter)
    #        argumentString += formulaToString(function.getArgument(i))
    #        if i != numArguments-1:
    #            argumentString += ";"
    #    argumentString += "\n"
    #    functionMath = functionMath[match.end()+1:-1]
    #    outputFile.write(argumentString)
    #    outputFile.write(functionMath + "\n")

    return newFunction


def ParseInitialAssignment(assignmentIndex, assignment):
    newAssignment = dataclasses.InitialAssignmentData()

    if assignment.isSetIdAttribute():
        newAssignment.Id = str(assignment.getIdAttribute())
    else:
        newAssignment.Id = str(assignmentIndex + 1)

    newAssignment.variable = assignment.getSymbol()
    newAssignment.math = libsbml.formulaToString(assignment.getMath())
    newAssignment.name = assignment.getName()
    return newAssignment


def ParseSBMLFile(filePath):
    """
    Parameters
    ----------
    filePath : string
        File path of the SBML model to be parsed


    Returns
    -------
    dict
        A dictionary containing the model's components and their properties in JSON-serializable format.

    Notes
    -----
    This function manages the process extracting an SBML model's elements using libSBML.
    The returned dictionary can be directly serialized to JSON using json.dumps().

    """
    doc = libsbml.readSBML(filePath)

    # Check for errors (but allow warnings)
    num_errors = doc.getNumErrors()
    if num_errors > 0:
        # Check if there are any errors with severity >= 2 (errors, not just warnings)
        has_errors = False
        for i in range(num_errors):
            error = doc.getError(i)
            if error.getSeverity() >= 2:  # Error or fatal error
                has_errors = True
                print(f"SBML Error: {error.getMessage()}")

        if has_errors:
            raise Exception(
                f"SBML file has validation errors. Use debug_sbml.py to see details."
            )
        else:
            print(f"SBML file has {num_errors} warnings but no errors. Proceeding...")

    model = doc.getModel()

    modelData = dataclasses.ModelData()
    #    outputFile = open(outputPath, "w")

    #    outputFile.write("Parameters"+ "\n")
    for i in range(model.getNumParameters()):
        newParameter = ParseParameterAssignment(i, model.getParameter(i))
        modelData.parameters[newParameter.Id] = newParameter
    #    outputFile.write("Compartments" + "\n")
    for i in range(model.getNumCompartments()):
        newCompartment = ParseCompartment(i, model.getCompartment(i))
        modelData.compartments[newCompartment.Id] = newCompartment
    #    outputFile.write("Species"+ "\n")
    for i in range(model.getNumSpecies()):
        newSpecies = ParseSpecies(i, model.getSpecies(i))
        modelData.species[newSpecies.Id] = newSpecies
    #    outputFile.write("Functions" + "\n")
    for i in range(model.getNumFunctionDefinitions()):
        newFunction = ParseFunction(i, model.getFunctionDefinition(i))
        modelData.functions[newFunction.Id] = newFunction
    #    outputFile.write("Rules"+ "\n")
    for i in range(model.getNumRules()):
        newRule = ParseRule(i, model.getRule(i))
        if type(newRule) == dataclasses.AssignmentRuleData:
            modelData.assignmentRules[newRule.Id] = newRule
        elif type(newRule) == dataclasses.RateRuleData:
            modelData.rateRules[newRule.Id] = newRule
    #    outputFile.write("Reactions"+ "\n")
    for i in range(model.getNumReactions()):
        newReaction = ParseReaction(i, model.getReaction(i))
        modelData.reactions[newReaction.Id] = newReaction

    for i in range(model.getNumInitialAssignments()):
        newAssignment = ParseInitialAssignment(i, model.getInitialAssignment(i))
        modelData.initialAssignments[newAssignment.Id] = newAssignment
    # print(model.getNumSpecies())

    # Convert ModelData to dictionary format for JSON serialization
    modelDictionary = {
        "parameters": {},
        "compartments": {},
        "species": {},
        "reactions": {},
        "functions": {},
        "assignmentRules": {},
        "rateRules": {},
        "initialAssignments": {},
    }

    for key, component in modelData.parameters.items():
        modelDictionary["parameters"][key] = component.ToDictionary()

    for key, component in modelData.compartments.items():
        modelDictionary["compartments"][key] = component.ToDictionary()

    for key, component in modelData.species.items():
        modelDictionary["species"][key] = component.ToDictionary()

    for key, component in modelData.reactions.items():
        modelDictionary["reactions"][key] = component.ToDictionary()

    for key, component in modelData.functions.items():
        modelDictionary["functions"][key] = component.ToDictionary()

    for key, component in modelData.assignmentRules.items():
        modelDictionary["assignmentRules"][key] = component.ToDictionary()

    for key, component in modelData.rateRules.items():
        modelDictionary["rateRules"][key] = component.ToDictionary()

    for key, component in modelData.initialAssignments.items():
        modelDictionary["initialAssignments"][key] = component.ToDictionary()

    return modelDictionary


if __name__ == "__main__":
    import json

    filePath = sys.argv[1]
    #    outputPath = sys.argv[2]
    modelData = ParseSBMLFile(filePath)
    print(json.dumps(modelData, indent=4))
