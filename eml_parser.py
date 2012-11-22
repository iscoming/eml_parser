#-*- encoding: gb2312 -*-
#!/usr/bin/python

import os
import sys
import email
import getopt
import re
import os.path

def usage():
	print '''Help Information:
-i: eml file you want to decode
-d: path where you want to echo
-h: help'''

def decode_email(msgfile):
	fp = open(msgfile)
	msg = email.message_from_file(fp)
	fp.close()
	
	print "="*60
	
	#header
	
	#parse and decode subject
	subject = msg.get("subject")
	h_subject = email.Header.Header(subject)
	dh_subject = email.Header.decode_header(h_subject)
	subject = dh_subject[0][0]
	subjectcode = dh_subject[0][1]
	if(subjectcode != None):
		subject = unicode(subject,subjectcode)
		
	print "subject:", subject
	
	#parse and decode from
	hmail_from = email.utils.parseaddr(msg.get("from"))
	ptr = hmail_from[1] .find('@')
	username = hmail_from[1][:ptr]
	domain = hmail_from[1] [ptr:]
	print "from: ",username,domain
	
	#parse and decode to
	if(msg.get("to") !=None) :
		hmail_tos = msg.get("to").split(',')
		for hmail_to in hmail_tos:
			hmail_to = email.utils.parseaddr(hmail_to)
			ptr = hmail_to[1] .find('@')
			username = hmail_to[1][:ptr]
			domain = hmail_to[1] [ptr:]
			print "to: ",username,domain
	
	#parse and decode Cc
	if(msg.get("Cc") !=None) :
		hmail_ccs = msg.get("Cc").split(',')
		for hmail_cc in hmail_ccs:
			hmail_cc = email.utils.parseaddr(hmail_cc)
			ptr = hmail_cc[1] .find('@')
			username = hmail_cc[1][:ptr]
			domain = hmail_cc[1] [ptr:]
			print "cc: ",username,domain
	
	#parse and decode Date
	hmail_date = email.utils.parsedate(msg.get("Date"))
	print "Date: ",hmail_date
	
	#parse and decode sender ip
	IP = ""
	hmail_recv = msg.get("X-Originating-IP")
	if(hmail_recv != None):
		hmail_recv = hmail_recv.strip("[]")
		IP = hmail_recv
	else :
		hmail_receiveds =  msg.get_all("Received")
		if(hmail_receiveds !=None):
			for hmail_received in hmail_receiveds:
				m = re.findall(r'from[^\n]*\[(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])',hmail_received)
				if(len(m)>=1):
					hmail_recv = re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])',m[0])
					if(len(hmail_recv)>=1):
						IP = hmail_recv[0]
	
	print "IP:",IP
				
	
	#header end
	print "+"*60
	
	#body
	counter = 1
	for part in msg.walk():
		if part.get_content_maintype() == 'multipart':
			continue

		#content plain
		if (part.get_content_type() == "text/plain"):
			
			code = part.get_content_charset()
			if( code == None):
				print part.get_payload()
			else:
				print unicode(part.get_payload(decode=True),code)
			print "+"*60
			continue
			
		#content html
		if (part.get_content_type() == "text/html"):
			
			code = part.get_content_charset()
			if( code == None):
				print part.get_payload()
			else:
				print unicode(part.get_payload(decode=True),code)
			print "+"*60
			continue
		
		#attachment
		if (part.get('Content-Disposition') != None):
			# this part is an attachment
			name = part.get_filename()
		#name = part.get_param("filename")
			
			counter += 1
			h = email.Header.Header(name)
			dh = email.Header.decode_header(h)
			filename = dh[0][0]
			filecode = dh[0][1]
			if(filecode != None):
				filename = unicode(filename,filecode)
			if not filename:
				filename = 'part-%03d' % (counter)
			print 'attachmentL:', filename
			fp = open(os.path.join('./', filename), 'wb')
			fp.write(part.get_payload(decode=True))
			fp.close()
			print "+"*60
			continue
	
	print "="*60

def main():
	if sys.argv[1:]==[]:
		sys.argv[1:]=['-h']
		
	opts,args=getopt.getopt(sys.argv[1:], 'i:d:h')
	
	for o, k in opts:
		if o=='-h':
			usage()
			sys.exit()
		if o=='-i':
			msgfile=k
		if o=='-d':
			startdir = k
	
	if(startdir!=None):
		for dirpath, dirnames, filenames in os.walk(startdir):
			for filename in filenames:
				if os.path.splitext(filename)[1] == '.eml':
					filepath = os.path.join(dirpath, filename)
					print "Parsing:",filepath
					decode_email(filepath)
	else:
		decode_email(msgfile)


	
if __name__ == '__main__':
	main()