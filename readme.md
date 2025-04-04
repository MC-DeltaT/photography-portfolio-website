# Photo Portfolio Website

## Overview

Static website, dynamically built from a list of photos and metadata.

## Adding Photos

Add image files to the `ingest` directory. They may have any file and directory structure.

Each image file must:

- Be a supported image file type, with the corresponding file extension (currently JPG and PNG).
- Have a sidecar metadatafile, with the same name but with `.json` appended. See the `PhotoMetadataFile` class for required format.

After adding the files here, do not commit them! Run the site build as described in the next section, which will ingest the files into the right structure within the repo.

## Building the Site

1. Navigate to `source` directory.
2. Create a Python virtual environment
3. Install requirements in `requirements.txt`
4. Run `python -m buildtool`
5. Output will be in `../site`

For use in CI, the convenience script [`deploy.sh`](./deploy.sh) can be used.

## Requirements

- Python 3.12
- See [requirements.txt](source/requirements.txt)
- ExifTool
- ImageMagick
