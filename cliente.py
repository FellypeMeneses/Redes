import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

# Função para gerenciar conexões dos clientes
def conexao_cliente(cliente_socket, endereco_cliente):
    lista_clientes.append(cliente_socket)
    log_text.insert(tk.END, f"Conexão estabelecida com {endereco_cliente}\n")

    # Thread para receber mensagens do cliente
    def receber_mensagens():
        while True:
            try:
                mensagem = cliente_socket.recv(1500)
                if mensagem:
                    texto = f"Cliente ({endereco_cliente}): {mensagem.decode()}\n"
                    log_text.insert(tk.END, texto)
                else:
                    break
            except:
                break
        lista_clientes.remove(cliente_socket)
        cliente_socket.close()
        log_text.insert(tk.END, f"Conexão encerrada com {endereco_cliente}\n")

    Thread(target=receber_mensagens).start()

# Função para iniciar o servidor
def iniciar_servidor():
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', int(porta_entrada.get())))
        server_socket.listen()
        log_text.insert(tk.END, f"Servidor iniciado na porta {porta_entrada.get()}...\n")

        # Thread para aceitar conexões
        def aceitar_conexoes():
            while True:
                cliente_socket, endereco_cliente = server_socket.accept()
                Thread(target=conexao_cliente, args=(cliente_socket, endereco_cliente)).start()

        Thread(target=aceitar_conexoes).start()

    except OSError as e:
        log_text.insert(tk.END, f"Erro ao iniciar servidor: {e}\n")

# Função para enviar mensagens para todos os clientes
def enviar_mensagem():
    mensagem = entrada_mensagem.get()
    entrada_mensagem.delete(0, tk.END)
    for cliente in lista_clientes:
        cliente.send(mensagem.encode())
    log_text.insert(tk.END, f"Servidor: {mensagem}\n")

# Configuração da interface gráfica
janela = tk.Tk()
janela.title("Servidor")

log_text = tk.Text(janela, height=15, width=50)
log_text.pack()

porta_entrada = tk.Entry(janela, width=10)
porta_entrada.insert(0, "8000")  # Porta padrão
porta_entrada.pack()

entrada_mensagem = tk.Entry(janela, width=40)
entrada_mensagem.pack()

botao_enviar = tk.Button(janela, text="Enviar", command=enviar_mensagem)
botao_enviar.pack()

# Inicializa o socket do servidor
server_socket = socket(AF_INET, SOCK_STREAM)
lista_clientes = []

# Botão para iniciar o servidor
botao_iniciar = tk.Button(janela, text="Iniciar Servidor", command=iniciar_servidor)
botao_iniciar.pack()

# Executa o loop principal
janela.mainloop()
