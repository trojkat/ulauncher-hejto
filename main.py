import json
from typing import Dict, List
from urllib.request import urlopen, Request

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction


class HejtoExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        return RenderResultListAction(self._get_news())

    @staticmethod
    def _get_news() -> List[ExtensionResultItem]:
        BASE_URL = 'https://www.hejto.pl/wpis/'
        result: Dict[str, ExtensionResultItem] = {}
        for hejto_type in ('link', 'discussion', 'article'):
            try:
                r = Request(
                    f"https://api.hejto.pl/posts?page=1&period=week&limit=5&orderDir=desc&type[]={hejto_type}&orderBy=p.createdAt",
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'}
                )
                data = json.loads(urlopen(r).read().decode("utf-8"))
            except Exception:
                pass
            for item in data['_embedded']['items']:
                tags = ['#' + t['name'] for t in item['tags']]
                result[item['created_at']] = ExtensionResultItem(
                    icon=f'images/{hejto_type}.png', 
                    name=item['title'], 
                    description=' '.join(tags),
                    on_enter=OpenUrlAction(BASE_URL + item['slug']), 
                )
        return [result[k] for k in sorted(result.keys(), reverse=True)]

if __name__ == '__main__':
    HejtoExtension().run()
