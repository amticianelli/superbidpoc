from fastapi import APIRouter, UploadFile
from pdf2image import convert_from_bytes
from openai import AzureOpenAI
import os
import base64
import json
import requests
from PIL import Image
import io

router = APIRouter(
    prefix="/openai",
    tags=["openai"]
    #responses={}
)

API_BASE = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY= os.getenv("AZURE_OPENAI_API_KEY")

###
# How does it work
###

## Input: PDF file
## Output: Semi-Structured Data

# Aux methods
def pdfToImage(files: list[UploadFile]):
    invoices: list[dict]= []

    for file in files:
        invoices.append({
           "filename": file.filename,
           "image": convert_from_bytes(file.read())
           })

        # Save pages as images in the pdf
        

    return invoices

def getCNPJStatus(CNPJ: str):
  CNPJ = CNPJ.replace('.','').replace('-','').replace('/','')
  print(f'Looking for {CNPJ}')
  data = requests.get(f"https://publica.cnpj.ws/cnpj/{CNPJ}")
  print(f"Checking {CNPJ}")

  data = json.loads(data.text)

  # Checking if tag estabelecimento exists
  if 'estabelecimento' in data:
    print(data)

    finalResult: dict = {
        "situacao": data['estabelecimento']['situacao_cadastral'],
        "tipoempresa": data['simples']
    }

    if finalResult['tipoempresa'] is None:
      finalResult['tipoempresa'] = 'Lucro presumido'
    else:
      if finalResult['tipoempresa']['simples'] == 'Sim':
        finalResult['tipoempresa'] = 'Simples nacional'
      else:
        finalResult['tipoempresa'] = 'MEI'
  else:
    finalResult = {
        "situacao": "429 Throttling",
        "tipoempresa": "429 Throttling"
    }

  return json.dumps(finalResult)

def azopaiRequest(fileInfo: dict):

    fileName: str = fileInfo["filename"]
    image: Image.Image = fileInfo["image"]

    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')

    encoded_image = base64.b64encode(imgByteArr).decode('ascii')
    
    deployment_name = '<your_deployment_name>'
    api_version = '2023-12-01-preview' # this might change in the future

    client = AzureOpenAI(
        api_key=API_KEY,  
        api_version=api_version,
        base_url=f"{API_BASE}/openai/deployments/{deployment_name}",
        max_retries=3,
        timeout=60
    )

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            { "role": "system", "content": "You are a helpful assistant." },
            { "role": "user", "content": [  
                { 
                    "type": "text", 
                    "text": "Describe this picture:" 
                },
                { 
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ] } 
        ],
        max_tokens=4096 
    )

    print(response)




@router.post("/convertInvoice")
async def convertInvoice(files: list[UploadFile]):
    listFiles: list[dict] = [] # PDF List
    listFiles = pdfToImage(files=files)

    for file in listFiles:
        azopaiRequest(file)


    

        
        

