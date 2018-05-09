#/////////////////  Use this pattern to gererate a GUI to manipulate a struct.

import progSpec
import codeDogParser
from progSpec import cdlog, cdErr


classesToProcess=[]
classesEncoded={}
currentClassName=''
currentModelSpec=None

# Code accmulator strings:
newWidgetFields=''
widgetInitFuncCode=''
widgetFromVarsCode=''
varsFromWidgetCode=''

def getFieldSpec(fldCat, field):
    parameters={}
    if fldCat=='mode': fldCat='enum'
    elif fldCat=='double': fldCat='float'

    if fldCat=='enum':
        parameters=field['typeSpec']['enumList']
    elif fldCat=='RANGE':
        parameters={1, 10}

    typeSpec=field['typeSpec']
    if 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:
        innerFieldType=typeSpec['fieldType']
        datastructID = typeSpec['arraySpec']['datastructID']
        return [datastructID, innerFieldType]
    else:
        if fldCat=='struct':
            fldCat='struct' #field['typeSpec']['fieldType'][0]
        return [fldCat, parameters]

def deCamelCase(identifier):
    outStr=''
    chPos=0
    for ch in identifier:
        if chPos==0: outStr += ch.upper()
        else:
            if ch.isupper() and ch.isalpha():
                outStr += ' '+ch.lower()
            elif ch=='_':
                outStr += ' '
            else: outStr += ch
        chPos+=1
    return outStr

def codeListWidgetManagerClassOverride(classes, listManagerStructName, structTypeName):
    funcTextToUpdateViewWidget      = ''
    funcTextToUpdateEditWidget      = ''
    funcTextToUpdateCrntFromWidget  = ''
    funcTextToPushCrntToListView    = ''
    rowHeaderCode                   = ''
    rowViewCode                     = ''

    # Find the model
    modelRef = progSpec.findSpecOf(classes[0], structTypeName, 'model')
    currentModelSpec = modelRef
    if modelRef==None:
        cdErr('To build a list GUI for list of "'+structTypeName+'" a model is needed but is not found.')

    ### Write code for each field
    for field in modelRef['fields']:
        typeSpec        = field['typeSpec']
        fldCat          = progSpec.fieldsTypeCategory(typeSpec)
        fieldName       = field['fieldName']
        label           = deCamelCase(fieldName)
        CasedFieldName          = fieldName[0].upper() + fieldName[1:]
        widgetName         = CasedFieldName + 'Widget'

        if not ('arraySpec' in typeSpec and typeSpec['arraySpec']!=None):
            if(fldCat!='struct'):
                rowHeaderCode   += '        their GUI_Frame: '+fieldName + '_header <- makeLabelWidget("'+fieldName+'")\n'
                rowHeaderCode   += '        setLabelWidth('+fieldName+'_header, 15)\n'
                rowHeaderCode   += '        addToContainer(headerBox, '+fieldName+'_header)\n'

            if fldCat=='struct':
                funcTextToUpdateViewWidget     += ''
                funcTextToUpdateEditWidget     += '   /- updateWidgetFromVars()\n'
                funcTextToUpdateCrntFromWidget += '   /- updateVarsFromWidget()\n'
            elif fldCat=='enum' or fldCat=='mode':
                funcTextToUpdateViewWidget     += ''
                funcTextToUpdateEditWidget     += ''
                funcTextToUpdateCrntFromWidget += ''#  crntRecord.'+fieldName+' <- dialog.' + widgetName + '.getValue()\n'
            elif fldCat=='bool':
                funcTextToUpdateViewWidget     += ''
                funcTextToUpdateEditWidget     += ''
                funcTextToUpdateCrntFromWidget += '    crntRecord.'+fieldName+' <- dialog.' + widgetName + '.getValue()\n'
            elif fldCat=='string':
                funcTextToUpdateViewWidget     += ''
                funcTextToUpdateEditWidget     += '    dialog.' + widgetName + '.setValue(crntRecord.'+fieldName+')\n'
                funcTextToUpdateCrntFromWidget += '    me string: '+widgetName+'Str <- string(dialog.' + widgetName + '.getValue())\n'
                funcTextToUpdateCrntFromWidget += '    crntRecord.'+fieldName+' <- '+widgetName+'Str\n'
                rowViewCode                    += '        their GUI_Frame: '+fieldName + '_value <- makeLabelWidget(crntRecord.'+fieldName+'.data())\n'
                rowViewCode                    += '        setLabelWidth('+fieldName+'_value, 15)\n'
                rowViewCode                    += '        addToContainer(rowBox, '+fieldName+'_value)\n'
                rowViewCode                    += '        showWidget('+fieldName+'_value)\n'
            elif fldCat=='int':
                funcTextToUpdateViewWidget     += ''
                funcTextToUpdateEditWidget     += '    dialog.' + widgetName + '.setValue(crntRecord.'+fieldName+')\n'
                #funcTextToUpdateCrntFromWidget += '    me string: '+widgetName+'Str <- string(dialog.' + widgetName + '.getValue())\n'
                #funcTextToUpdateCrntFromWidget += '    crntRecord.'+fieldName+' <- dataStr\n'
                rowViewCode                    += '        their GUI_Frame: '+fieldName + '_value <- makeLabelWidget(toString(crntRecord.'+fieldName+').data())\n'
                rowViewCode                    += '        setLabelWidth('+fieldName+'_value, 15)\n'
                rowViewCode                    += '        addToContainer(rowBox, '+fieldName+'_value)\n'
                rowViewCode                    += '        showWidget('+fieldName+'_value)\n'
            else: print"pattern_MakeGUI.codeListWidgetManagerClassOverride fldCat not specified: ", fldCat;  exit(2)

###############
    CODE = 'struct '+listManagerStructName+''': inherits = "ListWidgetManager" {
    our <STRUCTNAME>: crntRecord
    our <STRUCTNAME>[their list]: <STRUCTNAME>_ListData
    me <STRUCTNAME>_Dialog_GUI: dialog
    our listWidget:  listViewWidget

    /- Override all these for each new list editing widget
    their GUI_Frame: makeRowView() <- {
        their GUI_Frame: rowBox <- makeMakeXStackWidget("")
        <ROWVIEWCODE>
        return(rowBox)
    }
    void: insertNewRow(our <STRUCTNAME>: item) <- {
        crntRecord <- item
        their GUI_Frame: row <- makeRowWidget ("")
        their GUI_Frame: rowBox <- makeRowView()
        addToContainer(listViewWidget, row)
        showWidget(row)
        addToContainer(row, rowBox)
        showWidget(rowBox)
    }
    our listWidget: makeListViewWidget() <- {
        listViewWidget <- makeListWidget("")
        setListWidgetSelectionMode (listViewWidget, SINGLE)
        their GUI_Frame: headerRow <- makeRowWidget("")
        their GUI_Frame: headerBox <- makeMakeXStackWidget("")
        <ROWHEADERCODE>
        addToContainer(headerRow, headerBox)
        addToContainer(listViewWidget, headerRow)
        withEach item in <STRUCTNAME>_ListData {
            insertNewRow(item)
        }
        return(listViewWidget)
    }
    void: updateViewableWidget() <- {<funcTextToUpdateViewWidget>}
    their GUI_item: makeEditableWidget() <- {return(dialog.make<STRUCTNAME>Widget(crntRecord))}
    void: updateEditableWidget() <- {<funcTextToUpdateEditWidget>}
    void: updateCrntFromEdited(their GUI_item: Wid) <- {<funcTextToUpdateCrntFromWidget>}
    void: allocateNewCurrentItem() <- {Allocate(crntRecord)}
    void: pushCrntToList() <- {<STRUCTNAME>_ListData.pushLast(crntRecord)}
    void: pushCrntToListView() <- {insertNewRow(crntRecord)}
    void: deleteNthItem(me int: N) <- {}
    void: copyCrntBackToList() <- {}
    void: setCurrentItem(me int: idx) <- {}
    void: setValue(our <STRUCTNAME>[their list]: ListData) <- {<STRUCTNAME>_ListData <- ListData}

    their GUI_item: initWidget(our <STRUCTNAME>[their list]: Data) <- {
        <STRUCTNAME>_ListData <- Data
        return(ListEdBox.init_dialog(self))
    }
}
'''
    CODE = CODE.replace('<STRUCTNAME>', structTypeName)
    CODE = CODE.replace('<funcTextToUpdateViewWidget>', funcTextToUpdateViewWidget)
    CODE = CODE.replace('<funcTextToUpdateEditWidget>', funcTextToUpdateEditWidget)
    CODE = CODE.replace('<funcTextToUpdateCrntFromWidget>', funcTextToUpdateCrntFromWidget)
    CODE = CODE.replace('<funcTextToPushCrntToListView>', funcTextToPushCrntToListView)
    CODE = CODE.replace('<ROWHEADERCODE>', rowHeaderCode)
    CODE = CODE.replace('<ROWVIEWCODE>', rowViewCode)
    codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, listManagerStructName)

def getWidgetHandlingCode(classes, fldCat, fieldName, field, structTypeName, dialogStyle, indent):
    # _Dialog_GUI is editable widget
    global newWidgetFields
    global widgetInitFuncCode
    global widgetFromVarsCode
    global varsFromWidgetCode

    label               = deCamelCase(fieldName)
    [fieldSpec, params] = getFieldSpec(fldCat, field)
    typeName            = fieldSpec+'Widget'
    CasedFieldName      = fieldName[0].upper() + fieldName[1:]
    widgetName          = CasedFieldName + 'Widget'
    fieldType           = field['typeSpec']['fieldType'][0]
    typeSpec            = field['typeSpec']
    widgetBoxName       =  widgetName
    localWidgetVarName  = widgetName

    if fieldSpec=='widget':
        typeName              = CasedFieldName +'Widget'
        widgetName            = fieldName +'Widget'
        widgetBoxName         = fieldName
        localWidgetVarName    = fieldName
        newWidgetFields      += '    their GUI_item' + ': ' + fieldName + '\n'
        makeTypeNameCall      = fieldName + '<- appModel_data.'+fieldName+".init(style)\n"
    elif fieldSpec=='struct':
        typeName              = 'GUI_Frame'
        guiStructName         = structTypeName + '_Dialog_GUI'
        guiMgrName            = fieldType + '_GUI_Mgr'
        if progSpec.typeIsPointer(typeSpec): widgetInitFuncCode += '        Allocate('+currentClassName+'_data.'+fieldName+')\n'
        widgetInitFuncCode   += '        Allocate('+guiMgrName+')\n'
        makeTypeNameCall      = widgetName+' <- '+guiMgrName+'.make'+structTypeName+'Widget('+currentClassName+'_data.'+fieldName+')\n'
        newWidgetFields      += '    our ' + guiStructName + ': '+ guiMgrName+'\n'
        widgetFromVarsCode   += '        '+guiMgrName+ '.setValue(var.'+fieldName+')\n'
        varsFromWidgetCode    = "        " + fieldName + ' <- ' + widgetName + '.getValue()\n'
    elif fieldSpec=='enum':
        typeName = 'enumWidget'
        EnumItems=[]
        for enumItem in params: EnumItems.append('"'+deCamelCase(enumItem)+'"')
        optionString          = '[' + ', '.join(EnumItems) + ']'
        widgetBoxName         =  widgetName +'.box'
        makeTypeNameCall      = widgetBoxName+' <- '+ widgetName+'.makeEnumWidget("'+label+'", '+optionString+')\n'
        widgetFromVarsCode   += "        " + widgetName+ '.setValue(var.'+ fieldName +')\n'
        varsFromWidgetCode    = "        " + fieldName + ' <- ' + widgetName + '.getValue()\n'
    elif fieldSpec=='string':
        widgetBoxName         =  widgetName +'.box'
        makeTypeNameCall      = "Allocate("+widgetName+"); " + widgetBoxName + ' <- '+ widgetName+'.makeStringWidget("'+label+'")\n'
        widgetFromVarsCode   += "        " + widgetName+ '.setValue(var.'+ fieldName +')\n'
        varsFromWidgetCode    = "        " + fieldName + ' <- ' + widgetName + '.getValue()\n'
    elif fieldSpec=='int':
        widgetBoxName         =  widgetName +'.box'
        makeTypeNameCall      =  widgetBoxName + ' <- '+ widgetName+'.makeIntWidget("'+label+'")\n'
        widgetFromVarsCode   += "        " + widgetName+ '.setValue(var.'+ fieldName +')\n'
        varsFromWidgetCode    = "        " + fieldName + ' <- ' + widgetName + '.getValue()\n'
    elif fieldSpec=='list' or fieldSpec=='map': pass
    else: print"pattern_MakeGUI.getWidgetHandlingCode fieldSpec not specified: ", fieldSpec;  exit(2)

    # If this is a list or map, populate it
    if 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:
        makeTypeNameCall      =  widgetName+' <- make'+typeName[0].upper() + typeName[1:]+'("'+label+'")\n'
        innerFieldType        = typeSpec['fieldType']
        fldCatInner           = progSpec.innerTypeCategory(innerFieldType)

        # If it hasn't already been added, make a struct <ItemType>_ListWidgetManager:ListWidgetManager{}
        listManagerStructName = structTypeName+'_ListWidgetManager'
        codeListWidgetManagerClassOverride(classes, listManagerStructName, structTypeName)

        listWidMgrName        = widgetName+'_LEWM'
        newWidgetFields      += '    me '+listManagerStructName+': '+listWidMgrName+'\n'

        widgetListEditorName  = widgetName+'_Editor'
        localWidgetVarName    = widgetListEditorName
        if progSpec.typeIsPointer(typeSpec): widgetInitFuncCode += '        Allocate('+currentClassName+'_data.'+fieldName+')\n'
        widgetInitFuncCode   += '        their GUI_item: '+widgetListEditorName+' <- '+listWidMgrName+'.initWidget('+currentClassName+'_data.'+fieldName+')\n'
        widgetInitFuncCode   += '        addToContainer(box, '+widgetListEditorName+')\n'
        widgetFromVarsCode   += "        " + listWidMgrName + '.setValue(var.'+ fieldName +')\n'
        varsFromWidgetCode    = "        " + listWidMgrName + ' <- ' + widgetName + '.getValue()\n'
    else: # Not an ArraySpec:
        newWidgetFields      += '    our '+typeName+': '+widgetName+'\n'
        widgetInitFuncCode   += '        '+makeTypeNameCall
        widgetInitFuncCode   += '        addToContainer(box, '+widgetBoxName+')\n'
    if dialogStyle == 'Z_stack':
        widgetInitFuncCode+='             '+'gtk_notebook_set_tab_label_text(GTK_NOTEBOOK(box), '+ localWidgetVarName+', "'+label+'")\n'

def BuildGuiForList(classes, className, dialogStyle, newStructName):
    # This makes 4 types of changes to the class:
    #   It adds a widget variable for items in model // newWidgetFields: '    their '+typeName+': '+widgetName
    #   It adds a set Widget from Vars function      // widgetFromVarsCode: Func UpdateWidgetFromVars()
    #   It adds a set Vars from Widget function      // varsFromWidgetCode: Func UpdateVarsFromWidget()
    #   It add an initialize Widgets function.       // widgetInitFuncCode: widgetName+' <- '+makeTypeNameCall+'\n    addToContainer(box, '+widgetName+')\n'

    # dialogStyles: 'Z_stack', 'X_stack', 'Y_stack', 'TabbedStack', 'FlowStack', 'WizardStack', 'Dialog', 'SectionedDialogStack'
    # also, handle non-modal dialogs

    global classesEncoded
    global currentClassName
    global currentModelSpec
    classesEncoded[className]=1
    currentClassName = className

    # reset the string vars that accumulate the code
    global newWidgetFields
    global widgetInitFuncCode
    global widgetFromVarsCode
    global varsFromWidgetCode

    newWidgetFields=''
    widgetInitFuncCode=''
    widgetFromVarsCode=''
    varsFromWidgetCode=''

    # Find the model
    modelRef            = progSpec.findSpecOf(classes[0], className, 'model')
    if modelRef==None: cdErr('To build a GUI for a list of "'+className+'" a model is needed but is not found.')
    currentModelSpec    = modelRef
    rowHeaderCode       = ''
    rowViewCode         = ''
    for field in modelRef['fields']:
        fieldName       = field['fieldName']
        typeSpec        = field['typeSpec']
        fldCat          = progSpec.fieldsTypeCategory(typeSpec)
        fieldType       = progSpec.fieldTypeKeyword(field['typeSpec']['fieldType'])
        [fieldSpec, params] = getFieldSpec(fldCat, field)
        structTypeName  =''
        if fldCat=='struct': # Add a new class to be processed
            structTypeName =typeSpec['fieldType'][0]
            newGUIStyle    = 'Dialog'
            guiStructName  = structTypeName+'_'+newGUIStyle+'_GUI'
            if not(guiStructName in classesEncoded):
                classesEncoded[guiStructName]=1
                classesToProcess.append([structTypeName, 'struct', 'Dialog', guiStructName])

        if 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:# Add a new list to be processed
            structTypeName = typeSpec['fieldType'][0]
            guiStructName  = structTypeName+'_LIST_View'
            if not(guiStructName in classesEncoded):
                classesEncoded[guiStructName]=1
                classesToProcess.append([structTypeName, 'list', 'Dialog', guiStructName])


    CODE =  '''struct <NEWSTRUCTNAME>{
    our <CLASSNAME>[their list]: <CLASSNAME>_ListData
    our <CLASSNAME>:   crntRecord
}
'''

    CODE = CODE.replace('<NEWSTRUCTNAME>', newStructName)
    CODE = CODE.replace('<CLASSNAME>', className)
    CODE = CODE.replace('<NEWWIDGETFIELDS>', newWidgetFields)
    CODE = CODE.replace('<WIDGETFROMVARSCODE>', widgetFromVarsCode)
    CODE = CODE.replace('<VARSFROMWIDGETCODE>', varsFromWidgetCode)
    #print '==========================================================\n'+CODE
    codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, newStructName)

def BuildGuiForStruct(classes, className, dialogStyle, newStructName):
    # This makes 4 types of changes to the class:
    #   It adds a widget variable for items in model // newWidgetFields: '    their '+typeName+': '+widgetName
    #   It adds a set Widget from Vars function      // widgetFromVarsCode: Func UpdateWidgetFromVars()
    #   It adds a set Vars from Widget function      // varsFromWidgetCode: Func UpdateVarsFromWidget()
    #   It add an initialize Widgets function.       // widgetInitFuncCode: widgetName+' <- '+makeTypeNameCall+'\n    addToContainer(box, '+widgetName+')\n'

    # dialogStyles: 'Z_stack', 'X_stack', 'Y_stack', 'TabbedStack', 'FlowStack', 'WizardStack', 'Dialog', 'SectionedDialogStack', 'V_viewable'
    # also, handle non-modal dialogs

    global classesEncoded
    global currentClassName
    global currentModelSpec
    classesEncoded[className]=1
    currentClassName = className

    # reset the string vars that accumulate the code
    global newWidgetFields
    global widgetInitFuncCode
    global widgetFromVarsCode
    global varsFromWidgetCode

    newWidgetFields=''
    widgetInitFuncCode=''
    widgetFromVarsCode=''
    varsFromWidgetCode=''

    # Find the model
    modelRef         = progSpec.findSpecOf(classes[0], className, 'model')
    currentModelSpec = modelRef
    if modelRef==None: cdErr('To build a GUI for class "'+className+'" a model is needed but is not found.')
    #TODO: write func body for: widgetFromVarsCode(selected item & click edit) & varsFromWidgetCode(ckick OK from editMode)
    ### Write code for each field
    for field in modelRef['fields']:
        typeSpec     = field['typeSpec']
        fldCat       = progSpec.fieldsTypeCategory(typeSpec)
        fieldName    = field['fieldName']
        labelText    = deCamelCase(fieldName)
        if fieldName=='settings':
            # add settings
            continue

        structTypeName=''
        if fldCat=='struct': # Add a new class to be processed
            structTypeName =typeSpec['fieldType'][0]
            if (progSpec.doesClassDirectlyImlementThisField(classes, structTypeName, structTypeName+':managedWidget')
                    or structTypeName.endswith('Widget')):
                fldCat = 'widget'
            else:
                newGUIStyle    = 'Dialog'
                guiStructName  = structTypeName+'_'+newGUIStyle+'_GUI'
                if not(guiStructName in classesEncoded):
                    classesEncoded[guiStructName]=1
                    classesToProcess.append([structTypeName, 'struct', 'Dialog', guiStructName])

        if fldCat != 'widget' and 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:# Add a new list to be processed
            structTypeName = typeSpec['fieldType'][0]
            guiStructName  = structTypeName+'_LIST_View'
            if not(guiStructName in classesEncoded):
                classesEncoded[guiStructName]=1
                classesToProcess.append([structTypeName, 'list', 'Dialog', guiStructName])

        #TODO: make actions for each function
        if fldCat=='func': continue

        getWidgetHandlingCode(classes, fldCat, fieldName, field, structTypeName, dialogStyle, '')

    # Parse everything
    initFuncName = 'make'+className[0].upper() + className[1:]+'Widget'
    if dialogStyle == 'Z_stack': containerWidget='makeStoryBoardWidget("makeStoryBoardWidget")'
    else: containerWidget='makeFrameWidget()'

    CODE =  '''
struct <CLASSNAME> {}
struct <NEWSTRUCTNAME> {
    <NEWWIDGETFIELDS>
    their <CLASSNAME>: <CLASSNAME>_data
    their GUI_Frame: <INITFUNCNAME>(their <CLASSNAME>: Data) <- {
        <CLASSNAME>_data<-Data
        their GUI_Frame:box <- <CONTAINERWIDGET>
        <WIDGETINITFUNCCODE>
        return(box)
    }
    void: setValue(their <CLASSNAME>: var) <- {
        <WIDGETFROMVARSCODE>
    }
    void: getValue() <- {
        /-  <VARSFROMWIDGETCODE>
    }
}\n'''  # TODO: add <VARSFROMWIDGETCODE>

    CODE = CODE.replace('<NEWSTRUCTNAME>', newStructName)
    CODE = CODE.replace('<NEWWIDGETFIELDS>', newWidgetFields)
    CODE = CODE.replace('<CLASSNAME>', className)
    CODE = CODE.replace('<WIDGETINITFUNCCODE>', widgetInitFuncCode)
    CODE = CODE.replace('<INITFUNCNAME>', initFuncName)
    CODE = CODE.replace('<WIDGETFROMVARSCODE>', widgetFromVarsCode)
    CODE = CODE.replace('<VARSFROMWIDGETCODE>', varsFromWidgetCode)
    CODE = CODE.replace('<CONTAINERWIDGET>', containerWidget)
    #print '==========================================================\n'+CODE
    codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, newStructName)

def apply(classes, tags, topClassName):
    print "APPLY: in Apply\n"
    global classesToProcess
    global classesEncoded
    classesEncoded={}

    # Choose an appropriate app style
    appStype='default'
    if (True): # if all data fields are classes
        appStype='Z_stack'
    guiStructName = topClassName+'_GUI'
    classesEncoded[guiStructName]=1
    classesToProcess=[[topClassName, 'struct', appStype, guiStructName]]

    # Amend items to each GUI data class
    for classToAmend in classesToProcess:
        [className, widgetType, dialogStyle, newStructName] = classToAmend
        cdlog(2, "BUILDING "+dialogStyle+" GUI for "+widgetType+" " + className + ' ('+newStructName+')')
        if widgetType == 'struct':
            BuildGuiForStruct(classes, className, dialogStyle, newStructName)
        elif widgetType == 'list':
            BuildGuiForList(classes, className, dialogStyle, newStructName)

    # Fill createAppArea()
    primaryGUIName = 'primary_GUI_Mgr'
    primaryMakerFuncName = 'make'+topClassName[0].upper() + topClassName[1:]+'Widget'

    CODE ='''
struct APP{
    their <TOPCLASSNAME>: primary
    our <GUI_STRUCTNAME>: <PRIMARY_GUI>
    me void: createAppArea(me GUI_Frame: frame) <- {
        me string:s
        Allocate(primary)
        Allocate(primary.dashboard)
        Allocate(<PRIMARY_GUI>)
        their GUI_storyBoard: appStoryBoard <- <PRIMARY_GUI>.<PRIMARY_MAKERFUNCNAME>(primary)
        initializeAppGui()
        gui.addToContainerAndExpand (frame, appStoryBoard)
    }
}'''

    CODE = CODE.replace('<PRIMARY_GUI>', primaryGUIName)
    CODE = CODE.replace('<TOPCLASSNAME>', topClassName)
    CODE = CODE.replace('<GUI_STRUCTNAME>', guiStructName)
    CODE = CODE.replace('<PRIMARY_MAKERFUNCNAME>', primaryMakerFuncName)
    codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE, 'APP')

    return
