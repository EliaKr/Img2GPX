# Img2GPX (WIP)

A python script to create a GPX path from image metadata. Useful for creating a visual plot of a path followed during travel.

Supported formats: TIFF, JPEG, PNG, Webp, HEIC

## Dependencies

- Python version >= 3.11
- [ExifRead](https://pypi.org/project/ExifRead/) library (For HEIC files a version below 3.0.0 is required. You can download it using `pip install "exifread<3"`)
- [tzdata](https://pypi.org/project/tzdata/) library

## Usage

Run using the command: `python3 img2gpx.py -d "~/directory" -f "filename" --verbose`.
If no directory is specified, then the directory where the `img2gpx.py` file is will be used. If no filename is specified then the current unix time will be used. --verbose prints a detailed output of the images processed and the arguments entered by the user.
The GPX file is saved in the same directory as the photo files.

## TODO

- Add altitude data
- Add more options for formatting
- Add graphics and package to release
- Add option to create image with static map and path
