#!/usr/bin/env python3

import click
from lxml import etree

downsteps = {
    "C": ("B", -1),
    "D": ("C", 0),
    "E": ("D", 0),
    "F": ("E", 0),
    "G": ("F", 0),
    "A": ("G", 0),
    "B": ("A", 0)
}

durations = {
    1: (8, ""),
    2: (4, ""),
    3: (4, "."),
    4: (2, ""),
    6: (2, "."),
    8: (1, "")
}

filetypeHeader = """Filetype: Flipper Music Format
Version: 0
BPM: 90
Duration: 8
Octave: 5
Notes: """


@click.command()
@click.option("--input")
@click.option("--output")
def convert(input, output):
    with open(output, 'w') as o:
        o.write(filetypeHeader)
        tree = etree.parse(input)
        res = tree.xpath("//score-partwise/part/measure/note")
        for note in res:
            duration = note.xpath("duration")[0].text
            fduration, fdot = durations[int(duration)]
            if note.xpath("rest"):
                o.write(f"{fduration}P, ")
                continue
            alter = False
            if note.xpath("pitch/alter"):
                alter = int(note.xpath("pitch/alter")[0].text)
            step = note.xpath("pitch/step")[0].text
            octave = int(note.xpath("pitch/octave")[0].text)
            sharp = ""
            if alter:
                if alter < 0:
                    step, octaveShift = downsteps[step]
                    octave = octave + octaveShift
                sharp = "#"
            o.write(f"{fduration}{step}{sharp}{octave}{fdot}, ")
