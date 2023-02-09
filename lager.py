from pynput import keyboard
from pynput.keyboard import Listener, Key
import time
from event import Event


def events2log(events):
    output = ''
    prev_time = 0.0
    for event in events:
        output += '%s\n' % (event.to_string(-prev_time))
        prev_time = event.timestamp
    return output


class Logger:
    def __init__(self, events):
        self.events = events
        self.pause_log = False
        self.offset = 0

    def elapsed_time(self):
        return time.time() - self.start_time + self.offset

    def key2name(self, key):
        key_str = str(key).strip("'").strip("\n")
        if len(key_str) == 1:
            # letter
            return 'DIK_%s' % (key_str.upper())
        elif key_str.startswith('Key.'):
            key_str_rest = key_str.split('Key.')[1]
            return 'DIK_%s' % (key_str_rest.upper().replace('_', ''))

    def key_press(self, key):
        if key == Key.pause:
            return False
        elif key == Key.backspace:
            print("Pausing recording.")
            self.paused_time = time.time()
            self.pause_log = True
            return
        elif key == Key.space:
            print("Resuming")
            self.start_time = time.time()
            self.offset += self.start_time - self.paused_time
            self.pause_log = False
            return

        if not self.pause_log:
            keyName = self.key2name(key)
            self.events.append(Event('press', keyName, self.elapsed_time()))

    def key_release(self, key):
        if not self.pause_log:
            keyName = self.key2name(key)
            self.events.append(Event('release', keyName, self.elapsed_time()))

    def run(self):
        print("Recording events.")
        print("Press PAUSE to stop recording.")
        print("Press BACKSPACE to pause recording, then SPACE to resume recording.")
        self.start_time = time.time()
        with Listener(
                on_press=self.key_press, on_release=self.key_release) as listener:
            listener.join()


def main():
    events = []
    logger = Logger(events)
    logger.run()
    output = events2log(events)
    f = open("crees.txt", 'w')
    f.write(output)
    f.close()


if __name__ == '__main__':
    main()
