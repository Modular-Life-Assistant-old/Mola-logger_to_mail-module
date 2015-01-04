from core import Log
from modules.send_mail_lib.Module import send_mail

from circuits import Component
import json
import os

class Module(Component):
    channel = 'log'
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
                if 'your-email@example.com' in config['emails']
                    Log.error('is the email address example')
                    return

                self.to = config['emails']

    def log(self, event, **kwargs):
        if kwargs['levelno'] < self.min_level or not self.to:
            return

        if 'pathname' in kwargs and 'send_mail_lib' in kwargs['pathname'] or \
                'msg' in kwargs and 'send_mail_lib' in kwargs['msg']: # infinite loop
            return

        subject = '[LOG]%s[%s] %s' % (
            '[%s]' % self.tag if self.tag else '',
            kwargs['levelname'],
            kwargs['msg'] if len(kwargs['msg']) <= 40 else kwargs['msg'][0:40-3] + '...'
        )
        msg = 'Infos:\n'

        for index in kwargs:
            msg += '    - %s: %s\n' % (index, kwargs[index])

        self.fire(send_mail(subject, self.to, msg))

    def started(self, component):
        self.load_configuration()

