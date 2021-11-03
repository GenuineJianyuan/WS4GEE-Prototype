import ee
import os,json

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='C:\\Users\\Administrator\\Desktop\\GEE_Project\\sturdy-now-326804-c9a4b9d204cf.json'

os.environ['HTTP_PROXY']="http://127.0.0.1:7890"
os.environ['HTTPS_PROXY']='http://127.0.0.1:7890'

# ee.Authenticate()
ee.Initialize()