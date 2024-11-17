import cv2
import pyautogui
import numpy as np
import time

# Função para localizar a imagem na tela e clicar
def localizar_e_clicar(imagem, confidencia=0.8):
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot, dtype=np.uint8)  # Garante que seja CV_8U
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Carrega a imagem do botão e converte para CV_8U, se necessário
    template = cv2.imread(imagem, cv2.IMREAD_COLOR)
    template = template.astype(np.uint8)

    # Usa o método de correspondência de imagem
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
        print(f"Imagem encontrada e clicada em ({centro_x}, {centro_y})")
        return True
    else:
        print("Imagem não encontrada na tela.")
        return False

# Exemplo de uso
imagem_ver_produto = 'botao_ver_produto.png'
imagem_botao = 'botao_gerar_link.png'
if localizar_e_clicar(imagem_ver_produto):
    time.sleep(2)
    if localizar_e_clicar(imagem_botao):
        print("Botão clicado com sucesso!")
    else:
        print("Botão não foi encontrado.")
