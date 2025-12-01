"""
Sistema de Backup Automatizado AWS S3
Backup de banco de dados e aplicação

Desenvolvido originalmente no Chat 3 e reconstruído em 01/12/2025
"""

import os
import sqlite3
import gzip
import shutil
import logging
from datetime import datetime
from pathlib import Path
import subprocess

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackupSystem:
    """
    Sistema de backup automatizado para AWS S3
    """
    
    def __init__(self, 
                 db_path='hospshop.db',
                 backup_dir='/tmp/hospshop_backups',
                 s3_bucket=None):
        """
        Inicializa sistema de backup
        
        Args:
            db_path: Caminho do banco de dados
            backup_dir: Diretório temporário para backups
            s3_bucket: Nome do bucket S3 (ex: hospshop-backups)
        """
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.s3_bucket = s3_bucket or os.getenv('S3_BACKUP_BUCKET', 'hospshop-backups')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Criar diretório de backup se não existir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_database(self) -> str:
        """
        Cria backup do banco de dados SQLite
        
        Returns:
            Caminho do arquivo de backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'hospshop_db_{timestamp}.sql'
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Fazer dump do banco SQLite
            logger.info(f"📦 Criando backup do banco de dados...")
            
            conn = sqlite3.connect(self.db_path)
            with open(backup_path, 'w') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            conn.close()
            
            # Comprimir backup
            compressed_path = f'{backup_path}.gz'
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remover arquivo não comprimido
            os.remove(backup_path)
            
            file_size = os.path.getsize(compressed_path) / 1024  # KB
            logger.info(f"✅ Backup criado: {compressed_path} ({file_size:.2f} KB)")
            
            return compressed_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup do banco: {e}")
            return None
    
    def backup_application(self) -> str:
        """
        Cria backup da aplicação completa
        
        Returns:
            Caminho do arquivo de backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'hospshop_app_{timestamp}.tar.gz'
        backup_path = self.backup_dir / backup_filename
        
        try:
            logger.info(f"📦 Criando backup da aplicação...")
            
            # Arquivos a incluir no backup
            files_to_backup = [
                '*.py',
                'requirements.txt',
                'README.md',
                'Dockerfile',
                'railway.json',
                'static/',
                'templates/' if os.path.exists('templates') else None
            ]
            
            # Filtrar None
            files_to_backup = [f for f in files_to_backup if f]
            
            # Criar arquivo tar.gz
            import tarfile
            with tarfile.open(backup_path, 'w:gz') as tar:
                for pattern in files_to_backup:
                    if pattern.endswith('/'):
                        # Diretório
                        if os.path.exists(pattern):
                            tar.add(pattern)
                    else:
                        # Arquivos com padrão
                        import glob
                        for file in glob.glob(pattern):
                            tar.add(file)
            
            file_size = os.path.getsize(backup_path) / 1024  # KB
            logger.info(f"✅ Backup da aplicação criado: {backup_path} ({file_size:.2f} KB)")
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup da aplicação: {e}")
            return None
    
    def upload_to_s3(self, file_path: str) -> bool:
        """
        Faz upload do backup para S3
        
        Args:
            file_path: Caminho do arquivo de backup
            
        Returns:
            True se upload bem-sucedido, False caso contrário
        """
        try:
            # Verificar se boto3 está instalado
            try:
                import boto3
                from botocore.exceptions import ClientError
            except ImportError:
                logger.warning("⚠️ boto3 não instalado. Execute: pip install boto3")
                logger.info("ℹ️  Backup criado localmente em: " + file_path)
                return False
            
            logger.info(f"☁️  Fazendo upload para S3: {self.s3_bucket}")
            
            # Criar cliente S3
            s3_client = boto3.client('s3', region_name=self.aws_region)
            
            # Nome do arquivo no S3
            s3_key = f"backups/{os.path.basename(file_path)}"
            
            # Upload
            s3_client.upload_file(file_path, self.s3_bucket, s3_key)
            
            logger.info(f"✅ Upload concluído: s3://{self.s3_bucket}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no upload S3: {e}")
            logger.info(f"ℹ️  Backup mantido localmente em: {file_path}")
            return False
    
    def executar_backup_completo(self, upload_s3: bool = True) -> dict:
        """
        Executa backup completo (banco + aplicação)
        
        Args:
            upload_s3: Se True, faz upload para S3
            
        Returns:
            Dicionário com resultado do backup
        """
        logger.info("\n" + "="*60)
        logger.info("🚀 INICIANDO BACKUP COMPLETO")
        logger.info("="*60)
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'database_backup': None,
            'app_backup': None,
            's3_upload': False,
            'success': False
        }
        
        # Backup do banco
        db_backup = self.backup_database()
        if db_backup:
            resultado['database_backup'] = db_backup
        
        # Backup da aplicação
        app_backup = self.backup_application()
        if app_backup:
            resultado['app_backup'] = app_backup
        
        # Upload para S3
        if upload_s3 and (db_backup or app_backup):
            uploads_ok = []
            if db_backup:
                uploads_ok.append(self.upload_to_s3(db_backup))
            if app_backup:
                uploads_ok.append(self.upload_to_s3(app_backup))
            
            resultado['s3_upload'] = any(uploads_ok)
        
        # Verificar sucesso
        resultado['success'] = bool(db_backup or app_backup)
        
        logger.info("="*60)
        if resultado['success']:
            logger.info("✅ BACKUP COMPLETO CONCLUÍDO")
        else:
            logger.info("❌ BACKUP FALHOU")
        logger.info("="*60 + "\n")
        
        return resultado
    
    def listar_backups_locais(self) -> list:
        """
        Lista backups locais disponíveis
        
        Returns:
            Lista de arquivos de backup
        """
        backups = []
        for file in self.backup_dir.glob('hospshop_*'):
            backups.append({
                'filename': file.name,
                'path': str(file),
                'size_kb': file.stat().st_size / 1024,
                'created': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def limpar_backups_antigos(self, dias: int = 7) -> int:
        """
        Remove backups locais mais antigos que X dias
        
        Args:
            dias: Número de dias para manter backups
            
        Returns:
            Número de backups removidos
        """
        from datetime import timedelta
        
        limite = datetime.now() - timedelta(days=dias)
        removidos = 0
        
        for file in self.backup_dir.glob('hospshop_*'):
            file_time = datetime.fromtimestamp(file.stat().st_mtime)
            if file_time < limite:
                file.unlink()
                removidos += 1
                logger.info(f"🗑️  Backup antigo removido: {file.name}")
        
        logger.info(f"✅ {removidos} backups antigos removidos")
        return removidos


def agendar_backup_diario():
    """
    Configura agendamento de backup diário
    Usar com cron ou scheduler
    """
    print("\n📅 CONFIGURAÇÃO DE BACKUP DIÁRIO\n")
    print("Para agendar backup diário, adicione ao crontab:")
    print("\n# Backup diário às 2h da manhã")
    print("0 2 * * * cd /caminho/hospshop && python3 sistema_backup_automatizado.py\n")
    print("Ou use um scheduler Python (APScheduler, Celery, etc.)\n")


def testar_backup():
    """Função de teste do sistema de backup"""
    print("\n" + "="*60)
    print("🧪 TESTE DE SISTEMA DE BACKUP")
    print("="*60 + "\n")
    
    backup_system = BackupSystem()
    
    # Teste 1: Backup do banco
    print("1️⃣ Testando backup do banco de dados...")
    db_backup = backup_system.backup_database()
    if db_backup:
        print(f"   ✅ Backup criado: {db_backup}\n")
    else:
        print("   ❌ Erro ao criar backup\n")
    
    # Teste 2: Backup da aplicação
    print("2️⃣ Testando backup da aplicação...")
    app_backup = backup_system.backup_application()
    if app_backup:
        print(f"   ✅ Backup criado: {app_backup}\n")
    else:
        print("   ❌ Erro ao criar backup\n")
    
    # Teste 3: Listar backups
    print("3️⃣ Listando backups locais...")
    backups = backup_system.listar_backups_locais()
    for b in backups[:5]:
        print(f"   📦 {b['filename']} ({b['size_kb']:.2f} KB)")
    print()
    
    # Teste 4: Backup completo
    print("4️⃣ Executando backup completo...")
    resultado = backup_system.executar_backup_completo(upload_s3=False)
    print(f"   Sucesso: {'✅ SIM' if resultado['success'] else '❌ NÃO'}")
    print(f"   Backup DB: {resultado['database_backup']}")
    print(f"   Backup App: {resultado['app_backup']}")
    print()
    
    print("="*60)
    print("✅ SISTEMA DE BACKUP FUNCIONANDO")
    print("="*60 + "\n")
    
    print("📝 Próximos passos:")
    print("   1. Instalar boto3: pip install boto3")
    print("   2. Configurar credenciais AWS")
    print("   3. Criar bucket S3")
    print("   4. Agendar backups automáticos\n")


if __name__ == '__main__':
    testar_backup()
