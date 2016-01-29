# CodeDog Program Maker

import progSpec
import codeDogParser

import pattern_Write_Main
import pattern_Gen_ParsePrint
import pattern_Gen_EventHandler
import pattern_BigNums
#import pattern_Gen_GUI

import stringStructs

import CodeGenerator_CPP
#import CodeGenerator_JavaScript
#import CodeGenerator_ObjectiveC
#import CodeGenerator_Java

import re
import os
import sys
import errno
import platform

def writeFile(path, fileName, outStr):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST: raise

    fo=open(path + os.sep + fileName, 'w')
    fo.write(outStr)
    fo.close()

def stringFromFile(filename):
    f=open(filename)
    Str = f.read()
    f.close()
    return Str

def processIncludedFiles(fileString):
    pattern = re.compile(r'#include +([\w -\.\/\\]+)')
    return pattern.sub(replaceFileName, fileString)

def replaceFileName(fileMatch):
    includedStr = stringFromFile(fileMatch.group(1))
    includedStr = processIncludedFiles(includedStr)
    return includedStr


def ScanAndApplyPatterns(objects, tags):
    print "    Applying Patterns..."
    for item in objects[1]:
        if item[0]=='!':
            pattName=item[1:]
            patternArgs=objects[0][pattName]['parameters']
            print "        PATTERN:", pattName, ':', patternArgs

            if pattName=='Write_Main': pattern_Write_Main.apply(objects, tags, patternArgs[0])
            elif pattName=='Gen_EventHandler': pattern_Gen_EventHandler.apply(objects, tags, patternArgs[0])
            #elif pattName=='writeParser': pattern_Gen_ParsePrint.apply(objects, tags, patternArgs[0], patternArgs[1])
            elif pattName=='useBigNums': pattern_BigNums.apply(tags)

def AutoGenerateStructsFromModels(objects, tags):
    #TODO: Convert ranges and deduce field types if possible.
    print "    Generating Auto-structs..."
    for objName in objects[1]:
        if objName[0]!='!':
            autoFlag = 'autoGen' in objects[0][objName]
            stateType=objects[0][objName]['stateType']
            if(autoFlag and stateType=='struct'):
                thisModel=progSpec.findModelOf(objects, objName)
                newFields=[]
                for F in thisModel['fields']:
                    #print 'FIELD:', F
                    newFields.append(F)
                objects[0][objName]['fields'] = newFields


def GroomTags(tags):
    # Set tag defaults as needed
    if not ('featuresNeeded' in tags[0]):
        tags[0]['featuresNeeded']={}

    # TODO: default to localhost for Platform, and CPU, etc. Add more combinations as needed.
    if not ('Platform' in tags[0]):
        platformID=platform.system()
        if platformID=='Darwin': platformID="OSX_Devices"
        tags[0]['Platform']=platformID
    if not ('Language' in tags[0]):
        tags[0]['Language']="CPP"

    # Find any needed features based on types used
    for typeName in progSpec.storeOfBaseTypesUsed:
        if(typeName=='BigNum' or typeName=='BigFrac'):
            print 'NOTE: Need Large Numbers'
            progSpec.setFeatureNeeded(tags, 'largeNumbers', progSpec.storeOfBaseTypesUsed[typeName])


def GenerateProgram(objects, buildSpec, tags, libsToUse):
    result='No Language Generator Found for '+tags['langToGen']
    langGenTag = tags['langToGen']
    if(langGenTag == 'CPP'):
        print '        Generating C++ Program...'
        result=CodeGenerator_CPP.generate(objects, [tags, buildSpec[1]], libsToUse)
    else:
        print "ERROR: No language generator found for ", langGenTag
    return result

def ChooseLibs(objects, buildSpec, tags):
    print "\n\n######################   C H O O S I N G   L I B R A R I E S"
    # TODO: Why is fetchTagValue called with tags, not [tags]?
    libList = progSpec.fetchTagValue([tags], 'libraries')
    Platform= progSpec.fetchTagValue([tags, buildSpec[1]], 'Platform')
    Language= progSpec.fetchTagValue([tags, buildSpec[1]], 'Language')
    CPU     = progSpec.fetchTagValue([tags, buildSpec[1]], 'CPU')

    compatibleLibs=[]
    for lib in libList:
        libPlatforms=progSpec.fetchTagValue([tags], 'libraries."+lib+".platforms')
        libBindings =progSpec.fetchTagValue([tags], 'libraries."+lib+".bindings')
        libCPUs     =progSpec.fetchTagValue([tags], 'libraries."+lib+".CPUs')
        libFeatures =progSpec.fetchTagValue([tags], 'libraries."+lib+".features')

       # if (libPlatforms[?]==Platform and libBindings[?]==Language and libCPUs[?]==CPU):
       #     compatibleLibs.append([lib, libFeatures])

    libsToUse=[]
#   for need in featuresNeeded:
#       if():

    return libsToUse

def GenerateSystem(objects, buildSpecs, tags):
    print "\n\n######################   G E N E R A T I N G   S Y S T E M"
    ScanAndApplyPatterns(objects, tags)
    stringStructs.CreateStructsForStringModels(objects, tags)
    AutoGenerateStructsFromModels(objects, tags)
    GroomTags([tags, buildSpecs])
    for buildSpec in buildSpecs:
        buildName=buildSpec[0]
        print "    Generating code for build", buildName
        libsToUse=ChooseLibs(objects, buildSpec, tags)
        outStr = GenerateProgram(objects, buildSpec, tags, libsToUse)
        writeFile(buildName, tagStore['FileName'], outStr)
        #GenerateBuildSystem()
    # GenerateTests()
    # GenerateDocuments()
    return outStr


#############################################    L o a d / P a r s e   P r o g r a m   S p e c

if(len(sys.argv) < 2):
    print "No Filename given.\n"
    exit(1)

file_name = sys.argv[1]
codeDogStr = stringFromFile(file_name)
codeDogStr = processIncludedFiles(codeDogStr)


# objectSpecs is like: [ProgSpec, objNames]
print "######################   P A R S I N G   S Y S T E M  (", file_name, ")"
[tagStore, buildSpecs, objectSpecs] = codeDogParser.parseCodeDogString(codeDogStr)
tagStore['dogFilename']=file_name

outputScript = GenerateSystem(objectSpecs, buildSpecs, tagStore)
print "\n\n######################   D O N E"
