from sys import settrace
from typing import Literal
from GEEUtils.runtime import json,os
from Utils.general_utils import *
from xml.dom.minidom import Document
import time

# def test(request):
#     curSearchRequest=SearchRequest.objects.get(uuid='492fdd01-a6b6-4fa6-aca2-25a1235a35e9')
    
#     # geojsonData=curSearchRequest.boundary
#     # print(getBoundary(geojsonData))
#     return HttpResponse("Success")

def generateGetCapabilitiesResponse(requestType,content):
    doc = Document() 
    docStr=""

    if requestType=='WCS':   
        DOCUMENT = doc.createElement('wcs:Capabilities')
        namespace={'xmlns:wcs':"http://www.opengis.new/wcs/1.1.1",
        "xmlns:xlink":"http://www.w3.org/1999/xlink",
        "xmlns:ogc":"http://www.opengis.net/ogc",
        "xmlns:ows":"http://www.opengis.net/ows/1.1",
        "xmlns:gml":"http://www.opengis.net/gml",
        "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation":"http://www.opengis.net/wcs/1.1.1"}
        setAttributes(DOCUMENT,namespace)
        ###### add  attributes ..........
        doc.appendChild(DOCUMENT)
        serviceIdentification=doc.createElement('ows:ServiceIdentification')
        serviceProvider=doc.createElement('ows:ServiceProvider')
        operationsMetadata=doc.createElement('ows:OperationsMetadata')
        contents=doc.createElement('ows:Contents')
        setElements(DOCUMENT,[serviceIdentification,serviceProvider,operationsMetadata,contents])

        #service identification
        title=setText(doc.createElement('ows:Title'),content['serviceIdentification']["title"])
        keywords=setTexts(doc.createElement("ows:Keywords"),'ows:Keyword',['WCS','WS4GEE']) ##!!!@!!
        serviceType=setText(doc.createElement('ows:ServiceType'),content['serviceIdentification']["serviceType"])
        serviceTypeVersion=setText(doc.createElement('ows:ServiceTypeVersion'),content['serviceIdentification']["serviceTypeVersion"])
        fees=setText(doc.createElement('ows:Fees'),'NONE')
        accessConstraints=setText(doc.createElement('ows:AccessConstraints'),'NONE')
        setElements(serviceIdentification,[title,keywords,serviceType,serviceTypeVersion,fees,accessConstraints])

        #service provider
        provideName=setText(doc.createElement('ows:providerName'),content["serviceProvider"]["providerName"])
        provideSite=setText(doc.createElement('ows:providerName'),content["serviceProvider"]["providerSite"])
        setElements(serviceProvider,[provideName,provideSite])

        #metadata
        groups_operationsMetadata=[]
        for operationName in content["operationsMetadata"]["operationName"]:
            DCP=doc.createElement('ows:DCP')
            HTTPGet=setAttributes(doc.createElement("ows:Get"),{"xlink:href":content["operationsMetadata"]["url"]})
            HTTPPost=setAttributes(doc.createElement("ows:Post"),{"xlink:href":content["operationsMetadata"]["url"]})
            HTTP1=setElements(doc.createElement("ows:HTTP"),[HTTPGet])
            HTTP2=setElements(doc.createElement("ows:HTTP"),[HTTPPost])
            DCP1=setElements(DCP,[HTTP1])
            DCP2=setElements(DCP,[HTTP2])
            curTemplate=setAttributes(doc.createElement('ows:Operation'),{"name":operationName})
            setElements(curTemplate,[DCP1,DCP2])
            groups_operationsMetadata.append(curTemplate)
        setElements(operationsMetadata,groups_operationsMetadata)

        #content
        groups_content=[]
        for coverageSummary in content["Contents"]:
            curCoverageSummary=doc.createElement('ows:CoverageSummary')
            title=setText(doc.createElement('ows:Title'),coverageSummary['title'])
            abstract=setText(doc.createElement('ows:Abstract'),coverageSummary['abstract'])
            keywords=setTexts(doc.createElement("ows:Keywords"),'ows:Keyword',coverageSummary['keywords'])
            lowerCorner=setText(doc.createElement('ows:LowerCorner'),str(coverageSummary['extent'][0])+' '+str(coverageSummary['extent'][1]))
            upperCorner=setText(doc.createElement('ows:UpperCorner'),str(coverageSummary['extent'][2])+' '+str(coverageSummary['extent'][3]))
            WGS84BoundingBox=setElements(doc.createElement('ows:WGS84BoundingBox'),[lowerCorner,upperCorner])
            identifier=setText(doc.createElement('ows:Identifier'),coverageSummary['identifier'])
            setElements(curCoverageSummary,[title,abstract,keywords,WGS84BoundingBox,identifier])
            # print(curCoverageSummary)
            groups_content.append(curCoverageSummary)
        setElements(contents,groups_content)
        
        docStr=getXMLStrfromMinidom(doc)

    elif requestType=='WPS':
        DOCUMENT = doc.createElement('wps:Capabilities')
        namespace={'xmlns:wcs':"http://www.opengis.new/wcs/1.1.1",
        "xmlns:xlink":"http://www.w3.org/1999/xlink",
        "xmlns:wps":"http://www.opengis.net/wps/1.0.0",
        "xmlns:ows":"http://www.opengis.net/ows/1.1",
        "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
        "service":"WPS",
        "version":"1.0.0",
        "xml:lang":"en-US",
        "xsi:schemaLocation":"http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd",
        "updateSequence":"1"}
        setAttributes(DOCUMENT,namespace)
        ###### add  attributes ..........
        doc.appendChild(DOCUMENT)
        serviceIdentification=doc.createElement('ows:ServiceIdentification')
        serviceProvider=doc.createElement('ows:ServiceProvider')
        operationsMetadata=doc.createElement('ows:OperationsMetadata')
        processOfferings=doc.createElement('ows:ProcessOfferings')
        setElements(DOCUMENT,[serviceIdentification,serviceProvider,operationsMetadata,processOfferings])

        #service identification
        title=setText(doc.createElement('ows:Title'),content['serviceIdentification']["title"])
        keywords=setTexts(doc.createElement("ows:Keywords"),'ows:Keyword',['WPS','WS4GEE']) ##!!!@!!
        serviceType=setText(doc.createElement('ows:ServiceType'),content['serviceIdentification']["serviceType"])
        serviceTypeVersion=setText(doc.createElement('ows:ServiceTypeVersion'),content['serviceIdentification']["serviceTypeVersion"])
        fees=setText(doc.createElement('ows:Fees'),'NONE')
        accessConstraints=setText(doc.createElement('ows:AccessConstraints'),'NONE')
        setElements(serviceIdentification,[title,keywords,serviceType,serviceTypeVersion,fees,accessConstraints])

        #service provider
        provideName=setText(doc.createElement('ows:providerName'),content["serviceProvider"]["providerName"])
        provideSite=setText(doc.createElement('ows:providerName'),content["serviceProvider"]["providerSite"])
        setElements(serviceProvider,[provideName,provideSite])

        
        #metadata
        groups_operationsMetadata=[]
        for operationName in content["operationsMetadata"]["operationName"]:
            DCP=doc.createElement('ows:DCP')
            HTTPGet=setAttributes(doc.createElement("ows:Get"),{"xlink:href":content["operationsMetadata"]["url"]})
            HTTPPost=setAttributes(doc.createElement("ows:Post"),{"xlink:href":content["operationsMetadata"]["url"]+"?"})
            HTTP=setElements(doc.createElement("ows:HTTP"),[HTTPGet,HTTPPost])
            setElements(DCP,[HTTP])
            curTemplate=setAttributes(doc.createElement('ows:Operation'),{"name":operationName})
            setElements(curTemplate,[DCP])
            groups_operationsMetadata.append(curTemplate)
        setElements(operationsMetadata,groups_operationsMetadata)

        #process offerings
        groups_processes=[]
        for process in  content["processes"]:
            curIdentifier=setText(doc.createElement('ows:Identifier'),process["identifier"])
            curTitle=setText(doc.createElement('ows:Title'),process["title"])
            curProcess=setElements(doc.createElement('wps:Process'),[curTitle,curIdentifier])
            setAttributes(curProcess,{"wps:processVersion":"1"})
            groups_processes.append(curProcess)
        setElements(processOfferings,groups_processes)

        docStr=getXMLStrfromMinidom(doc)

    return docStr

def generateDescribeCoverageResponse(content):
    doc = Document() 
    DOCUMENT = doc.createElement('wcs:CoverageDescriptions')
    docStr=""
    namespace={'xmlns:wcs':"http://www.opengis.new/wcs/1.1.1",
        "xmlns:xlink":"http://www.w3.org/1999/xlink",
        "xmlns:ogc":"http://www.opengis.net/ogc",
        "xmlns:ows":"http://www.opengis.net/ows/1.1",
        "xmlns:gml":"http://www.opengis.net/gml",
        "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation":"http://www.opengis.net/wcs/1.1.1"}
    setAttributes(DOCUMENT,namespace)
    ###### add  attributes ..........
    doc.appendChild(DOCUMENT)
    title=setText(doc.createElement('ows:Title'),content['title'])
    abstract=setText(doc.createElement('ows:Abstract'),content['abstract'])
    keywords=setTexts(doc.createElement("ows:Keywords"),'ows:Keyword',content['keywords'])
    identifier=setText(doc.createElement('ows:Identifier'),content['identifier'])
    domain=doc.createElement("wcs:Domain")
    range=doc.createElement("wcs:Range")
    supportedCRS=setText(doc.createElement('ows:SupportedCRS'),'urn:ogc:def:crs:EPSG::4326')
    supportFormat=setText(doc.createElement('ows:SupportedFormat'),'image/tiff')

    # setup domain
    spatialDomain=doc.createElement("wcs:SpatialDomain")
    lowerCorner=setText(doc.createElement('ows:LowerCorner'),str(content['extent'][0])+' '+str(content['extent'][1]))
    upperCorner=setText(doc.createElement('ows:UpperCorner'),str(content['extent'][2])+' '+str(content['extent'][3]))
    boundingbox=setElements(doc.createElement('ows:Boundingbox'),[lowerCorner,upperCorner])
    setAttributes(boundingbox,{"crs":"urn:ogc:def:crs:OGC:1.3:CRS84","dimensions":"2"})
    setElements(spatialDomain,[boundingbox])
    setElements(domain,[spatialDomain])

    # setup range
    rField=doc.createElement("wcs:Field")
    rIdentifier=setText(doc.createElement("wcs:Identifier"),"content")
   
    rMinimumValue=setText(doc.createElement("ows:MinimumValue"),content["minimumValue"])
    rMaximumValue=setText(doc.createElement("ows:MaximumValue"),content["maximumValue"])
    rRange=setElements(doc.createElement("ows:Range"),[rMinimumValue,rMaximumValue])
    rAllowedValues=setElements(doc.createElement("ows:AllowedValues"),[rRange])
    rDefination=setElements(doc.createElement("wcs:Defination"),[rAllowedValues])

    rDefault=setText(doc.createElement("wcs:Default"),"nearest neighbor")
    rInterpolationMethods=setTexts(doc.createElement("wcs:InterpolationMethods"),"wcs:InterpolationMethod",["nearest","linear","cubic"])
    rInterpolationMethods.appendChild(rDefault)
    rAxis=setAttributes(doc.createElement("wcs:Axis"),{"identifier":"Bands"})
    rAvailableKeys=setTexts(doc.createElement("wcs:AvailableKeys"),"wcs:Key",content["availableBands"])
    rAxis.appendChild(rAvailableKeys)
    setElements(rField,[rIdentifier,rDefination,rInterpolationMethods,rAxis])
    setElements(range,[rField])


    coverageDescription=setElements(doc.createElement('ows:CoverageDescription'),[title,abstract,keywords,identifier,domain,range,supportedCRS,supportFormat])
    setElements(DOCUMENT,[coverageDescription])
    docStr=getXMLStrfromMinidom(doc)

    return docStr

def generateDescribeProcessResponse(content):
    ## two generation methods for literal and complex data 
    def generateLiteralElement(paramDict):
        doc = Document()
        root=None
        if (paramDict["paramType"]=='input'):
            root=setAttributes(doc.createElement("Input"),{"minOccurs":str(paramDict["minOccurs"]),"maxOccurs":str(paramDict["maxOccurs"])})
        elif (paramDict["paramType"]=='output'):
            root=doc.createElement("Output")
        group_elements=[]
        identifier=setText(doc.createElement("ows:Identifier"),paramDict["identifier"])
        title=setText(doc.createElement("ows:Title"),paramDict["title"])
        group_elements.extend([identifier,title])
        if ("abstract" in paramDict.keys()):
            group_elements.append(setText(doc.createElement("ows:Abstract"),paramDict["abstract"]))

        literalData=doc.createElement("LiteralData")
        dataType=setAttributes(doc.createElement("ows:DataType"),{"ows:reference":"xs:"+paramDict["dataType"]})
        literalData.appendChild(dataType)
        if ("anyValue" in paramDict.keys()):
            anyValue=doc.createElement("ows:AnyValue")
            literalData.appendChild(anyValue)
        elif ("defaultValue" in paramDict.keys()):
            defaultValue=setText(doc.createElement("ows:DefaultValue"),paramDict["defaultValue"])
            literalData.appendChild(defaultValue)
        elif ("allowedValues" in paramDict.keys()):
            allowedValues=setTexts(doc.createElement("ows:AllowedValues"),"ows:Value",paramDict["allowedValues"])
            literalData.appendChild(allowedValues)

        group_elements.append(literalData)
        root=setElements(root,group_elements)
        return root

    def generateComplexElement(paramDict):    # Text, Vector or Raster (accept shp.zip/tiff)
        doc = Document()
        root=None
        if (paramDict["paramType"]=='input'):
            root=setAttributes(doc.createElement("Input"),{"minOccurs":str(paramDict["minOccurs"]),"maxOccurs":str(paramDict["maxOccurs"])})
        elif (paramDict["paramType"]=='output'):
            root=doc.createElement("Output")
        group_elements=[]
        identifier=setText(doc.createElement("ows:Identifier"),paramDict["identifier"])
        title=setText(doc.createElement("ows:Title"),paramDict["title"])
        group_elements.extend([identifier,title])
        complexData=doc.createElement("ComplexData")
        if ("abstract" in paramDict.keys()):
            group_elements.append(setText(doc.createElement("ows:Abstract"),paramDict["abstract"]))
        if (paramDict["dataType"]=='Text'):
            mimeType=setText(doc.createElement("MimeType"),"text/plain")
            format=setElements(doc.createElement("Format"),[mimeType])
            mimeType2=setText(doc.createElement("MimeType"),"text/plain")
            format2=setElements(doc.createElement("Format"),[mimeType2])
            default=setElements(doc.createElement("Default"),[format])
            supported=setElements(doc.createElement("Supported"),[format2])
            setElements(complexData,[default,supported])
        elif (paramDict['dataType']=='Vector'):
            mimeType=setText(doc.createElement("MimeType"),"text/plain")
            format=setElements(doc.createElement("Format"),[mimeType])
            mimeType2=setText(doc.createElement("MimeType"),"text/plain")
            format2=setElements(doc.createElement("Format"),[mimeType2])
            mimeType3=setText(doc.createElement("MimeType"),"application/x-zipped-shp")
            format3=setElements(doc.createElement("Format"),[mimeType3])
            default=setElements(doc.createElement("Default"),[format])
            supported=setElements(doc.createElement("Supported"),[format2,format3])
            setElements(complexData,[default,supported])
        elif (paramDict['dataType']=='Raster'):
            mimeType=setText(doc.createElement("MimeType"),"image/tiff")
            format=setElements(doc.createElement("Format"),[mimeType])
            mimeType2=setText(doc.createElement("MimeType"),"image/tiff")
            format2=setElements(doc.createElement("Format"),[mimeType2])
            default=setElements(doc.createElement("Default"),[format])
            supported=setElements(doc.createElement("Supported"),[format2])
            setElements(complexData,[default,supported])
        group_elements.append(complexData)
        return setElements(root,group_elements)

    doc = Document() 
    DOCUMENT = doc.createElement('wps:ProcessDescriptions')
    docStr=""
    namespace={"xmlns:wps":"http://www.opengis.net/wps/1.0.0",
        "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation":"http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd",     
        "service":"WPS",
        "version":"1.0.0",
        "xml:lang":"en-US",
        "updateSequence":"1"}
    setAttributes(DOCUMENT,namespace)
    ###### add  attributes .......... 
    doc.appendChild(DOCUMENT)
    for process in content:
        group_elements=[]
        processDescription=setAttributes(doc.createElement("ProcessDescription"),{"xmlns:ows":"http://www.opengis.net/ows/1.1","xmlns:xlink":"http://www.w3.org/1999/xlink","statusSupported":"true", "storeSupported":"true","wps:processVersion":"1.0.0"})
        identifier=setText(doc.createElement("ows:Identifier"),process["identifier"])
        title=setText(doc.createElement("ows:Title"),process["title"])
        group_elements.extend([identifier,title])
        if ("abstract" in process.keys()):
            group_elements.append(setText(doc.createElement("ows:Abstract"),process['abstract']))
        
        dataInputs=doc.createElement("DataInputs")
        processOutputs=doc.createElement("ProcessOutputs")
        group_elements.extend([dataInputs,processOutputs])

        # DataInputs and ProcessOutputs
        for param in process["params"]:
            if param["dataType"] in ['Text','Vector','Raster']:
                if param["paramType"]=='input':
                    dataInputs.appendChild(generateComplexElement(param))
                else:
                    processOutputs.appendChild(generateComplexElement(param))
            else:
                if param["paramType"]=='input':
                    dataInputs.appendChild(generateLiteralElement(param))
                else:
                    processOutputs.appendChild(generateLiteralElement(param))
        
        setElements(processDescription,group_elements)
        DOCUMENT.appendChild(processDescription)            

    docStr=getXMLStrfromMinidom(doc)
    return docStr

def generateGetCoverageResponse(content):
    doc = Document() 
    DOCUMENT = doc.createElement('wcs:Coverages')
    docStr=""
    namespace={'xmlns:wcs':"http://www.opengis.new/wcs/1.1.1",
        "xmlns:xlink":"http://www.w3.org/1999/xlink",
        "xmlns:ogc":"http://www.opengis.net/ogc",
        "xmlns:ows":"http://www.opengis.net/ows/1.1",
        "xmlns:gml":"http://www.opengis.net/gml",
        "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation":"http://www.opengis.net/wcs/1.1.1 http://schemas.opengis.net/wcs/1.1.1/wcsAll.xsd",
    }
    setAttributes(DOCUMENT,namespace)
    doc.appendChild(DOCUMENT)

    title=setText(doc.createElement('ows:Title'),content['title'])
    abstract=setText(doc.createElement('ows:Abstract'),content['abstract'])
    identifier=setText(doc.createElement('ows:Identifier'),content['identifier'])
    reference=setAttributes(doc.createElement('ows:Reference'),{"xlink:href":content['resultUrl']})
    coverage=setElements(doc.createElement("wcs:Coverage"),[title,abstract,identifier,reference])
    setElements(DOCUMENT,[coverage])
    docStr=getXMLStrfromMinidom(doc)
    return docStr

def generateExecuteResponse(content):
    doc = Document() 
    docStr=""
    DOCUMENT = doc.createElement('wps:ExecuteResponse')
    namespace={"xmlns:wps":"http://www.opengis.net/wps/1.0.0",
        "xmlns:xlink":"http://www.w3.org/1999/xlink",
        "xmlns:ows":"http://www.opengis.net/ows/1.1",
        "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation":"http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd",
        "serviceInstance":"http://127.0.0.1:8000/ws4gee/wps?request=GetCapabilities&service=WPS",
        "service":"WPS",
        "version":"1.0.0",
        "xml:lang":"en-US",
        "statusLocation":"http://127.0.0.1:8000/ws4gee/wps/RetrieveResults?id="+content["statusUuid"]
        }
    setAttributes(DOCUMENT,namespace)
        ###### add  attributes ..........
    doc.appendChild(DOCUMENT)
    identifier=setText(doc.createElement("ows:Identifer"),content["identifier"])
    title=setText(doc.createElement("ows:Title"),content["title"])
    processStatus=setText(doc.createElement("wps:ProcessAccepted"),"Process Accept")
    wpsProcess=setElements(doc.createElement("wps:Process"),[identifier,title])
    wpsStatus=setElements(doc.createElement("wps:Status"),[processStatus])
    setAttributes(wpsStatus,{"creationTime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
    setElements(DOCUMENT,[wpsProcess,wpsStatus])

    docStr=getXMLStrfromMinidom(doc)
    return docStr

def generateExecuteStatus(content):
    doc = Document() 
    docStr=""
    DOCUMENT = doc.createElement('wps:ExecuteResponse')
    namespace={"xmlns:wps":"http://www.opengis.net/wps/1.0.0",
        "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:ows":"http://www.opengis.net/ows/1.1",   
        "xsi:schemaLocation":"http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd",
        "serviceInstance":"http://127.0.0.1:8000/ws4gee/wps?request=GetCapabilities&service=WPS",
        "service":"WPS",
        "version":"1.0.0",
        "xml:lang":"en-US",
        "statusLocation":"http://127.0.0.1:8000/ws4gee/wps/RetrieveResults?id="+content["statusUuid"]
        }
    setAttributes(DOCUMENT,namespace)
        ###### add  attributes ..........
    doc.appendChild(DOCUMENT)
    identifier=setText(doc.createElement("ows:Identifer"),content["identifier"])
    title=setText(doc.createElement("ows:Title"),content["title"])
    statusLabel=""
    
    if content["status"]=="READY" or content["status"]=="RUNNING" or content["status"]=="COMPLETED IN THE CLOUD" or content["status"]=="DOWNLOADING":
        statusLabel="wps:ProcessStarted"
    elif content["status"]=="DOWNLOADED":
        statusLabel="wps:ProcessSucceeded"
    processStatus=setText(doc.createElement(statusLabel),content["status"])
    wpsProcess=setElements(doc.createElement("wps:Process"),[identifier,title])
    wpsStatus=setElements(doc.createElement("wps:Status"),[processStatus])
    setAttributes(wpsStatus,{"creationTime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
    group_elements=[wpsProcess,wpsStatus]

    if ("resultUrl" in content.keys()):
        outputIdentifier=setText(doc.createElement("ows:Identifer"),'result')
        outputTitle=setText(doc.createElement("ows:Title"),'result')
        wpsReference=setAttributes(doc.createElement("wps:Reference"),{"mimeType":content["mimeType"],"href":content["resultUrl"]})
        wpsOutput=setElements(doc.createElement("wps:Output"),[outputIdentifier,outputTitle,wpsReference])
        wpsProcessOutputs=setElements(doc.createElement("wps:ProcessOutputs"),[wpsOutput])
        group_elements.append(wpsProcessOutputs)

    setElements(DOCUMENT,group_elements)
    docStr=getXMLStrfromMinidom(doc)
    return docStr

def generate_service_description(method,content,type='WCS'):
    if method=='DescribeCoverage':
        return generateDescribeCoverageResponse(content)
    if method=='GetCapabilities':
        return generateGetCapabilitiesResponse(type,content)
    if method=='DescribeProcess':
        return generateDescribeProcessResponse(content)
    return

def generate_service_outcome(method,content):
    docStr=""
    if method=='GetCoverage':
        return generateGetCoverageResponse(content)
    elif method=='Execute':
        return generateExecuteResponse(content)
    elif method=='ExecuteStatus':
        return generateExecuteStatus(content)
    return docStr
