from __future__ import annotations

import json
import os
import sys

from collections import OrderedDict


class Entry:
    def __init__(
        self, name, letter, position, name_location, guide_position_location
    ) -> None:
        self.name = name
        self.letter = letter
        self.position = position
        self.name_location = name_location
        self.guide_position_location = guide_position_location

    def __str__(self) -> str:
        openbrack = "{"
        closebrack = "}"
        return f'{openbrack} "name": "{self.name}", "guide_position_location": {self.guide_position_location} {closebrack}'  # , \"position\": {self.position} {closebrack}'


def export_data(dictfile: str, outputfile: str) -> None:
    with open(dictfile, "rb") as f:
        f.seek(0x2C, os.SEEK_SET)  # skip to first unit (should be Avatar)
        entries: dict[str, list[Entry]] = {}
        while True:
            # get pointer to the character's internal name and add 0x20 bytes to account for file header
            unitptr = int.from_bytes(f.read(2), "little") + 0x20

            # skip to the character's guide alphabetization data
            f.seek(10, os.SEEK_CUR)

            guide_position_location = f.tell()

            # get the letter this character is indexed by in the guide
            letter = chr(int.from_bytes(f.read(1), "little"))

            # skip next byte (unknown purpose)
            f.read(1)

            # position of the character's name within it's letter grouping
            position = str(int.from_bytes(f.read(1), "little"))

            # save current position so we can jump back here
            saved_pos = f.tell()

            # go grab the current characters internal name
            f.seek(unitptr, os.SEEK_SET)
            unitname = ""
            while True:
                nextbyte = f.read(1)
                if nextbyte == b"\x00":
                    break
                unitname += chr(int.from_bytes(nextbyte, "little"))
            if entries.get(letter) is None:
                entries[letter] = []
            entries[letter].append(
                Entry(unitname, letter, position, unitptr, guide_position_location)
            )

            # hardcode the last guide entry, there's a better way to do this but it works
            if saved_pos == 0x116B:
                break

            f.seek(saved_pos + 0x1D, os.SEEK_SET)

        with open(outputfile, "w") as output:
            output.write("{\n")
            orderedentries = OrderedDict(sorted(entries.items()))
            for i, (letter, orderedentries) in enumerate(orderedentries.items()):
                output.write(f'  "{letter}":\n    [\n')
                orderedentries.sort(key=lambda e: (e.letter, int(e.position)))
                for j, entry in enumerate(orderedentries):
                    output.write(f"      {entry}")
                    if j < len(orderedentries) - 1:
                        output.write(",")
                    output.write("\n")
                output.write("    ]")
                if i < len(entries.keys()) - 1:
                    output.write(",")
                output.write("\n")
            output.write("}\n")


def import_data(inputfilename: str, dictfilename: str) -> None:
    with open(dictfilename, "r+b") as dictfile:
        with open(inputfilename, "r") as inputfile:
            indata: dict[str, dict] = json.load(inputfile)
            char_no = 1
            for letter, entries in indata.items():
                for entry in entries:
                    dictfile.seek(entry.get("guide_position_location"), os.SEEK_SET)
                    dictfile.write(int.to_bytes(ord(letter), 1, "little"))
                    dictfile.seek(dictfile.tell() + 1)
                    dictfile.write(int.to_bytes(char_no, 1, "little"))
                    char_no += 1


def main() -> None:
    if len(sys.argv) != 4 or (sys.argv[1] != "-import" and sys.argv[1] != "-export"):
        print("ERROR: Invalid arguments provided.")
        print("\nUSAGE: python guide.py -[import|export] inputfile outputfile")
        print("\nTo export a FE12 dictionary to editable JSON:")
        print("\tpython guide.py -export FE12Dictionary.bin dict.json")
        print("\nTo import a valid JSON file into a FE12 dictionary file:")
        print("\tpython guide.py -import dict.json FE12Dictionary.bin")
        exit(1)

    if sys.argv[1] == "-import":
        import_data(sys.argv[2], sys.argv[3])

    else:
        export_data(sys.argv[2], sys.argv[3])

    print("Done.")


if __name__ == "__main__":
    main()
