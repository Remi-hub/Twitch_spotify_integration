# import os
#
#
# def write_files(filename, values, keys, overwrite=False):
#     if not os.path.isfile(filename) or overwrite == True:
#         with open(filename, "w") as f:
#             for i in range(len(values)):
#                 f.write(keys[i] + ";" + values[i] + "\n")
#             f.close()
#
#
# def read_informations(filename, key):
#     informations = {}
#     if os.path.isfile(filename):
#         with open(filename, "r") as f:
#             for line in f:
#                 split_line = line.split(";")
#                 if len(split_line) == 2:
#                     informations[split_line[0]] = split_line[1].strip("\n")
#             f.close()
#             if key in informations:
#                 return informations[key]
#             return None
#     else:
#         return None
