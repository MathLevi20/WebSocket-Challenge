# Olá, avaliador(a)! 👋

Antes de mais nada, obrigado por dedicar seu tempo para conferir este projeto.  
Tentei manter tudo simples, funcional e bem organizado.

Fique à vontade para explorar, testar e, claro, sugerir qualquer melhoria!

Abraços,  
**Matheus Levi**

---

## Como rodar

```bash
# 0. Instale o Python 3.13 (Ubuntu/Debian)
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev

# 1. Crie e ative um ambiente virtual
python3.13 -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate  # Windows

# 2. Instale as dependências do projeto
cd realmate_challenge
poetry install

# 3. Aplique as migrações no banco de dados SQLite
python manage.py migrate

# 4. Execute o servidor de desenvolvimento
python manage.py runserver
