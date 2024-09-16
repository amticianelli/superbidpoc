from fastapi import APIRouter, UploadFile
from pdf2image import convert_from_bytes
from openai import AzureOpenAI
import os
import base64
import json
import requests
from PIL import Image
import io
from openai.types.chat.chat_completion import ChatCompletion
import yaml

router = APIRouter(
    prefix="/openai",
    tags=["openai"]
    #responses={}
)

# Setting auth credentials
API_BASE = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY= os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT_NAME= os.getenv("MODEL_NAME")

BRGOV_API_KEY = os.getenv("BRGOV_API_KEY")
BRGOV_ENDPOINT = os.getenv("BRGOV_ENDPOINT")

# Obtaining prompts
with open("prompt.yaml", 'r') as stream:
    try:
        PROMPT_CONF = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


###
# How does it work
###

## Input: PDF file
## Output: Semi-Structured Data

# Aux methods
def pdfToImage(files: list[UploadFile]):
    invoices: list[dict]= []

    
    for coroutine in files:
        contentBytes = coroutine.file.read()


        invoices.append({
           "filename": coroutine.filename,
           "image": convert_from_bytes(pdf_file=contentBytes)
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

def getCompanyStatus(CNPJ: str):
   
    # https://cnpja.com/api
   response = requests.get(
      url=f'{BRGOV_ENDPOINT}/{CNPJ}?simples=true',
      headers={'Authorization': BRGOV_API_KEY}
      )

def azopaiRequest(fileInfo: dict):

    fileName: str = fileInfo["filename"]


    image: Image.Image = fileInfo["image"][0] # Getting the first image only

    print(f'Image size: {image.size} Image type: {type(image)}')


    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')

    # DEBUG
    #image.save(f'./{fileName}'.replace('pdf','png')) # DEBUG

    print(f'File to be processed: {fileName}, size: {imgByteArr.getbuffer().nbytes}')
       

    encoded_image = base64.b64encode(imgByteArr.getvalue()).decode('ascii')
    
    deployment_name = DEPLOYMENT_NAME
    api_version = '2023-12-01-preview' # this might change in the future

    client = AzureOpenAI(
        api_key=API_KEY,  
        api_version=api_version,
        base_url=f"{API_BASE}/openai/deployments/{deployment_name}",
        max_retries=3,
        timeout=60,
        
    )

    response = client.chat.completions.create(
        model=deployment_name,
        response_format={"type":"json_object"},
        messages=[
            { "role": "system", "content": PROMPT_CONF['systemMessage'] },
            { "role": "user", "content": [  
                { 
                    "type": "text", 
                    "text": PROMPT_CONF['mainPrompt'] + PROMPT_CONF['result_output']
                },
                { 
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded_image}"
                    }
                }
            ] } 
        ],
        max_tokens=4096 
    )

    

    #print(response)

    return json.loads(response.choices[0].message.content)




@router.post("/convertInvoice")
def convertInvoice(files: list[UploadFile]):
    listFiles: list[dict] = [] # PDF List
    listFiles = pdfToImage(files=files)

    responseList: list[dict] = []

    for file in listFiles:
        responseList.append(azopaiRequest(file)) 

    return responseList


    

        
        

