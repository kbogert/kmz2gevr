#!/usr/bin/python
# -*- coding: utf8 -*-


import cgi
import cgitb
import os, sys
import kmz2gevr
import tempfile
import shutil
from StringIO import StringIO
import zipfile

def hexColorToDecimal(hexcolor):

	return ( int( hexcolor[1:3], 16), int( hexcolor[3:5], 16), int( hexcolor[5:7], 16)  )


def multipleFileResponse(points):
	# create response, a zipfile of all the gevr place files

	zipout = StringIO()
	z = zipfile.ZipFile(zipout, 'w', zipfile.ZIP_DEFLATED)

	for place in points:

		mangledName = "".join(i for i in place['name'] if i not in "\/:*?<>|")
		mangledName += ".jpg"

		z.write(place['filename'], mangledName)		

	z.close()

	# send to the user

	length = zipout.tell()
	zipout.seek(0)

	sys.stdout.write("Content-type: application/zip;\r\n")
	sys.stdout.write("Content-Disposition: attachment; filename=GEVRPlaces.zip\r\n")
	sys.stdout.write("Content-Title: GEVRPlaces.zip\r\n")
	sys.stdout.write("Content-Length: " + str(length) + "\r\n")
	sys.stdout.write("\r\n")
	sys.stdout.write(zipout.read())
	
	zipout.close()

def singleFileResponse(points):

	point = points[0]
	mangledName = "".join(i for i in point['name'] if i not in "\/:*?<>|")
	mangledName += ".jpg"

	f = open(point['filename'])
	f.seek(0, os.SEEK_END)
	length = f.tell()
	f.seek(0, os.SEEK_SET)

	sys.stdout.write("Content-type: image/jpeg;\r\n")
	sys.stdout.write("Content-Disposition: attachment; filename="+ mangledName + "\r\n")
	sys.stdout.write("Content-Title: "+ mangledName +"\r\n")
	sys.stdout.write("Content-Length: " + str(length) + "\r\n")
	sys.stdout.write("\r\n")
	sys.stdout.write(f.read())

def err_redirect():
	sys.stdout.write("Content-type: text/html;\r\n")
	sys.stdout.write("Location: /upload.html\r\n\r\n")


def process_kmz_file(file_field, height_field, bg_field, text_field):
	form = cgi.FieldStorage()
	if not form.has_key(file_field):
		err_redirect()
		return

	thefile = form[file_field]

	if not thefile.file:
		err_redirect()
		return

	if not thefile.filename:
		err_redirect()
		return

	# did they upload a kmz or kml file?
	if thefile.filename.endswith(".kml") or thefile.filename.endswith(".KML"):
		kml = kmz2gevr.loadkml(thefile.file)
	else:
		kml = kmz2gevr.getkml(thefile.file)

	height = float(form[height_field].value)
	bgColor = hexColorToDecimal(form[bg_field].value) + (255,)
	textColor = hexColorToDecimal(form[text_field].value)

	tmp_dir = tempfile.mkdtemp()

	points = kmz2gevr.kml2gevr(kml, tmp_dir, height, bgColor, textColor)


	if len(points) == 1:
		singleFileResponse(points)
	else:
		multipleFileResponse(points)



	# delete tmp dir

	shutil.rmtree(tmp_dir)

if __name__ == '__main__':
	process_kmz_file("kmz_file", "desiredHeight", "bgColor", "textColor")
