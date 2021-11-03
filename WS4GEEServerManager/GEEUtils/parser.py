from GEEUtils.runtime import ee,json,os
from GEEUtils import gee_utils
from xml.dom.minidom import Document,parseString
from Utils.general_utils import getXMLStrfromMinidom

def getServiceName(xmlDoc,serviceType):
    return

def retrieve_attr(rawData,method):
    dom = parseString(rawData) 
    root = dom.documentElement
    rootName=root.nodeName
    if method=="GetCoverage":
        if (rootName!="GetCoverage"):
            return "{'error':'Please check the XML document'}"
        identifier=root.getElementsByTagName('ows:Identifier')[0].firstChild.data
        lowerCorner=root.getElementsByTagName('ows:LowerCorner')[0].firstChild.data.split(" ")
        upperCorner=root.getElementsByTagName('ows:UpperCorner')[0].firstChild.data.split(" ")
        crs=root.getElementsByTagName('ows:BoundingBox')[0].getAttribute("crs") 
        return {'identifier':identifier,'lowerCorner':lowerCorner,'upperCorner':upperCorner,'crs':crs}
    elif method=="Execute":
        print(rootName)
        if (rootName!="wps:Execute"):
            return "{'error':'Please check the XML document'}"
        identifier=root.getElementsByTagName('ows:Identifier')[0].firstChild.data
        inputs=root.getElementsByTagName('wps:Input')
        variables=[]
        for input in inputs:
            curInputParam={}
            curInputParam["identifier"]=input.getElementsByTagName('ows:Identifier')[0].firstChild.data
            if len(input.getElementsByTagName('wps:Reference')) !=0:
                ## Currently just accept wps:Reference and href
                curInputParam["value"]=input.getElementsByTagName('wps:Reference')[0].getAttribute("xlink:href")
                curInputParam["mimeType"]=input.getElementsByTagName('wps:Reference')[0].getAttribute("mimeType")
            if len(input.getElementsByTagName('wps:LiteralData')) !=0:
                curInputParam["value"]=input.getElementsByTagName('wps:LiteralData')[0].firstChild.data
            variables.append(curInputParam)

        #currently accept raw output
        outputs=root.getElementsByTagName('wps:RawDataOutput')
        for output in outputs:
            curOutputParam={}
            curOutputParam["mimeType"]=output.getAttribute("mimeType")
            curOutputParam["identifier"]=output.getElementsByTagName('ows:Identifier')[0].firstChild.data
            variables.append(curOutputParam)
        
    params={"identifier":identifier,"variables":variables}
    print(params)
    return params

def convert_to_ee_vector(content,type="geojson"):
    if (type=='geojson'):
        return gee_utils.generateEEFeaturesFromJSON(content)

def convert_to_ee_image():
    return

def convert_by_ee_cloud(url,type="tiff"):
    return
