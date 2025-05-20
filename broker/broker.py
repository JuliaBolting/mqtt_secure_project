import socket
import threading
import ssl
import os
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

HOST = '127.0.0.1'
PORT = 8888

CERT_DIR = 'certs/'
KEYS_DIR = 'keys/'

# Carregar certificado e chave do broker
with open(os.path.join(CERT_DIR, 'broker_cert.pem'), 'rb') as f:
    broker_cert = x509.load_pem_x509_certificate(f.read())

with open(os.path.join(KEYS_DIR, 'broker_private_key.pem'), 'rb') as f:
    broker_private_key = serialization.load_pem_private_key(f.read(), password=None)

# Carregar certificado da AC (para validar clientes)
with open(os.path.join(CERT_DIR, 'ac_cert.pem'), 'rb') as f:
    ac_cert = x509.load_pem_x509_certificate(f.read())
    ac_pub_key = ac_cert.public_key()

def autenticar_cliente(cert_bytes):
    try:
        cert = x509.load_pem_x509_certificate(cert_bytes)
        # Verificar se o certificado foi assinado pela AC
        ac_pub_key.verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
        cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        return cn
    except Exception as e:
        print(f"❌ Falha na autenticação do cliente: {e}")
        return None

def tratar_cliente(conn, addr):
    try:
        print(f"📡 Conexão recebida de {addr}")

        # 1. Receber certificado do cliente
        cert_len = int.from_bytes(conn.recv(4), 'big')
        cert_bytes = conn.recv(cert_len)

        # 2. Autenticar certificado
        nome_cliente = autenticar_cliente(cert_bytes)
        if not nome_cliente:
            conn.sendall('ERRO: Certificado inválido.'.encode('utf-8'))
            conn.close()
            return

        print(f"🔐 Cliente '{nome_cliente}' autenticado com sucesso!")
        conn.sendall(b'AUTENTICADO')

        while True:
            data = conn.recv(4096)
            if not data:
                break
            print(f"📨 Msg de {nome_cliente}: {data.decode(errors='ignore')}")

    except Exception as e:
        print(f"Erro com cliente {addr}: {e}")
    finally:
        print(f"🔌 Cliente {addr} desconectado.")
        conn.close()

def iniciar_broker():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🚀 Broker escutando em {HOST}:{PORT}...\n")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=tratar_cliente, args=(conn, addr))
            thread.start()

if __name__ == '__main__':
    iniciar_broker()