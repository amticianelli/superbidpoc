from fastapi import APIRouter, UploadFile, FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
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

# VertexAI integration
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models


router = APIRouter(
    prefix="/openai",
    tags=["openai"]
    #responses={}
)

security = HTTPBasic()

# Setting auth credentials
# ENGINE
ENGINE = os.getenv("ENGINE",'OPENAI')

# AZ Open AI
API_BASE = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY= os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT_NAME= os.getenv("MODEL_NAME")
API_VERSION = os.getenv('API_VERSION','2023-12-01-preview')

# Vertex
VERTEX_MODEL = os.getenv('VERTEX_MODEL','gemini-2.0-flash-exp')
VERTEX_KEYPATH = os.getenv('KEYPATH','./gcloud_key.json')
VERTEX_PROJECT = os.getenv('VERTEX_PROJECT','adeconnect-dev')
VERTEX_LOC = os.getenv('VERTEX_LOC','us-central1')

#BR Gov
BRGOV_API_KEY = os.getenv("BRGOV_API_KEY")
BRGOV_ENDPOINT = os.getenv("BRGOV_ENDPOINT")

# FastAPI
PREDEFINED_SECRET = os.getenv("PREDEFINED_SECRET")

# Obtaining prompts
with open("prompt.yaml", 'r') as stream:
    try:
        PROMPT_CONF = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

## Check credentials
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = credentials.username == "admin"
    correct_password = credentials.password == PREDEFINED_SECRET
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


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
           "image": convert_from_bytes(pdf_file=contentBytes,dpi=400, grayscale=True, jpegopt={'quality': 100})
           })

        # Save pages as images in the pdf
        

    return invoices


def getCompanyStatus(CNPJ: str):

    CNPJ = CNPJ \
            .replace('.','')\
            .replace('-','')\
            .replace('/','')

    finalResult: dict = {
        "situacao": None,
        "tipoempresa": None
    }
   
    # https://cnpja.com/api
    response = requests.get(
      url=f'{BRGOV_ENDPOINT}/{CNPJ}?simples=true',
      headers={'Authorization': BRGOV_API_KEY}
      )
    
    if response.status_code == 200:
        companyData: dict = json.loads(response.text)

        if companyData['company']['simei']['optant'] == True:
            finalResult['tipoempresa'] = 'MEI'
        elif 'simples' in companyData['company'] and companyData['company']['simples']['optant'] == True:
            finalResult['tipoempresa'] = 'Simples nacional'
        else:
            finalResult['tipoempresa'] = 'Lucro presumido'


        finalResult['situacao'] = companyData['status']['text']

    else:
       return { 
          'Error': {response.status_code},
          'Response':  {response.text}
          }
    
    return finalResult
   

def azopaiRequest(fileInfo: dict):

    fileName: str = fileInfo["filename"]


    image: Image.Image = fileInfo["image"][0] # Getting the first image only

    print(f'Image size: {image.size} Image type: {type(image)}')


    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')

    # DEBUG
    image.save(f'./{fileName}'.replace('pdf','jpeg')) # DEBUG

    print(f'File to be processed: {fileName}, size: {imgByteArr.getbuffer().nbytes}')
       

    encoded_image = base64.b64encode(imgByteArr.getvalue()).decode('ascii')
    
    deployment_name = DEPLOYMENT_NAME
    api_version = API_VERSION # this might change in the future

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
        max_tokens=4096,
        temperature=0.0
    )

    

    invoiceData: dict = json.loads(response.choices[0].message.content)

    if invoiceData is not None:
        if 'prestador' in invoiceData:
            checkCompany: dict = getCompanyStatus(invoiceData['prestador']['cpf_cnpj'])

            if 'Error' not in checkCompany:
                print(checkCompany)
                invoiceData['situacao'], invoiceData['tipo_empresa'] = checkCompany['situacao'],checkCompany['tipoempresa']
            else:
                 print(checkCompany)
    return invoiceData


def vertexRequest(fileInfo: dict) -> dict:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = VERTEX_KEYPATH

    fileName: str = fileInfo["filename"]


    image: Image.Image = fileInfo["image"][0] # Getting the first image only

    print(f'Image size: {image.size} Image type: {type(image)}')


    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')

    # DEBUG
    image.save(f'./{fileName}'.replace('pdf','jpeg')) # DEBUG

    print(f'File to be processed: {fileName}, size: {imgByteArr.getbuffer().nbytes}')
       

    encoded_image = base64.b64encode(imgByteArr.getvalue()).decode('ascii')

    image1 = Part.from_data(
        mime_type="image/jpeg",
        data=base64.b64decode(encoded_image))

    generation_config = {
        "max_output_tokens": 2048,
        "top_p": 0.4,
        "top_k": 32,
        "temperature": 0
        }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    vertexai.init(project=VERTEX_PROJECT, location=VERTEX_LOC)
    
    model = GenerativeModel(VERTEX_MODEL)

    response = model.generate_content(
        [PROMPT_CONF['systemMessage']+PROMPT_CONF['mainPrompt'] + PROMPT_CONF['result_output'], image1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,

    )

    #print(response.text)

    jsonResult = response.text \
                .replace("```","") \
                .replace("json","") \
                .replace("\n","")
  
    invoiceData: dict = json.loads(jsonResult)

    if invoiceData is not None:
        if 'prestador' in invoiceData:
            checkCompany: dict = getCompanyStatus(invoiceData['prestador']['cpf_cnpj'])

            if 'Error' not in checkCompany:
                print(checkCompany)
                invoiceData['situacao'], invoiceData['tipo_empresa'] = checkCompany['situacao'],checkCompany['tipoempresa']
            else:
                 print(checkCompany)
    return invoiceData




@router.post("/convertInvoice/")
def convertInvoice(files: list[UploadFile], user: str = Depends(verify_credentials)):
    
    print(f'User: {user}')
    
    listFiles: list[dict] = [] # PDF List
    listFiles = pdfToImage(files=files)

    responseList: list[dict] = []

    for file in listFiles:
        responseList.append(azopaiRequest(file)) if ENGINE == 'OPENAI' else responseList.append(vertexRequest(file)) 

    

    return responseList


    

        
        

