# -*- coding: utf-8 -*-
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
	try:
		h_subject = email.Header.Header(subject)
		dh_subject = email.Header.decode_header(h_subject)
		subject = dh_subject[0][0]
		subjectcode = dh_subject[0][1]
		if(subjectcode != None):
			#subject = unicode(subject,subjectcode)
			subject = subject.decode(subjectcode,'ignore')
	except:
		subject = subject.decode('ascii','ignore')
	finally:
		print "subject:", subject.encode('GBK','ignore')
	
	
	
	#parse and decode from
	from_username = ""
	from_domain = ""
	try:
		hmail_from = email.utils.parseaddr(msg.get("from"))
		ptr = hmail_from[1] .find('@')
		from_username = hmail_from[1][:ptr]
		from_domain = hmail_from[1] [ptr:]
	except:
		from_username = ""
		from_domain = ""
	finally:
		print "from: ",from_username,from_domain
	

	
	#parse and decode to
	to_username = ""
	to_domain = ""
	try:
		if(msg.get("to") !=None) :
			hmail_tos = msg.get("to").split(',')
			for hmail_to in hmail_tos:
				hmail_to = email.utils.parseaddr(hmail_to)
				ptr = hmail_to[1] .find('@')
				to_username = hmail_to[1][:ptr]
				to_domain = hmail_to[1] [ptr:]
				
	except:
		to_username = ""
		to_domain = ""
	finally:
		print "to: ",to_username,to_domain

	
	#parse and decode Cc
	cc_username = ""
	cc_domain = ""
	try:
		if(msg.get("Cc") !=None) :
			hmail_ccs = msg.get("Cc").split(',')
			for hmail_cc in hmail_ccs:
				hmail_cc = email.utils.parseaddr(hmail_cc)
				ptr = hmail_cc[1] .find('@')
				cc_username = hmail_cc[1][:ptr]
				cc_domain = hmail_cc[1][ptr:]
	except:
		cc_username = ""
		cc_domain = ""
	finally:
		print "cc: ",cc_username,cc_domain
		
		
	
	#parse and decode Date
	hmail_date = ""
	try:
		hmail_date = email.utils.parsedate(msg.get("Date"))
	except:
		hmail_date = ""
	finally:
		print "Date: ",hmail_date
	

	#parse and decode sender ip
	IP = ""
	try:
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
	except:
		IP = ""
	finally:
		print "IP:",IP
				
	#header end
	print "+"*60
	
	#body
	counter = 1
	for part in msg.walk():
		if part.get_content_maintype() == 'multipart':
			continue

		#content plain
		content_plain = ""
		try:
			if (part.get_content_type() == "text/plain"):
				
				code = part.get_content_charset()
				if( code == None):
					content_plain = part.get_payload()
				else:
					content_plain = part.get_payload(decode=True).decode(code,'ignore')
					#print unicode(part.get_payload(decode=True),code)
		except:
			content_plain = ""
		finally:
			print content_plain.encode('GBK','ignore')
			print "+"*60
			#continue
			
		#content html
		content_html = ""
		try:
			if (part.get_content_type() == "text/html"):
				
				code = part.get_content_charset()
				print code
				if( code == None):
					content_html = part.get_payload()
				else:
					content_html = part.get_payload(decode=True).decode(code,'ignore')
					#print unicode(part.get_payload(decode=True),code)
		except:
			content_html = ""
		finally:	
			print content_html.encode('GBK','ignore')
			print "+"*60
			#continue
		
		#attachment
		try:
			if (part.get('Content-Disposition') != None):
				# this part is an attachment
				name = part.get_filename()
				
				counter += 1
				h = email.Header.Header(name)
				dh = email.Header.decode_header(h)
				filename = dh[0][0]
				filecode = dh[0][1]
				if(filecode != None):
					filename = filename.decode(filecode,'ignore')
				if not filename:
					filename = 'part-%03d' % (counter)
				print 'attachmentL:', filename
				fp = open(os.path.join('./', filename), 'wb')
				fp.write(part.get_payload(decode=True))
				fp.close()
		except:
			print "attachment parse error"
		finally:
			print "+"*60
			#continue
	
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