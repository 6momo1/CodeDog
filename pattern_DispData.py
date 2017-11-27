#/////////////////  Use this pattern to write to_string() or drawData() to display each member of the model for a struct.

import progSpec
import codeDogParser
from progSpec import cdlog, cdErr

import pattern_GenSymbols

classesToProcess=[]
classesEncoded={}

class structProcessor:

    def addGlobalCode(self, classes):
        pass

    def resetVars(self, modelRef):
        pass

    def processField(self, fieldName, field, fldCat):
        pass

    def addOrAmendClasses(self, classes, className, modelRef):
        pass

    def processStruct(self, classes, className):
        global classesEncoded
        classesEncoded[className]=1
        self.currentClassName = className
        modelRef = progSpec.findSpecOf(classes[0], className, 'model')
        self.resetVars(modelRef)
        self.currentModelSpec = modelRef
        if modelRef==None:
            cdErr('To write a processing function for class "'+className+'" a model is needed but is not found.')
        ### Write code for each field
        for field in modelRef['fields']:
            fldCat=progSpec.fieldsTypeCategory(field['typeSpec'])
            fieldName=field['fieldName']
            self.processField(fieldName, field, fldCat)
        self.addOrAmendClasses(classes, className, modelRef)

#---------------------------------------------------------------  WRITE: .asGUI()
# This makes 4 types of changes:
   # It adds a widget variable for items in the model
   # It adds a set Widget from Vars function
   # It adds a set Vars from Widget function
   # It add an initialize Widgets function.
class GUI_FromStructWriter(structProcessor):

    asProteusGlobalsWritten=False

    def addGlobalCode(self, classes):
        if structAsProteusWriter.asProteusGlobalsWritten: return
        else: structAsProteusWriter.asProteusGlobalsWritten=True
        CODE='''
struct GLOBAL{

}
    '''
        codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, 'Global items for asGUI()')

    def resetVars(self, modelRef):
        print 'CLASS: ' + self.currentClassName
        global classesToProcess
        self.topLevelStruct = (classesToProcess[0]==self.currentClassName)
        self.hasDraw = False
        self.currentClassCode = ''
        if(self.topLevelStruct and progSpec.isStruct(modelRef)):
            self.storyBoardApp=True
            #self.currentClassCode += '    their GUI_storyBoard: appStoryBoard <- gtk_stack_new()\n'   # If storyboard, add the stack view
        if progSpec.isStruct(modelRef):
            self.widgetFromVarsCode = '    void: updateWidgetFromVars() <- {\n'     # Func header for UpdateWidgetFromVars()
            self.varsFromWidgetCode = '    void: updateVarsFromWidget() <- {\n'     # Func header for UpdateVarsFromWidget()
        self.newWidgetFields = ''                                                   # For built-in widgets like intWidget, listWidget, etc.


    def getFieldSpec(self, fldCat, field):
        params={}
        if fldCat=='mode': fldCat='enum'
        elif fldCat=='double': fldCat='float'

        if fldCat=='enum': parameters={'mon', 'tue', 'wed', 'thur', 'fri', 'sat', 'sun'}
        elif fldCat=='RANGE': pareameters={1, 10}

        typeSpec=field['typeSpec']
        if 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:
            innerFieldType=typeSpec['fieldType']
            datastructID = typeSpec['arraySpec']['datastructID']
            return [datastructID, innerFieldType]
        else:
            if fldCat=='struct':
                fldCat='struct' #field['typeSpec']['fieldType'][0]
            return [fldCat, params]



    def processField(self, fieldName, field, fldCat):
        global classesEncoded
        print "    :"+fieldName
        if fieldName=='settings':
            # add settings
            return
        structTypeName=''
        if fldCat=='struct': # Add a new class to be processed
            structTypeName=field['typeSpec']['fieldType'][0]
            if not(structTypeName in classesEncoded):
                #print "TO ENCODE:", structTypeName
                classesEncoded[structTypeName]=1
                classesToProcess.append(structTypeName)

        S=""
        if fldCat=='func': return ''

        fieldSpec = self.getFieldSpec(fldCat, field)
        fldSpec = fieldSpec[0]
        typeName = fldSpec+'Widget'
        if fldSpec=='struct': makeTypeNameCall = fieldName+'.make'+structTypeName+'Widget(s)'
        else: makeTypeNameCall = 'make'+typeName[0].upper() + typeName[1:]+'()'
        widgetFieldName = fieldName[0].upper() + fieldName[1:] + 'Widget'

        if fldSpec=='struct': typeName = 'GUI_Frame'

        typeSpec=field['typeSpec']
        self.newWidgetFields += '    their '+typeName+': '+widgetFieldName+'\n'
        if progSpec.typeIsPointer(typeSpec): self.currentClassCode += '    Allocate('+fieldName+')\n'
        self.currentClassCode += '    '+widgetFieldName+' <- '+makeTypeNameCall+'\n'

        '''if 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:
            innerFieldType=typeSpec['fieldType']
            print "ARRAYSPEC:",innerFieldType, field
            fldCatInner=progSpec.innerTypeCategory(innerFieldType)
            calcdName=fieldName #+'["+toString(_item_key)+"]'
       #     self.currentClassCode +="    withEach _item in "+fieldName+":{\n"
       #     self.makeCodeToInitField(calcdName, '_item', field, fldCatInner)
       #     self.currentClassCode +="    }\n"
        else:
            self.makeCodeToInitField(fieldName, field, fldCat, structTypeName)
'''
        if progSpec.typeIsPointer(typeSpec):
            T ="    if("+fieldName+' == NULL){print('+'indent, dispFieldAsText("'+fieldName+'", 15)+"NULL\\n")}\n'
            T+="    else{\n    "+S+"    }\n"
            S=T
        return S


    def addOrAmendClasses(self, classes, className, modelRef):
        if self.topLevelStruct:  # Top Level class
            print "TOP-LEVEL:", self.currentClassName
            declAPP_fields = '  their '+self.currentClassName+': primary\n'
            declAPP_fields+='''
                me void: createAppArea(me GUI_frame: frame) <- {
                    me string:s
                    Allocate(primary)
                    their GUI_storyBoard: appStoryBoard <- primary.makeAppModelWidget(s)
                    gui.addToContainer (frame, appStoryBoard)
                }
'''
            CODE = progSpec.wrapFieldListInObjectDef('APP', declAPP_fields)
            codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, 'APP')

        #print "MAKE CLASS:" + className
        initFuncName = 'make'+className[0].upper() + className[1:]+'Widget'
        self.currentClassCode = '\n  their GUI_item: '+initFuncName+'(me string: S) <- {\n    me string:s\n' + self.currentClassCode + '\n  }\n'
        self.widgetFromVarsCode += '\n    }\n'
        self.varsFromWidgetCode += '\n    }\n'
        functionsCode = self.newWidgetFields + self.currentClassCode + self.widgetFromVarsCode + self.varsFromWidgetCode
        CODE = 'struct '+className+" {\n" + functionsCode + '\n}\n'         # Add the new fields to the STRUCT being processed
        codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, className)
      #  print '==========================================================\n'+CODE

#---------------------------------------------------------------  WRITE: .asProteus()
class structAsProteusWriter(structProcessor):

    asProteusGlobalsWritten=False

    def addGlobalCode(self, classes):
        if structAsProteusWriter.asProteusGlobalsWritten: return
        else: structAsProteusWriter.asProteusGlobalsWritten=True
        CODE='''
struct GLOBAL{
    me string: dispFieldAsText(me string: label, me int:labelLen) <- {
        me string: S <- ""
        me int: labelSize<-label.size()
        withEach count in RANGE(0..labelLen):{
            if (count<labelSize){S <- S+label[count]}
            else if(count==labelSize){ S <- S+":"}
            else {S <- S+" "}
        }
        return(S)
    }
}
    '''
        codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, 'Global function used by asProteus()')

    def resetVars(self, modelRef):
        self.textFuncBody=''

    def toProteusTextFieldAction(self, label, fieldName, field, fldCat):
        global classesToProcess
        global classesEncoded
        valStr=''
        if(fldCat=='int' or fldCat=='double'):
            valStr='toString('+fieldName+')'
        elif(fldCat=='string' or fldCat=='char'):
            valStr= "'"+fieldName+"'"
        elif(fldCat=='flag' or fldCat=='bool'):
            valStr='dispBool(('+fieldName+')!=0)'
        elif(fldCat=='mode'):
            valStr='toString('+fieldName+')'  #fieldName+'Strings['+fieldName+'] '
        elif(fldCat=='struct'):
            valStr=fieldName+'.to_string(indent+"|   ")\n'

            structTypeName=field['typeSpec']['fieldType'][0]
            if not(structTypeName in classesEncoded):
                #print "TO ENDODE:", structTypeName
                classesEncoded[structTypeName]=1
                classesToProcess.append(structTypeName)
        if(fldCat=='struct'):
            S="    "+'print(indent, dispFieldAsText("'+label+'", 15), "\\n")\n    '+valStr+'\n    print("\\n")\n'
        else:
            S="    "+'print(indent, dispFieldAsText("'+label+'", 15), '+valStr+', "\\n")\n'
        return S

    def processField(self, fieldName, field, fldCat):
        S=""
        if fldCat=='func': return ''
        typeSpec=field['typeSpec']
        if 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:
            innerFieldType=typeSpec['fieldType']
            #print "ARRAYSPEC:",innerFieldType, field
            fldCatInner=progSpec.innerTypeCategory(innerFieldType)
            calcdName=fieldName+'["+toString(_item_key)+"]'
            S+="    withEach _item in "+fieldName+":{\n"
            S+="        "+self.toProteusTextFieldAction(calcdName, '_item', field, fldCatInner)+"    }\n"
        else: S+=self.toProteusTextFieldAction(fieldName, fieldName, field, fldCat)
        if progSpec.typeIsPointer(typeSpec):
            T ="    if("+fieldName+' == NULL){print('+'indent, dispFieldAsText("'+fieldName+'", 15)+"NULL\\n")}\n'
            T+="    else{\n    "+S+"    }\n"
            S=T
        return S

    def addOrAmendClasses(self, classes, className, modelRef):
        self.textFuncBody = '    me string: S <- S + "{\\n"\n' + self.textFuncBody + '    S <- S + "\\n"\n'
        Code="me void: asProteus(me string:indent) <- {\n"+self.textFuncBody+"    }\n"
        Code=progSpec.wrapFieldListInObjectDef(className, Code)
        codeDogParser.AddToObjectFromText(classes[0], classes[1], Code, className+'.asProteus()')

#---------------------------------------------------------------  WRITE: .toString()

class structToStringWriter(structProcessor):

    toStringGlobalsWritten=False

    def addGlobalCode(self, classes):
        if structToStringWriter.toStringGlobalsWritten: return
        else: structToStringWriter.toStringGlobalsWritten=True
        CODE='''
struct GLOBAL{
    me string: dispFieldAsText(me string: label, me int:labelLen) <- {
        me string: S <- ""
        me int: labelSize<-label.size()
        withEach count in RANGE(0..labelLen):{
            if (count<labelSize){S <- S+label[count]}
            else if(count==labelSize){ S <- S+":"}
            else {S <- S+" "}
        }
        return(S)
    }
}
    '''
        codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, 'Global function used by toString()')

    def resetVars(self, modelRef):
        self.textFuncBody=''

    def displayTextFieldAction(self, label, fieldName, field, fldCat):
        global classesToProcess
        global classesEncoded
        valStr=''
        if(fldCat=='int' or fldCat=='double'):
            valStr='toString('+fieldName+')'
        elif(fldCat=='string' or fldCat=='char'):
            valStr= "'"+fieldName+"'"
        elif(fldCat=='flag' or fldCat=='bool'):
            valStr='dispBool(('+fieldName+')!=0)'
        elif(fldCat=='mode'):
            valStr='toString('+fieldName+')'  #fieldName+'Strings['+fieldName+'] '
        elif(fldCat=='struct'):
            valStr=fieldName+'.to_string(indent+"|   ")\n'

            structTypeName=field['typeSpec']['fieldType'][0]
            if not(structTypeName in classesEncoded):
                #print "TO ENDODE:", structTypeName
                classesEncoded[structTypeName]=1
                classesToProcess.append(structTypeName)
        if(fldCat=='struct'):
            S="    "+'print(indent, dispFieldAsText("'+label+'", 15), "\\n")\n    '+valStr+'\n    print("\\n")\n'
        else:
            S="    "+'print(indent, dispFieldAsText("'+label+'", 15), '+valStr+', "\\n")\n'
        return S

    def processField(self, fieldName, field, fldCat):
        S=""
        if fldCat=='func': return ''
        typeSpec=field['typeSpec']
        if 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:
            innerFieldType=typeSpec['fieldType']
            #print "ARRAYSPEC:",innerFieldType, field
            fldCatInner=progSpec.innerTypeCategory(innerFieldType)
            calcdName=fieldName+'["+toString(_item_key)+"]'
            S+="    withEach _item in "+fieldName+":{\n"
            S+="        "+self.displayTextFieldAction(calcdName, '_item', field, fldCatInner)+"    }\n"
        else: S+=self.displayTextFieldAction(fieldName, fieldName, field, fldCat)
        if progSpec.typeIsPointer(typeSpec):
            T ="    if("+fieldName+' == NULL){print('+'indent, dispFieldAsText("'+fieldName+'", 15)+"NULL\\n")}\n'
            T+="    else{\n    "+S+"    }\n"
            S=T
        return S

    def addOrAmendClasses(self, classes, className, modelRef):
        Code="me void: to_string(me string:indent) <- {\n"+self.textFuncBody+"    }\n"
        Code=progSpec.wrapFieldListInObjectDef(className, Code)
        codeDogParser.AddToObjectFromText(classes[0], classes[1], Code, className+'.toString()')

#---------------------------------------------------------------  WRITE CODE TO DRAW STRUCTS

class structDrawingWriter(structProcessor):

    structDrawGlobalsWritten=False

    def addGlobalCode(self, classes):
        if structDrawingWriter.structDrawGlobalsWritten: return
        else: structDrawingWriter.structDrawGlobalsWritten=True
        CODE='''
struct GLOBAL{
    const int: fontSize <- 10

    me bool: isNull(me string: value) <- {
        if(value=="0" or value=="''" or value=="Size:0" or value=="NULL" or value=="false"){return(true)}
        else{return(false)}
    }
}
    '''
        codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, 'Global functions to draw structs')

    def resetVars(self, modelRef):
        [self.structTextAcc, self.updateFuncTextAcc, self.drawFuncTextAcc, self.setPosFuncTextAcc, self.handleClicksFuncTextAcc, self.handleClicksFuncTxtAcc2] = ['', '', '', '', '', '']
        self.updateFuncTextPart2Acc=''; self.drawFuncTextPart2Acc=''

    def processField(self, fieldName, field, fldCat):
        [structText, updateFuncText, drawFuncText, setPosFuncText, handleClicksFuncText] = self.getDashDeclAndUpdateCode(
            'me', '"'+fieldName+'"', fieldName, fieldName, field, 'skipNone', '    ')
        self.structTextAcc     += structText
        self.updateFuncTextAcc += updateFuncText
        self.drawFuncTextAcc   += drawFuncText
        self.setPosFuncTextAcc += setPosFuncText
        self.handleClicksFuncTextAcc += handleClicksFuncText

    def addOrAmendClasses(self, classes, className, modelRef):
        self.setPosFuncTextAcc += '\n        y <- y+5'+'\n        height <- y-posY'+'\n        me int:depX <- posX+width+40\n'
        countOfRefs=0
        for field in modelRef['fields']:
            typeSpec=field['typeSpec']
            fldCat=progSpec.fieldsTypeCategory(typeSpec)
            if fldCat=='func': continue
            if progSpec.typeIsPointer(typeSpec):  # Draw dereferenced POINTER
                fieldName=field['fieldName']
                declSymbolStr='    '
                if(countOfRefs==0):declSymbolStr+='me string: '
                countOfRefs+=1
                [structText, updateFuncText, drawFuncText, setPosFuncText, handleClicksFuncText] = self.getDashDeclAndUpdateCode(
                    'our', '"'+fieldName+'"', fieldName, fieldName, field, 'skipPtr', '    ')
                self.structTextAcc += structText
                tempFuncText = updateFuncText
                updateFuncText = declSymbolStr+'mySymbol <- data.'+fieldName+'.mySymbol(data.'+fieldName+')\n'
                updateFuncText += (  '    if(data.'+fieldName+' != NULL){\n'+
                                    '        if(!dashBoard.dependentIsRegistered(mySymbol)){'
                                    '\n            Allocate('+fieldName+')\n'+
                                    tempFuncText+
                                    '\n            dashBoard.addDependent(mySymbol, '+fieldName+')'+
                                    '\n        }\n    } else {'+fieldName+' <- NULL}\n')
                self.updateFuncTextPart2Acc += updateFuncText
                self.setPosFuncTextAcc      += '''
    if(<fieldName> != NULL and !<fieldName>Ptr.refHidden){
        <fieldName>.setPos(depX, extC, extC)
        extC <- <fieldName>.extY + 40
        extX <- max(extX, <fieldName>.extX)
        extY <- max(extY, <fieldName>.extY)
        me int: fromX<fieldName> <- <fieldName>Ptr.posX+135
        me int: fromY<fieldName> <- <fieldName>Ptr.posY+12
        me int: smallToX<fieldName> <- <fieldName>.posX
        me int: largeToX<fieldName> <- <fieldName>.posX + <fieldName>.width
        me int: smallToY<fieldName> <- <fieldName>.posY
        me int: largeToY<fieldName> <- <fieldName>.posY + <fieldName>.height
        our arrow:: Arrow(fromX<fieldName>, fromY<fieldName>, intersectPoint(fromX<fieldName>, smallToX<fieldName>, largeToX<fieldName>), intersectPoint(fromY<fieldName>, smallToY<fieldName>, largeToY<fieldName>))
        dashBoard.decorations.pushLast(Arrow)
    }
'''.replace('<fieldName>', fieldName)
                self.handleClicksFuncTxtAcc2+= '    if('+fieldName+' != NULL and !'+fieldName+'Ptr.refHidden){\n'+fieldName+'.isHidden<-false\n    }\n'

        Code='''
struct display_'''+className+": inherits = 'dash' "+'''{
    me dataField: header
    me mode[headerOnly, fullDisplay, noZeros]: displayMode
    their '''+className+''': data
'''+self.structTextAcc+'''

    void: update(me string: _label, me string: textValue, their '''+className+''': _Data) <- {
        data <- _Data
        header.update(90, 150, _label, textValue, false)
        displayMode<-headerOnly
'''+self.updateFuncTextAcc+'''

'''+self.updateFuncTextPart2Acc+'''
    }

    void: setPos(me int:x, me int:y, me int: extCursor) <- {
        posX <- x;
        posY <- y;
        extC <- extCursor
        isHidden<-false
        header.setPos(x,y,extC)
        y <- y+header.height
        width <- header.width
        height <- y-posY
        extX <- header.extX
        extY <- max(y, extC)
        if(displayMode!=headerOnly){
            x <- x+10    /- Indent fields in a struct
'''+self.setPosFuncTextAcc+'''
            width <- width+10
        }
    }


    me bool: primaryClick(their GUI_ButtonEvent: event) <- {
        if(isHidden){return(false)}
        me GUI_scalar: eventX <- event.x
        me GUI_scalar: eventY <- event.y
        if( header.isTouchingMe(eventX, eventY)){
            if(displayMode==headerOnly){displayMode <- noZeros}
            else if(displayMode==noZeros){displayMode <- fullDisplay}
            else if(displayMode==fullDisplay){displayMode <- headerOnly}
        } else {
'''+self.handleClicksFuncTextAcc+'''
        }

'''+self.handleClicksFuncTxtAcc2+'''

        return(true)
    }

    void: draw(me GUI_ctxt: cr) <- {
        header.isHidden <- false
        header.draw(cr)
        if(displayMode!=headerOnly){
'''+self.drawFuncTextAcc+'''
            cr.rectangle(posX, posY, width, height)
            cr.strokeNow()
'''+self.drawFuncTextPart2Acc+'''
        }
    }
}\n'''
        codeDogParser.AddToObjectFromText(classes[0], classes[1], Code, 'display_'+className)

    def getDashDeclAndUpdateCode(self, owner, fieldLabel, fieldRef, fieldName, field, skipFlags, indent):
        global classesToProcess
        global classesEncoded
        [structText, updateFuncText, setPosFuncText, drawFuncText, handleClicksFuncText]=['', '', '', '', '']
        typeSpec=field['typeSpec']
        fldCat=progSpec.fieldsTypeCategory(typeSpec)
        if fldCat=='func': return ['', '', '', '', '']
        if progSpec.typeIsPointer(typeSpec) and skipFlags != 'skipPtr':  # Header for a POINTER
            fieldName+='Ptr'
            innerUpdateFuncStr = 'data.'+fieldRef+'.mySymbol(data.'+fieldRef+')'
            updateFuncText+="        "+fieldName+'.update('+fieldLabel+', '+innerUpdateFuncStr+', isNull('+innerUpdateFuncStr+'))\n'
            structText += "    "+owner+" ptrToItem: "+fieldName+"\n"

        elif 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None and skipFlags != 'skipLists': # Header and items for LIST
            innerUpdateFuncStr = '"Size:"+toString(data.'+fieldName+'.size())'
            updateFuncText="        "+fieldName+'.update('+fieldLabel+', '+innerUpdateFuncStr+', isNull('+innerUpdateFuncStr+'))\n'
             ## Now push each item
            innerFieldType=typeSpec['fieldType']
            #print "ARRAYSPEC:",innerFieldType, field
            fldCatInner=progSpec.innerTypeCategory(innerFieldType)
            newFieldRef=fieldName+'[_item_key]'
            newFieldLabel='"'+fieldName+'["+toString(_item_key)+"]"'
            updateFuncText+="\n        withEach _item in data."+fieldName+":{\n"
            [innerStructText, innerUpdateFuncText, innerDrawFuncText, innerSetPosFuncText, innerHandleClicksFuncText] = self.getDashDeclAndUpdateCode('our', newFieldLabel, newFieldRef, 'newItem', field, 'skipLists', '    ')
            updateFuncText+=innerStructText+'\n        Allocate(newItem)\n'+innerUpdateFuncText
            updateFuncText+="\n        "+fieldName+'.updatePush(newItem)'
            updateFuncText+='\n        }\n'
            structText += "    "+owner+" listOfItems: "+fieldName+"\n"
        elif(fldCat=='struct'):  # Header for a STRUCT
            updateFuncText="        "+fieldName+'.update('+fieldLabel+', ">", data.'+fieldRef+')\n'
            structTypeName=field['typeSpec']['fieldType'][0]
            structText += "    "+owner+" display_"+structTypeName+': '+fieldName+"\n"


            # Add new classname to a list so it can be encoded.
            if not(structTypeName in classesEncoded):
                classesEncoded[structTypeName]=1
                classesToProcess.append(structTypeName)

        else:   # Display field for a BASIC TYPES
            valStr=''
            if(fldCat=='int' or fldCat=='double'):
                valStr='toString(data.'+fieldName+')'
            elif(fldCat=='string' or fldCat=='char'):
                valStr= '"\'"+'+'data.'+fieldName+'+"\'"'
            elif(fldCat=='flag' or fldCat=='bool'):
                valStr='dispBool((data.'+fieldName+')!=0)'
            elif(fldCat=='mode'):
                valStr= fieldRef+'Strings[data.'+fieldName+'] '

            updateFuncText="        "+fieldName+'.update(90, 150, '+fieldLabel+', '+valStr+', isNull('+valStr+'))\n'
            structText += "    "+owner+" dataField: "+fieldName+"\n"

        drawFuncText  ="        "+fieldName+'.draw(cr)\n'
        setPosFuncText += '''        if(!<fieldName>.isNullLike or displayMode==fullDisplay){
                <fieldName>.setPos(x,y,extC)
                extC <- <fieldName>.extC
                y <- y + <fieldName>.height
                extX <- max(extX, <fieldName>.extX)
                extY <- max(extY, <fieldName>.extY)
                width<- max(width, <fieldName>.width)
                <fieldName>.isHidden<-false
            } else {<fieldName>.isHidden<-true}
    '''.replace('<fieldName>', fieldName)
      #  updateFuncText+='        if(crntWidth<'+fieldName+'.width){crntWidth <- '+fieldName+'.width}'
        handleClicksFuncText = '            '+fieldName+'.primaryClick(event)'
        return [structText, updateFuncText, drawFuncText, setPosFuncText, handleClicksFuncText]

#---------------------------------------------------------------------  MAIN APPLY CODE

def apply(classes, tags, className, dispMode):
    if dispMode[:4]=='TAG_':
        dispModeTagName=dispMode[4:]
        dispMode=progSpec.fetchTagValue(tags, dispModeTagName)
    if(dispMode!='none' and dispMode!='text' and dispMode!='draw' and dispMode!='Proteus' and dispMode!='toGUI'):
        cdErr('Invalid parameter for display mode in Code Data Display pattern: '+str(dispMode))
    if dispMode=='none': return

    global classesToProcess
    classesToProcess=[className]
    global classesEncoded
    classesEncoded={}

    if(dispMode=='Proteus'):   processor = structAsProteusWriter()
    elif(dispMode=='text'):    processor = structToStringWriter()
    elif(dispMode=='draw'):    processor = structDrawingWriter()
    elif(dispMode=='toGUI'):   processor = GUI_FromStructWriter()
    processor.addGlobalCode(classes)

    for classToEncode in classesToProcess:
        cdlog(2, "ENCODING "+dispMode+": "+ classToEncode)
        pattern_GenSymbols.apply(classes, {}, [classToEncode])      # Invoke the GenSymbols pattern
        processor.processStruct(classes, classToEncode)
    return
