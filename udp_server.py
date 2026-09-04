"""Servidor UDP do conversor de moedas."""

import argparse
import socket

from currency import convert_request, decode_message, encode_message


def serve(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((host, port))
        print(f"Servidor UDP ouvindo em {host}:{port}. Pressione Ctrl+C para sair.")
        while True:
            data, address = server.recvfrom(4096)
            try:
                response = convert_request(decode_message(data))
            except ValueError as error:
                response = {"ok": False, "erro": str(error)}
            server.sendto(encode_message(response), address)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor UDP de conversão de moedas")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
