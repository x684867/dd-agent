
import os
import subprocess
from checks import AgentCheck

class MailCheck(AgentCheck):
    """
    This class performs a log analysis for the exim4 mail server (MTA)

    YAML config options:
        exim log file (logfile)
        None.  This only monitors localhost exim
    """
    def _get_config(self, instance):
        mainlog = instance.get('mainlog', None)
        rejectlog = instance.get('rejectlog', None)
        tags = instance.get('tags', [])
        if not rejectlog or not mainlog:
            raise Exception('missing required yaml config entry')


    def check(self, instance):
        #config = self._get_config(instance)
        tags=['mailq','exim4']
        self._get_queue_stats(tags)
        return {'tags': tags}

    def _get_queue_stats(self,tags):
        #
        # We are gonna do checks in the background and chain them together
        # so we don't pause the healthchecks.
        #
        p1=subprocess.Popen(['mailq'],bufsize=65536,stdout=subprocess.PIPE)
        p2=subprocess.Popen(['wc','-l'],bufsize=65536,stdin=p1.stdout,stdout=subprocess.PIPE)
        count=0
        try:
            count=int(p2.communicate()[0])
        except Exception as e:
            pass
        p1=subprocess.Popen(['wc -l wc -l /var/log/exim4/rejectlog'],bufsize=32,stdout=subprocess.PIPE)
        rejected_count=0
        try:
            rejected_count=int(p1.communicate()[0])
        except Exception as e:
            pass
        p1=subprocess.Popen(['/etc/init.d/exim4'],bufsize=32,stdout=subprocess.PIPE)
        exim_status=9
        try:
            exim_status=int(p1.communicate()[1])
        except Exception as e:
            pass
        self.gauge('mail.queue.size', count, tags=tags)
        self.gauge('mail.reject.log.size',rejected_count,tags=tags)
        self.gauge('mail.exim_runstate',exim_status,tags=tags)