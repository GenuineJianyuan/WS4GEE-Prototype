import ee
import os
import json
import time

os.environ['HTTP_PROXY']="http://127.0.0.1:7890"
os.environ['HTTPS_PROXY']='http://127.0.0.1:7890'

# ee.Authenticate()
ee.Initialize()
feature=None
with open(r"C:\\Users\\Administrator\\Desktop\\GEE_Project\\WuhanBoundary2.json","rb") as f:
       geo_json = json.loads(f.read())
       # print(geo_json["features"])
       features = ee.FeatureCollection(geo_json["features"])
def test():
       print("test1") 
def cloudMaskL457(image):
  qa = image.select('pixel_qa')
#   If the cloud bit (5) is set and the cloud confidence (7) is high
#   or the cloud shadow bit is set (3), then it's a bad pixel.
  cloud = qa.bitwiseAnd(1 << 5).And(qa.bitwiseAnd(1 << 7)).Or(qa.bitwiseAnd(1 << 3))
#   // Remove edge pixels that don't occur in all bands
  mask2 = image.mask().reduce(ee.Reducer.min())
  return image.updateMask(cloud.Not()).updateMask(mask2)


AOI = ee.Geometry.Rectangle([115.647,-33.669,115.690,-33.685])
dataset = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').filterDate('2020-01-01', '2020-12-31').map(cloudMaskL457).filterBounds(features)
print(dataset.getInfo())
# for img in (dataset.getInfo()['features']):
#        print(img["id"])
# imageCollection = ee.ImageCollection('MODIS/006/MOD13Q1').filterDate('2017-01-01', '2018-10-01').filterBounds(AOI).select('EVI')
# collectionList = imageCollection.toList(imageCollection.size())

out_image = ee.Image(collectionList.get(1))#export first image
out_image=dataset.mean().clip(features).select(['B1','B2','B3','B4'])
# task = ee.batch.Export.image.toCloudStorage(
#        image=out_image,
#        bucket='image_bucket_leismars',
#        fileNamePrefix='Wuhan2',
#        scale=30,
#        region=features.geometry())
# task.start()
# start_time = time.time()
# state=""
# while state!='COMPLETED':
#        print(task.status())
#        state=task.status()['state']
#        time.sleep(10)
# print("finish")




