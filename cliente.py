from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

#Codigo do socket
s = socket(AF_INET, SOCK_STREAM)
s.connect(('127.0.0.1', 8000))
print('Conectado ao servidor')

#Mensage do servidor
def receber_mensagens():
    while True:
        try:
            mensagem = s.recv(1500)
            if mensagem:
                print(f'Servidor: {mensagem.decode()}')
            else:
                break
        except:
            break

# Thread para receber mensagens do servidor
Thread(target=receber_mensagens).start()

# Loop para enviar mensagens ao servidor
while True:
    mensagem_cliente = input("Cliente: ")
    s.send(mensagem_cliente.encode())

# Fecha a conexão
s.close()
