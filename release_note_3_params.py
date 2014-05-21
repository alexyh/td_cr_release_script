import sys
import re
import smtplib
import sys,os 
import datetime
import socket
import smtplib

# Import Prism module
from Prism import Prism
from suds.client import Client
from getpass import getuser, getpass
from prism import PrismChangeRequestWebService
from suds.transport.https import WindowsHttpAuthenticated
# Import smtplib for the actual sending function

# Import the email modules we'll need
from email.mime.text import MIMEText

#Logging Options
import logging
logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
#logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)

#test mode
test_mode = 1;

#constant
qualcomm_addr = '@qti.qualcomm.com'

def send_relNote_email(msg,plName,labelName, user):
  
   print msg
 
   if( test_mode == 0):
      recipients = [user, 'tdscdma.sw.int.admin@qualcomm.com', 'tdscdma.sw@qti.qualcomm.com']
   else:
      recipients = [user]

   msg['Subject'] = plName + ": " +  labelName + " Release Note"
   msg['From'] = user 
   msg['To'] = ", ".join(recipients) 

   # Send the message via our own SMTP server, but don't include the
   # envelope header.
   s = smtplib.SMTP('qcmail1.qualcomm.com')
   s.sendmail(user, recipients, msg.as_string())
   s.quit()

def processRequestSummary(summary, label, user, prismClient):

   print "ARIS information:"	
   #initialized Predecessor.
   Predecessor = "None"

   DepList = summary.DependencyList
   Predecessor = summary.Predecessor
   plName = summary.IntegrationUnit.VersionedIuName
   #print plName
   #print DepList

   if(Predecessor):
      print Predecessor
   else:
      Predecessor = "None"
	  
   if(DepList):

      for dependency in DepList.string:
         	   print dependency

   file = open("email.txt", "w")

   currLabel= label 

   file.write("1. Label Name:\n")
   file.write("Current Label: " + currLabel + "\n")
   file.write("Predecessor: " + Predecessor + "\n\n")

   #ws = PrismChangeRequestWebService(username=raw_input("Username: "), password=getpass())
   #print '\n'

   p4user = "jrtan"
   p4ticket = "9C123C4BC0735D33676554081BCAB369"
   p4port = "qctp401:1666"
   #int = "-i ";
   command = "p4 -u " + p4user + " -P " + p4ticket + " -p " + p4port + " jobs "
   #print command +"@" + label 

   # get the command info
   cr_1 = os.popen3(command +"@" + Predecessor)
   cr_1_out = cr_1[1].read().splitlines(1)
   if cr_1[2]: #process errors
      err=cr_1[2].read()
      if err:
	  print err
	  print "Terminating..."
	  sys.exit()

   cr_2 = os.popen3(command +"@" + label)
   cr_2_out = cr_2[1].read().splitlines(1)
   if cr_2[2]: #process errors
       err=cr_2[2].read()
       if err:
	   print err
	   print "Terminating..."
	   sys.exit()

   # diff the two outputs
   import difflib
   differ = difflib.Differ()
   from pprint import pprint
   print "\nDiff with Predecessor:"
   diff = [a for a in list(differ.compare(cr_1_out,cr_2_out)) if a[0]=="+" or a[0]=="?" or a[0]=="-"]
   print ''.join(diff)

   #pirismClient = Prism('http://prism.qualcomm.com:8000/ChangeRequestWebService.svc?wsdl', 'prismauth.txt')
   
   
   file.write("2. CR List: \n")

   #table=['<htm><body><table border="1">']

   #table.append('</table></body></html>')

   for line in diff:
       if "ChangeRequest" in line:
	    CRid = line.split("ChangeRequest")[-1].strip().split(" ")[0]
	    # Get CR Titles
	    try:
	       CR = prismClient.getChangeRequestById(CRid)
	       
	       for SoftwareImageRecordEntity in CR.SoftwareImageRecords:
		       print type(SoftwareImageRecordEntity)     #tuple
                       print type(SoftwareImageRecordEntity[1])  #list
                       print type(SoftwareImageRecordEntity[1][1]) #instance
		       devStatus = SoftwareImageRecordEntity[1][1].IsDevelopmentComplete
		       Assignee = SoftwareImageRecordEntity[1][1].AssigneeUserName
		       print devStatus
		       print Assignee
		       #file.write( line[0] + SoftwareImageRecordEntity['SoftwareImageRecordEntity']  + "\n")
		       #print SoftwareImageRecordEntity
		       #if (SoftwareImageRecordEntity.SoftwareImageName == "MPSS.DI.3.0.c7"):
		          #file.write( line[0] + str(SoftwareImageRecordEntity.IsDevelopmentComplete) + "\n")
		          #file.write( line[0] + str(SoftwareImageRecordEntity.AssigneeUserName) + "\n")
	       #print CR.items()
	       #print CR.SoftwareImageRecords
	       #print CRid + ":" + CR['Title'] + "\n"
	       file.write( line[0] + " CR" + CRid + " " + CR['Title'] + "\n")
               #table.append(r'<tr><td>{}</td><td>{}</td></tr>'.format(*line.split(' ')))
	    except Exception:
	       file.write(line[0] + " CR" + CRid + " " + "\n")
   #table.append('</table></body></html>')
   #print ''.join(table)  

   #file.write( ''.join(table))
   file.write("\n3. Dependency List: \n")

   if(DepList):
      for dependency in DepList.string:
         file.write(dependency + "\n")
   else:
      file.write("None\n")

   file.write("\n4. CR Status: \n")
   
   for line in diff:
       if "ChangeRequest" in line:
	    CRid = line.split("ChangeRequest")[-1].strip().split(" ")[0]
	    # Get CR Titles
	    try:
	       CR = prismClient.getChangeRequestById(CRid)
	       
	       for SoftwareImageRecordEntity in CR.SoftwareImageRecords:
		       #if (SoftwareImageRecordEntity.SoftwareImageName == "MPSS.DI.3.0.c7"):
		          print type(SoftwareImageRecordEntity)     #tuple
                          print type(SoftwareImageRecordEntity[1])  #list
                          print type(SoftwareImageRecordEntity[1][1]) #instance

			  for softwareEntity in SoftwareImageRecordEntity[1]:
		         	  if softwareEntity.SoftwareImageName == plName:
			              print "Yes"
		                      devStatus = softwareEntity.IsDevelopmentComplete
		                      Assignee = softwareEntity.AssigneeUserName
		                      crStatus = softwareEntity.Status
	       #print CR.items()
	       #print CR.SoftwareImageRecords
	       #print CRid + ":" + CR['Title'] + "\n"
	                              file.write( line[0] + " CR" + CRid + " [CR Status:]" + str(crStatus) + "  [DevComplete]:" + str(devStatus) + "  [POC]:" + str(Assignee) + "\n")
               #table.append(r'<tr><td>{}</td><td>{}</td></tr>'.format(*line.split(' ')))
	    except Exception:
	       file.write(line[0] + " CR" + CRid + " " + "\n")
   file.close()

   fp = open("email.txt", 'rb')
   # Create a text/plain message
   msg = MIMEText(fp.read())
   fp.close()
  
   #if(plName == "MPSS.TR.3.0"):
   send_relNote_email(msg,plName,label, user)

def release_note(label1, user, passwd):

   #Step 1: Connecting to Aris Service
   url = 'http://hci/arisservice/arisexternalservice.svc?wsdl'
   #url2 = 'http://prism.qualcomm.com:8000/ChangeRequestWebService.svc?wsdl'

   client = Client(url)

   #step 2: create label details requests with the given label.
   request = client.factory.create('ns4:LabelDetailRequest')
   request.LabelName = label1 

   #step 3: create response and wait for service return response.
   response = client.factory.create('ns5:LabelDetailsResponse')

   try:
      response = client.service.GetLabelDetails(request)
   except:
      print ("The provided label is either not submitted or invalid. Please double check.")

   #prismClient = PrismChangeRequestWebService(username=user, password=passwd)
   prism = Prism('http://prism:8000/ChangeRequestWebService.svc?wsdl', 'prismauth.txt')
   #print Prism

   for requestSummary in response.Requests.RequestSummary:
      #if( ( response.Requests.RequestSummary[0].IntegrationUnit.IuName ) == "MPSS.TR.3.0"):
      print requestSummary.IntegrationUnit.IuName
      processRequestSummary (requestSummary, label1, user, prism)

###################################################
#Main Function:
#Parameter: Label1 (the label for the release note)
###################################################
if __name__ == '__main__':
	
    if (len(sys.argv) < 4 or len(sys.argv) > 5):
        print "Usage: ArisReleaseNote.exe label1"
        sys.exit()
    else:
	
         # get the two labels from command line input
        label1 = sys.argv[1]
        user = sys.argv[2]
        passwd = sys.argv[3]

    os.system("echo Running... Please wait...")
    os.system("echo.")
    release_note(label1, user, passwd)

