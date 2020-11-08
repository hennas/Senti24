import time
import logging
import argparse
import pandas as pd
import xml.etree.ElementTree as XML

"""
This can be used to extract the topics of threads in the Suomi24 dataset. Was not used in the analysis though
"""


class ExtractTopic:
    def __init__(self, vrt_file: str, db_loc: str):
        self.logger = logging.getLogger('extract-topic')
        self.db_loc = db_loc
        self.year = self.get_year(vrt_file)
        self.filename = vrt_file
        self.topics = {}

    def get_year(self, filename):
        """
        Extracts the year from a s24_xxxx.vrt file's name
        :param filename: Name of the .vrt file
        :return: Year
        """
        year = filename.replace('s24_', '').replace('.vrt', '')
        self.logger.info(f'This .vrt file contains data for the year {year}')
        return year

    def load_vrt(self):
        self.logger.info(f'Opening {self.filename}')
        try:
            return open(self.filename, 'r')
        except FileNotFoundError:
            self.logger.info('Could not open the .vrt file')
            return

    def is_target(self, line: str) -> bool:
        # Remove possible leading spaces
        return line.lstrip().startswith('<text comment_id="0"')

    def extract(self):
        file = self.load_vrt()
        self.logger.info('Extracting threads')
        start = time.time()
        for line in file:
            # Only attempt to extract if line is correct
            if self.is_target(line):
                # Add the closing text tag to make the line have proper XML
                xml_attributes = XML.fromstring(line.rstrip()+'</text>').attrib
                self.topics[xml_attributes['thread_id']] = {
                    'topic': xml_attributes['topic_name_top'],
                    'topic_leaf': xml_attributes['topic_name_leaf']
                }
        self.save()

    def save(self):
        # open(f'{self.db_loc}{self.year}_topics.json', 'w').write(json.dumps(self.topics, indent=4))
        topics_array = []
        for thread_id in self.topics:
            topics_array.append([thread_id, self.topics[thread_id]['topic'], self.topics[thread_id]['topic_leaf']])
        df = pd.DataFrame(topics_array, columns=['thread_id', 'topic', 'topic_leaf'])
        df.to_csv(f'{self.db_loc}topics_{self.year}.csv', index=False)


if __name__ == '__main__':
    # Set logging format
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='Name of the .vrt file you want to parse')
    parser.add_argument('-d', '--db', type=str, default='topics/', help='Directory where results will be stored')
    args = parser.parse_args()
    # Make sure a .vrt file was given as param
    if args.file.endswith('.vrt'):
        # Start the VRTParser
        ExtractTopic(args.file, args.db).extract()
    else:
        print('Please input a .vrt file')

