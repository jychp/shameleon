import requests

from shameleon_client.providers.base import ShameleonProvider

PROVIDER_NAME = 'dummy'


class DummyShameleonProvider(ShameleonProvider):
    """ A dummy provider for testing purposes.

    This provider is used to test the Shameleon client without having to
    deploy a Shameleon backdoor.
    This provider is not intended to be used in production.
    """

    def _send_payload(self, payload: list[str]):
        req = requests.post(
            f"{self._profile.backdoor_custom['url']}/in",
            json={'elements': payload},
            timeout=self._profile.http_timeout,
        )
        req.raise_for_status()

    def _get_payload(self) -> list[tuple[str, str]]:
        output: list[tuple[str, str]] = []
        req = requests.get(
            f"{self._profile.backdoor_custom['url']}/out",
            timeout=self._profile.http_timeout,
        )
        req.raise_for_status()
        results = req.json()['elements']
        if len(results) > 0:
            for result in results:
                result = result.strip()
                if len(result) == 0:
                    continue
                tunnel_id, packet_data = result.split(':', 2)
                output.append((tunnel_id, packet_data))
        return output
