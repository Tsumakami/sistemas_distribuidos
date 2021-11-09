# Trabalho de Sistemas Distribuidos

Autores: João Paulo Malvesti, Guilherme Henrique Portigliotti, Danilo Marmentini

## Objetivo do trabalho

Simular um centralizador de estoque com socket e threads.

A arquitetura é constituida de 3 Serviços, a aplicação principal onde vai centralizar as requests de consulta, o Centro de distribuição e um serviço que disponibiliza os estoque das lojas. Para se comunicar com a aplicação principal foi implementado um "cliente" capaz de interagir com os serviços, sendo possivel subir várias instancias do mesmo.

![Arquitetura da aplicação](https://github.com/Tsumakami/sistemas_distribuidos/blob/7c9b2ccebf7bc52e89a9734f086f72ec3adedfbb/img/arq.png)

## Linguagem utilizada

- Python 3.8.10

## Bibliotecas uitlizadas

- socket
- threading
- logging
- os
- json
- typing
- collections
- time

## Como excutar e simular os serviços


Para Simular é necessário subir os 3 serviços antes da aplicação que interage com os serviços

Serviço do Centro de Distribuição:
```sh
python3 dc_service.py
```
Serviço de Estoque nas lojas:
```sh
python3 store_service.py
```
Aplicação principal:
```sh
python3 application_serve.py
```
Cliente para interagir com a aplicação (pode subir várias instâncias):
```sh
python3 consult_client.py
```

