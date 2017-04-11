from mycroft.knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

import wptools

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class WikipediaService(KnowledgeBackend):
    def __init__(self, config, emitter, name='wikipedia'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.subject = None
        self.emitter.on('WikipediaKnowledgeAdquire', self._adquire)

    def set_subject(self, subject):
        self.subject = subject

    def _adquire(self, message=None):
        logger.info('WikipediaKnowledge_Adquire')
        if self.subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            node_data = {}
            subject = self.subject
            # get knowledge about
            # TODO exceptions for erros
            try:
                page = wptools.page(subject).get_query()
                node_data["pic"] = page.image('page')['url']
                node_data["name"] = page.label
                node_data["description"] = page.description
                node_data["summary"] = page.extext
                node_data["url"] = page.url
                # parse infobox
                node_data["infobox"] = self.parse_infobox(subject)
                # id info source
                dict["wikipedia"] = node_data
                self.emit_node_info(dict)
            except:
                logger.error("Could not parse wikipedia for " + str(subject))

    def parse_infobox(self, subject):
        page = wptools.page(subject).get_parse()
        data = {}
        # TODO decent parsing, info is messy
        for entry in page.infobox:
            print entry + " : " + page.infobox[entry]
            data[entry] = page.infobox[entry]

        return data


    def adquire(self):
        logger.info('Call WikipediaKnowledgeAdquire')
        self.emitter.emit(Message('WikipediaKnowledgeAdquire'))

    def emit_node_info(self, info):
        # TODO emit node_info for node manager to update/create node
        for source in info:
            print source
            for key in source:
                print key + " : " + str(source[key])

    def stop(self):
        logger.info('WikipediaKnowledge_Stop')
        self.subject = None
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wikipedia']
    instances = [WikipediaService(s[1], emitter, s[0]) for s in services]
    return instances