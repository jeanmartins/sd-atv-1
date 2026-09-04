"""Cliente UDP interativo do conversor de moedas."""

import argparse
import socket

from currency import decode_message, encode_message, format_response


def run(host: str, port: int) -> None:
    server_address = (host, port)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(5)
        print("Cliente UDP iniciado. Deixe o valor vazio para sair.")
        while True:
            value = input("\nValor em reais: ").strip()
            if not value:
                break
            currency = input("Moeda desejada: ").strip()
            client.sendto(encode_message({"valor": value, "moeda": currency}), server_address)
            try:
                data, _ = client.recvfrom(4096)
            except socket.timeout:
                print("Erro: o servidor não respondeu em 5 segundos.")
                continue
            print(format_response(decode_message(data)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente UDP de conversão de moedas")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    try:
        run(args.host, args.port)
    except (OSError, ValueError) as error:
        print(f"Erro: {error}")
