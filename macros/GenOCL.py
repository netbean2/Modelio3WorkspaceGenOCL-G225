"""
=========================================================
                       GenOCL.py
 Generate a USE OCL specification from a UML package
=========================================================

FILL THIS SECTION AS SHOWN BELOW AND LINES STARTING WITH ###
@author Marc-Alexandre Blanchard marc.alexandre.blanchard.pro@gmail.com
@author Enis Kulla eniskulla89@gmail.com
@group  G225

Current state of the generator
----------------------------------
FILL THIS SECTION 
Explain which UML constructs are supported, which ones are not.
What is good in your generator?
    - enum generation
    - package generation
    - class generation
    - association generation
    - composition generation
    - associationclass generation
What are the current limitations?
    - isTutoredBy from CyberResidence

Current state of the tests
--------------------------
FILL THIS SECTION 
Explain how did you test this generator.
Which test are working? 
    - CyberResidence
    - Classes
    - Attributes_simple
    - Attributes_enumeration
    - Operations
    - Inheritance_simple
    - Inheritance_multiple
    - association_class
    - Associations_Composition
    - Associations_Aggregation
    - Attributes_visibility - TOCHECK
    - Attributes_cardinality

Which are not?
    - Association_unspecified
    - Association_qualified
    - Association_NARY
    - Notes

To improve
    -association_simple : visibility missing
    -association_ordered : visibility missing

Observations
------------
Additional observations could go there
"""

associationsNames = []

#---------------------------------------------------------
#   Helpers for the python language
#---------------------------------------------------------
def contains(str,list):
    """
        utilities method
        return true if str is in list
    """
    return any(str in s for s in list)

def printWithTab(nbtab,content):
    """
        utilities method
        print content with nbtab before
    """
    res = ""
    for i in range(0,nbtab,1):
        res+='\t'
    print res+content

#---------------------------------------------------------
#   Helpers on the source metamodel (UML metamodel)
#---------------------------------------------------------
# The functions below can be seen as extensions of the
# modelio metamodel. They define useful elements that 
# are missing in the current metamodel but that allow to
# explorer the UML metamodel with ease.
# These functions are independent from the particular 
# problem at hand and could be reused in other 
# transformations taken UML models as input.
#---------------------------------------------------------

def computeMultiplicity(target):
    multiplicity=""
    if target.getMultiplicityMin()==target.getMultiplicityMax():
        multiplicity=target.getMultiplicityMin()
    else:
        multiplicity=target.getMultiplicityMin()+".."+target.getMultiplicityMax()
    if multiplicity=="0..*":
        multiplicity="*"
    return multiplicity

def isAssociationClass(element):
    """ 
    Return True if and only if the element is an association 
    that have an associated class, or if this is a class that
    has a associated association. (see the Modelio metamodel
    for details)
    """
    if isinstance(element,Class):
        return element.getLinkToAssociation()!=None
    return False
    
def isEnum(element):
    try:
        element.getValue()
        return True
    except AttributeError:
        return False

#---------------------------------------------------------
#   Application dependent helpers on the source metamodel
#---------------------------------------------------------
# The functions below are defined on the UML metamodel
# but they are defined in the context of the transformation
# from UML Class diagramm to USE OCL. There are not
# intended to be reusable. 
#--------------------------------------------------------- 

# example UNUSED
def associationsInPackage(package):
    """
    Return the list of all associations that start or
    arrive to a class which is recursively contained in
    a package.
    """
    
#---------------------------------------------------------
#   Helpers for the target representation (text)
#---------------------------------------------------------
# The functions below aims to simplify the production of
# textual languages. They are independent from the 
# problem at hand and could be reused in other 
# transformation generating text as output.
#---------------------------------------------------------
def aggregationToString(ag):
    """
        convert an object Kind of aggregation to string
    """
    if str(ag)=="KindIsAssociation":
        return "association"
    elif str(ag)=="KindIsComposition":
        return "composition"
    elif str(ag)=="KindIsAggregation":
        return "aggregation"
    else:
        return ""

def printAggregationAttributes(target,end):
    """
        print the elements that compose an aggregation
        an aggregation is 'composition' or 'association'
    """
    first = target.getTarget().getName()+"["+computeMultiplicity(target)+"]"+" "+"role"+" "+target.getName()
    second = end.getTarget().getName()+"["+computeMultiplicity(end)+"]"+" "+"role"+" "+end.getName()
    printWithTab(1,first)
    if(first!=second):
        printWithTab(1,second)

def printAttributesForClass(c):
    """
        print attributes for a class
    """
    if(len(c.getOwnedAttribute())!=0):
        printWithTab(1,"attributes")
        for attribute in c.getOwnedAttribute():
            attr = UMLVisibility2OCL(attribute.getVisibility())+" "+attribute.getName() + " : " + umlBasicType2OCL(attribute.getType().getName())
            if(computeMultiplicity(attribute)!="1"):
                attr+=" "+"["+computeMultiplicity(attribute)+"]"
            if(attribute.isIsDerived()) :
                attr+=" -- @derived"
            printWithTab(2,attr)

def printOperationsForClass(c):
    """
        print operations of a class
    """
    if(len(c.getOwnedOperation())!=0):
        printWithTab(1,"operations")
        for operation in c.getOwnedOperation():
            printWithTab(2,operation.getName() + "()" +" : "+"<body to add>")

# for instance a function to indent a multi line string if
# needed, or to wrap long lines after 80 characters, etc.

#---------------------------------------------------------
#           Transformation functions: UML2OCL
#---------------------------------------------------------
# The functions below transform each element of the
# UML metamodel into relevant elements in the OCL language.
# This is the core of the transformation. These functions
# are based on the helpers defined before. They can use
# print statement to produce the output sequentially.
# Another alternative is to produce the output in a
# string and output the result at the end.
#---------------------------------------------------------
def associations2OCL(target,end):
    """
        print association 2 OCL
    """
    
    name = target.getAssociation().getName()
    if contains(name,associationsNames) == False :
        associationsNames.append(name)
        print "\n"
        if(aggregationToString(target.getAggregation())=="association"):
            print aggregationToString(end.getAggregation())+" "+name+" "+"between"
        else:
            print aggregationToString(target.getAggregation())+" "+name+" "+"between"
        if(printAggregationAttributes(target,end)!=None):
            printAggregationAttributes(target,end)
        print "end"

def umlAssociationClass2OCL(c):
    """
        Convert an association class 2 OCL
    """
    print "\n"

    #class name
    className = "associationclass "+c.getName()
    print className
    print "between"
    for i in range(0,len(c.getTargetingEnd()),1):
        printAggregationAttributes(c.getTargetingEnd()[i],c.getOwnedEnd()[i])
    #attributes
    printAttributesForClass(c)
    #operations
    printOperationsForClass(c)
    print "end"

def umlBasicType2OCL(basicType):
    """
    Generate USE OCL basic type. Note that
    type conversions are required.
    """
    if basicType=="float":
        return "Real"
    elif basicType=="string":
        return "String"
    elif basicType=="integer":
        return "Integer"
    elif basicType=="boolean":
        return "Boolean"
    else :
        return basicType

def umlClass2OCL(c):
    """
        Convert a class to OCL
    """

    print "\n"

    #class name
    className = "class "+c.getName()
    
    #inheritance
    if (len(c.getParent())!=0) :
        className+= " < "
        #multiple inheritance
        for i in range(0,len(c.getParent()),1) :
            if(i>0):
                className+=" , "
            className+=c.getParent()[i].getSuperType().getName()
    print className

    #attributes
    printAttributesForClass(c)
    #operations
    printOperationsForClass(c)

    print "end"

    if(len(c.getTargetingEnd())==len(c.getOwnedEnd()) and len(c.getOwnedEnd())>0):
        for i in range(0,len(c.getTargetingEnd()),1):
            associations2OCL(c.getTargetingEnd()[i],c.getOwnedEnd()[i])

def umlEnumeration2OCL(enumeration):
    """
    Generate USE OCL code for the enumeration
    """
    print "\n"
    print "enum "+enumeration.getName()+"{"
    for i in range(0,len(enumeration.getCompositionChildren()),1):
        line = enumeration.getCompositionChildren()[i].getName()
        if(i<len(enumeration.getCompositionChildren())-1):
            line+=","
        printWithTab(1,line)
    print "}"

def package2OCL(package):
    """
    Generate a complete OCL specification for a given package.
    The inner package structure is ignored. That is, all
    elements useful for USE OCL (enumerations, classes, 
    associationClasses, associations and invariants) are looked
    recursively in the given package and output in the OCL
    specification. The possibly nested package structure that
    might exist is not reflected in the USE OCL specification
    as USE is not supporting the concept of package.
    """
    #for each element of the package
    for e in package.getOwnedElement():
        #an inner package
        if isinstance(e,Package):
            print "\n--"+"Package"+e.getName()
            package2OCL(e)
            print "\n--"+"End Package"+e.getName()
        #an association class
        elif isAssociationClass(e):
            umlAssociationClass2OCL(e)
        #an enum
        elif isEnum(e):
            umlEnumeration2OCL(e)
        #a class
        else:
            umlClass2OCL(e)

def UMLVisibility2OCL(visibility):
    if(str(visibility)=="VisibilityUndefined"):
        return ""
    elif(str(visibility)=="Private"):
        return "-"
    elif(str(visibility)=="Protected"):
        return "#"
    elif(str(visibility)=="Public"):
        return "+"
    elif(str(visibility)=="PackageVisibility"):
        return "~"
    else:
        return ""

#Called at launch check parameters then proceed to build
def main():
    #you don't select smthg
    if len(selectedElements)==0:   
        print indent(4)+"Ah no, sorry. You have no selected elements."
    else:
        print 'they are {nb} elements'.format(nb=len(selectedElements))
        for c in selectedElements:
            if isinstance(c,Package):
                package2OCL(c)

#---------------------------------------------------------
#           User interface for the Transformation 
#---------------------------------------------------------
# The code below makes the link between the parameter(s)
# provided by the user or the environment and the 
# transformation functions above.
# It also produces the end result of the transformation.
# For instance the output can be written in a file or
# printed on the console.
#---------------------------------------------------------

# (1) computation of the 'package' parameter
print "--- start translation ---"
main()
print "--- end translation ---"