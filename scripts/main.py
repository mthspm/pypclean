from window import Window

if __name__ == '__main__':
    try: 
        window = Window()
        window.run()
    except Exception as e:
        print('Erro ao inicializar aplicacao...',e)
        input("Pressione qualquer tecla para sair...")