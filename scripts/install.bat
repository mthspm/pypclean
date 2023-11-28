@echo off
title PC_SCAN
echo Initializing the scanner...
cls
echo Installing the required modules...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Modules installed successfully!
cls
python main.py
echo #===============================================================# 
echo #                    Programa Finalizado.                       # 
echo #                                                               # 
echo #   Obrigado por confia e utilizar o software. Toda a equipe    # 
echo #          de desenvolvimento e contribuicao agradece!          # 
echo #                                                               #
echo #   Sinta-se a vontade para contribuir para o desenvolvimento   #
echo #   do App, pois-se trata de um projeto open-source e aberto    #
echo #                      para contribuicoes!                      #
echo #                                                               #
echo #                                                               #
echo #                         Obrigado!                             #
echo #===============================================================# 
echo.
echo.
pause