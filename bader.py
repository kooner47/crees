import board
from pynput.keyboard import Key
import time
from event import Event


def curr_time(startTime):
    return time.time() - startTime


def handle_event(event):
    keyName = event.keyName.strip('\n')
    if event.action == 'press':
        board.press_key(keyName)
    else:
        board.release_key(keyName)


def execute_events(events):
    startTime = time.time()
    for event in events:
        while curr_time(startTime) < float(event.timestamp):
            continue
        handle_event(event)


def read_events(fileName):
    with open(fileName, 'r') as key_file:
        key_sequence = key_file.readlines()

    sum_time = 0.0
    events = []
    for line in key_sequence:
        line = line.strip('\n')
        if line.startswith("="):
            continue
        event = Event.from_line(line, sum_time)
        sum_time += event.timestamp - sum_time
        events.append(event)

    return events


def main():
    time.sleep(2)
    events = read_events("crees.txt")
    execute_events(events, lambda: False)


if __name__ == '__main__':
    main()
