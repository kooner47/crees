from pynput import keyboard
from pynput.keyboard import Listener, Key
import time
from event import Event
from bader import execute_events, read_events
from lager import Logger, events2log
import traceback

FILES_FOLDER = './data'

'''



'''


class StateMachine:
    def __init__(self):
        self.segments = []
        self.segment_id = 0
        self.stop_execution = False

    def print_segments(self):
        print("Current segments:")
        for s in self.segments:
            id = s[0]
            events = s[1]
            length_seconds = events[-1].timestamp if events else 0
            print("    Segment %2d: length %.2fs" % (id, length_seconds))

    def start(self):
        while True:
            print("Enter a command:")

            string = str(input())
            if string.startswith('n'):
                events = []
                logger = Logger(events)
                logger.run()
                self.segments.append((self.segment_id, events))
                self.segment_id += 1
                print("Stopping recording.")
                self.print_segments()
            elif string.startswith("s"):
                try:
                    [_, idstr, filename] = string.split(' ')
                    id = int(idstr)
                except ValueError as e:
                    print(traceback.format_exc())
                    continue
                wrote = False
                for s in self.segments:
                    if s[0] == id:
                        print("Writing segment %d to %s." % (id, filename))
                        f = open('%s/%s' % (FILES_FOLDER, filename), 'w')
                        f.write(events2log(s[1]))
                        f.close()
                        wrote = True
                        break
                if wrote:
                    print("Finished writing.")
                else:
                    print("Invalid segment id.")
                continue
            elif string.startswith("d"):
                try:
                    [_, idstr] = string.split(' ')
                    id = int(idstr)
                except ValueError as e:
                    print(traceback.format_exc())
                    continue
                deleted = False
                for s in self.segments:
                    if s[0] == id:
                        self.segments.remove(s)
                        deleted = True
                        break
                if deleted:
                    print("Deleted segment %d." % (id))
                    self.print_segments()
                else:
                    print("Segment %d not found." % (id))
                continue
            elif string.startswith("e"):
                try:
                    [_, idstr] = string.split(' ')
                    id = int(idstr)
                except ValueError as e:
                    print(traceback.format_exc())
                    continue
                executed = False
                for s in self.segments:
                    if s[0] == id:
                        print("Executing events in segment %d in 3 seconds." % (id))
                        time.sleep(3)
                        print("Beginning execution.")
                        execute_events(s[1])
                        executed = True
                        break
                if executed:
                    print("Finished executing.")
                else:
                    print("Segment %d not found." % (id))
                continue
            elif string.startswith("a"):
                try:
                    [_, id1str, id2str] = string.split(' ')
                    id1 = int(id1str)
                    id2 = int(id2str)
                except ValueError as e:
                    print(traceback.format_exc())
                    continue
                s1 = None
                s2 = None
                for s in self.segments:
                    if s[0] == id1:
                        s1 = s
                    if s[0] == id2:
                        s2 = s
                if s1 is None:
                    print("Segment %d not found." % (id))
                elif s2 is None:
                    print("Segment %d not found." % (id))
                else:
                    print("Appending %d events from segment %d at the end of segment %d." % (
                        len(s2[1]), id2, id1))
                    time_offset = s1[1][-1].timestamp if s1[1] else 0.0

                    length = len(s2[1])
                    for i in range(length):
                        event = s2[1][i]
                        s1[1].append(event.offset_time(time_offset))
                    self.print_segments()
                continue
            elif string.startswith("r"):
                try:
                    [_, filename] = string.split(' ')
                except ValueError as e:
                    print(traceback.format_exc())
                    continue
                print("Reading events from %s into segment %d." %
                      (filename, self.segment_id))
                events = read_events('%s/%s' % (FILES_FOLDER, filename))
                self.segments.append((self.segment_id, events))
                self.segment_id += 1
                self.print_segments()
                continue
            elif string.startswith("v"):
                try:
                    [_, idstr] = string.split(' ')
                    id = int(idstr)
                except ValueError as e:
                    print(traceback.format_exc())
                    continue
                printed = False
                for s in self.segments:
                    if s[0] == id:
                        print("Printing last 5 events from segment %d." % (id))
                        events = s[1]
                        for i in range(len(events) - 1, max(len(events) - 6, 0), -1):
                            print(events[i].to_string())
                        printed = True
                        break
                if not printed:
                    print("Segment %d not found." % (id))
                continue
            elif string.startswith("p"):
                try:
                    [_, idstr] = string.split(' ')
                    id = int(idstr)
                except ValueError as e:
                    print(traceback.format_exc())
                    continue
                deleted = False
                for s in self.segments:
                    if s[0] == id:
                        print("Deleting last event from segment %d." % (id))
                        events = s[1]
                        events.pop()
                        print("Printing new last 5 events from segment %d." % (id))
                        for i in range(len(events) - 1, max(len(events) - 6, 0), -1):
                            print(events[i].to_string())
                        deleted = True
                        break
                if not deleted:
                    print("Segment %d not found." % (id))
                continue
            elif string.startswith("q"):
                print("Exiting.")
                exit()


def main():
    state_machine = StateMachine()

    print("Commands:")
    print("    n to record a new segment")
    print("    s <number> <filename> to save segment <number> to <filename> (overwrite contents)")
    print("    d <number> to delete segment <number>")
    print("    e <number> to execute segment <number>")
    print("    a <number1> <number2> to append segment <number2> to segment <number1>")
    print("    r <filename> to read <filename> into a new segment")
    print("    v <number> to view the last 5 recorded events in segment <number>")
    print("    p <number> to pop the last recorded event from segment <number>")
    print("    q to quit")

    state_machine.start()


if __name__ == '__main__':
    main()
