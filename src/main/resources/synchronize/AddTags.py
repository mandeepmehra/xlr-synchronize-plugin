release = getCurrentRelease()
tags    = release.tags

for tag in taglist:
   tags.append( tag )

release.tags = tags
releaseApi.updateRelease( release )

