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

xlrAPIUrl = xlrUrl + '/api/v1/releases'


########################################################################
def findReleaseWithTag( xlrUrl, credentials, tagValue ):
   tagValue = "MASTER_%s" % tagValue
   xlrAPIUrl = xlrUrl + '/api/v1/releases'
   request = XLRequest(xlrAPIUrl, 'GET', None, credentials['username'], credentials['password'], 'application/json').send()
   releases = json.loads(request.read())
   if request.status == 200:
      for release in releases:
         for tag in release["tags"]:
            if tag == tagValue and release["status"] != "TEMPLATE":
                return release
            # End if
         # End for
      # End for
   # End if
# End def
########################################################################
########################################################################
##
##                        M A I N
##

# Validate the inout parameters
if releaseID is None:
   print "Error: Release ID not provided"\n
   sys.exit(1)

if deploymentStatusVar is None:
   print "Error: DeploymentStatus Variable Name not provided"\n
   sys.exit(1)


# Find the release and update variables 
masterRelease = findReleaseWithTag( xlrUrl, credentials, releaseID )
variables     = masterRelease["variables"]

# Look for deployment status placeholder
varFound = False
for variable in variables:
    if variable["key"] == deploymentStatusVar :
       varFound = True
       break
    # end if
# end for

if not varFound :
   print "Err: Variable named %s not found in Master Release\n" % (deploymentStatusVar)
   sys.exit(1)

# Get the list and add/update the status
statuses  = variable["value"]
statuses[release.title] = 'Success' if status == True else 'Failed'

# Update the variables in the master release 
xlrAPIUrl = xlrUrl + '/api/v1/releases/' + masterRelease["id"] + '/variables'
request = XLRequest(xlrAPIUrl, 'PUT', json.dumps(variables), credentials['username'], credentials['password'], 'application/json').send()

