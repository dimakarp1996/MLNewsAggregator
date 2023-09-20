import requests  # 2.22.0
import json  # 2.0.9
import time
import os


class PaperDataReturner():
    def __init__(self, cache_name='papers.pkl', cache_dir=os.getcwd(), cache_seconds=1000):
        """
        Returner of papers from labml.ai. Returns for every category list of the papers sorted by the number of tweets. For every category, most popular recent, daily, weekly or monthly papers are tracked.

        Parameters:
            cache_name - name of pickled cache of the request. Default: papers.pkl
            cache_dir - directory where pickled request cache is stored. Default: current dir
            cache_secords: if the cache was updated less than cache_seconds ago, cache is returned. The cache is added to speed the computation up and to enable the information storage. Default: 1000
        """
        self.url = 'https://papers.labml.ai/'

        self.header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0',
            'DNT': '1', 'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'TE': 'trailers'}
        self.cookie = {
            'Authorization': requests.post('https://papers.labml.ai/api/v1/auth/user', json=self.header).headers[
                'authorization']}
        self.cache_name = cache_name
        self.cache_dir = cache_dir
        self.cache = '/'.join([self.cache_dir, self.cache_name])
        self.cache_seconds = cache_seconds

    def get_answer(self, modes=['recent', 'daily', 'weekly', 'monthly'], papers_by_mode=250, save_in_cache=True):
        """
        Function to return the dictionary containing papers.
        Parameters:
            modes - list of possible modes to return the papers for. Must be the iterable, the included values can be only of the following - ['recent','daily','weekly','monthly']
            papers_by_mode - max number of papers to be returned for every mode. Default 250
            save_in_cache - if True, the answer is at first saved in cache. Default True
        """
        if os.path.exists(self.cache):
            if os.path.getmtime(self.cache) + self.cache_seconds > time.time():
                return self.cache
        answer = dict()
        possible_modes = ['recent', 'daily', 'weekly', 'monthly']
        papers_by_mode = int(min(papers_by_mode, 250))  # no more than 250
        for mode in modes:
            assert mode in possible_modes, f'{mode} not in possible_modes: {possible_modes}'
            data = requests.get(f'https://papers.labml.ai/api/v1/papers/?sorted_by={mode}&start=0&end={papers_by_mode}',
                                headers=self.header, cookies=self.cookie).text
            papers = json.loads(data)['data']['papers']
            papers = sorted(papers, key=lambda x: -x['num_tweets'])
            for paper in papers:
                category_name = paper['primary_category']
                for category in [category_name, 'all']:
                    if category_name not in answer:
                        answer[category_name] = dict()
                    if mode not in answer[category_name]:
                        answer[category_name][mode] = []
                    answer[category_name][mode].append(paper)
        if save_in_cache:
            json.dump(answer, open(self.cache, 'w'),indent=4)
        return answer

def test():
    o = PaperDataReturner()
    a=o.get_answer()
