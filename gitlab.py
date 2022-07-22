import time

import requests

import guards
import logger
from topic import Topic


class GitLab:
    DEFAULT_BASE_URL = "https://gitlab.com"
    DEFAULT_API_VERSION = 4
    DEFAULT_USER_AGENT = "GitLab-Topics-Normalizer"

    def __init__(self, base_url=DEFAULT_BASE_URL,
                 api_version=DEFAULT_API_VERSION,
                 token=None,
                 user_agent=DEFAULT_USER_AGENT,
                 retries_limit=5):
        guards.against_none(token, "GitLab token")
        api_version_to_use = guards.this_or_default(api_version, self.DEFAULT_API_VERSION)
        base_url_to_use = guards.this_or_default(base_url, self.DEFAULT_BASE_URL)
        self.base_url = f"{base_url_to_use}/api/v{api_version_to_use}"
        self.headers = {
            'User-Agent': guards.this_or_default(user_agent, self.DEFAULT_USER_AGENT),
            'PRIVATE-TOKEN': token
        }
        self.retries_limit = retries_limit
        if not self.__verify():
            raise RuntimeError('Used token is not for admin user. Admin user access is required to manage topics.')

    def __verify(self):
        user = self.get('user')
        return True if user['is_admin'] else False

    def __start_session(self):
        session = requests.session()
        session.headers = self.headers
        session.keep_alive = False
        return session

    def _do_retry(self, function, retry_num, should_retry=True):
        return self._with_session(function,
                                  ++retry_num) if should_retry and retry_num <= self.retries_limit else None

    def _with_session(self, function, retry_num=0):
        try:
            session = self.__start_session()
            response = function(session)
            if self.__has_errors(response):
                should_retry = self.__handle_response_errors(response)
                return self._do_retry(function, retry_num, should_retry)
            if response.status_code == 204:
                return None
            return response.json()
        except TimeoutError:
            logger.warn("Request timed out. Waiting 10s before continuing.")
            time.sleep(10)
            return self._do_retry(function, retry_num)
        except ConnectionError:
            logger.warn("Unknown connection error. Waiting 10s before continuing.")
            time.sleep(10)
            return self._do_retry(function, retry_num)

    def post(self, path, body=None):
        return self._with_session(lambda session: session.post(url=f"{self.base_url}/{path}", json=body))

    def put(self, path, body=None):
        return self._with_session(lambda session: session.put(url=f"{self.base_url}/{path}", json=body))

    def get(self, path, params=None):
        return self._with_session(lambda session: session.get(url=f"{self.base_url}/{path}", params=params))

    def delete(self, path, params=None):
        return self._with_session(lambda session: session.delete(url=f"{self.base_url}/{path}", params=params))

    def __get_topics_page(self, page_num=1):
        return self.get("topics", params={'page': page_num, 'per_page': 100})

    def read_all_topics(self):
        next_page = 1
        topics = []
        # log.info(f"Reading all topics")
        while next_page > 0:
            # log.debug(f"Reading topics page {next_page}")
            topics_page = self.__get_topics_page(next_page)
            next_page = -1 if len(topics_page) == 0 else next_page + 1
            topics_page = list(map(lambda topic: Topic.from_dict(topic), topics_page))
            topics.extend(topics_page)
        # log.info(f"Read {len(topics)} topics")
        return topics

    @staticmethod
    def __has_errors(response):
        return response.status_code >= 400

    def __handle_response_errors(self, response):
        status_code = response.status_code
        wait_time_seconds = 10
        if status_code == 404:
            logger.error(f"Requested resource was not found under: {response.url}")
            return False
        elif status_code == 401:
            logger.error("Invalid or missing authentication. Check bearer token.")
            raise RuntimeError("invalid bearer token")
        elif status_code == 429:
            logger.warn(f"Request to {response.url} reached rate limit threshold")
            wait_time_seconds = self.__calculate_rate_limit_sleep_time(response)
        elif status_code == 403:
            if self.__is_rate_limited(response):
                logger.warn(f"Request to {response.url} reached rate limit threshold")
                wait_time_seconds = self.__calculate_rate_limit_sleep_time(response)
            else:
                logger.warn(f"Access to {response.url} is forbidden")
                return False
        else:
            logger.warn(f"Request failed with status code: {status_code}")
        wait_time_seconds = wait_time_seconds if wait_time_seconds > 0 else 10
        logger.warn(f"Waiting {wait_time_seconds}s for retry")
        sleep(wait_time_seconds)
        return True

    @staticmethod
    def __is_rate_limited(response):
        remaining_requests = response.headers['RateLimit-Remaining']
        return False if remaining_requests is None or int(remaining_requests) > 0 else True

    @staticmethod
    def __calculate_rate_limit_sleep_time(response):
        reset_timestamp_str = response.headers['RateLimit-Reset']
        current_timestamp = time.time()
        reset_timestamp = int(reset_timestamp_str) if reset_timestamp_str is not None else current_timestamp
        return round(reset_timestamp - current_timestamp)


def sleep(sleep_for_seconds):
    if sleep_for_seconds > 500:
        time.sleep(500)
        remaining = sleep_for_seconds - 500
        logger.warn(f"Sleeping remaining {remaining}s")
        sleep(remaining)
    elif sleep_for_seconds > 0:
        time.sleep(sleep_for_seconds)
