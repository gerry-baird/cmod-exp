#  Licensed Materials - Property of IBM (c) Copyright IBM Corp. 2025 All Rights Reserved.
 
#  US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP Schedule Contract with
#  IBM Corp.
 
#  DISCLAIMER OF WARRANTIES :
 
#  Permission is granted to copy and modify this Sample code, and to distribute modified versions provided that both the
#  copyright notice, and this permission notice and warranty disclaimer appear in all copies and modified versions.
 
#  THIS SAMPLE CODE IS LICENSED TO YOU AS-IS. IBM AND ITS SUPPLIERS AND LICENSORS DISCLAIM ALL WARRANTIES, EITHER
#  EXPRESS OR IMPLIED, IN SUCH SAMPLE CODE, INCLUDING THE WARRANTY OF NON-INFRINGEMENT AND THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT WILL IBM OR ITS LICENSORS OR SUPPLIERS BE LIABLE FOR
#  ANY DAMAGES ARISING OUT OF THE USE OF OR INABILITY TO USE THE SAMPLE CODE, DISTRIBUTION OF THE SAMPLE CODE, OR
#  COMBINATION OF THE SAMPLE CODE WITH ANY OTHER CODE. IN NO EVENT SHALL IBM OR ITS LICENSORS AND SUPPLIERS BE LIABLE
#  FOR ANY LOST REVENUE, LOST PROFITS OR DATA, OR FOR DIRECT, INDIRECT, SPECIAL, CONSEQUENTIAL, INCIDENTAL OR PUNITIVE
#  DAMAGES, HOWEVER CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY, EVEN IF IBM OR ITS LICENSORS OR SUPPLIERS HAVE
#  BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

# Libraries used in the CMOD library
#---------------------------------------------------------------------------------#
import http.client
import json
import base64
import urllib.parse
import os
from dotenv import load_dotenv
#---------------------------------------------------------------------------------#

# CMOD class and function definitions
'''
Ping
FolderList
FolderDetails
AppGroupList
AppGroupFields
Transform
Search
AddDocument
RetrieveDocument
RetrieveConvertDocument
'''
#---------------------------------------------------------------------------------#

load_dotenv()
CMODServer=os.getenv('CMODServer')
CMODAuthorization=os.getenv('CMODAuthorization')
class CMODClient: 
    def __init__ (self, CMODServer, CMODAuthorization):
        self.CMODServer=CMODServer
        self.CMODAuthorization=CMODAuthorization

    def CMODPing (self):
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        url="/cmod-rest/v1/ping"
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        if res.status == 200:
            data=res.read()
            print(data.decode("utf-8"))
        return res.status
    
    def CMODFolderList (self):
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        url="/cmod-rest/v1/folders"
        conn.request("GET",url , headers=headers)
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            folders=json.loads(data)
            folderlist=folders.get("folders")
        else:
            print('Error:', res.status, res.reason)
        return folderlist
    
    def CMODFolderDetails (self, folder):
        folder=urllib.parse.quote(folder) # to convert blanks in folder names to %20 (for URL)
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        url="/cmod-rest/v1/folders/"+folder
        conn.request("GET",url , headers=headers)
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            criteria=json.loads(data)
            folderdetails=criteria.get("criteria")
        else:
            print('Error:', res.status, res.reason)
        return folderdetails
    
    def CMODAppGroupList (self):
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        url="/cmod-rest/v1/appgroup"
        conn.request("GET",url , headers=headers)
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            appgroups=json.loads(data)
            appgrouplist=appgroups.get("appGroups")
        else:
            print('Error:', res.status, res.reason)
        return appgrouplist

    def CMODAppGroupFields (self, appGroup):
        appGroup=urllib.parse.quote(appGroup) # to convert blanks in folder names to %20 (for URL)
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        url="/cmod-rest/v1/appgroup/"+appGroup
        conn.request("GET",url , headers=headers)
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            appList=json.loads(data)
            appGroupdetails=appList.get("fieldList")
        else:
            print('Error:', res.status, res.reason)
        return appGroupdetails
    
    def CMODTransform (self):
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        url="/cmod-rest/v1/transform"
        conn.request("GET",url , headers=headers)
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            transforms=json.loads(data)
        else:
            print('Error:', res.status, res.reason)
        return transforms
    
    def CMODSearch (self, folder, criteria):
        hits=[]
        folder=urllib.parse.quote(folder) # to convert blanks in folder names to %20 (for URL)
        payload = {"criteria": criteria }
        url="/cmod-rest/v1/hits/"+folder
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        conn.request("POST",url ,json.dumps(payload), headers=headers)
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            hits=json.loads(data)
        else:
            print('Error:', res.status, res.reason)
        return hits
    
    def CMODAddDocument (self, filename, filecontent, appGroup, appName, fieldlist):
        encoded=base64.b64encode(filecontent) # Creates a byte string
        encoded=encoded.decode() # Convert from byte string to regular string 
        # Creating the payload is tricky and requires a correct field list!
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        payload = {"applicationGroupName":appGroup,"applicationName":appName,"status":"","documents":[{"fileName":filename,"pages":1,"status":"","fieldList":fieldlist,"base64bytes":""+encoded}]}
        url="/cmod-rest/v1/document/"
        conn.request("POST", url,json.dumps(payload), headers=headers)
        res = conn.getresponse()
        return res.status

    def CMODRetrieveDocument (self,docID, folder): 
        folder=urllib.parse.quote(folder) # to convert blanks in folder names to %20 (for URL)
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        url="/cmod-rest/v1/hits/"+folder+"/"+docID
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        if res.status == 200:
            filecontent = res.read()
        else:
            print('Error:', res.status, res.reason)
        return filecontent

    def CMODRetrieveConvertDocument (self,docID, folder,conversion): 
        folder=urllib.parse.quote(folder) # to convert blanks in folder names to %20 (for URL)
        conn = http.client.HTTPConnection(self.CMODServer)
        headers = { 'Authorization': self.CMODAuthorization,'Content-Type': "application/json"}
        url="/cmod-rest/v1/hits/"+folder+"/"+docID+"?viewerName="+conversion
        print(url)
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        if res.status == 200:
            filecontent = res.read()
        else:
            print('Error:', res.status, res.reason)
        return filecontent
     

