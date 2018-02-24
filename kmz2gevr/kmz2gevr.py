#!/usr/bin/env python
# -*- coding: utf8 -*-


#    Copyright (C) 2018  Kenneth Bogert and the University of North 
#    Carolina at Asheville
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


from pykml import parser
from zipfile import ZipFile
from libxmp import XMPFiles, consts
import gevrplace_pb2
from image_utils import ImageText
import base64
import sys
import googlemaps
import argparse
import tempfile
import os

font = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

def getkml(kmzfile):
	kmz = ZipFile(kmzfile, 'r')
	return parser.parse(kmz.open('doc.kml', 'r')).getroot()

# returns list of dicts for each file created
def kml2gevr(kml, output_dir, desiredHeight, bgColor, textColor):

	global font
	points = []

	# get the point data from the kml file

	for child in kml.Document.Folder.Placemark:
		entry = {}

		entry['name'] = child.name.text
		if child.description is not None:
			entry['desc'] = child.description.text
		else:
			entry['desc'] = entry['name']

		# if the placemark contains a lookat, prefer this
		if child.LookAt is not None:
			entry['lon'] = float(child.LookAt.longitude.text)
			entry['lat'] = float(child.LookAt.latitude.text)
			entry['heading'] = float(child.LookAt.heading.text)
		elif child.Camera is not None:
			entry['lon'] = float(child.Camera.longitude.text)
			entry['lat'] = float(child.Camera.latitude.text)
			entry['heading'] = float(child.Camera.heading.text)
		elif child.Point is not None:
			# just get the point
			coords = child.Point.coordinates.text.split(",")
			entry['lon'] = float(coords[0])
			entry['lat'] = float(coords[1])
			entry['heading'] = 0.01

		if ('lon' in entry):	
			points.append(entry)


	# get elevation from google maps

	script_dir = os.path.dirname(__file__)
	keyfile = open(os.path.join(script_dir, "googleapi.key"), 'r')
	key = keyfile.read().strip()

	client = googlemaps.Client(key)

	googleQuery = [(entry['lat'], entry['lon']) for entry in points]

	elevations = client.elevation(googleQuery)


	for i, elev in enumerate(elevations):

		points[i]['elev'] = elev['elevation']


	# create the image files
	for entry in points:

		image = ImageText((1512, 950), background=bgColor)

	#	(w, height) = image.write_text( ( 'center', 75) , entry['name'], 
	#		font_filename=font, font_size='fill', max_width=1400, 
	#		color=textColor)

		image.write_text_box(((1512-600) / 2.0, 110), entry['desc'], box_width=725,
			font_filename=font, font_size=72, color=textColor, place='center')


		newFile = tempfile.NamedTemporaryFile(suffix=".jpg", dir=output_dir, delete=False)
		newFile.close()

		image.save(newFile.name)
		entry['filename'] = newFile.name

		# now open that file back up and write an XMP containing the google protocol buffer to it	
	
		gevrplace = gevrplace_pb2.GEVRPlace()

		temp = gevrplace.summary.location.extend( [entry['name'], ""])
		gevrplace.summary.copyright = "Imagery ©2016 Google, Data SIO, NOAA, U.S. Navy, NGA, GEBCO, Google, IBCAO, INEGI, Landsat"
		gevrplace.summary.unknown1 = 438
		gevrplace.summary.unknown2 = 0
		gevrplace.summary.unknown3 = 756
		gevrplace.summary.unknown4 = 850

		gevrplace.places.savedPlace.Title = entry['name']
		gevrplace.places.savedPlace.SubTitle = entry['desc']

		gevrplace.places.savedPlace.location.latLong.lat = entry['lat']
		gevrplace.places.savedPlace.location.latLong.lon = entry['lon']
		gevrplace.places.savedPlace.location.latLong.earthRadius = -6371010.0
	
		gevrplace.places.savedPlace.location.picParams.roll = 0.0280364837203
		weirdAltitude = (-entry['elev']-6371010) / desiredHeight
		gevrplace.places.savedPlace.location.picParams.weirdAltitude = weirdAltitude
		gevrplace.places.savedPlace.location.picParams.pitch = 0.00692561878283

		gevrplace.places.savedPlace.location.heading = entry['heading']
		gevrplace.places.savedPlace.location.viewMode = gevrplace_pb2.GEVRPlace.Places.Place.Location.EARTH_BELOW
		gevrplace.places.savedPlace.location.elevation = desiredHeight
		gevrplace.places.savedPlace.location.unknown3 = gevrplace_pb2.GEVRPlace.Places.Place.Location.UNKNOWN0


		gevrplace.places.savedPlace.time.year = 2015
		gevrplace.places.savedPlace.time.month = 8
		gevrplace.places.savedPlace.time.day = 25
		gevrplace.places.savedPlace.time.hour = 5
		gevrplace.places.savedPlace.time.minute = 53
		gevrplace.places.savedPlace.time.second = 23

	
		ENCODED = base64.b64encode(gevrplace.SerializeToString()).decode().rstrip("=")


		xmpfile = XMPFiles( file_path=newFile.name, open_forupdate=True, open_usesmarthandler=True)
		xmp = xmpfile.get_xmp()
		xmp.register_namespace("http://ns.google.com/photos/1.0/earthvr/", "EarthVR")

		xmp.set_property(xmp.get_namespace_for_prefix("EarthVR"), "SerializedMetadata", ENCODED)
		xmp.set_property(xmp.get_namespace_for_prefix("EarthVR"), "Version", '1.0')


		xmpfile.put_xmp(xmp)
		xmpfile.close_file()

	return points



if __name__ == "__main__":

	p = argparse.ArgumentParser(description='Convert pins saved in a kmz file to Google Earth VR saved places.')
	p.add_argument('filename', nargs=1, help="Path to the KMZ file to open")
	p.add_argument('--height', nargs=1, type=float, help="Height in meters above the surface to place the user", default=[5])
	p.add_argument('--bgColor', nargs=1, type=str, help="Background color of the generated image, three ints separated by commas, example: 128,0,255", default=['0,128,0'])
	p.add_argument('--textColor', nargs=1, type=str, help="Text color of the generated image, three ints separated by commas, example: 255,255,255", default=['255,255,255'])
	p.add_argument('--output_dir', nargs=1, help="Path to output the GEVR images to (default current dir)", default=["."])

	args = p.parse_args()

	bgColor = tuple(int(x) for x in args.bgColor[0].split(","))
	bgColor = bgColor + (255,)
	textColor = tuple(int(x) for x in args.textColor[0].split(","))
	desiredHeight = args.height[0]

	filename = args.filename[0]
	output_dir = args.output_dir[0]
	
	kml = getkml(filename)


	points = kml2gevr(kml, ".", desiredHeight, bgColor, textColor)

	for entry in points:

		outFile = "".join(i for i in entry['name'] if i not in "\/:*?<>|")
		outFile += ".jpg"
		outFile = os.path.join(output_dir, outFile)

		os.rename(entry['filename'], outFile)

