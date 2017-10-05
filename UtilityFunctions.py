"""!@ functions for extracting the information from domain descriptor strings.
This includes functions to extract the preceeding class name, the specific descriptor name
and so forth
Created on Nov 7, 2015

@author: insyte
"""

from collections import OrderedDict
from compiler.ast import flatten
import copy
import os
import pickle


#===============================================================================
# 
#===============================================================================

def convertNestedListToNestedTuple(nestedList):
    '''
    '''
    ret_tuple = [] # yes the irony is not lost on me
    
    for entry in nestedList:
        if type(entry) == list:
            ret_tuple.append(convertNestedListToNestedTuple(entry))
        else:
            ret_tuple.append(entry)
    
    return tuple(ret_tuple)

#============================================================================================
def getFirstPrefixClassName(descriptorString):
    '''!@brief simply splits the string by "_" to get class prefix
    @param descriptorString to be split
    '''
    try:
        tokens = descriptorString.split("_");
        return tokens[0];
    except:
        return None
#============================================================================================
def getSpecificInstanceName(descriptorString):
    '''!@brief simply splits the string by "_" to get instance name (last part)
    @param descriptorString to be split
    '''
    tokens = descriptorString.split("_");
    return tokens[len(tokens)-1];
#============================================================================================
def compactPrintCompoundDataStructure(stateDescriptor,spacer,precursor):
    '''!@brief will print with each level in SAME line, and indented by spacer
    @param stateDescriptor: the data struct to be printed
    @param spacer: the indentation string
    @param precursor: What to print at the start of each line
    '''
    
    if type(stateDescriptor) == dict:
        for key in stateDescriptor:
            newPrecursor = precursor + spacer + key                        
            compactPrintCompoundDataStructure(stateDescriptor[key], spacer,newPrecursor)
    elif type(stateDescriptor) == list:
        for item in stateDescriptor:
            print(precursor,spacer,item)
            
    elif type(stateDescriptor) == tuple:
        for item in stateDescriptor:
            print(precursor,spacer,item)
    else:
        print(precursor,spacer,stateDescriptor);  
    

#============================================================================================
def printCompoundDataStructure(stateDescriptor, spacer):
    '''!@brief will print with each level in NEW line, and indented by spacer
    @param stateDescriptor: the data struct to be printed
    @param spacer: the indentation string
    '''
    if type(stateDescriptor) == dict or type(stateDescriptor) == OrderedDict:
        for key in stateDescriptor.keys():
            print(spacer,key)            
            printCompoundDataStructure(stateDescriptor[key], (spacer + spacer))
    elif type(stateDescriptor) == list:
        for item in stateDescriptor:
            print(spacer,item)
            
    elif type(stateDescriptor) == tuple:
        for item in stateDescriptor:
            print(spacer,item)
    else:
        print(spacer,stateDescriptor);

#============================================================================================
def getLayeredStringFormOfDataStructure(dataStruct,spacer="+"):
    '''!@brief returns list of lines to each leaf node
    @param dataStruct: the data struct to be parsed
    @param spacer: a string that connects the levels of the compound data struct    
    '''
    returnList =[]
    if type(dataStruct) == dict:
        keyList = dataStruct.keys()
        for key in sorted(keyList):
            stringVersion = str(key)
            returnListEntryStart = stringVersion            
            remainingPath = \
                getLayeredStringFormOfDataStructure(dataStruct[key],spacer)
            for addendum in remainingPath:
                returnList.append(spacer.join([returnListEntryStart,addendum]))
    #need a seperate entry for ordered dict, since I do NOT want to sort alphabetically
    #it is an ordered dict, and the order is in it.
    elif type(dataStruct) == OrderedDict:
        keyList = dataStruct.keys()
        for key in keyList:
            stringVersion = str(key)
            returnListEntryStart = stringVersion            
            remainingPath = \
                getLayeredStringFormOfDataStructure(dataStruct[key],spacer)
            for addendum in remainingPath:
                returnList.append(spacer.join([returnListEntryStart,addendum]))
    #for lists or tuples simply return as a list
    elif type(dataStruct) == list or type(dataStruct) == tuple:
        for unit in dataStruct:
            returnList.append(str(unit)) 
    #last case is when it is a single value             
    else:
        returnList = [str(dataStruct)]
    
    return returnList

#============================================================================================        
def getSingleStringRepresentationOfState(domainState):
    '''!@brief converts the state dict into a long string with space separators
    @param domainState: the dict containing the objects and their states
    @return the single string representation
    '''
    ret_string = ""
    ret_stringListFormat = []
    
    #need to get all the keys are order them into a list FIRST
    sortedKeys = list(domainState.keys())
    sortedKeys.sort()    
    for currentKey in sortedKeys:
        #then insert the string representation of the key into the return string
        ret_stringListFormat.append(str(currentKey))
        currentValue = domainState[currentKey]
        if type(currentValue) == dict:
            valueString = getSingleStringRepresentationOfState(currentValue)
            ret_stringListFormat.append(" " + valueString + " ")
        else:
            ret_stringListFormat.append(" " + str(currentValue) + " ")
            #even if it is a list or tuple
            
    ret_string = "".join(ret_stringListFormat)
    return ret_string

def flattenList(compoundList):
    '''!@brief:takes arbitrarily compound list to flatten
    can be a list of lists, or a list of lists of lists.
    @return: a flat list with all the entries from the container lists
    '''
    #change the implementation in python 3.0 as the compiler.ast is not supported(I think)
    return flatten(compoundList)


def returnIntersectionOfFlatStructures(listA,listB):
    '''!@brief: intersection of two flat structures (not dict)    
    @return: the list of the common elements
    '''    
    if type(listA) == list or type(listA) == tuple:
        if type(listB) == list or type(listB) == tuple:
            return list(set(listA) & set(listB))
        else:
            if listB in listA:
                return [listB]
            else:
                return []
    else:
        if type(listB) == list or type(listB) == tuple:
            if listA in listB:
                return [listA]
            else:
                return []
        else:
            if listA == listB:
                return [listA]
            else:
                return []
        


#=====================================================================================

def differenceInCompoundStructure(structureBefore,structureAfter):
    '''!@brief: if structs are similar, then return any value diffs
    At each matching level, they must be of the same types. 
    If at a matching level (eg: two dicts), there are different values, 
    then that value and all subsequent values are returned as a diff
    '''    
    diffStructure = None;    
    try:
        if type(structureBefore) == dict:
            diffStructure = {}
            for keyA in structureAfter:                
                if keyA not in structureBefore:
                    diffStructure[keyA] = structureAfter[keyA]
                else:
                    #go recursively in, at each level return only the diffs, or 0 len struct
                    smallerDiff =differenceInCompoundStructure(
                                    structureBefore[keyA],structureAfter[keyA])
                    if smallerDiff != None:
                        if hasattr(smallerDiff,"__len__"): 
                            if len(smallerDiff) >0:
                                diffStructure[keyA] = smallerDiff
                        else:
                            diffStructure[keyA] = smallerDiff                                                                                               
        elif type(structureBefore) == OrderedDict:
            diffStructure = OrderedDict([])
            for keyA in structureBefore:                
                if keyA not in structureAfter:
                    diffStructure[keyA] = structureBefore[keyA]
                else:
                    #go recursively in, at each level return only the diffs, or 0 len struct
                    smallerDiff =differenceInCompoundStructure(
                                structureBefore[keyA],structureAfter[keyA])
                    if smallerDiff != None:
                        if hasattr(smallerDiff,"__len__") and len(smallerDiff) >0:
                            diffStructure[keyA] = smallerDiff
                        else:
                            diffStructure[keyA] = smallerDiff                                                 
        elif type(structureBefore) == list or \
                type(structureBefore) == tuple:
            diffStructure = []
            for element in structureAfter:
                if element not in structureBefore:
                    diffStructure.append(element)
            if type(structureAfter) == tuple:
                diffStructure = tuple(diffStructure)
        else: #it is a primitive type (int or string)
            if structureBefore != structureAfter:
                diffStructure = structureAfter
    except Exception as e:
        print(e)
        pass    
    
    return diffStructure            
#===============================================================================
# 
#===============================================================================
def convertFlattenedAtomListToDict(visitedAtoms, partSeparator = "+"):
    '''
    @param visitedCompleteStates: A list of states. Each state is a list of atoms
    @return : A dict mapping obj -> properties -> SET of values
    '''
    
    returnDict = {}
    for atom in visitedAtoms:
        #split the atom into the object, prop, and value
        [obj,prop,value] = atom.split(partSeparator)
        try:
            if type(value) == list or type(value) ==  tuple:
                for unit in value:
                    returnDict[obj][prop].add(unit)
            else: #it is a single primitive value,
                returnDict[obj][prop].add(value)                    
        except:
            if not obj in returnDict.keys():
                returnDict[obj] = {}
                returnDict[obj][prop] = set()
            elif not prop in returnDict[obj].keys():
                returnDict[obj][prop] = set()
            #now we added the key entries, add the value
            if type(value) == list or type(value) == tuple:
                for unit in value:
                    returnDict[obj][prop].add(unit)
            else: # it is a single primitive value
                returnDict[obj][prop].add(value)
    #---END FOR loop through the atoms in the complete state
    return returnDict


#===============================================================================
# 
#===============================================================================
def convertFlattenedAtomListToDict_ver2(visitedAtoms, partSeparator = "+"):
    '''
    @param visitedCompleteStates: A list of states. Each state is a list of atoms
    @return : A dict mapping obj -> properties -> SET of values
    '''
    
    returnDict = {}
    for atom in visitedAtoms:
        #split the atom into the object, prop, and value
        [obj,prop,value] = atom.split(partSeparator)
        try:
            if type(value) == list or type(value) ==  tuple:
                for unit in value:                    
                    returnDict[obj][prop].append(unit)
                    returnDict[obj][prop] = list(set(returnDict[obj][prop]))
            else: #it is a single primitive value,
                returnDict[obj][prop].append(value)
                returnDict[obj][prop] = list(set(returnDict[obj][prop]))                    
        except:
            if not obj in returnDict.keys():
                returnDict[obj] = {}
                returnDict[obj][prop] = []
            elif not prop in returnDict[obj].keys():
                returnDict[obj][prop] = []
            #now we added the key entries, add the value
            if type(value) == list or type(value) == tuple:
                for unit in value:
                    returnDict[obj][prop].append(unit)
                    returnDict[obj][prop] = list(set(returnDict[obj][prop]))
            else: # it is a single primitive value
                returnDict[obj][prop].append(value)
                returnDict[obj][prop] = list(set(returnDict[obj][prop]))                
    #---END FOR loop through the atoms in the complete state
    return returnDict

#===============================================================================
# 
#===============================================================================
def convertFlattenedAtomListToDict_ver3(visitedAtoms, partSeparator = "+"):
    '''
    @param visitedCompleteStates: A list of states. Each state is a list of atoms
    @return : A dict mapping obj -> properties -> SET of values
    '''
    
    returnDict = {}
    for atom in visitedAtoms:
        #split the atom into the object, prop, and value
        [obj,prop,value] = atom.split(partSeparator)
        try:
            returnDict[obj][prop] = value                                
        except:
            if not obj in returnDict.keys():
                returnDict[obj] = {}                
            returnDict[obj][prop] = value                     
    #---END FOR loop through the atoms in the complete state
    return returnDict

#===============================================================================
# 
#===============================================================================

def convertFlattenedAtomStringListToDictWithListValues(visitedAtoms, partSeparator = "+"):
    '''
    @param visitedCompleteStates: A list of states. Each state is a list of atoms
    @return : A dict mapping obj -> properties -> SET of values
    '''
    
    returnDict = {}
    for atom in visitedAtoms:
        #split the atom into the object, prop, and value
        [obj,prop,value] = atom.split(partSeparator)
        try:
            if type(value) == list or type(value) ==  tuple:
                for unit in value:
                    returnDict[obj][prop].append(unit)
            else: #it is a single primitive value,
                returnDict[obj][prop].append(value)                    
        except:
            if not obj in returnDict.keys():
                returnDict[obj] = {}
                returnDict[obj][prop] = list()
            elif not prop in returnDict[obj].keys():
                returnDict[obj][prop] = list()
            #now we added the key entries, add the value
            if type(value) == list or type(value) == tuple:
                for unit in value:
                    returnDict[obj][prop].append(unit)
            else: # it is a single primitive value
                returnDict[obj][prop].append(value)
    #---END FOR loop through the atoms in the complete state
    return returnDict


#===============================================================================
# 
#===============================================================================

def pickleListOfObjects(pickleFolder, pickleFileName, listOfObjects):
    '''
    @summary: Self explanatory. NOTE: if the folder is a relative path, note that it should be relative to this file
    @todo: Improve this to allow file appends and such
    '''

    if not os.path.exists(pickleFolder):
        os.makedirs(pickleFolder)
    
    if os.path.exists(pickleFileName):
        os.remove(pickleFileName)
    
    with open(pickleFolder+pickleFileName,'wb') as pickleFile:
        for singleObject in listOfObjects:
            pickle.dump(singleObject,pickleFile)
            
#===================================================================
# 
#===================================================================

def getIntersectionOfDicts(sourceDict,compareDict,allowMissing = False, listOfKeysAllowed = []):
    '''
        @summary: compares two dictionaries and returns a dict of only those entries
        which are unchanged. The dictionaries can be arbitrarily deep,
        only the last level of entries are compared. All other preceeding keys
        must be matched.
        @param sourceDict: the entries that could be returned if not in compare dict, or same as compare dict
        @param compareDict: the dict with the entries for the source to compare with
        @param allowMissing: If the compare dict does NOT have a key, it is assumed that it just didn't have the entry, but is the same
        @return: a dict containing those entries from the sourceDict that are in the compareDict   
    '''
    
    returnDict = {}
        
    for sourceKey in sourceDict:
        if listOfKeysAllowed != []:
            if sourceKey not in listOfKeysAllowed:
                continue #onto the next iteration of the for loop
        #---END IF  the list of keys allowed is not empty i.e. allow all
        if sourceKey not in compareDict.keys():
            if allowMissing == True:
                #then we assume that it is unchanged
                returnDict[sourceKey] = sourceDict[sourceKey]
        else:
            #need compare values to return only what is unchanged
            #check if value is a dict
            sourceValue = sourceDict[sourceKey]
            compareValue = compareDict[sourceKey] 
            valueType = type(sourceValue)
            compareType = type(compareDict[sourceKey])  
            typeMismatch = False
            if valueType != compareType:
                typeMismatch = True
                #there is one type of mismatch which can be resolved.
                # if they are both lists, or tuples or sets, then they can all be made sets
                if valueType == tuple or valueType == list or valueType == set:
                    if compareType == tuple or compareType == list or compareType == set:  
                        sourceValue = set(sourceValue)
                        compareValue = set(compareValue)
                        typeMismatch = False # we can handle this. We dont allow duplicates in lists,tuples,sets 
            if typeMismatch:
                # do nothing, unresolvable mismatch
                print ("unexpected type mismatch in the source and compare dict")
                print (sourceValue,compareValue)
                print (sourceDict,compareDict)
            else:                
                if valueType == dict:
                    #!@todo: the allowed keys is only for 1 level. Improve code to get a dict of allowed keys for deeper level matching                    
                    intersectionDict = getIntersectionOfDicts(sourceValue,compareValue,allowMissing)                    
                    returnDict[sourceKey] = intersectionDict                     
                elif (valueType == list or valueType == tuple or valueType == set):
                    #then only return the values that are unchanged
                    returnValue  = (set(sourceValue).intersection(set(compareValue)))
                    if valueType == compareType:
                        if valueType == tuple:
                            returnValue = tuple(returnValue)
                        elif valueType == list:
                            returnValue = list(returnValue)
                        # it is already a set, so no need to handle that case                                            
                    returnDict[sourceKey] = returnValue
                elif sourceValue == compareValue:#is a single value, so only return value if the same
                    returnDict[sourceKey] = sourceValue
        #END ELSE the key is also in the compare dict
    #END FOR loop through the keys in the source dict
    return copy.deepcopy(returnDict)

#===============================================================================
# 
#===============================================================================
def updateAndReturnDict(mainDict,newValuesDict, updateConflicts = True, listsAdd = True, listReplace = False):
    '''
    @summary:  Update the main dict with entries from the source
    '''
    hasConflicts = False
    originalMainDict = copy.deepcopy(mainDict)
    mainDict = copy.deepcopy(mainDict) # this is the copy that is actually modified and returned
    for sourceKey in newValuesDict.keys():
        if sourceKey not in mainDict.keys():
            mainDict[sourceKey] = copy.deepcopy(newValuesDict[sourceKey])
        else:
            mainValue = mainDict[sourceKey]
            sourceValue = newValuesDict[sourceKey]
            if not type(mainValue) == type (sourceValue):
                mainDict = originalMainDict
                hasConflicts = True
                print("ERROR! the data types do not match, cannot update mismatched dicts")
                break#out of the for loop through  the keys
            elif type(mainValue) == list:
                if listsAdd:
                    try:
                        mainDict[sourceKey] = list(set(mainDict[sourceKey]).union(newValuesDict[sourceKey]))
                    except: #this would happen if the list contained dicts which were not hashable
                        mainDict[sourceKey] = mainDict[sourceKey] + newValuesDict[sourceKey]
                else:
                    if listReplace:
                        mainDict[sourceKey] = newValuesDict[sourceKey]
                    else:
                        mainDict[sourceKey] = list(set(mainDict[sourceKey]).intersection(set(newValuesDict[sourceKey])))                    
            elif type(mainValue) == tuple:
                if listsAdd:
                    mainDict[sourceKey] = tuple(set(mainDict[sourceKey]).union(newValuesDict[sourceKey]))
                else:
                    if listReplace:
                        mainDict[sourceKey] = newValuesDict[sourceKey]
                    else:
                        mainDict[sourceKey] = tuple(set(mainDict[sourceKey]).intersection(set(newValuesDict[sourceKey])))
            #end elif type is a tuple
            elif type(mainValue) == set:
                if listsAdd:
                    mainDict[sourceKey] = mainDict[sourceKey].union(newValuesDict[sourceKey])
                else:
                    if listReplace:
                        mainDict[sourceKey] = newValuesDict[sourceKey]
                    else:
                        mainDict[sourceKey] = mainDict[sourceKey].intersection((newValuesDict[sourceKey]))
            #---END elif the type is a set
            elif type(mainValue) == dict:
                #in addition to recursively calling for nested dicts, also update the "has conflicts" variable
                (mainDict[sourceKey],deeperConflicts) = updateAndReturnDict(mainDict[sourceKey] , newValuesDict[sourceKey],updateConflicts,listsAdd )
                hasConflicts = hasConflicts or deeperConflicts
            else: # it is a single primitive type
                if updateConflicts:
                    mainDict[sourceKey] = sourceValue
                else: # do NOT update conflicts, keep as is
                    if mainValue != sourceValue: 
                        hasConflicts = True
            #---END ELSE the value is a single primitive type
        #---END ELSE the key is there in both dicts        
    #---END FOR loop through the keys of the main dict 
    return (mainDict,hasConflicts)
    

#===============================================================================
# 
#===============================================================================

def getDifferenceOfDicts(dictA,dictB,allowMissing = True,allowedKeys = []):
    '''
        A-B, such that lists,sets and tuples have common elements dropped, and only uncommon elements from A
        are kept. 
        Primitive values are preserved from dict A. 
        Missing keys are preserved from dict A
        
        if allowedKeys = [<empty list>], it means all
    '''
    differenceDict = {}   
    allAllowed = (len(allowedKeys) == 0) 
    for dictAKey in dictA.keys():
        if not allAllowed:
            if dictAKey not in allowedKeys:
                continue # this key is not allowed for checking the difference, continue on to the other keys
        try:
            dictAValue = dictA[dictAKey]
            dictBValue = dictB[dictAKey]
            dictAValueType = type(dictAValue)
            dictBValueType = type(dictBValue)
            typeMismatch = False
            if dictAValueType != dictBValueType:
                typeMismatch = True
                #there is one type of mismatch that we can handle
                # if they are both lists, or tuples or sets, then they can all be made sets
                if dictAValueType == tuple or dictAValueType == list or dictAValueType == set:
                    if dictBValueType == tuple or dictBValueType == list or dictBValueType == set:  
                        dictAValue = set(dictAValue)
                        dictBValue = set(dictBValue)
                        typeMismatch = False # we can handle this. We dont allow duplicates in lists,tuples,sets 
                
            if typeMismatch:
                #could not handle type mismatch
                print("Mismatched Values when taking the difference between dicts")
                print(dictAKey,dictAValue,dictBValue)
            else:
                if type(dictAValue) == list:
                    dictAValue = list(dictAValue)#creates a new object and allows removal
                    for bValue in dictBValue:
                        if bValue in dictAValue:
                            dictAValue.remove(bValue)
                elif type(dictAValue) == tuple:
                    dictAValue = list(dictAValue)#creates a new object and allows removal
                    for bValue in dictBValue:
                        if bValue in dictAValue:
                            dictAValue.remove(bValue)
                    dictAValue = tuple(dictAValue)
                elif type(dictAValue) == set:
                    dictAValue = dictAValue.difference(dictBValue)
                elif type(dictAValue) == dict:
                    dictAValue = getDifferenceOfDicts(dictAValue, dictBValue)                    
                else:#primitive (single) values
                    if dictAValue == dictBValue:
                        dictAValue = None
                    #else dictAValue is taken as it is    
                if dictAValue != None:                                        
                    differenceDict[dictAKey] = dictAValue
            #---END else the type of A and B values match        
        except:
            # the entry is not in dictB so it is taken as is for the difference A-B
            if allowMissing:
                differenceDict[dictAKey] = dictA[dictAKey]
    #---END for loop through the keys of dictA
    return differenceDict

#===========================================================================
# 
#===========================================================================

def getDroppedEntriesInDict(fromDict,resultDict,checkSingleValues = False):
    '''
        Go through each key in the main dict, and check if the value in the comparison
        dict is a list, tuple or set. if so, return in a dict, those entries that were dropped 
        (i.e. not in the main , but in the comparison)
    '''
    droppedDict = {}
    for mainKey in fromDict.keys():
        try:
            mainValue = fromDict[mainKey]
            compareValue = resultDict[mainKey]
            if type(mainValue) != type(compareValue):
                print("Error Value types do not match for the key in the two dicts")
                print(mainKey,fromDict,resultDict)
            else:
                if type(mainValue) == list:
                    droppedDict[mainKey] = list(set(mainValue).difference(set(compareValue)))
                elif type(mainValue) == tuple:
                    droppedDict[mainKey] = tuple(set(mainValue).difference(set(compareValue)))
                elif type(mainValue) == set:
                    droppedDict[mainKey] = mainValue.difference(compareValue)                                        
                elif type(mainValue) == dict:
                    droppedDict[mainKey] = getDroppedEntriesInDict(mainValue,compareValue,checkSingleValues)
                else:
                    if checkSingleValues and mainValue != compareValue:
                        droppedDict[mainKey] = mainValue # it was dropped                        
        except:
            pass # do nothing if the key is not in the comparison dict
    return droppedDict

#===========================================================================
# 
#===========================================================================
def getNthLevelLeavesOfDict(sourceDict,depthLevelOfKeys):
    '''
        Recurse through the dictionary for the depth specified. The starting depth is 1
        then return all the keys at the nth level. Duplicates are allowed in the return list
    '''
    returnKeys = [] #can be duplicates
    if depthLevelOfKeys == 1:
        returnKeys = list(sourceDict.keys())
    else:        
        for singleKey in sourceDict.keys():
            if type(sourceDict[singleKey]) == dict:
                returnKeys = returnKeys +  getNthLevelLeavesOfDict(sourceDict[singleKey],depthLevelOfKeys-1)
            elif depthLevelOfKeys == 2:
                if type(sourceDict[singleKey]) == list  or  type(sourceDict[singleKey]) == tuple or\
                            type(sourceDict[singleKey]) == set :
                    returnKeys = returnKeys + list(sourceDict[singleKey])
                else:#it is a primitive/single value
                    returnKeys.append(sourceDict[singleKey])    
    return returnKeys 
#===================================================================
# 
#===================================================================

def getNthLevelValuesOfDict(sourceDict,depthLevelOfKeys):
    '''
        Recurse through the dictionary for the depth specified. The starting depth is 1
        then return all the keys at the nth level. Duplicates are allowed in the return list
    '''
    returnValues = [] #can be duplicates
    if depthLevelOfKeys == 1:
        returnValues = [sourceDict]
    else:        
        for singleKey in sourceDict.keys():
            if type(sourceDict[singleKey]) == dict:
                returnValues = returnValues +  getNthLevelValuesOfDict(sourceDict[singleKey],depthLevelOfKeys-1)
            elif depthLevelOfKeys == 2:
                returnValues.append(sourceDict[singleKey])    
    return returnValues 
#===================================================================
# 
#===================================================================

def filterDict(sourceDict, allowedKeys = []):
    '''
        @summary: Go to the leaf nodes of a possibly recursive dict, and if empty, remove the preceeding key
    '''
    nonEmptyDict = {}
    if allowedKeys == []:
        allowedKeys = sourceDict.keys()    
    for singleKey in allowedKeys:
        try:
            singleValue = sourceDict[singleKey]
            if type(singleValue) == dict:
                singleValue = filterDict(singleValue)
                if len(singleValue) != 0: 
                    nonEmptyDict[singleKey] = singleValue        
            elif type(singleValue) == list or type(singleValue) == tuple or type(singleValue) == set:  
                if len(singleValue) != 0: 
                    nonEmptyDict[singleKey] = singleValue
            elif singleValue != None or singleValue != "": # if single value is a primitive type
                nonEmptyDict[singleKey] = singleValue        
        except:
            pass
#             print("Possible error, tried to access key in dict, but key not present")
#             print(singleKey)
#             print(sourceDict)
    #---END FOR loop through the keys
    return nonEmptyDict        
                
        