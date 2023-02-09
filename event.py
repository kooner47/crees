class Event:
    def __init__(self, action, keyName, timestamp):
        self.action = action
        self.keyName = keyName
        self.timestamp = timestamp

    @staticmethod
    def from_line(line, time_offset):
        [action, keyName, timestamp] = line.split(',')
        return Event(action, keyName, float(timestamp) + time_offset)

    def to_string(self, time_offset):
        return '%s,%s,%.6f' % (self.action, self.keyName, self.timestamp + time_offset)

    def offset_time(self, time_offset):
        return Event(self.action, self.keyName, self.timestamp + time_offset)
