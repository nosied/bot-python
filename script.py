import cv2
import pyautogui
import numpy as np
import time
import mysql.connector
import pyperclip
import requests

# Conectar ao banco de dados MySQL
def conectar_banco():
    conexao = mysql.connector.connect(
        host='192.168.3.99',  # Atualize com seu host
        user='root',       # Atualize com seu usuário
        password='',  # Atualize com sua senha
        database='bot-wwp-prd'  # Atualize com o nome do seu banco de dados
    )
    return conexao

# Verifica URLs no banco de dados
def obter_urls_nao_abertas(conexao):
    cursor = conexao.cursor()
    cursor.execute("SELECT id, link, details FROM ml_generate WHERE status = 0")
    resultados = cursor.fetchall()
    print("Log: Linhas retornadas do banco de dados:", resultados)  # Log das linhas do banco de dados
    return resultados

# Atualiza o status da URL para 'aberta'
def marcar_url_como_aberta(conexao, id_url):
    cursor = conexao.cursor()
    cursor.execute("UPDATE ml_generate SET status = 1 WHERE id = %s", (id_url,))
    conexao.commit()

def marcar_url_como_aberta_erro(conexao, id_url):
    cursor = conexao.cursor()
    cursor.execute("UPDATE ml_generate SET status = 2 WHERE id = %s", (id_url,))

    conexao.commit()

# Função para localizar a imagem na tela e clicar
def localizar_e_clicar(imagem, confidencia=0.8):
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot, dtype=np.uint8)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    template = cv2.imread(imagem, cv2.IMREAD_COLOR)
    template = template.astype(np.uint8)
    resultado = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultado)
    if max_val >= confidencia:
        x, y = max_loc
        altura, largura = template.shape[:2]
        centro_x = x + largura // 2
        centro_y = y + altura // 2
        pyautogui.moveTo(centro_x, centro_y, duration=0.2)
        pyautogui.click()
        time.sleep(0.5)
        return True
    else:
        return False

# Função para localizar o primeiro botão entre vários iguais e clicar
def localizar_e_clicar_primeiro(imagem, confidencia=0.8):
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot, dtype=np.uint8)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    template = cv2.imread(imagem, cv2.IMREAD_COLOR)
    template = template.astype(np.uint8)
    resultado = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    locais = np.where(resultado >= confidencia)

    if len(locais[0]) > 0:
        # Pega o primeiro resultado encontrado
        x, y = locais[1][0], locais[0][0]
        altura, largura = template.shape[:2]
        centro_x = x + largura // 2
        centro_y = y + altura // 2
        pyautogui.moveTo(centro_x, centro_y, duration=0.2)
        pyautogui.click()
        time.sleep(0.5)
        return True
    else:
        return False

# Envia a URL concatenada para uma API
def enviar_para_api(url_completa, link):
    response = requests.post('http://192.168.3.99:3001/send-message', json={'groupId': "120363343009794218@g.us", '_data': {'notifyName': "Deison"}, 'message': url_completa})
    if response.status_code == 200:
        # Marca a URL como aberta no banco
        marcar_url_como_aberta(conexao, id_url)
        print("URL: "+link+ " enviada com sucesso!")
    else:
        print("Falha ao enviar a URL:", response.status_code)

# Loop principal para verificar e abrir URLs
conexao = conectar_banco()
try:
    time.sleep(20)
    while True:
        # Fecha a conexão existente e cria uma nova para garantir resultados atualizados
        conexao.close()
        conexao = conectar_banco()

        # Executa a consulta
        urls = obter_urls_nao_abertas(conexao)
        if urls:
            print("URLs encontradas:", urls)  # Log para verificar os registros
            for id_url, link, details in urls:
                try:
                    # Acessa a URL diretamente na aba atual
                    pyperclip.copy(link)
                    pyautogui.hotkey('ctrl', 'l')  # Seleciona a barra de endereço
                    pyautogui.hotkey('ctrl', 'v')  # Cola a URL
                    pyautogui.press('enter')
                    time.sleep(6)  # Espera a página carregar

                    # Clica nos botões sequenciais
                    if localizar_e_clicar('botao_ver_produto.png'):
                        time.sleep(4)
                        if localizar_e_clicar('botao_gerar_link.png'):
                            time.sleep(1.5)
                            if localizar_e_clicar_primeiro('botao_copiar.png'):
                                print("Primeiro botão clicado com sucesso!")
                            else:
                                print("Não foi possível clicar no primeiro botão.")
                            url_gerada = pyperclip.paste()  # Pega a URL copiada automaticamente
                            url_completa = details + ' \n ' + url_gerada
                            time.sleep(1)
                            enviar_para_api(url_completa, link)

                        else:
                            print("Botão 'gerar link' não encontrado.")
                            # Marca a URL como aberta
                            marcar_url_como_aberta_erro(conexao, id_url)
                    else:
                        print("Botão 'ver produto' não encontrado.")
                        time.sleep(3)
                        if localizar_e_clicar('botao_gerar_link.png'):
                            time.sleep(1.5)
                            if localizar_e_clicar_primeiro('botao_copiar.png'):
                                print("Primeiro botão clicado com sucesso!")
                            else:
                                print("Não foi possível clicar no primeiro botão.")
                            url_gerada = pyperclip.paste()  # Pega a URL copiada automaticamente
                            url_completa = details + ' \n ' + url_gerada
                            time.sleep(1)
                            enviar_para_api(url_completa, link)

                            # Marca a URL como aberta no banco
                            marcar_url_como_aberta(conexao, id_url)
                        else:
                            print("Botão 'gerar link' não encontrado.")
                            # Marca a URL como aberta
                            marcar_url_como_aberta_erro(conexao, id_url)
                    
                    # Redireciona para uma página neutra (ex: Google) para preparar a próxima iteração
                    pyperclip.copy("https://google.com")
                    pyautogui.hotkey('ctrl', 'l')  # Seleciona a barra de endereço
                    pyautogui.hotkey('ctrl', 'v')  # Cola a URL
                    pyautogui.press('enter')
                    time.sleep(2)  # Espera a página carregar
                except Exception as e:
                    print(f"Erro ao processar a URL {link}: {e}")
        else:
            print("Nenhuma nova URL encontrada. Verificando novamente em 30 segundos.")
            time.sleep(30)  # Aguarda 30 segundos antes da próxima verificação
except Exception as e:
    print(f"Erro crítico no loop principal: {e}")
finally:
    conexao.close()  # Fecha a conexão ao final da execução do script
