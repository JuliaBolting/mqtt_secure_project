from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509.oid import NameOID
from cryptography import x509
from datetime import datetime, timedelta
import os

# Diretórios de saída
os.makedirs("keys", exist_ok=True)
os.makedirs("certs", exist_ok=True)

# 1. Gerar chave privada da AC
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# 2. Serializar e salvar chave privada
with open("keys/ac_private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# 3. Criar dados para o certificado
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Santa Catarina"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Lages"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"IFSC"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"AC-Professor-Robson"),
])

# 4. Criar certificado X.509 autoassinado
cert = x509.CertificateBuilder().subject_name(subject)
cert = cert.issuer_name(issuer)
cert = cert.public_key(private_key.public_key())
cert = cert.serial_number(x509.random_serial_number())
cert = cert.not_valid_before(datetime.utcnow())
cert = cert.not_valid_after(datetime.utcnow() + timedelta(days=3650))  # 10 anos
cert = cert.add_extension(
    x509.BasicConstraints(ca=True, path_length=None), critical=True,
)
cert = cert.sign(private_key, hashes.SHA256())

# 5. Salvar certificado
with open("certs/ac_cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("✅ Certificado da AC gerado com sucesso!")
