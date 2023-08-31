# Neurobooth_Personal

This script goes through all of the BIN files in a specified folder and pulls out the first n lines of code from them, 
which contain all of the important information we need about the Geneactive devices. The script also looks at device drift and flags files with a drift larger than 99.999s.


Please rename the folder input and output before running. A condensed file is made at the output folder,
named "condensed_{filename}" or "flagged_condensed_{filename}". The latter name is given to flagged files. 
