import guards
import logger


class TopicsCleaner(object):

    def __init__(self, gitlab, topics_config, apply=False):
        guards.against_none(gitlab, "GitLab client")
        guards.against_none(topics_config, "Topics configuration")
        self.topics_config = topics_config
        self._topics = []
        self.apply = apply
        self.gitlab = gitlab

    def __read_topics(self):
        if len(self._topics) == 0:
            self._topics = self.gitlab.read_all_topics()
        return self._topics

    def __remove_topic(self, topic):
        if self.apply:
            logger.info(f"Removing topic '{topic.title}'")
            self.gitlab.delete(f"topics/{topic.id}")
        else:
            logger.info(f"Topic '{topic.title}' would be removed, but in dry-run mode")

    def remove_empty(self):
        logger.info('Unused topics will be removed', color=logger.BLUE)
        topics = self.__read_topics()
        topics_to_clean = list(filter(lambda topic: topic.total_projects_count == 0, topics))
        logger.info(f"{len(topics_to_clean)} topics are not connected with any project and will be removed")
        for topic in topics_to_clean:
            self.__remove_topic(topic)
        if self.apply:
            logger.info(f"{len(topics_to_clean)} were removed", color=logger.GREEN)
        else:
            logger.info(f"{len(topics_to_clean)} would be removed, but running in dry-run mode.", color=logger.GREEN)

    def __map_to_synonyms(self, topics):
        mapped = {}
        for i in range(len(topics)):
            topic = topics[i]
            topic_title = topic.title
            synonyms = self.topics_config.get(topic_title)
            if synonyms is not None and len(synonyms) > 0:
                found_synonym_topics = self.__find_synonyms(topics, synonyms)
                if len(found_synonym_topics) > 0:
                    mapped[topic] = found_synonym_topics
        return mapped

    def migrate_synonyms(self):
        logger.info('Synonymous topics will be migrated to their primary form.', color=logger.BLUE)
        guards.against_empty(self.topics_config, "Topics and their synonyms configuration")
        topics = self.__read_topics()
        topics_to_migrate = self.__map_to_synonyms(topics)
        synonyms_count = 0
        for _, synonyms in topics_to_migrate.items():
            synonyms_count = synonyms_count + len(synonyms)
        logger.info(f"{synonyms_count} synonyms were identified.")
        for main_topic, synonyms in topics_to_migrate.items():
            for topic in synonyms:
                logger.info()
                projects = self.gitlab.get(path='projects', params={'topic': topic.title, 'per_page': 100})
                logger.info(f"Migrating synonym {topic.title} to {main_topic.title} in {len(projects)} projects")
                for project in projects:
                    logger.debug(
                        f"Migrating '{topic.title}' synonym to '{main_topic.title}' in '{project['name']}' project")
                    project_topics = project['topics']
                    if topic.title in project_topics:
                        idx = project_topics.index(topic.title)
                        project_topics.remove(topic.title)
                        project_topics.insert(idx, main_topic.title)
                        for st in self._topics:
                            if st.title == main_topic.title:
                                st.total_projects_count = st.total_projects_count + 1
                        if self.apply:
                            self.gitlab.put(path=f"projects/{project['id']}", body={'topics': project_topics})
                logger.info(
                    f"Synonym '{topic.title}' was migrated to '{main_topic.title}' in all {len(projects)} projects")
                self.__remove_topic(topic)
        logger.info()
        logger.info(f"{synonyms_count} synonyms were migrated!", color=logger.GREEN)

    @staticmethod
    def __find_synonyms(topics, synonyms):
        synonym_topics = []
        for topic in topics:
            if topic.title in synonyms and topic.total_projects_count > 0:
                synonym_topics.append(topic)
        return synonym_topics
