"""Cliente TCP interativo do conversor de moedas."""

import argparse
import socket

from currency import decode_message, encode_message, format_response


def run(host: str, port: int) -> None:
    with socket.create_connection((host, port), timeout=10) as connection:
        stream = connection.makefile("rb")
        print("Conectado ao servidor TCP. Deixe o valor vazio para sair.")
        while True:
            value = input("\nValor em reais: ").strip()
            if not value:
                break
            currency = input("Moeda desejada: ").strip()
            connection.sendall(encode_message({"valor": value, "moeda": currency}) + b"\n")
            line = stream.readline()
            if not line:
                raise ConnectionError("O servidor encerrou a conexão sem responder.")
            print(format_response(decode_message(line)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente TCP de conversão de moedas")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    try:
        run(args.host, args.port)
    except (ConnectionError, OSError, ValueError) as error:
        print(f"Erro: {error}")
