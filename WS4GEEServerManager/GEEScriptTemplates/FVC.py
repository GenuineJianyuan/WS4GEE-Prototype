import ee
import os
import json
import time

os.environ['HTTP_PROXY']="http://127.0.0.1:7890"
os.environ['HTTPS_PROXY']='http://127.0.0.1:7890'

ee.Initialize()


def maskL8sr(image):
  #    Bits 3 and 5 are cloud shadow and cloud, respectively.
  cloudShadowBitMask = (1 << 3)
  cloudsBitMask = (1 << 5)
  #    Get the pixel QA band.
  qa = image.select('pixel_qa')
  #    Both flags should be set to zero, indicating clear conditions.
  mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(qa.bitwiseAnd(cloudsBitMask).eq(0))
  return image.updateMask(mask)

def maskL457(image):
  qa = image.select('pixel_qa')
  #    If the cloud bit (5) is set and the cloud confidence (7) is high
  #    or the cloud shadow bit is set (3), then it's a bad pixel.
  cloud = qa.bitwiseAnd(1 << 5).And(qa.bitwiseAnd(1 << 7)).Or(qa.bitwiseAnd(1 << 3))
  #    Remove edge pixels that don't occur in all bands
  mask2 = image.mask().reduce(ee.Reducer.min())
  return image.updateMask(cloud.Not()).updateMask(mask2)

def calFVC(BestVI,region,scale):
    num = BestVI.reduceRegion(
      reducer=ee.Reducer.percentile([5,95]),
      geometry=region,
      scale=scale,
      maxPixels=1e13
    )
    # print(num)
    min = ee.Number(num.get("nd_p5"))
    max = ee.Number(num.get("nd_p95"))
    # print(top_min)
    # print(top_max)
    # quantile and combine
    greaterPart = BestVI.gt(max)
    lessPart = BestVI.lt(min)
    middlePart =ee.Image(1).subtract(greaterPart).subtract(lessPart)
    # calculate FVC
    tempf1=BestVI.subtract(min).divide(max.subtract(min))
    FVC=ee.Image(1).multiply(greaterPart).add(ee.Image(0).multiply(lessPart)).add(tempf1.multiply(middlePart))
    return FVC.rename('FVC')

def entrance(bounds,dataset,start_time,end_time,scale):
  bounds = ee.FeatureCollection(bounds)
  dataset = ee.ImageCollection(dataset).filterDate(start_time, end_time).filterBounds(bounds)
  if (dataset=='LANDSAT/LC08/C01/T1_SR'):
    dataset=dataset.map(maskL8sr)
  else:
    dataset=dataset.map(maskL457)
  def calNDVI(image):
      return image.normalizedDifference(["B5","B4"])
  dataset=dataset.map(calNDVI)
  ndvi=dataset.max().clip(bounds)
  mask_water_NDVI=ndvi.updateMask(ndvi.gt(0))
  FVC=calFVC(mask_water_NDVI,bounds.geometry(),scale)
  return FVC