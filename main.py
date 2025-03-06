from fastapi import FastAPI
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import cmod
import json
import os
from model import Folder, FolderList, BambooBankList, BambooBankSearch

load_dotenv()

app = FastAPI()

# Create CMOD connection
#---------------------------------------------------------------------------------#
CMODServer=os.getenv('CMODServer')
CMODAuthorization=os.getenv('CMODAuthorization')
tmp=cmod.CMODClient(CMODServer,CMODAuthorization)
#---------------------------------------------------------------------------------#


@app.get("/")
def root():
    return {"message": "IBM Content Manager OnDemand FastAPI"}

@app.get("/allfolders",summary="List all folders on the connected CMOD server", response_description="List of all folders on the connected CMOD server")
def get_folders()-> FolderList:
# def get_folders():
    result=tmp.CMODFolderList()
    number=len(result)
    return {"number": number, "folders": result}

@app.get("/r_BambooBank", summary="Retrieve a single document from Bamboo folder", response_description="Single document in binary form")
def r_BambooBank(docID:str) -> FileResponse:
    filename="cmod.pdf"
    # foldername="Bamboo Bank"
    # filecontent=tmp.CMODRetrieveDocument(docID,foldername)
    # with open(filename, "wb") as f:
    #     f.write(filecontent)
    return FileResponse(filename)

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
        link="http://"+CMODServer+"/cmod-rest/v1/hits/Bamboo%20Bank/"+docID
        mimeType=x[i].get("mimeType")
        # Folder specific fields
        AccountType=x[i].get("folderFields").get("Account Type")
        StatementDate=x[i].get("folderFields").get("Statement Date")
        AccountNumber=int(x[i].get("folderFields").get("Account Number"))
        docproperties= {"docID": docID, "link": link, "mimeType": mimeType,"AccountType": AccountType,"StatementDate": StatementDate,"AccountNumber": AccountNumber }
        result.append(docproperties)
    return {"number": number, "documents": result}