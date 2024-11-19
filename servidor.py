import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread

# Lista para manter os clientes conectados
lista_clientes = []
clientes_endereco = {}
clientes_nomes = {}

# Função para gerenciar conexões dos clientes
def conexao_cliente(cliente_socket, endereco_cliente):
    try:
        nome_cliente = cliente_socket.recv(1500).decode().strip()  # Recebe o nome do cliente
        if not nome_cliente:
            nome_cliente = f"Cliente-{len(clientes_nomes) + 1}"
        clientes_nomes[cliente_socket] = nome_cliente
        lista_clientes.append(cliente_socket)
        clientes_endereco[cliente_socket] = endereco_cliente
        enviar_lista_clientes()

        log_text.insert(tk.END, f"Conexão estabelecida com {nome_cliente} ({endereco_cliente})\n")

        # Thread para receber mensagens do cliente
        def receber_mensagens():
            while True:
                try:
                    mensagem = cliente_socket.recv(1500).decode()
                    if mensagem:
                        destinatario, conteudo = mensagem.split(":", 1)
                        log_text.insert(tk.END, f"{nome_cliente} para {destinatario}: {conteudo}\n")
                        # Envia a mensagem para o destinatário
                        enviar_para_destinatario(destinatario.strip(), f"{nome_cliente}: {conteudo}")
                    else:
                        break
                except:
                    break

            # Desconexão do cliente
            lista_clientes.remove(cliente_socket)
            del clientes_endereco[cliente_socket]
            del clientes_nomes[cliente_socket]
            cliente_socket.close()
            log_text.insert(tk.END, f"Conexão encerrada com {nome_cliente} ({endereco_cliente})\n")
            enviar_lista_clientes()

        Thread(target=receber_mensagens).start()
    except Exception as e:
        log_text.insert(tk.END, f"Erro com cliente {endereco_cliente}: {e}\n")

# Função para enviar a lista de clientes a todos os clientes
def enviar_lista_clientes():
    lista = [f"{nome_cliente}" for cliente_socket, nome_cliente in clientes_nomes.items()]
    for cliente_socket in lista_clientes:
        try:
            cliente_socket.send(f"UPDATE_LIST:{','.join(lista)}".encode())
        except:
            pass  # Ignora erros ao enviar para clientes desconectados

# Função para enviar mensagem para um destinatário específico
def enviar_para_destinatario(destinatario, mensagem):
    for cliente_socket, nome_cliente in clientes_nomes.items():
        if nome_cliente == destinatario:
            try:
                cliente_socket.send(mensagem.encode())
            except:
                log_text.insert(tk.END, f"Erro ao enviar mensagem para {destinatario}\n")

# Função para iniciar o servidor
def iniciar_servidor():
    try:
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

tk.Label(janela, text="Porta:").pack()
porta_entrada = tk.Entry(janela, width=10)
porta_entrada.insert(0, "8000")  # Porta padrão
porta_entrada.pack()

# Botão para iniciar o servidor
botao_iniciar = tk.Button(janela, text="Iniciar Servidor", command=iniciar_servidor)
botao_iniciar.pack()

# Inicializa o socket do servidor
server_socket = socket(AF_INET, SOCK_STREAM)

# Executa o loop principal
janela.mainloop()

# Fecha o socket do servidor ao sair
server_socket.close()
