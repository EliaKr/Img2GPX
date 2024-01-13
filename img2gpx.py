import exifread
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import sys
import time

class Image:
    def __init__(self, latitude, longitude, timestamp, timezone, num):
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.timezone = timezone
        self.num = num
        self.formatImageMetadata()

    def formatImageMetadata(self):
        def formatTimestamp():
            def formatDate(timestamp_date):
                timestamp_date_list = list(timestamp_date)
                formatted_date = ""
                for i in timestamp_date_list:
                    if i == ":":
                        timestamp_date_list[timestamp_date_list.index(i)] = "-"
                for i in timestamp_date_list:
                    formatted_date += i
                
                return formatted_date

            # Convert to ISO date format
            timestamp_date = self.timestamp.split(" ")[0]
            timestamp_date = formatDate(timestamp_date)

            # Extract time from timestamp
            timestamp_time = self.timestamp.split(" ")[1]

            # Create datetime object and convert to UTC
            timestamp_obj = datetime.fromisoformat(timestamp_date + "T" + timestamp_time + self.timezone)
            timestamp_obj = timestamp_obj.astimezone(ZoneInfo("UTC"))
            
            # Create final timestamp string
            temp_list = str(timestamp_obj).split(" ")
            temp_string = temp_list[0] + "T" + temp_list[1]
            temp_list = temp_string.split("+")
            formatted_timestamp = temp_list[0] + "Z"

            # Delete timezone attribute
            del self.timezone

            return formatted_timestamp

        def formatLatitude():
            formatted_latitude = f"{self.latitude:.6f}"
            
            return formatted_latitude

        def formatLongitude():
            formatted_longitude = f"{self.longitude:.6f}"
            
            return formatted_longitude

        self.timestamp = formatTimestamp()
        self.latitude = formatLatitude()
        self.longitude = formatLongitude()
        
    def __str__(self):
        return f"Image no. {self.num} with timestamp {self.timestamp} and lat, long: {self.latitude}, {self.longitude}"

class RoutePoint:
    def __init__(self, image_object):
        self.latitude = image_object.latitude
        self.longitude = image_object.longitude
        self.timestamp = image_object.timestamp
        self.num = image_object.num
    
    def __str__(self):
        # Return formatted route entry
        return f"<rtept lat=\"{self.latitude}\" lon=\"{self.longitude}\">\n<time>{self.timestamp}</time>\n<desc>{self.num}</desc>\n<sym>Dot</sym>\n<type><![CDATA[Dot]]></type>\n</rtept>"

class Main:
    def __init__(self):
        # Get arguments given by user when running
        args = sys.argv
        print(args)
        # Check for --verbose argument
        if "--verbose" in args:
            self.verbose = True
        else:
            self.verbose = False
        
        # Check for -d directory argument (Directory must not have a trailing slash)
        try:
            if "-d" in args:
                self.directory = args[args.index("-d") + 1]
                self.verbose_print(f"Working directory: {self.directory}")
            else:
                self.directory = ""
                self.verbose_print(f"Working directory: {os.getcwd()}")
            self.permscheck()
        except Exception:
            print("Directory doesn't exist or don't have permission to access. Please try again.")
        
        # check for -f filename argument
        try:
            if "-f" in args:
                if ".gpx" not in args[args.index("-f") + 1]:
                    self.filename = args[args.index("-f") + 1]
                else:
                    self.filename = args[args.index("-f") + 1][0:-4]
            else:
                self.filename = str(int(time.time()))

            self.namecheck()
            self.verbose_print(f"Filename: {self.filename}")
        except Exception:
            print("Filename too long or contains illegal character. Please try again.")
        
        self.run()

    # Check if script has directory read/write permissions
    def permscheck(self):
        tempfile = open(f"{self.directory}/496D67324750585F74657374.tmp", "w")
        tempfile.write("Img2GPX test file. Feel free to delete.")
        tempfile.close()
        
        self.verbose_print("Permissions check passed!")
    
    # Check if filename is legal for use in all operating systems
    def namecheck(self):
        if len(self.filename) > 127:
            print("Filenames up to 127 characters allowed.")
            raise Exception("Filename too long")
        elif any(illegal_char in self.filename for illegal_char in ["*", "\"", "/", "\\", "<", ">", ": ", " | ", "?", "'"]):
            print("The following characters are not allowed in filenames: * \" / \ < > : | ? '")
            raise Exception("Illegal characters in filename")
        self.verbose_print("Filename check passed!")
    
    def verbose_print(self, msg):
        if self.verbose == True:
            print(msg)
    
    # Create list of image files
    def createFileList(self):
        self.filelist = []
        all_files = os.listdir(path=self.directory)
        for i in all_files:
            if any(ext in i for ext in [".tiff", ".jpeg", ".jpg", ".png", ".webp", ".heic", ".TIFF", ".JPEG", ".JPG", ".PNG", ".WEBP", ".HEIC"]):
                self.filelist.append(i)
        self.verbose_print(f"All chosen files: {self.filelist}")

    # Create list of Image objects
    def createImageObjectList(self):
        self.image_object_list = []
        num = 1
        self.total_num = 1
        for i in sorted(self.filelist):
            with open(f"{self.directory}/{i}", "rb") as img:
                try:
                    tags = exifread.process_file(img, details=False)
                    obj = Image(exifread.utils.get_gps_coords(tags)[0], exifread.utils.get_gps_coords(tags)[1], str(tags["Image DateTime"]), str(tags["EXIF OffsetTimeOriginal"]), num)
                    self.image_object_list.append(obj)
                    self.verbose_print(f"Created Image object for photo {self.total_num}/{len(self.filelist)}: {obj}")
                    num = num + 1
                    self.total_num = self.total_num + 1
                except Exception as err:
                    if str(err) == "'NoneType' object is not subscriptable":
                        self.verbose_print(f"Error creating Image object for photo {self.total_num}/{len(self.filelist)}: No location metadata")
                    else:
                        self.verbose_print(f"Error creating Image object for photo {self.total_num}/{len(self.filelist)}: {err}")
                    self.total_num = self.total_num + 1
    
    # Create list of RoutePoint objects
    def createRoutePointObjectList(self):
        self.routepoint_object_list = []
        for i in sorted(self.image_object_list, key=lambda item: item.timestamp):
            obj = RoutePoint(i)
            self.routepoint_object_list.append(obj)
            self.verbose_print(f"Created RoutePoint object for photo: {i}")
    
    # Create .gpx file using the RoutePoint class __str__ method
    def makeGPXFile(self):
        file_header = "<?xml version=\"1.0\"?>\n<gpx\nversion=\"1.0\"\ncreator=\"Img2GPX - github: EliKr\"\nxmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n<rte>"
        file_lastline = "\n</rte>\n</gpx>"

        with open(f"{self.directory}/{self.filename}.gpx", "w", encoding="utf-8") as file:
            file.writelines(file_header)
            for i in self.routepoint_object_list:
                file.writelines(str(i))
            del i
            file.writelines(file_lastline)
    
    def timeProcess(self, control = None):
        if not control:
            self.start_time = time.process_time()
        elif control == "stop":
            self.end_time = time.process_time()

    def run(self):
        self.verbose_print("Program started")
        self.timeProcess()
        self.createFileList()
        self.createImageObjectList()
        self.createRoutePointObjectList()
        self.makeGPXFile()
        self.timeProcess("stop")
        self.verbose_print(f"Processed {self.total_num} photos in {self.end_time - self.start_time}s")

run = Main()