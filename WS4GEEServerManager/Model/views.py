from ast import Param
from django.core.checks.messages import Error
from django.shortcuts import render
from django.http import HttpResponse, response
import sys
from Utils import general_utils
from GEEUtils import gee_utils,generator,parser
from Model.models import SearchRequest,DynamicWcs,DownloadingLog,Process,ProcessParams,ParamRecord,ParamRequest,ExecuteStatusRecord
import threading
import json


# Create your views here.
def post(request):
    modelName=request.POST.get('modelName',0)
    entrance=request.POST.get('entrance',0)
    param1=request.POST.get('a',0)
    param2=request.POST.get('b',0)
    model=__import__(modelName)
    print(model)
    f=getattr(model,entrance)
    return HttpResponse(f(param1,param2))


def generateDynamicService(request):
    serviceType= request.POST.get('serviceType', 0)
    datasetName = request.POST.get('datasetName', 0)
    stackingMethod = request.POST.get('stackingMethod', 0)
    start = request.POST.get('start', 0)
    end = request.POST.get('end', 0)
    boundaryName = request.POST.get('boundaryName', 0)
    boundary = request.POST.get('boundary', 0)
    noCloud = request.POST.get('noCloud', 0)
    byYear = request.POST.get('byYear', 0)
    byMonth = request.POST.get('byMonth', 0)
    bands= request.POST.get('bands', 0)
    # datasetInfo=""
    datasetInfo=gee_utils.getTargetDatasetInfo(general_utils.matchDatasetSnippetName(datasetName),start,end,boundary)
    response=""
    # Store data
    requestUuid=general_utils.getuuid()
    newSearchRequest=SearchRequest(uuid=requestUuid,dataset_name=datasetName,service_type=serviceType,
        stacking_method=stackingMethod,start=start,end=end,boundary=boundary,
        boundary_name=boundaryName,no_cloud=int(noCloud),by_year=int(byYear),by_month=int(byMonth),dataset_info=datasetInfo,bands=bands)
    newSearchRequest.save()

    if (serviceType=='WCS'):
        WCSNames=[]
        if int(byMonth)==1:    #generate by month
            periods=general_utils.split_time_by_month(start,end)
            bandsName=str(bands).replace('[','').replace(']','').replace(',','').replace('\'',"")
            for period in periods:
                # store each dynamic WCS,record requestUuid and this Uuid, start, end, method (mean, max or min)
                curWCSUuid=general_utils.matchDatasetName(datasetName)+'_'+boundaryName+'_'+period['start_year']+period['start_month']+period['start_day']+'_'+period['end_year']+period['end_month']+period['end_day']+'_'+bandsName+'_'+general_utils.getuuid12()
                WCSNames.append(curWCSUuid)
                newDynamicWcs=DynamicWcs(uuid=curWCSUuid,req_uuid=requestUuid,
                    start=period['start_year']+'-'+period['start_month']+'-'+period['start_day'],
                    end=period['end_year']+'-'+period['end_month']+'-'+period['end_day'])
                newDynamicWcs.save()
        responseDir={}
        responseDir['code']=0
        responseDir['data']=WCSNames
        return HttpResponse(str(responseDir))

def get_service(request,dataset,type):
    docStr=""
    if request.method=='GET':
        service=request.GET.get('service')
        version=request.GET.get('version',default="1.1.0")
        requestType=request.GET.get('request')
        if (service is None) or (requestType is None):
            return HttpResponse("error")

        # WCS GetCapabilities
        if (str(requestType).lower()=='getcapabilities'):
            if (str(type).lower()=='wcs'):
                curSearchRequest=SearchRequest.objects.get(uuid=dataset)
                geojsonData=curSearchRequest.boundary
                extent=general_utils.getBoundary(geojsonData)
                datasetName=curSearchRequest.dataset_name
                noCloud=curSearchRequest.no_cloud
                method=curSearchRequest.stacking_method
                
                curWCSs=DynamicWcs.objects.filter(req_uuid=dataset)
                content={}
                content["serviceIdentification"]={}
                content["serviceIdentification"]["title"]="Web Coverage Service for : (boundary:)"+curSearchRequest.boundary_name
                content["serviceIdentification"]["serviceType"]="WCS"
                content["serviceIdentification"]["serviceTypeVersion"]="1.1.1"
                content["serviceProvider"]={}
                content["serviceProvider"]["providerName"]="WS4GEE"
                content["serviceProvider"]["providerSite"]="http://127.0.0.1:8000"
                content["operationsMetadata"]={}
                content["operationsMetadata"]["url"]="http://127.0.0.1:8000"+"/test/wcs?"
                content["operationsMetadata"]["operationName"]=["GetCapabilities","DescribeCoverage","GetCoverage"]
                content["Contents"]=[]
                for curWCS in curWCSs:
                    curCoverageSummary={}
                    curCoverageSummary['title']=curWCS.uuid
                    curCoverageSummary['abstract']='Stacking method: '+method+'; no cloud:'+str(bool(noCloud))+'; start time: '+curWCS.start+'; end time: '+curWCS.end
                    curCoverageSummary['keywords']=[datasetName,"WCS","GeoTIFF"]
                    curCoverageSummary['extent']=extent
                    curCoverageSummary['identifier']=curWCS.uuid
                    content["Contents"].append(curCoverageSummary)
            
                docStr=generator.generate_service_description('GetCapabilities',content,'WCS')
        elif (str(requestType).lower()=='describecoverage'):
            # WCS DescribeCoverage
            identifier=request.GET.get('identifiers')
            ## Check if the xml exist in the Cache
            ############
            # docPath=None
            # ## Firstly search if it exists in the storage, if true return directly
            # if docPath!=None:
            #     responseXML= general_utils.readXMLFileToStr(docPath)
            #     return HttpResponse(responseXML, content_type='text/xml')
            ############
            ## a new request
            if (identifier is None):
                return HttpResponse("error")
            curWCS=DynamicWcs.objects.get(uuid=identifier)
            if (curWCS is None):
                return HttpResponse("error")
            curSearchRequest=SearchRequest.objects.get(uuid=curWCS.req_uuid)
            datasetInfo,imageInfo=None,None
            if (curWCS.dataset_info is None):
                datasetInfo=gee_utils.getTargetDatasetInfo(general_utils.matchDatasetSnippetName(curSearchRequest.dataset_name),curWCS.start,curWCS.end,curSearchRequest.boundary)
                curWCS.dataset_info=datasetInfo
                curWCS.save()
            else:
                datasetInfo=eval(curWCS.dataset_info)
            if (curWCS.image_info is None):
                imageInfo=gee_utils.getImageInfo(general_utils.matchDatasetSnippetName(curSearchRequest.dataset_name),curWCS.start,curWCS.end,curSearchRequest.boundary,curSearchRequest.bands,curSearchRequest.stacking_method,curSearchRequest.no_cloud)
                curWCS.image_info=imageInfo
                curWCS.save()
            else:
                imageInfo=eval(curWCS.image_info)
                # print(datasetInfo)            

            geojsonData=curSearchRequest.boundary
            extent=general_utils.getBoundary(geojsonData)
            usingImages=[]
            for image in (datasetInfo['features']):
                usingImages.append(image["id"])
            
            content={}
            content["title"]=identifier
            content["abstract"]="Generate by images(id):"+",".join(usingImages)
            if "keywords" in (datasetInfo['properties'].keys()):
                content['keywords']=datasetInfo['properties']['keywords']
            else:
                content['keywords']=["WS4GEE","GeoTIFF","WCS"]
            content['identifier']=identifier
            content['extent']=extent
            if 'min' in imageInfo['bands'][0]['data_type']:
                content['minimumValue']=str(imageInfo['bands'][0]['data_type']['min'])
                content['maximumValue']=str(imageInfo['bands'][0]['data_type']['max'])
            else:
                content['minimumValue']="-Infinity"
                content['maximumValue']="Infinity"
            content["availableBands"]=eval(curSearchRequest.bands)
            docStr=generator.generate_service_description('DescribeCoverage',content,'WCS')
    
    if request.method=='POST':
        if str(type)=='wcs':
            ## GetCoverage Method
            params=parser.retrieve_attr(request.body,"GetCoverage")
            if ("error" in params.keys()):
                return HttpResponse('<error>{0}<error>'.format(params["error"]),"text/xml")
            tempImageName=general_utils.getuuid12()
            content={}
            content["title"]=params["identifier"]
            content['abstract']="Generated from GEE. Please see check the status in the url: {0} . Then download after the generation completes.".format("http://127.0.0.1:8000/status/"+tempImageName)
            content['identifier']=params["identifier"]
            minX,minY,maxX,maxY=float(params['lowerCorner'][0]),float(params['lowerCorner'][1]),float(params['upperCorner'][0]),float(params['upperCorner'][1])

            curWCS=DynamicWcs.objects.get(uuid=params["identifier"])
            curSearchRequest=SearchRequest.objects.get(uuid=curWCS.req_uuid)
            content['resultUrl']="http://127.0.0.1:8080/examples/temp/"+tempImageName+".tif"
            docStr=generator.generate_service_outcome("GetCoverage",content)
            
            ## current  the resolution was set initially
            def func():
                curImage=gee_utils.getTargetImage(general_utils.matchDatasetSnippetName(curSearchRequest.dataset_name),curWCS.start,curWCS.end,curSearchRequest.boundary,curSearchRequest.bands,curSearchRequest.stacking_method,curSearchRequest.no_cloud)
                gee_utils.generateUrlForTargetImage(256,curImage,tempImageName,minX,minY,maxX,maxY)
            thread = threading.Thread(target=func)
            thread.start() 
            return HttpResponse(docStr,"text/xml")
    return HttpResponse(docStr,"text/xml")

def get_process_service(request):
    docStr=""
    if request.method=='GET':
        requestType=request.GET.get('request')
        if (requestType=='GetCapabilities'):
            # WPS GetCapabilities
            content={}
            content["serviceIdentification"]={}
            content["serviceIdentification"]["serviceType"]="WPS"
            content["serviceIdentification"]["serviceTypeVersion"]="1.0.0"
            content["serviceIdentification"]["title"]="WS4GEE WPS v0.0.1-beta"
            content["serviceIdentification"]["abstract"]="Services generated by WS4GEE from google earth engine"
            content["serviceProvider"]={}
            content["serviceProvider"]["providerName"]="WS4GEE"
            content["serviceProvider"]["providerSite"]="http://127.0.0.1:8000"
            content["operationsMetadata"]={}
            content["operationsMetadata"]["url"]="http://127.0.0.1:8000"+"/test/wps"
            content["operationsMetadata"]["operationName"]=["GetCapabilities","DescribeProcess","Execute"]
            content["processes"]=[]
            curProcesses=Process.objects.all()
            for process in curProcesses:
                content["processes"].append({"identifier":process.name,"title":process.title})
                # print(process.uuid,process.name,process.entrance_func,process.script_path,process.title)
                # curProcessParams=ProcessParams.objects.filter(process_uuid=process.uuid)
                # for param in curProcessParams:
                    # print(param.param_name,param.data_type,param.data_type,param.order,param.param_type,param.process_uuid,param.title,param.other_content)
            docStr=generator.generate_service_description("GetCapabilities",content,"WPS")
            return  HttpResponse(docStr,"text/xml")
        elif (requestType=='DescribeProcess'):
            content=[]
            identifiers=str(request.GET.get('identifier')).split(';')
            docPath=None
            ## Firstly search if it exists in the storage, if true return directly
            # if docPath!=None:
            #     doc= general_utils.readXMLFileToStr(docPath)
            #     return HttpResponse(doc,content_type='text/xml')
            # else:   # a new request 
            for identifier in identifiers:
                curContent={}    
                curProcess=Process.objects.get(name=identifier)
                curContent["identifier"]=curProcess.name
                curContent["title"]=curProcess.title
                if (curProcess.abstract is not None):
                    curContent["abstract"]=curProcess.abstract
                curParams=ProcessParams.objects.filter(process_uuid=curProcess.uuid)
                params=[]
                for curParam in curParams:
                    paramDict={}
                    paramDict["identifier"]=curParam.param_name
                    paramDict["title"]=curParam.title
                    paramDict["paramType"]=curParam.param_type
                    paramDict["dataType"]=curParam.data_type
                    otherContent=curParam.other_content
                    if (otherContent is not None) and (otherContent.strip()!=""):
                        print(otherContent)
                        paramDict.update(eval(otherContent))
                    params.append(paramDict)
                curContent["params"]=params
                content.append(curContent) 
            docStr=generator.generate_service_description("DescribeProcess",content)
            return HttpResponse(docStr,"text/xml")
        return
    if request.method=='POST':
        curParamsDir=parser.retrieve_attr(request.body,"Execute")
        identifier=curParamsDir["identifier"]
        curProcess=Process.objects.get(name=identifier)
        entrance_func=curProcess.entrance_func
        entrance_name=curProcess.entrance_name
        curProcessParams=ProcessParams.objects.filter(process_uuid=curProcess.uuid).order_by("order")
        usedScale=30
        usedBounds=""
        paramsVariableList=[]
        for i in range(0,len(curProcessParams)):
            paramName=curProcessParams[i].param_name
            for variable in curParamsDir['variables']:
                if (variable["identifier"]=="export_scale"):
                    usedScale=int(variable["value"])
                    continue
                if (variable["identifier"]=="export_bounds"):
                    usedBounds=eval(general_utils.readStrFromUrl(variable["value"]))
                    continue
                if (variable["identifier"]==paramName):
                    curType=curProcessParams[i].data_type
                    if ('value' not in variable.keys()):
                        continue
                    if curType=='float' or curType=='double':
                        paramsVariableList.append(float(variable["value"]))
                    elif curType=='int':
                        paramsVariableList.append(int(variable["value"]))
                    elif curType=='string':   
                        paramsVariableList.append(str(variable["value"]))
                    elif curType=='boolean':
                        paramsVariableList.append(bool(variable["value"]))
                    elif curType=='Vector':
                        ## temporarily accept only geojson
                        if (variable["mimeType"]=="text/plain"):
                            geojsonData=general_utils.readStrFromUrl(variable["value"])
                            paramsVariableList.append(parser.convert_to_ee_vector(geojsonData,"geojson"))  # value is a url
                            # paramsVariableList.append(geojsonData)  
                    elif curType=='Raster':
                        ## temporarily accept only ref
                        paramsVariableList.append(parser.convert_by_ee_cloud(variable["value"],variable["mimeType"]))

        ##execute model
        model=__import__(entrance_name)
        f=getattr(model,entrance_func)
        result=f(*paramsVariableList)

        ##save this record
        statusUuid=general_utils.getuuid12()
        curRecord=ExecuteStatusRecord(uuid=statusUuid,process_uuid=curProcess.uuid)
        curRecord.save()

        content={"identifier":curProcess.name,"title":curProcess.title,"statusUuid":statusUuid}
        docStr=generator.generate_service_outcome("Execute",content)
        #Currently just accept one output
        outputParam= ProcessParams.objects.get(process_uuid=curProcess.uuid,param_type='output')
        if (outputParam.data_type == "Vector"):
            return HttpResponse("Vector")
        elif (outputParam.data_type == "Raster"):
            tempImageName=general_utils.getuuid12()
            curRecord.execution_uuid=tempImageName
            curRecord.save()

            def func():
               gee_utils.generateUrlForTargetImageWithBounds(usedScale,result,tempImageName,usedBounds)
            thread = threading.Thread(target=func)
            thread.start() 
            
            return HttpResponse(docStr,"text/xml")
        else:
            return HttpResponse(result)


def checkCoverageStatus(request,uuid):
    list=DownloadingLog.objects.filter(image_uuid=uuid).order_by("create_time")
    status=list[len(list)-1].status
    print(status)
    return HttpResponse(status) 

def checkExecuteStatus(request):
    curStatusUuid=request.GET.get("id")
    curStatus=ExecuteStatusRecord.objects.get(uuid=curStatusUuid)
    curProcess=Process.objects.get(uuid=curStatus.process_uuid)
    list=DownloadingLog.objects.filter(image_uuid=curStatus.execution_uuid).order_by("create_time")
    status=list[len(list)-1].status
    content={}
    content["statusUuid"]=curStatusUuid
    content["identifier"]=curProcess.entrance_name
    content["title"]=curProcess.title
    content["status"]=status

    if (status=='DOWNLOADED'):
        content["resultUrl"]="http://127.0.0.1:8080/examples/temp/"+curStatus.execution_uuid+".tif"
        content["mimeType"]="image/tiff"

    docStr=generator.generate_service_outcome('ExecuteStatus',content)
    return HttpResponse(docStr,"text/xml")

## Obsoleted methods
def execute(request):
    xmlDoc=request.POST.get('xmlDoc', 0)
    serviceName=parser.getServiceName(xmlDoc)
    ## get entrance_func function to the model from the Storage (db), obtains its variables
    ######
    entrance_func=None
    paramsNameList=[]
    paramsVariableList=[]
    paramsTypeList=[]
    curParamsDir=parser.retrieve_attr()  # obtain user input params
    
    size=len(paramsNameList)
    for i in range(0,size):
        paramName=paramsNameList[i]
        for key in curParamsDir.keys():
            if (key==paramName):
                curType=paramsTypeList[i]
                if curType=='float' or curType=='double':
                    paramsVariableList.append({float(curParamsDir[key])})
                elif curType=='integer':
                    paramsVariableList.append(int(curParamsDir[key]))
                elif curType=='string':
                    paramsVariableList.append(str(curParamsDir[key]))
                elif curType=='boolean':
                    paramsVariableList.append(bool(curParamsDir[key]))
                elif curType=='Vector':
                    ## temporarily accept only ref
                   paramsVariableList.append(parser.convert_to_ee_vector(curParamsDir[key]))
                elif curType=='Raster':
                    ## temporarily accept only ref
                   paramsVariableList.append(parser.convert_by_ee_cloud(curParamsDir[key]))
    
    model=__import__(serviceName)
    func=getattr(model,entrance_func)
    result = func(*paramsVariableList)

    outputType=paramsTypeList[size-1]  ## temporarily accept only one outcome
    responseXML=generator.generate_service_outcome(outputType,result)
    return HttpResponse(responseXML,content_type='text/xml') 







