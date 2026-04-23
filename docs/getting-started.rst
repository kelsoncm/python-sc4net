=====================
Guia de Introdução
=====================

O **sc4net** é um pacote Python que fornece atalhos para downloads HTTP(S) e FTP usando apenas a biblioteca padrão, além de utilitários para leitura de JSON e arquivos ZIP.

Instalação
----------

.. code-block:: bash

    pip install sc4net

Uso Básico
----------

Exemplo de como baixar um conteúdo HTTP:

.. code-block:: python

    from sc4net import get
    conteudo = get('https://exemplo.com/dados.txt')
    print(conteudo)

Exemplo para baixar e ler um JSON:

.. code-block:: python

    from sc4net import get_json
    dados = get_json('https://exemplo.com/dados.json')
    print(dados)

Exemplo para baixar e ler um arquivo ZIP:

.. code-block:: python

    from sc4net import get_zip_content
    texto = get_zip_content('https://exemplo.com/arquivo.zip', file_id=0)
    print(texto)

Contribuindo
------------

1. Clone o repositório:

.. code-block:: bash

    git clone git@github.com:kelsoncm/sc4.git ~/projetos/PESSOAL/sc4net
    cd ~/projetos/PESSOAL/sc4net

2. Crie o ambiente virtual e instale as dependências de desenvolvimento:

.. code-block:: bash

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install --upgrade pip uv
    uv pip install --upgrade -e ".[dev]"

3. Instale os hooks do pre-commit:

.. code-block:: bash

    pre-commit install
    pre-commit install --hook-type pre-push

4. Execute os testes e validações:

.. code-block:: bash

    pre-commit run --all-files
    pre-commit run --hook-stage pre-push --all-files

Veja o README.md para mais detalhes.
