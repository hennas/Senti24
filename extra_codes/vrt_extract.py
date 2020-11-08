import json
import logging
import argparse
import xml.etree.ElementTree as XML

"""
Old version of vrt extract, use vrt_extract2.py instead
This file is used to extract thread titles, ids, and dates from the Suomi24 .vrt files
Example execution:
    python3 vrt_extract.py s24_2004.vrt -d database/
"""


class VRTExtract:
    def __init__(self, vrt_file: str, db_loc: str):
        self.logger = logging.getLogger('vrt-extract')
        self.file = vrt_file
        self.db_loc = db_loc
        self.year = self.get_year(self.file)
        self.db = {}  # self.load_db()

    # Remove this
    def load_db(self) -> dict:
        """
        Attempts to read an existing Suomi24 json database
        :return: The database as dictionary, or {} if db not found
        """
        try:
            self.logger.info(f'Loading the database from {self.db_file}')
            return json.loads(open(self.db_file, 'r').read())
        except FileNotFoundError:
            self.logger.info('Could not find existing database')
            return {}

    def get_year(self, filename):
        """
        Extracts the year from a s24_xxxx.vrt file's name
        :param filename: Name of the .vrt file
        :return: Year
        """
        year = self.file.replace('s24_', '').replace('.vrt', '')
        self.logger.info(f'This .vrt file contains data for the year {year}')
        return year

    def is_target(self, line: str) -> bool:
        """
        Determines if a lne read from a .vrt file contains the title of a thread
        :param line: Line from a .vrt file
        :return: True if title; False otherwise
        """
        # Remove possible leading spaces
        return line.lstrip().startswith('<text comment_id="0"')

    def extract(self):
        """
        Read the given .vrt file line by line. When a line contains the start of a thread,
        the thread title, id, and date are extracted into a dictionary. The dictionary follows this format:
            {
                'month': [
                    {
                        'title': 'Thread title',
                        'id': 'Thread id',
                        'datetime': 'Time and date of the thread creation'
                    }
                ]
            }
        :return: None
        """
        self.logger.info(f'Opening {self.file}')
        try:
            f = open(self.file, 'r')
        except FileNotFoundError:
            self.logger.info('Could not open the .vrt file')
            return

        result = {}
        self.logger.info('Extracting')
        for line in f:
            # Only attempt to extract if line is correct
            if self.is_target(line):
                # Add the closing text tag to make the line have proper XML
                xml_attributes = XML.fromstring(line.rstrip()+'</text>').attrib
                # Extract wanted parameters
                month = xml_attributes['date'][5:7]             # Extract month
                # Add month to the keys
                if month not in result.keys():
                    result[month] = []
                result[month].append({
                    'title': xml_attributes['title'],           # Extract thread title
                    'thread_id': xml_attributes['thread_id'],   # Extract thread id
                    'datetime': xml_attributes['datetime']      # Extract datetime
                })
        self.logger.info('Extraction complete')
        self.db = result
        # self.db[self.year] = result  # Assign results to year
        self.save_result()  # Save the results

    def save_result(self):
        """
        Save the extraction results to the given json file
        :return: None
        """
        self.logger.info(f'Saving results to {self.db_loc}s24_{self.year}.json')
        open(f'{self.db_loc}s24_{self.year}.json', 'w').write(json.dumps(self.db, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    # Set logging format
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='Name of the .vrt file you want to parse')
    parser.add_argument('-d', '--db', type=str, default='database/', help='Directory where results will be stored')
    args = parser.parse_args()
    # Make sure a .vrt file was given as param
    if args.file.endswith('.vrt'):
        # Start the VRTParser
        VRTExtract(args.file, args.db).extract()
    else:
        print('Please input a .vrt file')


