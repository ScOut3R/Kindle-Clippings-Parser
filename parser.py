#!/usr/bin/env python
import re
import codecs

EOR = u"=========="

def records(file_path):
	clip_file = codecs.open( file_path )
	clip_file.seek( 3 ) # skip magic cookie

	record = list()
	for line in clip_file:
		line = line.decode( 'utf-8' )
		if line.strip() == EOR:
			assert record[2] == '', "Non-blank line expected separating the header from the body of the clipping:%s" % record[2]
			clip = dict()
			match = re.match( r'(.*?)\((.*)\)', record[0] )
			clip['title'], clip['attribution'] =match.groups() 
			clip['attribution'] = clip['attribution'].split( ') (' )

			try:
				match = re.match( r'- (\w+) on Page (\d+) \| Loc. ([^|]+)\| Added on (\w+), (\w+ \d+, \d+), (\d+:\d+ \w\w)', record[1] )
				clip['type'], clip['page'], clip['location'], clip['dow'], clip['date'], clip['time'] = match.groups()
			except AttributeError:
				match = re.match( r'- (\w+) Loc. ([^|]+)\| Added on (\w+), (\w+ \d+, \d+), (\d+:\d+ \w\w)', record[1] )
				clip['type'], clip['location'], clip['dow'], clip['date'], clip['time'] = match.groups()

			clip['body'] = "\n".join( record[3:] )

			# a little tidying
			clip['title'] = clip['title'].strip()
			clip['location'] = clip['location'].strip()

			# yield and reset for next record
			if clip['type'] == 'Highlight':
				yield clip
			record = list() 
		else:
			record.append( line.strip() )

	clip_file.close()



if __name__ == '__main__':
	from sys import argv
	data = { }
	for n,r in enumerate( records(argv[1] ) ): #'My Clippings.txt') ):
		if data.has_key(r['title']):
			data[r['title']].append(r)
		else:
			data[r['title']] = [ r ]

	for title in data.keys():
		output = open(title + '.txt', 'w')
		string = ("====== %s ======\n\n" % title).encode('utf-8')
		output.write(string)
		for item in data[title]:
			if item.has_key('page'):
				string = ("  * %s ((%s. p.))\n" % ( item['body'], item['page'] )).encode('utf-8')
			else:
				string = ("  * %s  ((%s. loc.))\n" % ( item['body'], item['location'] )).encode('utf-8')
			output.write(string)
		output.close()

