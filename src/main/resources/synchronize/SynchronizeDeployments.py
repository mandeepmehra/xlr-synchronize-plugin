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
   xlrAPIUrl = xlrUrl + '/api/v1/releases?depth=2'
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
def findMasterPhase( masterRelease, phaseName ):
   for phase in masterRelease["phases"]:
      if phaseName == phase["title"]:
         return phase
   # End for
# End def

########################################################################
def findMasterTask( masterRelease, phaseName, taskName ):
   for phase in masterRelease["phases"]:
      if phaseName == phase["title"]:
         for task in phase["tasks"]:
             if taskName == task["title"] :
                 return task
             # End if
         # End for
       # End if
   # End for
# End def

########################################################################
def addTagToRelease( release, tagName ):
   print "Adding %s as a tag" % (tagName)
   tags = release.tags
   tagExists = False
   for tag in tags:
       if tag == tagName:
          tagExists = True
          print "Found tag (%s) in Release (%s)" % ( tagName, release.id )
   # End for
   if not tagExists:
      tags.append( tagName )
      release.tags = tags
      releaseApi.updateRelease( release )
      print "Add tag (%s) to Release (%s)" % ( tagName, release.id )
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

if masterTargetPhase is None or masterTargetPhase == '' :
  print "Err: MasterTargetPhase not provided\n"
  sys.exit(1)

if subTargetPhase is None or subTargetPhase == '' :
  print "Err: SubTargetPhase not provided\n"
  sys.exit(1)

if HipChatURL is None or HipChatURL == '' :
  print "Err: HipChatnot provided\n"
  sys.exit(1)

# Find the sysId for the change task
masterRelease = findReleaseWithTag( xlrUrl, credentials, releaseID )
print "Master Release ID = %s" % ( masterRelease["id"] )
masterPhase   = findMasterPhase( masterRelease, masterTargetPhase )
print "Master Phase ID = %s" % ( masterPhase["id"] )
#-----------------------------------------------------------------------
#  Create Webhook Json Webhook in Master Release
task = taskApi.newTask( "webhook.JsonWebhook" )
taskTitle = "Start Deployment Task (%s)" % ( release.title )
task.title = taskTitle
task.pythonScript.URL = HipChatURL
task.pythonScript.method = "POST"
task.pythonScript.body = '{ "color":"%s", "message":"%s: %s", "notify":false, "message_format":"text" }' % (HipChatStartColor, release.title, HipChatStartMessage)
mTask = taskApi.addTask( masterPhase["id"], task )


#-----------------------------------------------------------------------
# Create GATE Task in Sub Release that depends on Master Task
thePhase = getCurrentPhase()
task = taskApi.newTask( "xlrelease.GateTask" )
task.title = "Wait for %s (%s) To Start" % ( masterRelease["title"], releaseID )
sTask = taskApi.addTask( thePhase.id, task )
taskApi.addDependency( sTask.id, mTask.id )

#-----------------------------------------------------------------------
# Create GATE Task in Master Release that depends on Sub Task
if subTargetPhase == "CURRENT" :
     thePhase = getCurrentPhase()
else:
     phaseList = phaseApi.searchPhasesByTitle( subTargetPhase, release.id )
     print phaseList
     thePhase = phaseList[0]
# End if
#-----------------------------------------------------------------------
#  Create Webhook Json Webhook in Sub Release
task = taskApi.newTask( "webhook.JsonWebhook" )
taskTitle = "%s Deployment Complete" % ( release.title )
task.title = taskTitle
task.pythonScript.URL = HipChatURL
task.pythonScript.method = "POST"
task.pythonScript.body = '{ "color":"%s", "message":"%s: %s", "notify":false, "message_format":"text" }' % (HipChatEndColor, release.title, HipChatEndMessage)
sTask = taskApi.addTask( thePhase.id, task )

#-----------------------------------------------------------------------
# Create GATE Task in Master Release that depends on sub  Task
task = taskApi.newTask( "xlrelease.GateTask" )
task.title = "Wait for %s To Finish" % ( release.title )
mTask = taskApi.addTask( masterPhase["id"], task )
taskApi.addDependency( mTask.id, sTask.id )

#-----------------------------------------------------------------------
# Create GATE Task in Sub Release that depends on task in Masterfor GO/NO-GO
#task = taskApi.newTask( "xlrelease.GateTask" )
#task.title = "Wait for Go/No-Go decison by %s" % ( masterRelease["title"] )
#sTask = taskApi.addTask( thePhase.id, task )


sRelease = getCurrentRelease()
mRelease = releaseApi.getRelease( masterRelease["id"] )
tags = sRelease.tags
addTagToRelease( sRelease, releaseID )

