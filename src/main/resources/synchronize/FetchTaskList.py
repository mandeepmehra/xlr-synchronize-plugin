#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
if phaseName is None:
   print "Err: Phase name not provided"
   sys.exit(1)

release = getCurrentRelease()
phases  = phaseApi.searchPhasesByTitle(phaseName, release.id)
tasklst = []
tasks   = phases[0].tasks
for task in tasks:
      tasklst.append(task.title)


tasklist = ' ,'.join(tasklst)
print tasklist
