from core import Log
from modules.send_mail_lib.Module import send_mail

from circuits import Component
import json
import os
import re


class Module(Component):
    channel = 'log'
    ignore_msg_regex = []
    min_level = 30 # no log debug / info
    tag = ''
    to = []

    def add_email(self, email):
        self.to.append(email)

    def load_configuration(self):
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'configs',
            'config.json'
        )

        if not os.path.isfile(config_path):
            return

        with open(config_path) as config_file:
            config = json.load(config_file)

            if 'min_level' in config:
                self.min_level = config['min_level']

            if 'tag' in config:
                self.tag = config['tag']

            if 'emails' in config:
                if 'your-email@example.com' in config['emails']:
                    Log.error('is the email address example')
                    return

                self.to = config['emails']

            if 'ignore_msg_regex' in config:
                self.ignore_msg_regex = config['ignore_msg_regex']
                self.ignore_msg_regex.append('send_mail_lib') # infinite loop

    def log(self, event, **kwargs):
        if kwargs['levelno'] < self.min_level or not self.to:
            return

        if 'pathname' in kwargs and 'send_mail_lib' in kwargs['pathname']: # infinite loop
            return

        if 'msg' in kwargs: # ignore msg regex
            for regex in self.ignore_msg_regex:
                if re.search(regex, kwargs['msg']):
                    return

        subject = '[LOG]%s[%s] %s' % (
            '[%s]' % self.tag if self.tag else '',
            kwargs['levelname'],
            kwargs['msg'] if len(kwargs['msg']) <= 40 else \
                kwargs['msg'][0:40-3] + '...'
        )
        msg = 'Infos:\n'

        for index in kwargs:
            msg += '    - %s: %s\n' % (index, kwargs[index])

        self.fire(send_mail(subject, self.to, msg))

    def started(self, component):
        self.load_configuration()

