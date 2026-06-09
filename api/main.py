from io import BytesIO
from pathlib import Path
import numpy as np 
import tensorflow as tf 
import uvicorn
from fastapi import FastAPI , File , HTTPException , UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image , UnidentifiedImageError

app = FastAPI(title="Tomatos Disease Classification API")
app.add_middleware( # ye allow karta hai jab frontend and backend ka port different rhta hai to us samay ye middleware ka kaam karta hai 
    CORSMiddleware,
    allow_origins = ["*"], #kisi ko bhi allow karta hai kisi web ka req 
    allow_credentials=False, #browser can send cookies / data if it is true
    allow_methods =["*"], #allows all http method like get post put delete usually in production we only allow get and post 
    allow_headers=["*"],#sare request header ko allow karta hai 
)

#load model 
BASE_DIR = Path(__file__).resolve().parent # RESOLVE MEANS KIS ABSOLUTE PATH ME CONVERT KARNA # parent malab parent folder me jaana 
MODEL_PATH = BASE_DIR.parent/"models"/"tomato_model.keras" # for fetching where the model is present 
print("Loading Model from " , MODEL_PATH)
Model = tf.keras.models.load_model(MODEL_PATH)

CLASS_NAMES = ['Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight', 'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot', 'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato__Target_Spot', 'Tomato__Tomato_YellowLeaf__Curl_Virus', 'Tomato__Tomato_mosaic_virus', 'Tomato_healthy']

@app.get("/")
async def home():
    return {"message" : "Tomato Disease Classification API Running"}

@app.get("ping")
async def ping():
    return "Working"

def read_file_as_image(data:bytes) ->np.ndarray: #CONVER IMAGE TO NUMPY ARRAY 
    try:
        image = Image.open(BytesIO(data))
        image = image.convert("RGB")
        return np.array(image)
    
    except UnidentifiedImageError as exc :
        raise HTTPException(
            status_code=400 , detail="Upload File Is not a valid Image"
        ) from exc
        

@app.post("/predict")
async def predict(file:UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400 , detail="Please Uplaod an Image")
    
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Image is Empty")
    image = read_file_as_image(contents)
    image_batch = np.expand_dims(image, axis=0)
    predictions = Model.predict(image_batch, verbose=0)
    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = float(np.max(predictions[0]))
    
    return {"class" : predicted_class , "confidence":confidence}



if __name__ == "__main__":
    uvicorn.run(app,host="localhost",port=8000)
    
    