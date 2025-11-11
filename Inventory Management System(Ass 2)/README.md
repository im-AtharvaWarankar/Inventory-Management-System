## Atomicloops Django Setup

### Project-Name : <>

### 1. Clone the repository

```
git clone <url>
cd <repo-name>
git checkout -b dev
```

### 2. Install AWS CLI and configurations as per your os

- [Install AWSCLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Install & Configure AWSCLI](https://medium.com/analytics-vidhya/configure-aws-cli-and-execute-commands-fc16a17b0aa2)

### 3. Create a new virtualenv and install requirements (Soon will be deprecated)

- [How to install virtualenv](./docs/Install%20Virtaulenv.pdf)

#### Windows

```
virtualenv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install "drf-yasg[validation]"
pip install git+https://github.com/atomic-loops/atomicloops-django-logger
```

#### Linux and Mac OS

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install "drf-yasg[validation]"
pip install git+https://github.com/atomic-loops/atomicloops-django-logger
```

### 4. Download vault file
Note: After downloading please update the vault file with your email credentials.


A. Initial
```
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

Windows

```
curl -o src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

B. Latest

```
wget -O src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

Windows

```
curl -o src/vault.py https://atomicloops-dev.s3.ap-south-1.amazonaws.com/vault.py
```

Note :- Update the urls for Lastest Section when you sync the vault file.

### 5. Initialize Project Setup

[Setup Email Password](http://165.232.181.62/books/backend-development/page/generate-password-for-automated-e-mail)

[Atomicloops Django Setup](./docs/ProjectSetup.pdf)

[Atomicloops Custom Commands with Bash](http://165.232.181.62/books/backend-development/page/django-atomicloops-commands-bash)

[Atomicloops Custom Commands python](https://drive.google.com/file/d/1dKK_Eo-7OAAFYTrEtS_N5pQGDLK06Y-a/view?usp=share_link)

### 6. Makemigrations and Create Table

```
./run.sh start-dev
./run.sh interactive-dev
python manage.py makemigrations
python manage.py migrate
```

### 7. Start Server

```sh
./run.sh start-dev
```

### 8. Update and Sync Vault

To Add Secret key add the variable to vault file.

```
./run.sh sync-vault
```

### 9. How to add new libraries
Bash scripts
```
./run.sh interactive-dev
pip install <package_name>
pip freeze > requirements.txt
exit
./run.sh start-dev
```
Python scripts
```
source venv/bin/activate
pip install <package_name>
pip freeze > requirements.txt
python manage.py run --mode start-dev
```

TODO:
Create atomicloops package
