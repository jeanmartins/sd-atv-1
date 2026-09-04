"""Servidor TCP do conversor de moedas."""

import argparse
import socket
import threading

from currency import convert_request, decode_message, encode_message


def handle_client(connection: socket.socket, address: tuple[str, int]) -> None:
    print(f"Cliente conectado: {address[0]}:{address[1]}")
    with connection:
        stream = connection.makefile("rb")
        for line in stream:
            try:
                response = convert_request(decode_message(line))
            except ValueError as error:
                response = {"ok": False, "erro": str(error)}
            connection.sendall(encode_message(response) + b"\n")
    print(f"Cliente desconectado: {address[0]}:{address[1]}")


def serve(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"Servidor TCP ouvindo em {host}:{port}. Pressione Ctrl+C para sair.")
        while True:
            connection, address = server.accept()
            threading.Thread(target=handle_client, args=(connection, address), daemon=True).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor TCP de conversão de moedas")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
