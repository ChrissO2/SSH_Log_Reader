import re
from datetime import datetime


class SSHLog:
    def __init__(self, raw_log, log_pattern=re.compile(
            r"^(?P<date>\w+\s+\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\w+)\s+sshd\[(?P<pid>\d+)\]:\s+(?P<event>.*)"
            ), date_format="%b %d %H:%M:%S"):
        
        self.date_format = date_format
        self.log_pattern = log_pattern
        self.raw_log = raw_log
        conv_log = self.convert_log(raw_log)
        self.date = conv_log.get('date') or 'Invalid'
        self.host = conv_log.get('host') or 'Invalid'
        self.pid = conv_log.get('pid') or 'Invalid'
        self.event = conv_log.get('event') or 'Invalid'

    def convert_log(self, log):
        re_log = re.match(self.log_pattern, log)
        if re_log:
            result = {}
            result['date'] = datetime.strptime(re_log.group('date'), self.date_format)
            result['host'] = re_log.group('host')
            result['pid'] = re_log.group('pid')
            result['event'] = re_log.group('event')
            return result
        return None

    def get_date(self):
        return datetime.strftime(self.date, self.date_format)

    def get_ipv4s(self):
        ipv4s = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", self.raw_log)
        return set([str(ip) for ip in ipv4s])
    

class LogJournal:
    def __init__(self, log_pattern=re.compile(
            r"^(?P<date>\w+\s+\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\w+)\s+sshd\[(?P<pid>\d+)\]:\s+(?P<event>.*)"
            ), date_format="%b %d %H:%M:%S"):
        self.logs = []
        self.log_pattern = log_pattern
        self.date_format = date_format
    
    def get_str_log_list(self):
        return [log.raw_log for i, log in enumerate(self.logs)]
    
    def read_log_file(self, filename):
        with open(filename, "r") as f:
            for line in f:
                if re.match(self.log_pattern, line):
                    self.logs.append(SSHLog(line, log_pattern=self.log_pattern, date_format=self.date_format))

    def __len__(self):
        return len(self.logs)

    def __iter__(self):
        return iter(self.logs)
    
    def __contains__(self, log_str):
        return log_str in [log.raw_log for log in self.logs]
    
    def find_log_index(self, log_str):
        for i in range(len(self.logs)):
            if self.logs[i].raw_log == log_str:
                return i
        return -1
    
    def get_log_of_str(self, log_str):
        for log in self.logs:
            if log.raw_log == log_str:
                return log
        return None
    
    def return_filtered_logs(self, **kwargs):
        filtered_logs = self.logs
        if 'start_date' in kwargs:
            try:
                start_date = datetime.strptime(kwargs['start_date'], self.date_format)
                filtered_logs = [log for log in filtered_logs if log.date >= start_date]
            except ValueError:
                pass
        if 'end_date' in kwargs:
            try:
                end_date = datetime.strptime(kwargs['end_date'], self.date_format)
                filtered_logs = [log for log in filtered_logs if log.date <= end_date]
            except ValueError:
                pass
        if 'ip' in kwargs:
            ip = kwargs['ip']
            if ip:
                filtered_logs = [log for log in filtered_logs if ip in log.get_ipv4s()]

        return [log.raw_log for log in filtered_logs]

    


    
    


