"""
Sistema de Autenticação para Hospshop
Gerenciamento de usuários, login, JWT tokens e permissões
"""

import sqlite3
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Configuração JWT
JWT_SECRET = secrets.token_hex(32)
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

class AuthSystem:
    """Sistema de autenticação e autorização"""
    
    def __init__(self, db_path: str = 'hospshop_auth.db'):
        self.db_path = db_path
        self._criar_tabelas()
        self._criar_usuario_admin_padrao()
    
    def _criar_tabelas(self):
        """Cria tabelas de usuários e permissões"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                nome_completo TEXT NOT NULL,
                nivel_acesso TEXT NOT NULL,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP,
                criado_por INTEGER,
                FOREIGN KEY (criado_por) REFERENCES usuarios(id)
            )
        ''')
        
        # Tabela de sessões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_expiracao TIMESTAMP NOT NULL,
                ativo BOOLEAN DEFAULT 1,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        # Tabela de log de acessos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                acao TEXT NOT NULL,
                detalhes TEXT,
                ip_address TEXT,
                sucesso BOOLEAN DEFAULT 1,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_senha(self, senha: str) -> str:
        """Gera hash SHA-256 da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def _criar_usuario_admin_padrao(self):
        """Cria usuário admin padrão se não existir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE nivel_acesso = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            senha_hash = self._hash_senha('admin123')
            cursor.execute('''
                INSERT INTO usuarios (username, email, senha_hash, nome_completo, nivel_acesso)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'admin@hospshop.com', senha_hash, 'Administrador', 'admin'))
            conn.commit()
            print("✅ Usuário admin padrão criado (username: admin, senha: admin123)")
        
        conn.close()
    
    def criar_usuario(self, username: str, email: str, senha: str, 
                     nome_completo: str, nivel_acesso: str = 'operador',
                     criado_por: Optional[int] = None) -> Dict:
        """
        Cria novo usuário
        
        Níveis de acesso:
        - admin: Acesso total ao sistema
        - operador: Pode criar e editar registros
        - visualizador: Apenas visualização
        """
        if nivel_acesso not in ['admin', 'operador', 'visualizador']:
            raise ValueError("Nível de acesso inválido")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            senha_hash = self._hash_senha(senha)
            cursor.execute('''
                INSERT INTO usuarios (username, email, senha_hash, nome_completo, nivel_acesso, criado_por)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, senha_hash, nome_completo, nivel_acesso, criado_por))
            
            usuario_id = cursor.lastrowid
            conn.commit()
            
            # Log
            self._log_acesso(usuario_id, 'usuario_criado', f'Usuário {username} criado', None, True)
            
            return {
                'id': usuario_id,
                'username': username,
                'email': email,
                'nome_completo': nome_completo,
                'nivel_acesso': nivel_acesso,
                'ativo': True
            }
        
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                raise ValueError("Username já existe")
            elif 'email' in str(e):
                raise ValueError("Email já cadastrado")
            raise
        
        finally:
            conn.close()
    
    def login(self, username: str, senha: str, ip_address: str = None, 
             user_agent: str = None) -> Dict:
        """
        Realiza login e retorna token JWT
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        senha_hash = self._hash_senha(senha)
        
        cursor.execute('''
            SELECT id, username, email, nome_completo, nivel_acesso, ativo
            FROM usuarios
            WHERE username = ? AND senha_hash = ?
        ''', (username, senha_hash))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            self._log_acesso(None, 'login_falhou', f'Tentativa de login: {username}', ip_address, False)
            conn.close()
            raise ValueError("Usuário ou senha incorretos")
        
        usuario_id, username, email, nome_completo, nivel_acesso, ativo = usuario
        
        if not ativo:
            self._log_acesso(usuario_id, 'login_bloqueado', f'Usuário inativo: {username}', ip_address, False)
            conn.close()
            raise ValueError("Usuário inativo")
        
        # Gerar token JWT
        expiracao = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        token_payload = {
            'usuario_id': usuario_id,
            'username': username,
            'nivel_acesso': nivel_acesso,
            'exp': expiracao
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        # Salvar sessão
        cursor.execute('''
            INSERT INTO sessoes (usuario_id, token, ip_address, user_agent, data_expiracao)
            VALUES (?, ?, ?, ?, ?)
        ''', (usuario_id, token, ip_address, user_agent, expiracao))
        
        # Atualizar último login
        cursor.execute('''
            UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP WHERE id = ?
        ''', (usuario_id,))
        
        conn.commit()
        
        # Log
        self._log_acesso(usuario_id, 'login_sucesso', f'Login bem-sucedido: {username}', ip_address, True)
        
        conn.close()
        
        return {
            'token': token,
            'usuario': {
                'id': usuario_id,
                'username': username,
                'email': email,
                'nome_completo': nome_completo,
                'nivel_acesso': nivel_acesso
            },
            'expiracao': expiracao.isoformat()
        }
    
    def verificar_token(self, token: str) -> Optional[Dict]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Verificar se sessão está ativa
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ativo FROM sessoes 
                WHERE token = ? AND data_expiracao > CURRENT_TIMESTAMP
            ''', (token,))
            
            sessao = cursor.fetchone()
            conn.close()
            
            if not sessao or not sessao[0]:
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def logout(self, token: str):
        """Encerra sessão"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE sessoes SET ativo = 0 WHERE token = ?', (token,))
        conn.commit()
        
        # Log
        payload = self.verificar_token(token)
        if payload:
            self._log_acesso(payload['usuario_id'], 'logout', 'Logout realizado', None, True)
        
        conn.close()
    
    def listar_usuarios(self) -> List[Dict]:
        """Lista todos os usuários"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, nome_completo, nivel_acesso, ativo, 
                   data_criacao, ultimo_login
            FROM usuarios
            ORDER BY data_criacao DESC
        ''')
        
        usuarios = []
        for row in cursor.fetchall():
            usuarios.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'nome_completo': row[3],
                'nivel_acesso': row[4],
                'ativo': bool(row[5]),
                'data_criacao': row[6],
                'ultimo_login': row[7]
            })
        
        conn.close()
        return usuarios
    
    def alterar_senha(self, usuario_id: int, senha_antiga: str, senha_nova: str):
        """Altera senha do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar senha antiga
        senha_antiga_hash = self._hash_senha(senha_antiga)
        cursor.execute('SELECT id FROM usuarios WHERE id = ? AND senha_hash = ?', 
                      (usuario_id, senha_antiga_hash))
        
        if not cursor.fetchone():
            conn.close()
            raise ValueError("Senha antiga incorreta")
        
        # Atualizar senha
        senha_nova_hash = self._hash_senha(senha_nova)
        cursor.execute('UPDATE usuarios SET senha_hash = ? WHERE id = ?', 
                      (senha_nova_hash, usuario_id))
        conn.commit()
        
        # Invalidar todas as sessões do usuário
        cursor.execute('UPDATE sessoes SET ativo = 0 WHERE usuario_id = ?', (usuario_id,))
        conn.commit()
        
        # Log
        self._log_acesso(usuario_id, 'senha_alterada', 'Senha alterada com sucesso', None, True)
        
        conn.close()
    
    def desativar_usuario(self, usuario_id: int):
        """Desativa usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE usuarios SET ativo = 0 WHERE id = ?', (usuario_id,))
        cursor.execute('UPDATE sessoes SET ativo = 0 WHERE usuario_id = ?', (usuario_id,))
        conn.commit()
        
        # Log
        self._log_acesso(usuario_id, 'usuario_desativado', f'Usuário ID {usuario_id} desativado', None, True)
        
        conn.close()
    
    def _log_acesso(self, usuario_id: Optional[int], acao: str, detalhes: str, 
                   ip_address: Optional[str], sucesso: bool):
        """Registra log de acesso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO log_acessos (usuario_id, acao, detalhes, ip_address, sucesso)
            VALUES (?, ?, ?, ?, ?)
        ''', (usuario_id, acao, detalhes, ip_address, sucesso))
        
        conn.commit()
        conn.close()
    
    def obter_logs(self, limite: int = 100) -> List[Dict]:
        """Obtém logs de acesso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT l.id, l.usuario_id, u.username, l.acao, l.detalhes, 
                   l.ip_address, l.sucesso, l.data_hora
            FROM log_acessos l
            LEFT JOIN usuarios u ON l.usuario_id = u.id
            ORDER BY l.data_hora DESC
            LIMIT ?
        ''', (limite,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'id': row[0],
                'usuario_id': row[1],
                'username': row[2],
                'acao': row[3],
                'detalhes': row[4],
                'ip_address': row[5],
                'sucesso': bool(row[6]),
                'data_hora': row[7]
            })
        
        conn.close()
        return logs


# Teste do sistema
if __name__ == '__main__':
    print("🔐 Testando Sistema de Autenticação Hospshop\n")
    
    auth = AuthSystem()
    
    # Teste 1: Login com admin padrão
    print("1️⃣ Testando login com admin padrão...")
    try:
        resultado = auth.login('admin', 'admin123', '127.0.0.1', 'Test Agent')
        print(f"✅ Login bem-sucedido!")
        print(f"   Token: {resultado['token'][:50]}...")
        print(f"   Usuário: {resultado['usuario']['nome_completo']}")
        print(f"   Nível: {resultado['usuario']['nivel_acesso']}")
        token_admin = resultado['token']
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Verificar token
    print("\n2️⃣ Testando verificação de token...")
    payload = auth.verificar_token(token_admin)
    if payload:
        print(f"✅ Token válido!")
        print(f"   Usuário ID: {payload['usuario_id']}")
        print(f"   Username: {payload['username']}")
    else:
        print("❌ Token inválido")
    
    # Teste 3: Criar novo usuário
    print("\n3️⃣ Testando criação de usuário...")
    try:
        novo_usuario = auth.criar_usuario(
            username='operador1',
            email='operador1@hospshop.com',
            senha='senha123',
            nome_completo='João Operador',
            nivel_acesso='operador',
            criado_por=1
        )
        print(f"✅ Usuário criado!")
        print(f"   ID: {novo_usuario['id']}")
        print(f"   Username: {novo_usuario['username']}")
        print(f"   Nível: {novo_usuario['nivel_acesso']}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 4: Listar usuários
    print("\n4️⃣ Testando listagem de usuários...")
    usuarios = auth.listar_usuarios()
    print(f"✅ {len(usuarios)} usuários encontrados:")
    for u in usuarios:
        print(f"   - {u['username']} ({u['nivel_acesso']}) - Ativo: {u['ativo']}")
    
    # Teste 5: Obter logs
    print("\n5️⃣ Testando logs de acesso...")
    logs = auth.obter_logs(limite=5)
    print(f"✅ {len(logs)} logs encontrados:")
    for log in logs:
        print(f"   - {log['acao']}: {log['detalhes']} ({log['data_hora']})")
    
    print("\n✅ Todos os testes concluídos!")
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de usuários: {len(usuarios)}")
    print(f"   - Usuários ativos: {sum(1 for u in usuarios if u['ativo'])}")
    print(f"   - Total de logs: {len(logs)}")
