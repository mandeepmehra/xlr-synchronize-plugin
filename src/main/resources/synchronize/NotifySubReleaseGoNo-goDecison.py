#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys, string, time, traceback
import com.xhaus.jyson.JysonCodec as json
from datetime import date
from com.xebialabs.xlrelease.domain import Task
from com.xebialabs.xlrelease.domain.status import TaskStatus
from com.xebialabs.deployit.plugin.api.reflect import Type
from java.text import SimpleDateFormat

xlrUrl = xlrServer['url']
xlrUrl = xlrUrl.rstrip("/")
username = xlrServer['username']
password = xlrServer['password']

credentials = CredentialsFallback(xlrServer, username, password).getCredentials()


########################################################################
def findReleaseWithId( credentials, releaseId ):
   xlrAPIUrl = xlrUrl + '/api/v1/releases/' + releaseId
   request = XLRequest(xlrAPIUrl , 'GET', None, credentials['username'], credentials['password'], 'application/json').send()
   if request.status == 200:
       release = json.loads(request.read())
       return release
   # End if
# End def

########################################################################
def getVariable(variables, varname):
    for variable in variables:
        if variable['key'] == varname:
           return variable
    return None
# End def

########################################################################
########################################################################
##
##                        M A I N
##

if subreleasesmap is None:
   print "Err: SubReleasesMap not provided"
   sys.exit(1)

if decisionmap is None:
   print "Err: DecisionMap not provided"
   sys.exit(1)  

release = getCurrentRelease()

for k,v in subreleasesmap.items():

    if k not in decisionmap :
       continue

    sRelease  = None
    govar     = None
    sRelease  = findReleaseWithId(credentials, v)

    if sRelease == None :
       continue

    variables = sRelease['variables'] 
    govar     = getVariable(variables,'GO')
    
    if govar == None:
       print "Warning: Could not find variable named %s in release %s" % ("GO", sRelease['title'])
       sys.exit(1)


    if decisionmap[k] == "Go" :
       govar['value'] = True
    else :
        govar['value'] = False
    # End if

    print sRelease['title'],'\t', str(govar['value']) + '\n'
   
    # Update the variable in the sub release 
    try :
      xlrAPIUrl = xlrUrl + '/api/v1/releases/' + v + '/variables'
      request = XLRequest(xlrAPIUrl, 'PUT', json.dumps(variables), credentials['username'], credentials['password'], 'application/json').send()
    except:
          print "Err: Could not notify %s" % (sRelease['title'])
          sys.exit(1)
# End for
