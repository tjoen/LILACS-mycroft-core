# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.skills.LILACS.concept import ConceptConnector, ConceptCrawler
from mycroft.skills.LILACS.storage import ConceptStorage

from os.path import dirname

storagepath = ""

logger = getLogger("Skills")

__authors__ = ["jarbas", "heinzschmidt"]

class LilacsSkill(MycroftSkill):

    def __init__(self):
        super(LilacsSkill, self).__init__(name="LilacsSkill")
        self.reload_skill = False

    def initialize(self):
        self.storagepath = str(dirname(__file__) + "/.db/")
        act_intent = IntentBuilder("ActivateIntent") \
            .require("ActivateKeyword") \
            .build()

        self.register_intent(act_intent, self.handle_act_intent)

    def handle_act_intent(self, message):
        knowledge = ConceptConnector(logger)
        storage = ConceptStorage(self.storagepath)

        self.speak("Reading concepts from db test")
      #  nodenames = {}
      #  for nodes in storage.getNodesAll():
      #      nodenames = nodes
      #      name = nodes
      #      parent_concepts = storage.getNodeParent(conceptname=str(name))
      #      child_concepts = storage.getNodeChildren(conceptname=str(name))
      #      knowledge.create_concept(name, parent_concepts=parent_concepts,
      #                               child_concepts=child_concepts)

        # create concepts for testing
        self.speak("Creating coded concepts test")
        name = "human"
        child_concepts = {"male": 1, "female": 1}
        parent_concepts = {"animal": 2, "mammal": 1}
        knowledge.create_concept(name, parent_concepts=parent_concepts,
                                 child_concepts=child_concepts)

        print "\n\n"
        name = "joana"
        child_concepts = {"wife": 1}
        parent_concepts = {"female": 2, "human": 1}
        knowledge.create_concept(name, parent_concepts=parent_concepts,
                                 child_concepts=child_concepts)

        print "\n\n"
        name = "animal"
        child_concepts = {"dog": 1, "cow": 1, "frog": 1, "cat": 1, "spider": 1, "insect": 1}
        parent_concepts = {"alive": 1}
        knowledge.create_concept(name, parent_concepts=parent_concepts,
                                 child_concepts=child_concepts)



        # lets see what concept connector can deduce from here
        key = "joana"
        childs = knowledge.concepts[key].child_concepts
        parents = knowledge.concepts[key].parent_concepts

        self.speak(key + " can be: ")
        for child in childs:
            self.speak(child + " from generation " + str(childs[child]))

        # in case of Joana everything here except human was deduced
        self.speak(key + " is:")
        for parent in parents:
            self.speak(parent + " from generation " + str(parents[parent]))

        # Crawler test
        crawler = ConceptCrawler(concept_connector=knowledge, center_node="joana")

        next = crawler.choose_next_node("joana")
        next = crawler.choose_next_node(next)
        next = crawler.choose_next_node(next)
        next = crawler.choose_next_node(next)

    def stop(self):
        pass


def create_skill():
    return LilacsSkill()


