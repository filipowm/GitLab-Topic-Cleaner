import json
import os

import yaml

import guards
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
    guards.against_none(config_path, "Cleaner configuration path")
    config = __read_config(config_path)
    config = {topic['topic']: topic['synonyms'] for topic in config}
    apply = apply if apply else os.getenv('DRY_RUN')
    return TopicsCleaner(gitlab, config, apply if apply else False)
    # return TopicsCleaner(
    #     gitlab, {
    #         'not-validated': ['non-validated', 'not validated', 'nor-validated', 'not-vaildated', 'unvailidated'],
    #         'aws': ['amazon web services'],
    #         'backend': ['back-end']
    #     }, dry_run if dry_run else False


def configure_synonyms_identifier(gitlab):
    return SimilarTopicsIdentifier(gitlab, discard_patterns=['^timo2022.*', '^pja220.*', '^feiyun.*', '^dev-.*',
                                                             '^bielinsl-.*'])
    # return SimilarTopicsIdentifier(gitlab)


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
