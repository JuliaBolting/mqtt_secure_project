import socket
import os
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

HOST = '127.0.0.1'
PORT = 8888

CERT_DIR = 'certs/'
KEYS_DIR = 'keys/'

# Nome do cliente (deve corresponder ao nome dos arquivos .pem)
CLIENTE_NOME = 'clienteA'

# Carregar certificado do cliente
with open(os.path.join(CERT_DIR, f'{CLIENTE_NOME}_cert.pem'), 'rb') as f:
    cliente_cert = f.read()

# Carregar certificado da AC (para validar o broker)
with open(os.path.join(CERT_DIR, 'ac_cert.pem'), 'rb') as f:
    ac_cert = x509.load_pem_x509_certificate(f.read())
    ac_pub_key = ac_cert.public_key()

def conectar():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"📡 Conectado ao broker em {HOST}:{PORT}")

        # 1. Enviar certificado do cliente
        s.send(len(cliente_cert).to_bytes(4, 'big'))
        s.send(cliente_cert)

        # 2. Aguardar resposta de autenticação
        resposta = s.recv(1024)
        if resposta != b'AUTENTICADO':
            print("❌ Conexão rejeitada pelo broker.")
            return
        print("🔐 Autenticado com sucesso pelo broker!")

        # 3. Enviar mensagens de teste
        while True:
            msg = input("✉️ Digite uma mensagem (ou 'sair'): ")
            if msg.lower() == 'sair':
                break
            s.send(msg.encode())

        print("🔌 Desconectando...")

if __name__ == '__main__':
    conectar()