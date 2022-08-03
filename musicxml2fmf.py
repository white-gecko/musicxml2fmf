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
BPM: {bpm}
Duration: {duration}
Octave: {octave}
Notes: """


class Note:
    def __init__(self, duration=8, step="C", sharp="", octave=5, dot=""):
        self.duration = duration
        self.step = step
        self.sharp = sharp
        self.octave = octave
        self.dot = dot

    def __str__(self):
        return f"{self.duration}{self.step}{self.sharp}{self.octave}{self.dot}"


class Rest:
    def __init__(self, duration=8, dot=""):
        self.duration = duration
        self.dot = dot

    def __str__(self):
        return f"{self.duration}P{self.dot}"


@click.command()
@click.option("--input", help="File to read the MusicXML from (suffix: '.musicxml').")
@click.option("--output", help="File to write the Flipper Music to (suffix: '.fmf').")
@click.option("--bpm", default=120, help="Beats per minute for the piece (default: 120).")
@click.option("--duration", default=8, help="Default duration of a tone (default: 8).")
@click.option("--octave", default=5, help="Default octave of a note (default: 5).")
def convert(input, output, bpm, duration, octave):
    flipperNotes = []
    tree = etree.parse(input)
    musicXmlNotes = tree.xpath("//score-partwise/part/measure/note")
    for noteTag in musicXmlNotes:
        noteDuration = noteTag.xpath("duration")[0].text
        flipperDuration, dot = durations[int(noteDuration)]
        if noteTag.xpath("rest"):
            flipperNotes.append(Rest(flipperDuration))
            continue
        alter = False
        if noteTag.xpath("pitch/alter"):
            alter = int(noteTag.xpath("pitch/alter")[0].text)
        step = noteTag.xpath("pitch/step")[0].text
        octave = int(noteTag.xpath("pitch/octave")[0].text)
        sharp = ""
        if alter:
            if alter < 0:
                step, octaveShift = downsteps[step]
                octave = octave + octaveShift
            sharp = "#"
        note = Note(flipperDuration, step, sharp, octave, dot)
        flipperNotes.append(note)

    with open(output, 'w') as o:
        o.write(filetypeHeader.format(bpm=bpm, duration=duration, octave=octave))
        o.write(", ".join(str(n) for n in flipperNotes))
