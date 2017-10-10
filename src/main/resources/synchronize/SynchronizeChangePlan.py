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
def expandGroup(taskOrGroup):
    if taskOrGroup.type != 'xlrelease.ParallelGroup' and taskOrGroup.type != 'xlrelease.SequentialGroup':
        return [taskOrGroup]
    else:
        tasks = []
        for task in taskOrGroup.tasks:
            tasks.extend(expandGroup(task))
        return tasks
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

# Validate mandatory paramteres

if releaseID is None or releaseID == '' :
  print "Err: Release ID not provided\n"
  sys.exit(1)

if subTargetPhase is None or subTargetPhase == '' :
  print "Err: SubTargetPhase not provided\n"
  sys.exit(1)
  
# Find the sysId for the change task
masterRelease = findReleaseWithTag( xlrUrl, credentials, releaseID )
if masterRelease is None:
   print "Err: Release with tag MASTER_%s not found\n" % (releaseID)
   sys.exit(1)
else:
    print "Master Release ID = %s\n" % ( masterRelease["id"] )

#-----------------------------------------------------------------------
# Update varoables in master release
taskNames   = []
tasks       = []
phases      = phaseApi.searchPhasesByTitle(subTargetPhase, release.id)
variables   = masterRelease["variables"]
for task in phases[0].tasks:
    tasks.extend(expandGroup(task))
#End for

for task in tasks:
    taskNames.append(task.title)
# End for

variable = getVariable(variables,releaseStepsVar)
if variable is not None:
    variable["value"][release.title] = ' \n'.join(taskNames)
else:
     print "Err: Variable named %s not found in Master Relase\n" % (releaseStepsVar)
     sys.exit(1)

# Update the variables in the master release 
xlrAPIUrl = xlrUrl + '/api/v1/releases/' + masterRelease["id"] + '/variables'
request = XLRequest(xlrAPIUrl, 'PUT', json.dumps(variables), credentials['username'], credentials['password'], 'application/json').send()

