from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509.oid import NameOID
from cryptography import x509
from datetime import datetime, timedelta
import os
import sys

# Diretórios de saída
os.makedirs("keys", exist_ok=True)
os.makedirs("certs", exist_ok=True)

def gerar_chaves_certificado(nome: str, tipo: str, ac_cert_path: str, ac_key_path: str):
    """
    Gera par de chaves e certificado X.509 assinado pela AC para cliente ou broker.
    :param nome: Nome comum (CN) do certificado
    :param tipo: "cliente" ou "broker"
    :param ac_cert_path: Caminho para o certificado da AC
    :param ac_key_path: Caminho para a chave privada da AC
    """
    # 1. Gerar chave privada
    chave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # 2. Salvar chave privada
    chave_arquivo = f"keys/{nome}_private_key.pem"
    with open(chave_arquivo, "wb") as f:
        f.write(chave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # 3. Construir nome do certificado
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Santa Catarina"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Lages"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"IFSC"),
        x509.NameAttribute(NameOID.COMMON_NAME, nome),
    ])

    # 4. Carregar chave privada e certificado da AC
    with open(ac_key_path, "rb") as f:
        ac_private_key = serialization.load_pem_private_key(f.read(), password=None)

    with open(ac_cert_path, "rb") as f:
        ac_cert = x509.load_pem_x509_certificate(f.read())

    # 5. Criar certificado assinado pela AC
    cert_builder = x509.CertificateBuilder()
    cert_builder = cert_builder.subject_name(subject)
    cert_builder = cert_builder.issuer_name(ac_cert.subject)
    cert_builder = cert_builder.public_key(chave_privada.public_key())
    cert_builder = cert_builder.serial_number(x509.random_serial_number())
    cert_builder = cert_builder.not_valid_before(datetime.utcnow())
    cert_builder = cert_builder.not_valid_after(datetime.utcnow() + timedelta(days=3650))
    cert_builder = cert_builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    )
    cert = cert_builder.sign(private_key=ac_private_key, algorithm=hashes.SHA256())

    # 6. Salvar certificado
    cert_arquivo = f"certs/{nome}_cert.pem"
    with open(cert_arquivo, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"✅ Certificado de {tipo} '{nome}' gerado com sucesso!")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python create_entity_cert.py <nome> <cliente|broker> <ac_cert.pem> <ac_key.pem>")
        sys.exit(1)

    nome = sys.argv[1]
    tipo = sys.argv[2]
    ac_cert_path = sys.argv[3]
    ac_key_path = sys.argv[4]
    gerar_chaves_certificado(nome, tipo, ac_cert_path, ac_key_path)