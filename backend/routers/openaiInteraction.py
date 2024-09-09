from fastapi import APIRouter, UploadFile
from pdf2image import convert_from_path
from openai import AzureOpenAI
import os
import base64
import json


router = APIRouter(
    prefix="/openai",
    tags=["openai"]
    #responses={}
)



###
# How does it work
###

## Input: PDF file
## Output: Semi-Structured Data

# Aux methods
def pdfToImage(files: list[UploadFile]):
    invoices: list[dict]= []
    for file in files:
        print(file)
        fileName = file.split(".")[0]
        invoiceImage = convert_from_path('sample_data/'+file, 400)

        # Save pages as images in the pdf
        fileOutputPath = f'output_data/{fileName}.jpg'
        invoiceImage[0].save(fileOutputPath, 'JPEG')

        invoices.append({
            "fileName":fileName,
            "path": fileOutputPath
        })

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
    api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key= os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = '<your_deployment_name>'
    api_version = '2023-12-01-preview' # this might change in the future

    client = AzureOpenAI(
        api_key=api_key,  
        api_version=api_version,
        base_url=f"{api_base}/openai/deployments/{deployment_name}"
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
                        "url": "<image URL>"
                    }
                }
            ] } 
        ],
        max_tokens=2000 
    )

    print(response)




@router.post("/convertInvoice")
async def convertInvoice(files: list[UploadFile]):
    listFiles: list[dict] = [] # PDF List
    listFiles = pdfToImage(files=files)

    for file in listFiles:
        azopaiRequest(file)


    

        
        

