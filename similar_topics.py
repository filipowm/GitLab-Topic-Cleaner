import re

import Levenshtein as lev

import guards
import logger


class SimilarTopicsIdentifier(object):

    def __init__(self, gitlab, discard_patterns=None, sensitivity=1):
        guards.against_none(gitlab, "GitLab client")
        guards.against_none(sensitivity, "Sensitivity")
        self.gitlab = gitlab
        self.sensitivity = sensitivity
        self.discard_pattern = re.compile('|'.join(discard_patterns)) if discard_patterns is not None else None

    def identify(self):
        logger.info("Finding similar / mis-spelled topics...", color=logger.BLUE)
        all_topics = self.gitlab.read_all_topics()
        grouped = self.__group_by_similarity(all_topics)
        logger.info(f"Found {len(grouped)} similar topics groups", color=logger.GREEN)
        return grouped

    def __should_be_discarded(self, topic):
        return self.discard_pattern is not None and self.discard_pattern.match(topic) is not None

    def __group_by_similarity(self, topics):
        topics_count = len(topics)
        all_similar_topics = []
        all_flatten_similars = []
        for i in range(topics_count):
            topic1 = topics[i]
            topic1_title = ''.join(filter(str.isalnum, topic1.title)).lower()
            if topic1_title in all_flatten_similars:
                continue
            elif self.__should_be_discarded(topic1.title):
                all_flatten_similars.append(topic1_title)
                continue
            similar_topics = [topic1]
            for j in range(i + 1, topics_count):
                topic2 = topics[j]
                topic2_title = ''.join(filter(str.isalnum, topic2.title)).lower()
                if topic2_title in all_flatten_similars:
                    continue
                elif self.__should_be_discarded(topic2.title):
                    all_flatten_similars.append(topic2_title)
                    continue
                elif self.__is_similar(topic1_title, topic2_title):
                    all_flatten_similars.append(topic2_title)
                    similar_topics.append(topic2)
            if len(similar_topics) > 1:
                all_similar_topics.append(similar_topics)
        return all_similar_topics

    def __is_similar(self, topic1, topic2):
        topic2 = ''.join(filter(str.isalnum, topic2)).lower()
        return topic1 == topic2 \
               or (len(topic1) > 7 and len(topic2) > 7 and lev.distance(topic1, topic2) <= self.sensitivity)
