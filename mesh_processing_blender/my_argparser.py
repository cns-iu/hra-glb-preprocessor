import sys
import os

class MyArgParser:

    def __init__(self):
        self.argv = sys.argv
        self.max_triangles = -1
        self.levels = {}
        self.max_triangles = {}
        self.input_file_path = ""
        self.parse()


    def parse(self):
        try:
            index = self.argv.index("--") + 1
        except ValueError:
            index = len(self.argv)

        try: 
            while index < len(self.argv):
                if self.argv[index] == '-input_file_path':
                    self.input_file_path = self.argv[index + 1]
                    index += 1
                elif self.argv[index] == '-lod':
                    level = int(self.argv[index + 1])
                    filename = self.argv[index + 2]
                    self.levels[level] = filename
                    index += 2
                elif self.argv[index] == '-max_triangles':
                    max_triangle = int(self.argv[index + 1])
                    filename = self.argv[index + 2]
                    self.max_triangles[max_triangle] = filename
                    index += 2
                
                index += 1
        except ValueError:
            print("please check argments!")

    
