import sys, os
import java
import time
sys.path.append('/WebSphere/ZS0X/scriptLibraries/utilities/V70')
import AdminUtilities
scriptDir = os.environ['mws_scriptUtils_dir']
sys.path.append(scriptDir)
import WAuJ_utilities as WAuJ

AdminApp = sys._getframe(1).f_locals['AdminApp']
AdminControl = sys._getframe(1).f_locals['AdminControl']
AdminTask = sys._getframe(1).f_locals['AdminTask']
AdminConfig = sys._getframe(1).f_locals['AdminConfig']

def logTime(scriptName):
    now = time.time()
    milliseconds = '%03d' % int((now - int(now)) * 1000)
    stampit = time.strftime('%d-%m-%Y %H:%M:%S') + '.' + milliseconds + ' ' + scriptName + '  INFO  '
    return stampit

def configureCookieForServer(nodeName, serverName, cookieName, domain, maxAge, secure,  otherAttrList=[], failonerror=AdminUtilities._BLANK_):
    if(failonerror==AdminUtilities._BLANK_):
        failonerror=AdminUtilities._FAIL_ON_ERROR_
    #endIf
    msgPrefix = "configureCookieForServer("+`nodeName`+", "+`serverName`+", "+`cookieName`+", "+`domain`+", "+`maxAge`+", "+`secure`+", "+`failonerror`+"): "

    try:
        if (len(otherAttrList) == 0):
            print " cookie.configureCookieForServer(\""+nodeName+"\", \""+serverName+"\", \""+cookieName+"\", \""+domain+"\", \""+`maxAge`+"\", \""+secure+"\")"
        else:
            print " cookie.configureCookieForServer(\""+nodeName+"\", \""+serverName+"\", \""+cookieName+"\", \""+domain+"\", \""+`maxAge`+"\", \""+secure+"\", %s)" % (otherAttrList)
        print " "
        print " "

        # checking required parameters
        # WASL6041E=WASL6041E: Invalid parameter value: {0}:{1}
        if (len(nodeName) == 0):
            raise AttributeError(AdminUtilities._formatNLS(resourceBundle, "WASL6041E", ["nodeName", nodeName]))

        if (len(serverName) == 0):
            raise AttributeError(AdminUtilities._formatNLS(resourceBundle, "WASL6041E", ["serverName", serverName]))

        if (len(cookieName) == 0):
            raise AttributeError(AdminUtilities._formatNLS(resourceBundle, "WASL6041E", ["cookieName", cookieName]))

        # if (len(domain) == 0):
        #     raise AttributeError(AdminUtilities._formatNLS(resourceBundle, "WASL6041E", ["domain", domain]))

        if (len(secure) == 0):
            raise AttributeError(AdminUtilities._formatNLS(resourceBundle, "WASL6041E", ["secure", secure]))

        # checking if the parameter value exists
        # WASL6040E=WASL6040E: The specified argument {0}:{1} does not exist.
        nodeExist = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeExist) == 0):
            raise AttributeError(AdminUtilities._formatNLS(resourceBundle, "WASL6040E", ["nodeName", nodeName]))

        serverExist = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (len(serverExist) == 0):
            raise AttributeError(AdminUtilities._formatNLS(resourceBundle, "WASL6040E", ["serverName", serverName]))

        # contruct required attributes
        requiredAttrs = [["name", cookieName], ["domain", domain], ["maximumAge", maxAge], ["secure", secure]]
        finalAttrs = requiredAttrs+otherAttrList

        server = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        sms = AdminConfig.list("SessionManager", server)
        smList = AdminUtilities.convertToList(sms)

        # check if there is more then one exists
        # WASL6045E=WASL6045E: Multiple {0} found in your configuration.
        sm = AdminUtilities._BLANK_
        cookie = AdminUtilities._BLANK_
        if (len(smList) > 1):
            raise AttributeError(AdminUtilities._formatNLS(resourceBundle, "WASL6045E", ["SessionManager"]))
        if (len(smList) == 1):
            sm = smList[0]

            # get Cookie
            cookies = AdminConfig.list("Cookie", sm)
            cookieList = AdminUtilities.convertToList(cookies)
            if (len(cookieList) == 0):
                cookie = AdminConfig.create("Cookie", sm, finalAttrs)
            else:
                cookieFound = "false"
                for c in cookieList:
                    cName = AdminConfig.showAttribute(c, "name")
                    if (cName == cookieName):
                        cookie = c
                        AdminConfig.modify(c, finalAttrs)
                        cookieFound = "true"
                        break

                if (cookieFound == "false"):
                    cookie = AdminConfig.create("Cookie", sm, finalAttrs)

        if (len(smList) == 0):
            sm = AdminConfig.create("SessionManager", server, [])
            cookie =AdminConfig.create("Cookie", sm, finalAttrs)

        if (AdminUtilities._AUTOSAVE_ == "true"):
            AdminConfig.save()

        print AdminConfig.showall(cookie)
        return 1
    except:
        typ, val, tb = sys.exc_info()
        if(typ==SystemExit):  raise SystemExit,`val`
        if (failonerror != AdminUtilities._TRUE_):
            print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
            val = "%s %s" % (sys.exc_type, sys.exc_value)
            raise "ScriptLibraryException: ", `val`
            return -1
        else:
            return AdminUtilities.fail(msgPrefix+AdminUtilities.getExceptionText(typ, val, tb), failonerror)
        #endIf
    #endTry
    AdminUtilities.infoNotice(AdminUtilities._OK_+msgPrefix)
#endDef

def syncNodes():
    # sync the nodes
    print
    print logTime('syncNodes           ')+ banner(' Node Sync output begins', ch='*')
    raw = AdminControl.queryNames( 'type=NodeSync,*' )
    if len(raw) > 5:  #arbitrary minimum string length
        ns = raw.splitlines()
        for x in ns:
            print
            print x
            AdminControl.invoke( x, 'sync' )
            print AdminControl.invoke( x, 'getResult' )
    print logTime('syncNodes           ')+ banner(' Node Sync output ends', ch='*')

def appClassloader(loaderMode, applicationName):
    print logTime('appClassloader      ')+ "Changing classloader mode to " + loaderMode + " for app " + applicationName
    deployment=AdminConfig.getid("/Deployment:" + applicationName + "/")
    deployedObject=AdminConfig.showAttribute(deployment, 'deployedObject')
    classloader=AdminConfig.showAttribute(deployedObject, 'classloader')
    attrs=[["mode", loaderMode]]
    AdminConfig.modify(classloader, attrs)

def warClassloader(loaderMode, clusterName, applicationName):
    clusterID = AdminConfig.getid("/ServerCluster:"+ clusterName + "/")
    deployment=AdminConfig.getid("/Deployment:" + applicationName + "/")
    deployedObject=AdminConfig.showAttribute(deployment, 'deployedObject')
    modules=AdminConfig.showAttribute(deployedObject, 'modules')
    moduleList=modules[1:-1].split(" ")
    for warModule in moduleList:
        uri=AdminConfig.showAttribute(warModule, 'uri')
        print logTime('warClassloader      ')+ "Changing classloader mode to " + loaderMode + " for war module " + uri
        warModuleClassLoader=AdminConfig.showAttribute(warModule, 'classloader')
        attrs=[["mode", loaderMode]]
        AdminConfig.modify(warModuleClassLoader, attrs)
        AdminConfig.save()
        print logTime('warClassloader      ')+ '*** ' + appName + '.war Classloader update saved ***'
        print

def loadInputFile(inputFile):
    stripedInput = []
    deployInput = open(inputFile,'r')
    for line in deployInput.readlines():
        # drop any comments
        if line.startswith("#"):
            pass
        else:
            fields = line.strip().split(";")
            # skip any blank lines
            if not fields[0]:
                pass
            # Process whats left
            else:
                print
                stripedInput.append(line.strip())
    print logTime('loadInputFile       ')+ ' Imported deployment details from: %s' % inputFile
    deployInput.close()
    return stripedInput

def uninstallApplication(appName):
    print('')
    print('')
    print(logTime('uninstallApplication') + " Application " + appName + " will be uninstalled")
    AdminApp.uninstall(appName)

def activateEdition(appName, edition):
    print
    print
    print logTime('activateEdition     ') + banner('Application Activation in progress!!!', ch='-')
    actEdition = AdminTask.activateEdition (['-appName', appName, '-edition', edition])
    AdminConfig.save()
    syncNodes()

def deactivateEdition(appName, clusterName, appVersion):
    print
    print
    editionsAvailable = AdminTask.listEditions (['-appName', appName ]).splitlines()
    deactEdition = ''
    print logTime('deactivateEdition   ') + banner('Application Edition Deactivation in progress', ch='-')
    for i in editionsAvailable:
        if not (i == appVersion):
            editionStatus = AdminTask.getEditionState (['-appName', appName, '-edition', i])
            print
            print logTime('deactivateEdition   ') + " Application " + appName + " Edition " + i + " was found to be " + editionStatus + "."
            # Checking if application is running
            appStatus = AdminControl.queryNames("type=Application,name="+appName+",*")
            if not (len(appStatus) == 0):
                print
                print logTime('deactivateEdition   ') + " Application " + appName + " was found to be running."
                print logTime('deactivateEdition   ') + " Deactivation step can not be performed for a running application."
                print
                print logTime('deactivateEdition   ') + " Stopping application " + appName
                stopApplication(appName,clusterName)
                print
                print logTime('deactivateEdition   ') + " " + appName + "  stopped. Proceeding with deactivation"
                print
                deactEdition = AdminTask.deactivateEdition (['-appName', appName, '-edition', i])
                AdminConfig.save()
                syncNodes()
            else:
                print logTime('deactivateEdition   ') + " " + appName + "  stopped!!! Proceeding with deactivation"
                print
                deactEdition = AdminTask.deactivateEdition (['-appName', appName, '-edition', i])
                AdminConfig.save()
                syncNodes()
            if (deactEdition == 'true'):
                print
                print logTime('deactivateEdition   ') + " Application " + appName + " Edition " + i + " deactivated now!!       "
                print
            else:
                print logTime('deactivateEdition ') + banner("Application " + appName + " Edition " + i + " couldn't be deactivated!!", ch='-')
                print logTime('deactivateEdition   ') + "     Its possible that edition is already deactiviated."
                print logTime('deactivateEdition   ') + "     Please check the application status in Admin Console.              "
                print


def stopApplication(appName,clusterName):
    print
    print
    servers = AdminConfig.getid("/ServerCluster:" + clusterName + "/ClusterMember:/")
    servers = commonFunctions.convertToList(servers)
    for server in servers:
        serverName = AdminConfig.showAttribute(server, "memberName")
        nodeName = AdminConfig.showAttribute(server, "nodeName")
        appMgr = AdminControl.queryNames("node=" + nodeName + ",process=" + serverName + ",type=ApplicationManager,*")
        appMgr = AdminUtilities.convertToList(appMgr)
        for mgr in appMgr:
            print logTime('stopApplication     ') + " Stopping application " + appName + " on server " + serverName
            checkAppOnNode = AdminControl.queryNames("type=Application,node=" + nodeName + ",name=" + appName + ",*")
            if not (len(checkAppOnNode) == 0):
                AdminControl.invoke(mgr, "stopApplication", appName)
            else:
                print logTime('stopApplication     ') + " Application " + appName + " not running on server " + serverName

def banner(text, ch='=', length=78):
    if text is None:
        return ch * length
    elif len(text) + 2 + len(ch)*2 > length:
        # Not enough space for even one line char (plus space) around text.
        return text
    else:
        remain = length - (len(text) + 2)
        prefix_len = remain / 2
        suffix_len = remain - prefix_len
        if len(ch) == 1:
            prefix = ch * prefix_len
            suffix = ch * suffix_len
        else:
            prefix = ch * (prefix_len/len(ch)) + ch[:prefix_len%len(ch)]
            suffix = ch * (suffix_len/len(ch)) + ch[:suffix_len%len(ch)]
        return prefix + ' ' + text + ' ' + suffix

def elapsedTime(stamp):
    global start
    global end
    if stamp.lower() == "start":
        start = time.time()
    elif stamp.lower() == "end":
        end = time.time()
        elapsed_time = end-start
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print logTime('elpasedTime:        ') + elapsed_time
        elapseText = banner('elpasedTime: ' + elapsed_time, ch='*')
        print logTime('deployMAS           ') + elapseText
    else:
        print time.time()


if __name__ == '__main__':
    print("This script should only be imported")
