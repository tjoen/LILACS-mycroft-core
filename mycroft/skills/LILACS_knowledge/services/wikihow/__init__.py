import bs4
from os.path import abspath

import requests

from mycroft.messagebus.message import Message
from mycroft.skills.LILACS_knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class WikiHowService(KnowledgeBackend):
    def __init__(self, config, emitter, name='wikihow'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('WikihowKnowledgeAdquire', self._adquire)

    def _adquire(self, message=None):
        logger.info('WikihowKnowledge_Adquire')
        subject = message.data["subject"]
        if subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                how_to = self.how_to(subject)
                dict["wikihow"] = how_to
            except:
                logger.error("Could not parse wikihow for " + str(subject))
            self.send_result(dict)

    def search_wikihow(self, search_term):
        # print "Seaching wikihow for " + search_term
        search_url = "http://www.wikihow.com/wikiHowTo?search="
        search_term_query = search_term.replace(" ", "+")
        search_url += search_term_query
        # print search_url
        # open url
        html = self.get_html(search_url)
        soup = bs4.BeautifulSoup(html, "lxml")
        # parse for links
        list = []
        links = soup.findAll('a', attrs={'class': "result_link"})
        for link in links:
            url = "http:" + link.get('href')
            list.append(url)
        return list

    def get_html(self, url):
        headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0"}
        r = requests.get(url, headers=headers)
        html = r.text.encode("utf8")
        return html

    def get_steps(self, url):
        # open url
        html = self.get_html(url)
        soup = bs4.BeautifulSoup(html, "lxml")
        # get title
        title_html = soup.findAll("h1", {"class": "firstHeading"})
        for html in title_html:
            url = "http:" + html.find("a").get("href")
        title = url.replace("http://www.wikihow.com/", "").replace("-", " ")
        # get steps
        steps = []
        ex_steps = []
        step_html = soup.findAll("div", {"class": "step"})
        for html in step_html:
            step = html.find("b")
            step = step.text

            trash = str(html.find("script"))
            trash = trash.replace("<script>", "").replace("</script>", "").replace(";", "")
            ex_step = html.text.replace(trash, "")

            trash_i = ex_step.find("//<![CDATA[")
            trash_e = ex_step.find(">")
            trash = ex_step[trash_i:trash_e + 1]
            ex_step = ex_step.replace(trash, "")

            trash_i = ex_step.find("http://")
            trash_e = ex_step.find(".mp4")
            trash = ex_step[trash_i:trash_e + 4]
            ex_step = ex_step.replace(trash, "")

            trash = "WH.performance.mark('step1_rendered');"
            ex_step = ex_step.replace(trash, "")
            ex_step = ex_step.replace("\n", "")

            steps.append(step)
            ex_steps.append(ex_step)

        # get step pic
        pic_links = []
        pic_html = soup.findAll("a", {"class": "image lightbox"})
        for html in pic_html:
            html = html.find("img")
            i = str(html).find("data-src=")
            pic = str(html)[i:].replace('data-src="', "")
            i = pic.find('"')
            pic = pic[:i]
            pic_links.append(pic)

        return title, steps, ex_steps, pic_links, url

    def how_to(self, subject):
        how_tos = {}
        links = self.search_wikihow(subject)
        if links == []:
            print "No wikihow results"
            return
        for link in links:
            try:
                how_to = {}
                # get steps and pics
                title, steps, descript, pics, link = self.get_steps(link)
                how_to["title"] = title
                how_to["steps"] = steps
                how_to["detailed"] = descript
                how_to["pics"] = pics
                how_to["url"] = link
                how_tos[title] = how_to
            except:
                print "error, skipping link " + link
        return how_tos

    def random_how_to(self):
        link = "http://www.wikihow.com/Special:Randomizer"
        # get steps and pics
        title, steps, descript, pics, link = self.get_steps(link)
        how_to = {}
        how_to["title"] = title
        how_to["steps"] = steps
        how_to["detailed"] = descript
        how_to["pics"] = pics
        how_to["url"] = link
        return how_to

    def adquire(self, subject):
        logger.info('Call WikihowKnowledgeAdquire')
        self.emitter.emit(Message('WikihowKnowledgeAdquire', {"subject": subject}))

    def send_result(self, result = {}):
        self.emitter.emit(Message("LILACS_result", {"data": result}))

    def stop(self):
        logger.info('WikihowKnowledge_Stop')
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wikihow']
    instances = [WikiHowService(s[1], emitter, s[0]) for s in services]
    return instances
