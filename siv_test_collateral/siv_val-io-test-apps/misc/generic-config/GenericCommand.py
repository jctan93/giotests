"""
GenericCommand.py
Version 3.0
<Date>      <Owner>      <Version>     <Changes>
2009        Raniero         1.0        Initial release
8/2/2011      CKH           2.0        Added XTP-no wait logging Execute (Timeexecute), Pingalive, Pingdead, Timetrace, Timedelete, timemasterdelete 
18/3/2011     CKH           3.0        Added timefiletransfers, timefilescript, timefiletrace, timefiledelete, timefolderflush, auto startup-setup, dejavunow, teststart
                                       Transformed GenericCommand towards Ajyl-independent architecture [Target: stand-alone single script module]
                                       
"""
import xmlrpclib
from xml.dom import minidom
import socket
import time
import hashlib
import os

class GenericCommand():
    
    def __init__(self):
        #self.ajyl = anobject
        self.host = ""
        self.port = ""
        self.ipAddress = ""
        self.prasename = ""
        self.temploctime = ""
        self.tempid = ""
        self.start_time = time.time()
        self.timeexecute_locker = time.time()
        self.timehost = ""
        self.timeexecute_interval = 3

#########################################################################################################################################
# This is to program GenericCommand parameters to enable the following functions protion.                                               #
# In this case, it's designed to specifically suits XTP's XMS.                                                                          #
#                                                                                                                                       #
# In case of engine migration, modify the "login", "Pingalive" and "Pingdead" only on how to obtain the IP, port number, address etc.   #
# The logics will pre-program accordingly to all the variable above, automatically.                                                     #
#                                                                                                                                       #
# Among the important parameters are:                                                                                                   #
# "self.host", "self.port"                                                                                                              #
# Please refers to GenericCommand Architecture Documentation for Modifications                                                          #
#########################################################################################################################################

#########################################################################################################################################
#    def Generic_Datafinder(self, moduleName, hostno, datatype):
#        "This is XTP's XMS Database Management System."
#        #If there's engine migration, you should change this part to suits the new engine's database management system.        
#        if datatype == 'port':
#            ret = str(self.ajyl.findPortOfModule(moduleName, hostno))
#        elif datatype == 'host':
#            ret = str(self.ajyl.findAddressOfModule(moduleName, hostno))
#        return ret
########################################################################################################################################

    def login(self, ip, hostport="2300"):
        "Changing GenericCommand to focus on a GCVS3 via its IP and Port"
        #Setting up GenericCommand to focus on that GCVS3
        if self.pingalive(ip, hostport, 120) == False:
            return "Ping Failed. Host is not connectable. Verify."        
        if (ip is not None):
            self.ip = ip
        else:
            return "Login Failed: Invalid IP Number."
        self.host = str(ip)
        self.port = str(hostport)
        self.ipAddress = "http://" + self.host + ":" + self.port
        self.server = xmlrpclib.ServerProxy(self.ipAddress)
                
        #Logon to host
        #----------------------------------
        #NOTE: You don't have to edit here
        self.printOnConsole("Connection to Remote Host " + self.ipAddress + "...")
        self.server = xmlrpclib.ServerProxy(self.ipAddress)
        try:
            ret = self.server.test()
            if ret == "XML-RPC connection is OK":
                self.printOnConsole("Login successful")
            else:
                self.printOnConsole("Login failed!")
                raise Exception("Login into " + self.ipAddress + " failed!")
            
        except:
                self.printOnConsole("Login failed!")
                raise Exception("Login into " + self.ipAddress + " failed!")
    
    def pingalive(self, host_ip, host_port="2300", timeout=1000):
        "To ping GCSV3 alive from dead from this GC."
        try:
            pinghost = str(host_ip)         #Change only this part since XTP XMS is using host number.
            pingport = str(host_port)         #Change only this part since XTP XMS is using host number.
            self.printOnConsole("Ping ALIVE now: %s %s " % (str(pinghost),str(pingport)))
            
            pingresult = 5
            i = 0
            while 1:
                s = socket.socket()
                s.settimeout (0.25)
                try:
                    s.connect ((str(pinghost), int(pingport)))
                except socket.error:                                
                    i += 1
                    time.sleep(1)
                else:
                    s.close()
                    pingresult = 1
                    break
                
                if i == int(timeout):
                    pingresult = 0
                    break
        
            if pingresult == 1:
                self.printOnConsole("%s %s connection is alive." % (str(pinghost),str(pingport)))
                return True
            if pingresult == 0:
                self.printOnConsole("%s %s ping alive timeout" % (str(pinghost),str(pingport)))
                return False
        except:
            return False

    def pingdead(self, hostno=0, timeout=1000):
        "To ping GCSV3 dead from alive from this GC"
        try:
            pinghost = self.Generic_Datafinder("GenericCommand", hostno, 'host')     #Change only this part since XTP XMS is using host number.
            pingport = self.Generic_Datafinder("GenericCommand", hostno, 'port')     #Change only this part since XTP XMS is using host number.
            self.printOnConsole("Ping DEAD now: %s %s " % (str(pinghost),str(pingport)))
            pingresult = 5
            i = 0
            while 1:
                s = socket.socket()
                s.settimeout (0.25)
                try:
                    s.connect ((str(pinghost), int(pingport)))
                except socket.error:                
                    pingresult = 1
                    break
                else:
                    s.close()
                    i += 1
                    time.sleep(1)
                if i == int(timeout):
                    pingresult = 0
                    break
        
            if pingresult == 1:
                self.printOnConsole("%s %s connection is dead." % (str(pinghost),str(pingport)))
                return True
            if pingresult == 0:
                self.printOnConsole("%s %s ping dead timeout" % (str(pinghost),str(pingport)))
                return False
        except:
            return False



#########################################################################################################
# GCSV3 DEVELOPMENT Since Jan 2011                                                                      #
#                                                                                                       #
# If any execution enginer migration occurs and the modifications earlier is made correctly,            #
# the following functions will not be affected as they're solely independent from other scripts.        #
#########################################################################################################

    def execute(self, command, timeout=None):
        "Sends the 'command' command to the remote server. Returns the data fetched on the remote server after command execution completion" 
        socket.setdefaulttimeout(timeout)  
        ret = self.server.execute(command)
#        self.printOnConsole("Command sent: " + command)
#        self.printOnConsole("Received: " + ret)
        socket.setdefaulttimeout(None)       
        return ret

    def teststart(self):
        "Flush the GCSV3 Scripts folder for a new test run"
        self.printOnConsole("Flushing GCSV3 Folder for a new test-run")
        ret = self.server.teststart()
        return ret

    def timeexecute(self, command, flag=1):
        "Sends 'command' to remote server without waiting returns and do next work. Returns logname for timereport or delete uses."
        while 1:
            timetrack = time.time()
            
            if timetrack - self.timeexecute_locker < self.timeexecute_interval and self.timeexecute_locker - self.start_time > .000001 and self.timehost == self.host:
#                self.printOnConsole("Timeexecute busy...re-comply in %s seconds" % str(self.timeexecute_interval))
                time.sleep(3)
                
            else:
                self.timeexecute_locker = time.time()
                self.timehost = self.host
                self.temploctime = str(time.asctime(time.localtime(time.time())))
                self.temploctime = self.temploctime.replace(" ", "_")
                self.temploctime = self.temploctime.replace(":", "_")
                self.server.timeexecute(command, self.temploctime, flag)
#                self.printOnConsole("TimeCommand sent: " + command)
                socket.setdefaulttimeout(None)
                return self.temploctime
                break

    def timereport(self, logname):
        "Sends logname to reterive its log report. Return all report contents."
        ret = self.server.timereport(str(logname))
        self.printOnConsole("""TIME-REPORTING:.....
-------------------------------------------------------------------------------""")
        for i in ret:
            self.printOnConsole(i)
        self.printOnConsole("""REPORT COMPLETED.
-------------------------------------------------------------------------------""")
        socket.setdefaulttimeout(None)       
        return ret

    def timetrace(self, logname, keywords, flag=1):
        "To trace a certain keywords in the report"
        check_result=[]
        try:
            ret = self.server.timereport(str(logname))
            if flag==2:
                self.printOnConsole("Finding corresponding keyword: %s" % str(keywords))
            for i in ret:
                parsewords = i[i.find(str(keywords)):i.find(str(keywords))+len(keywords)]
                if str(parsewords) == str(keywords):
                    check_result.append(True)
                else:
                    check_result.append(False)
            if True in check_result:
                return True
            else:
                return False                
            socket.setdefaulttimeout(None)       
        except:
                return False

    def timedelete(self, logname):
        """To Delete a particular log file under "logname" """
        ret = self.server.timedelete(str(logname))
        self.printOnConsole("Command sent: deleting %s.txt log" % str(logname))
        self.printOnConsole("Received: " + ret)

    def timemasterdeletelog(self):
        """To Empty Log Folder"""
        ret = self.server.timemasterdeletealllog()
        self.printOnConsole("Command sent: deleting all log Files")
        self.printOnConsole("Received: " + ret)          
    
    def timefiletrace(self, location):
        """To trace a file location and permission"""
#        self.printOnConsole("File tracing: %s" % str(location))
        ret = self.server.timefiletrace(str(location))
        return ret

    def timefilescript(self, contents, dir_path, filename, extension=".No_ext", permit=777):
        """to script a file with or w/o designated extension"""
        self.printOnConsole("File scripting: %s/%s%s" % (str(dir_path),str(filename),str(extension)))
        ret = self.server.timefilescript(str(contents), str(dir_path), str(filename), str(extension), int(permit))
        return ret

    def timefiledelete(self, file_location):
        """to delete a file in the DUT machine"""
        self.printOnConsole("File deleting: %s" % (str(file_location)))
        ret = self.server.timedeletefile(str(file_location))
        return ret

    def timefolderflush(self, folder_path):
        """to flush a particular directory to clean and tidy (nothing inside)"""
        self.printOnConsole("Folder Flushing: %s" % str(folder_path))                         
        ret = self.server.timefolderflush(str(folder_path))
        return ret

    def timefiletransfer(self, filename_w_location, desination_w_name, deg_port=8206, own_port=8206, buffsize=81920, ownbuffsize=81920):
        """to transfer file from XTP Location to DUT Location"""
        self.printOnConsole("Initializing file transfers sequence...")

        #1) Checking File existance
        ret = os.access(str(filename_w_location), os.F_OK)
        self.printOnConsole("Checking File Existances...")        
        if ret == False:
            self.printOnConsole("Transfers FAILED: Selected File Not Exists")
            return "Transfers FAILED: Selected File Not Exists"
        else:
            self.printOnConsole("[  OK  ]")

        #2) Checking File Health
        ret = os.path.getsize(str(filename_w_location))
        self.printOnConsole("Checking File Health...")        
        if ret == False:
            self.printOnConsole("Transfers FAILED: File is Faulty and Not Transferable.")
            return "Transfers FAILED: File is Faulty and Not Transferable."
        else:
            self.printOnConsole("[  OK  ]")

        #3) Checking Destination Directory:
        self.printOnConsole("Checking Destination Directory...")
        s = str(desination_w_name[:desination_w_name.rfind("/")])
        s2 = str(desination_w_name[:desination_w_name.rfind("\\")])
        ret = self.server.timefiletrace(s)
        ret2 = self.server.timefiletrace(s2)
        if (ret == "File Trace Error" or ret == "target not exists") and (ret2 == "File Trace Error" or ret2 == "target not exists"):
            self.printOnConsole("Transfers FAILED: Destination directory is not available.")
            return "Transfers FAILED: Destination directory is not available."
        else:
            self.printOnConsole("[  OK  ]")
        del ret2

        #4) Gathering logname, filesize, checksum
        self.printOnConsole("Gathering logname, filesize, checksum...")
        self.temploctime = str(time.asctime(time.localtime(time.time())))
        self.temploctime = self.temploctime.replace(" ", "_")
        self.temploctime = self.temploctime.replace(":", "_")
        self.printOnConsole("logname: [  OK  ]")
        filebodysize = str(os.path.getsize(str(filename_w_location)))
        self.printOnConsole("filesize: [  OK  ]")
        md5data = hashlib.md5()
        try:
            s = open(str(filename_w_location), 'rb')
            while True:
                data = s.read(10240)
                if len(data) == 0:
                    break
                md5data.update(data)
            s.close()
        except:
                s.close()
                self.printOnConsole("Transfers FAILED: Checksum error. File may not be readable.")
                return "Transfers FAILED: Checksum error. File may not be readable."
        else:
                s2 = md5data.hexdigest()
                del md5data
                self.printOnConsole("checksum: [  OK  ]")
        del s
        
        #5) Checking own-port Availability
        self.printOnConsole("Checking own-port availability...")
        s = socket.socket()
        s.settimeout (0.25)
        try:
            s.connect (('127.0.0.1', int(own_port)))
        except socket.error:
            try:
                s.close()
            except:
                pass
            self.printOnConsole("[  OK  ]")
            del s
            pass
        else:
            try:
                s.close()
            except:
                pass
            del s
            self.printOnConsole("Transfers FAILED: Current Attempt Own Port is Not Available.")
            return "Transfers FAILED: Current Attempt Own-Port is Not Available."
        """
        #6) Checking Destination Port Availability
        self.printOnConsole("Checking Destination-port availability...")        
        pings = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pings.settimeout (0.25)
        try:
            pings.connect ((str(self.host), int(deg_port)))
        except socket.error:
            try:
                pings.close()
            except:
                pass
            self.printOnConsole("[  OK  ]")
            del pings
            pass
        else:
            try:
                pings.close()
            except:
                pass
            del pings
            self.printOnConsole("Transfers FAILED: Current Attempt Destination Port is not available.")
            return "Transfers FAILED: Current Attempt Destination Port is not available."
"""
        #6) Activating Receiver Socket
        self.printOnConsole("Activating Receiver Socket Port...")
        self.server.timefiletransfer(str(desination_w_name), int(deg_port), int(buffsize), long(filebodysize), str(s2), str(self.temploctime))
        del s2
        self.printOnConsole("[  OK  ]")
        
        #7) Sensing Receiver Readiness
        self.printOnConsole("Sensing Receiver Socket Readiness...")        
        limit = 120
        count = 0
        while 1:
            retx = self.timetrace(str(self.temploctime), "Port is Not Available")
            ret = self.timetrace(str(self.temploctime), "Socket Client Begin to Listen")
            if retx == True:
                self.server.fileTx_script_kill()
                del retx
                self.printOnConsole("Transfers FAILED: Port is not available.")
                return "Transfers FAILED: Port is not available."
                break
            
            if ret == True:
                self.printOnConsole("[  OK  ]")
                break
            
            elif ret == False:
                count +=1
                time.sleep(1)
                
            if count >= limit:
                self.server.fileTx_script_kill()
                self.printOnConsole("Transfers FAILED: Waiting Connection Timeout")
                return "Transfers FAILED: Waiting Connection Timeout"
                break
        
        #8) Opening Transmitter Port
        self.printOnConsole("Opening Transmitter Socket...")
        buffersizeo = ownbuffsize       
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((str(self.host), int(deg_port)))
            f = open(str(filename_w_location), 'rb')        
            self.printOnConsole("[  OK  ]")
            self.printOnConsole("Transferring : Begin \n------------------------------->")
            densi = 10
            while True:
                file1 = f.read(102400)
                s.sendall(file1)
                percent =(float(buffersizeo)*100)/float(filebodysize)
                if int(percent) == int(densi):
                    print "===",
                    densi += 10
                buffersizeo=buffersizeo+ownbuffsize
                if not file1:
                    print("|>Completed\n------------------------------->")
                    self.printOnConsole("Transferring : Completed")
                    break
            f.close()
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            self.server.TxscriptPID_reset()
            del s, f, densi, buffersizeo, file1, percent
        except Exception, e:
            print e
            try:
                f.close()
            except:
                pass
            try:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                del s, f, densi, buffersizeo, file1, percent
            except:
                pass
            self.server.fileTx_script_kill()
            self.printOnConsole("Transfers FAILED: Transferring Link Broken.")
            return "Transfers FAILED: Transferring Link Broken."

        #9) Check File Received Status
        self.printOnConsole("Checking File Received Status...")       
        limit = 120
        count = 0
        while 1:
            ret = self.timetrace(str(self.temploctime), "File Recieved Successfully")
            ret2 = self.timetrace(str(self.temploctime), "File Recieved Failed")
            if ret == True:
                self.printOnConsole("[  OK  ]")
                self.printOnConsole("File Transfers Successfully.")
                return "File Transfers Successfully."
                break
            elif ret2 == True:
                self.printOnConsole("[  FAILED  ]")
                return "Transfers FAILED: File Received Faulty. Verify Log."
                break
            else:
                count +=1
                time.sleep(1)
            if count >= limit:
                return "Transfers FAILED: File Received Error. Verify Log."
                break            

    def Dejavunow(self):
        "To completely erase GCSV3 Trances once and for all."
        ret = self.server.self_destruct()
        return ret

    def printOnConsole(self, info):
        "Prints the info on the project console"
        print time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime()) + " - " + info

#######################################################################################


#For Debugging Purpose        
if __name__ == "__main__":
    print "GenericCommand module imported"
