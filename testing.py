import exifread

with open('/home/elias/Downloads/IMG_4600.heic', 'rb') as f:
    tags = exifread.process_file(f, details=False)

print(tags["EXIF OffsetTimeOriginal"])

coord = exifread.utils.get_gps_coords(tags)
print(coord)
print("filename.gpx"[0:-5])