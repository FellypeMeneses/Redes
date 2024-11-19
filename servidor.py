import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread

# Lista para manter os clientes conectados
lista_clientes = []
clientes_endereco = {}

# Função para gerenciar conexões dos clientes
def conexao_cliente(cliente_socket, endereco_cliente):
    lista_clientes.append(cliente_socket)
    clientes_endereco[cliente_socket] = endereco_cliente
    log_text.insert(tk.END, f"Conexão estabelecida com {endereco_cliente}\n")
    
    # Atualiza a Listbox com os clientes conectados
    clientes_lista.insert(tk.END, f"{endereco_cliente}")

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
        del clientes_endereco[cliente_socket]
        cliente_socket.close()
        log_text.insert(tk.END, f"Conexão encerrada com {endereco_cliente}\n")
        # Atualiza a Listbox ao remover cliente
        clientes_lista.delete(0, tk.END)
        for cliente in lista_clientes:
            clientes_lista.insert(tk.END, f"{clientes_endereco[cliente]}")

    Thread(target=receber_mensagens).start()

# Função para enviar mensagem a um cliente específico
def enviar_mensagem_para_cliente():
    mensagem = entrada_mensagem.get()  # Pega a mensagem digitada no campo de entrada
    entrada_mensagem.delete(0, tk.END)  # Limpa o campo de entrada
    cliente_selecionado = lista_clientes[clientes_lista.curselection()[0]]  # Pega o cliente selecionado
    cliente_selecionado.send(mensagem.encode())  # Envia para o cliente
    log_text.insert(tk.END, f"Servidor: {mensagem} para {clientes_endereco[cliente_selecionado]}\n")

# Função para iniciar o servidor
def iniciar_servidor():
    try:
        # Configurações do socket
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Permite reutilização da porta
        server_socket.bind(('127.0.0.1', int(porta_entrada.get())))
        server_socket.listen(5)  # Permite até 5 conexões simultâneas
        log_text.insert(tk.END, f"Servidor iniciado na porta {porta_entrada.get()}...\n")

        # Thread para aceitar conexões
        def aceitar_conexoes():
            while True:
                cliente_socket, endereco_cliente = server_socket.accept()
                Thread(target=conexao_cliente, args=(cliente_socket, endereco_cliente)).start()

        Thread(target=aceitar_conexoes).start()

    except OSError as e:
        log_text.insert(tk.END, f"Erro ao iniciar servidor: {e}\n")

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

# Lista de clientes conectados
clientes_lista = tk.Listbox(janela, height=6, width=40)
clientes_lista.pack()

# Botão para enviar mensagem ao cliente selecionado
botao_enviar = tk.Button(janela, text="Enviar para Cliente", command=enviar_mensagem_para_cliente)
botao_enviar.pack()

# Inicializa o socket do servidor
server_socket = socket(AF_INET, SOCK_STREAM)

# Botão para iniciar o servidor
botao_iniciar = tk.Button(janela, text="Iniciar Servidor", command=iniciar_servidor)
botao_iniciar.pack()

# Executa o loop principal
janela.mainloop()
