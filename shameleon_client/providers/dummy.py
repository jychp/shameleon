import aiohttp

from shameleon_client.providers.base import ShameleonProvider

PROVIDER_NAME = 'dummy'


class DummyShameleonProvider(ShameleonProvider):
    """ A dummy provider for testing purposes.

    This provider is used to test the Shameleon client without having to
    deploy a Shameleon backdoor.
    This provider is not intended to be used in production.
    """

    async def _send_payload(self, data: list[str]):
        # TODO: Handle HTTP errors
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            await session.post(
                f"{self._profile.backdoor_custom['url']}/in",
                json={'elements': data},
                timeout=self._profile.http_timeout,
            )

    async def _get_payload(self) -> list[tuple[str, str]]:
        # TODO: Handle HTTP errors
        output: list[tuple[str, str]] = []
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self._profile.backdoor_custom['url']}/out",
                timeout=self._profile.http_timeout,
            ) as req:
                data = await req.json()
                results = data['elements']
        if len(results) > 0:
            for result in results:
                result = result.strip()
                if len(result) == 0:
                    continue
                tunnel_id, packet_data = result.split(':', 2)
                output.append((tunnel_id, packet_data))
        return output
