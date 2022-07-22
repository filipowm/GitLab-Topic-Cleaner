import json
import os

import yaml

import logger
from cleaner import TopicsCleaner
from gitlab import GitLab
from similar_topics import SimilarTopicsIdentifier


def configure_gitlab():
    url = os.getenv('GITLAB_URL')
    token = os.getenv('GITLAB_TOKEN')
    api_version = os.getenv('GITLAB_API_VERSION')
    return GitLab(
        base_url=url,
        api_version=api_version,
        token=token
    )


def configure_cleaner(gitlab, config_path, apply=False):
    config = None
    if config_path is not None:
        config = __read_config(config_path)
        config = {topic['topic']: topic['synonyms'] for topic in config}
    apply = apply if apply else os.getenv('DRY_RUN')
    return TopicsCleaner(gitlab, config, apply if apply else False)


def configure_synonyms_identifier(gitlab):
    return SimilarTopicsIdentifier(gitlab)


def __read_config(config_path):
    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
        return __read_yaml(config_path)
    elif config_path.endswith('.json'):
        return __read_json(config_path)
    else:
        logger.error("Configuration file should be YAML or JSON.")
        raise RuntimeError()


def __read_yaml(config_path):
    with open(config_path, 'r') as stream:
        return yaml.safe_load(stream)


def __read_json(config_path):
    with open(config_path, 'r') as stream:
        return json.load(stream)
