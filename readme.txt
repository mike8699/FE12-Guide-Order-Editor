A small command-line program to modify the order of character names and locations in the FE12 "Guide"/"Index" screen.


To export a FE12 dictionary to editable JSON:
        python guide.py -export FE12Dictionary.bin dict.json

To import a valid JSON file into a FE12 dictionary file:    
        python guide.py -import dict.json FE12Dictionary.bin


The 'FE12 dictionary' referred to above is the file located in the FE12 ROM at `data/data/FE12Dictionary.bin`.

The order can be edited by exporting a JSON file (see above) and cutting and pasting the various character JSON objects to new spots.

***********************************************************************************************************************************************
* NOTE: make sure not to modify the 'guide_position_location' field in the JSON file or the program will be unable to reimport the JSON file. *
***********************************************************************************************************************************************
