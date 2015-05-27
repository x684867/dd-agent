
import os
import threading
from checks import AgentCheck

class EximCheck(AgentCheck):
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
        config = self._get_config(instance)

        logfile=config['logfile']
        tags = config['tags']

        self._get_queue_stats(tags)

        return {'tags': tags}

    def _get_queue_stats(self,tags):
        p1=subprocess.Popen(['mailq'],bufsize=8192,stdout=subprocess.PIPE)
        p2=subprocess.Popen(['wc','-l'],bufsize=65536,stdin=p1.stdout,stdout=subprocess.PIPE)
        count=0
        try:
            count=int(p2.communicate()[0])
        except Exception as e:
            pass
        self.gauge('mail.queue.size', count, tags=tags)
