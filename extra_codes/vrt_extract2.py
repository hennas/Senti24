import time
import logging
import argparse
import pandas as pd
import statistics
import xml.etree.ElementTree as XML


class VRTExtract2:
    def __init__(self, vrt_file: str, db_loc: str):
        self.logger = logging.getLogger('vrt-extract2')
        self.df = pd.DataFrame()  # thread_id, year, month, datetime, title, text, sentiment...
        self.db_loc = db_loc
        self.year = self.get_year(vrt_file)
        self.filename = vrt_file
        self.thread_info = []

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

    def is_thread_info(self, line: str) -> bool:
        # Remove possible leading spaces
        return line.lstrip().startswith('<text comment_id="0"')

    def extract(self):
        file = self.load_vrt()
        self.logger.info('Extracting threads')
        start = time.time()
        thread = []
        deleted = 0
        reading_thread = False
        for line in file:
            if not line.startswith('</text>') and (self.is_thread_info(line) or reading_thread):
                reading_thread = True
                thread.append(line)
            elif reading_thread and line.startswith('</text>'):
                thread.append(line)
                thread = ''.join(thread)
                xml_tree = XML.fromstring(thread)
                xml_attributes = xml_tree.attrib
                title, text, word_type = [[] for i in range(3)]
                for col in xml_tree.findall('paragraph'):
                    for sentence in col.findall('sentence'):
                        for l in sentence.text.split('\n'):
                            if l is not '':
                                l = l.split('\t')
                                if col.get('type') == 'title':
                                    title.append(l[2])
                                elif col.get('type') == 'body':
                                    text.append(l[2])
                                word_type.append(l[4])
                save_thread = True
                try:
                    if statistics.mode(word_type) == 'Foreign':
                        deleted += 1
                        save_thread = False
                except statistics.StatisticsError:
                    pass
                if save_thread:
                    self.thread_info.append([
                        xml_attributes['thread_id'],
                        xml_attributes['date'][0:4],
                        xml_attributes['date'][5:7],
                        xml_attributes['datetime'],
                        ' '.join(title),
                        ' '.join(text)
                    ])
                reading_thread = False
                thread = []
        self.logger.info(f'Extraction done, took {time.time()-start}s')
        self.logger.info(f'Ignored {deleted} threads for the year {self.year}')
        self.save()

    def save(self):
        self.logger.info(f'Saving results to {self.db_loc}s24_{self.year}.csv')
        df = pd.DataFrame(self.thread_info, columns=['thread_id', 'year', 'month', 'datetime', 'title', 'text'])
        df.to_csv(f'{self.db_loc}s24_{self.year}.csv', index=False)


if __name__ == '__main__':
    # Set logging format
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='Name of the .vrt file you want to parse')
    parser.add_argument('-d', '--db', type=str, default='database/', help='Directory where results will be stored')
    args = parser.parse_args()
    # Make sure a .vrt file was given as param
    if args.file.endswith('.vrt'):
        # Start the VRTParser
        VRTExtract2(args.file, args.db).extract()
    else:
        print('Please input a .vrt file')
