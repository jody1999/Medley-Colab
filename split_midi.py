import numpy as np
import pretty_midi
from os import listdir, mkdir, walk
import os
from os.path import isfile, join
from mido import MidiFile


def get_beats_intervals(pm, midiFile):
    # Note that the beat phase will be wrong until the first time signature change after 0s
    # So, let's start beat tracking from that point
    first_ts_after_0 = [ts.time for ts in pm.time_signature_changes if ts.time > 0.][0]
    # Get down beats from pretty_midi, supplying a start time
    downbeats = pm.get_downbeats(start_time=first_ts_after_0)
    bars = np.append([0], downbeats)
    bars = np.append(bars, [midiFile.length])
    #print(bars)

    return bars


def bars_split(song_path, new_path):
    try:
        pm = pretty_midi.PrettyMIDI(song_path)
        midiFile = MidiFile(song_path)
    except (OSError):
        return None

    partitions = get_beats_intervals(pm, midiFile)

    for partition in range(len(partitions) - 1):
        start_time = partitions[partition]
        end_time = partitions[partition + 1]

        new_midi = pretty_midi.PrettyMIDI()
        for instr_num in range(len(pm.instruments)):
            instrument = (pm.instruments[instr_num])

            notes_velocity = []
            notes_pitch = []
            notes_start = []
            notes_end = []

            # the first note after start_time is called note_num
            for start_note_num in range(len(instrument.notes)):
                note = instrument.notes[start_note_num]
                start = note.start
                if start >= start_time:
                    break

            for end_note_num in range(len(instrument.notes)):
                note = instrument.notes[end_note_num]
                end = note.end
                if end > end_time:
                    break
            # record the notes and info in the original midi file
            for k in range(start_note_num, end_note_num):
                note = instrument.notes[k]
                notes_pitch.append(note.pitch)
                notes_start.append(note.start)
                notes_end.append(note.end)
                notes_velocity.append(note.velocity)

            program = instrument.program
            is_drum = instrument.is_drum
            name = instrument.name
            inst = pretty_midi.Instrument(program=program, is_drum=is_drum, name=name)
            new_midi.instruments.append(inst)

            # copy into new midi
            for i in range(end_note_num - start_note_num):
                inst.notes.append(
                    pretty_midi.Note(notes_velocity[i], notes_pitch[i], notes_start[i] - float(start_time),
                                     notes_end[i] - float(start_time)))

        file_path = os.path.join(new_path, 'part' + str(partition) + '.mid')
        new_midi.write(file_path)
        #print(file_path)
    #print('finished processing song ' + song_path)

def process_folder(song_path):
    songs = [f for f in listdir(song_path) if isfile(join(song_path, f))]
    print('Total % songs in the folder' %str(len(songs)))
    try:
        for song_name in songs:
            print(song_name)
            new_path = song_path + "_" + song_name.split('.')[0]
            mkdir(new_path)
            bars_split(os.path.join(song_path, song_name), new_path)
    except:
        print ("exception")
    print('Folder ' + song_path +  ' done')

# code for clean_midi dataset
def process_clean_midi():
    subdirs_clean = [x[0] for x in walk('/Users/mac/Desktop/data/clean_midi')][1:]
    for subdir in subdirs_clean:
        process_folder(subdir)

# code for lmd_aligned dataset
def process_aligned_midi():
    subdirs_aligned = [x[0] for x in walk('/Users/mac/Desktop/data/lmd_aligned')][1:]
    for sub1dir in subdirs_aligned:
        sub1dirs = [x[0] for x in walk(sub1dir)][1:]
        for sub2dir in sub1dirs:
            sub2dirs = [x[0] for x in walk(sub2dir)][1:]
            for sub3dir in sub2dirs:
                sub3dirs = [x[0] for x in walk(sub3dir)][1:]
                for msd_id_dir in sub3dirs:
                    process_folder(msd_id_dir)

# code for unique_midi
def process_full_unique_midi():
    subdirs_unique = [x[0] for x in walk('/Users/mac/Desktop/data/unique_midi')][1:]
    for subdir in subdirs_unique:
        process_folder(subdir)

process_aligned_midi()