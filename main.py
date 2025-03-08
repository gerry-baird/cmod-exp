from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import cmod
import json
import os
from urllib.parse import quote


from model import Folder, FolderList, BambooBankList, BambooBankSearch

load_dotenv()

app = FastAPI()

# Create CMOD connection
#---------------------------------------------------------------------------------#
PROXYServer=os.getenv('PROXYServer')
CMODServer=os.getenv('CMODServer')
CMODAuthorization=os.getenv('CMODAuthorization')
tmp=cmod.CMODClient(CMODServer,CMODAuthorization)
#---------------------------------------------------------------------------------#


@app.get("/")
def root():
    return {"message": "IBM Content Manager OnDemand FastAPI"}

@app.get("/cmod-rest/v1/hits/{folder}/{rest_of_path:path}")
def cmod_proxy(folder:str, rest_of_path:str)-> FileResponse:

    print("folder: " + folder)
    print("rest_of_path: " + rest_of_path)

    encoded_folder = quote(folder, safe="")
    print("encoded_folder: " + encoded_folder)

    filecontent = tmp.CMODRetrieveDocument(rest_of_path, encoded_folder)
    filename="cmod.pdf"
    with open(filename, "wb") as f:
        f.write(filecontent)
    return FileResponse(filename, media_type="application/pdf")


@app.get("/allfolders",summary="List all folders on the connected CMOD server", response_description="List of all folders on the connected CMOD server")
def get_folders()-> FolderList:
# def get_folders():
    result=tmp.CMODFolderList()
    number=len(result)
    return {"number": number, "folders": result}

@app.get("/searchfolders", summary="Search for matching folders", response_description="List of matching folders")
def search_folders(char: str)-> FolderList:
    # Retrieve all folder
    folders=tmp.CMODFolderList()
    # Filter folders to select from
    k=0
    result=[]
    for i in range(len(folders)):
        foldername=folders[i].get("name")
        if char in foldername:
            result.append(folders[i])
            k=k+1
    return {"number": k, "folders": result}

@app.get("/r_BambooBank", summary="Retrieve a single document from Bamboo folder", response_description="Single document in binary form")
def r_BambooBank(docID:str) -> FileResponse:
    docID_encoded = requests.utils.requote_uri(docID)

    filename="cmod.pdf"
    foldername="Bamboo Bank"
    filecontent=tmp.CMODRetrieveDocument(docID_encoded,foldername)
    with open(filename, "wb") as f:
        f.write(filecontent)
    return FileResponse(filename, media_type="application/pdf")

@app.post("/s_BambooBank", summary="Search for documents in Bamboo Bank folder", response_description="List of matching documents")
async def s_BambooBank(payload: BambooBankSearch)-> BambooBankList:
    AccountType=payload.AccountType
    AccountNumber=payload.AccountNumber
    criteria=[{"fieldName":"Account Type","operator":"Like","values":[AccountType]}]
    if AccountNumber!= None:
        criteria.append({"fieldName":"Account Number","operator":"Like","values": [AccountNumber]})

    # Post-processing to reformat result to a valid document list
    x=tmp.CMODSearch("Bamboo Bank", criteria)
    x=x["hitList"]
    number=len(x)
    result=[]
    for i in range(len(x)):
        docID=x[i].get("docID")
        link=x[i].get("link")
        y=link.find(docID[0:2]) # link field includes valid URL information, but prefix needs to be removed (end of prefix determined by comparing with docID)
        docID=str(link[y:]) # docID extracted from link
        encoded_docID = quote(docID, safe="")
        link="http://"+PROXYServer+"/cmod-rest/v1/hits/Bamboo%20Bank/"+encoded_docID
        mimeType=x[i].get("mimeType")
        # Folder specific fields
        AccountType=x[i].get("folderFields").get("Account Type")
        StatementDate=x[i].get("folderFields").get("Statement Date")
        AccountNumber=int(x[i].get("folderFields").get("Account Number"))
        docproperties= {"docID": docID, "link": link, "mimeType": mimeType,"AccountType": AccountType,"StatementDate": StatementDate,"AccountNumber": AccountNumber }
        result.append(docproperties)

    bank_list = BambooBankList(
        number=number,
        documents=result
    )
    return bank_list
