# Trabalho de Redes II

Simulação de um modelo **publish/subscribe** inspirado no WhatsApp, com um broker semelhante ao MQTT. O foco é a **segurança de comunicação** (criptografia ponto-a-ponto) e autenticação com certificados digitais.

---

## 🧠 Objetivo

- Simular um **modelo publish/subscribe** como no WhatsApp.
- Implementar um sistema similar ao **MQTT**, com controle e criptografia em nível de aplicação.

---

## 🛠️ Requisitos

- Assinatura (`subscribe`) em nível de camada de aplicação.
- Cabeçalho próprio no formato **JSON**.
- **Payload livre**.
- Criar o sistema do zero (não copiar).
- Utilizar **TLS** para proteger o canal.

---

## 🔐 Criação de Tópico e Chaves

- O **cliente** cria o tópico e a chave **simétrica do grupo**.
- O **broker** apenas direciona a comunicação (não tem acesso às mensagens ou chaves).
- A **chave simétrica** é enviada aos inscritos por meio de **criptografia assimétrica (envelopada)**:
  - O novo cliente faz um `GET` com sua chave pública.
  - Outro cliente criptografa a chave simétrica com a pública do novo cliente.
- Cada cliente tem:
  - 1 chave simétrica por grupo.
  - 1 par de chaves pública/privada.
- Clientes fora do tópico não podem enviar mensagens.

---

## 💡 Broker

- Atua como um servidor **MQTT**.
- Interface via **terminal** (exibe eventos como `connect`, `subscribe`, etc.).
- Autenticação com certificado **xq19**.

---

## 🧵 Threads

- Cada thread representa o fluxo de dados de um cliente.
- Associada à chave simétrica do tópico.
- Desconexão: `close` na porta e encerramento da thread.

---

## 🔒 Segurança

- Criptografia **ponto-a-ponto**:
  - **TLS** para o canal.
  - Payload criptografado com chave simétrica.
- **Certificados digitais (X.509)**:
  - Cliente gera certificado.
  - Robson (professor) atua como **AC** e assina os certificados.
  - Handshake mútuo obrigatório (falha encerra a conexão).
- Certificados são salvos localmente e permitem login persistente.

---

## ⚠️ Problemas e Soluções

### Cliente novo precisa da chave, mas todos do grupo estão offline

- Broker detecta quem está online.
- Se todos offline:
  - Usar servidor de chaves (`km5`) – ponto único de falha.
  - Alternativas: algoritmos como **Diffie-Hellman**, ou **roteamento via eventos**.

### Cliente offline não recebe mensagens

- Controle de entrega feito em nível de aplicação.
- Cada cliente tem uma fila de mensagens pendentes.
- Mensagens são entregues ao reconectar.

---

## 🔌 Comunicação

- Toda comunicação entre clientes é feita por **TCP ponto-a-ponto**.
- O broker apenas gerencia a conexão e direcionamento de mensagens.

---

## ✅ Extras

- Autenticação baseada em certificados.
- Certificados contêm hash com informações do cliente.
- O broker verifica o certificado na conexão.
- Apenas clientes autorizados podem publicar ou assinar tópicos.

---

> Trabalho desenvolvido para a disciplina de **Redes II**, com foco em **protocolos de publicação/assinatura seguros**, autenticação digital e criptografia.
