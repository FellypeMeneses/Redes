from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

# Função para gerenciar a conexão com o cliente
def conexao_cliente(cliente_socket, endereco_cliente):
    print(f'Conexão estabelecida com {endereco_cliente}')
    
    # Função para receber mensagens do cliente
    def receber_mensagens():
        while True:
            try:
                mensagem = cliente_socket.recv(1500)
                if mensagem:
                    print(f'Cliente ({endereco_cliente}): {mensagem.decode()}')
                else:
                    break
            except:
                break
    
    # Thread mensagem docliente
    Thread(target=receber_mensagens).start()

    # Loop mensagens ao cliente
    while True:
        mensagem_servidor = input("Servidor: ")
        cliente_socket.send(mensagem_servidor.encode())

    # Fecha a conexão com o cliente
    cliente_socket.close()

#Socket do servidor
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('127.0.0.1', 8000))
server_socket.listen()

print('Servidor aguardando conexões na porta 8000')

# Loop conexões de clientes
while True:
    cliente_socket, endereco_cliente = server_socket.accept()
    Thread(target=conexao_cliente, args=(cliente_socket, endereco_cliente)).start()
