"""
Script de Preparação para Produção
Gera pacote completo e checklist de deploy

Desenvolvido originalmente no Chat 3 e reconstruído em 01/12/2025
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path


class PreparadorProducao:
    """
    Classe para preparar sistema para deploy em produção
    """
    
    def __init__(self, project_dir='.'):
        self.project_dir = Path(project_dir)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def verificar_arquivos_essenciais(self) -> dict:
        """
        Verifica se todos os arquivos essenciais existem
        
        Returns:
            Dicionário com status dos arquivos
        """
        print("\n📋 VERIFICANDO ARQUIVOS ESSENCIAIS\n")
        
        arquivos_essenciais = {
            'app.py': 'Aplicação Flask principal',
            'requirements.txt': 'Dependências Python',
            'Dockerfile': 'Configuração Docker',
            'railway.json': 'Configuração Railway',
            'README.md': 'Documentação',
            'effecti_integration.py': 'Integração Effecti',
            'api_analise.py': 'API Análise Concorrentes',
            'notifications.py': 'Sistema de Notificações',
            'padronizacao.py': 'Padronização de Captação',
            'sistema_backup_automatizado.py': 'Sistema de Backup'
        }
        
        status = {}
        for arquivo, descricao in arquivos_essenciais.items():
            existe = (self.project_dir / arquivo).exists()
            status[arquivo] = existe
            emoji = "✅" if existe else "❌"
            print(f"{emoji} {arquivo:40} - {descricao}")
        
        print()
        return status
    
    def gerar_requirements_completo(self) -> bool:
        """
        Gera requirements.txt completo com todas as dependências
        """
        print("📦 GERANDO REQUIREMENTS.TXT COMPLETO\n")
        
        dependencias = [
            "# Hospshop - Sistema de Gestão de Licitações",
            "# Gerado em: " + datetime.now().isoformat(),
            "",
            "# Framework Web",
            "Flask==3.0.0",
            "Flask-CORS==4.0.0",
            "gunicorn==21.2.0",
            "",
            "# Banco de Dados",
            "# SQLite (built-in Python)",
            "# Para PostgreSQL em produção:",
            "# psycopg2-binary==2.9.9",
            "",
            "# Segurança",
            "Werkzeug==3.0.1",
            "",
            "# Web Scraping e Requests",
            "requests==2.31.0",
            "beautifulsoup4==4.12.2",
            "lxml==4.9.3",
            "",
            "# Notificações",
            "# E-mail (built-in smtplib)",
            "",
            "# AWS SDK (para backup S3)",
            "boto3==1.34.0",
            "",
            "# Tarefas Assíncronas (opcional)",
            "# celery==5.3.4",
            "# redis==5.0.1",
            "",
            "# Utilitários",
            "python-dotenv==1.0.0",
            "",
            "# Desenvolvimento",
            "# pytest==7.4.3",
            "# black==23.12.0",
            "# flake8==6.1.0",
        ]
        
        try:
            requirements_path = self.project_dir / 'requirements.txt'
            with open(requirements_path, 'w') as f:
                f.write('\n'.join(dependencias))
            
            print(f"✅ requirements.txt atualizado\n")
            return True
        except Exception as e:
            print(f"❌ Erro ao gerar requirements.txt: {e}\n")
            return False
    
    def gerar_env_exemplo(self) -> bool:
        """
        Gera arquivo .env.example com variáveis de ambiente necessárias
        """
        print("🔐 GERANDO .ENV.EXAMPLE\n")
        
        env_vars = [
            "# Hospshop - Variáveis de Ambiente",
            "# Copie para .env e preencha os valores",
            "",
            "# Flask",
            "SECRET_KEY=sua-chave-secreta-aqui",
            "FLASK_ENV=production",
            "",
            "# Banco de Dados",
            "DATABASE_URL=hospshop.db",
            "# Para PostgreSQL:",
            "# DATABASE_URL=postgresql://user:password@host:5432/hospshop",
            "",
            "# E-mail (SMTP)",
            "SMTP_SERVER=smtp.gmail.com",
            "SMTP_PORT=587",
            "SMTP_USER=seu-email@gmail.com",
            "SMTP_PASSWORD=sua-senha-ou-app-password",
            "",
            "# WhatsApp",
            "WHATSAPP_API_KEY=sua-api-key",
            "WHATSAPP_API_URL=https://api.whatsapp.com/send",
            "",
            "# AWS S3 (Backup)",
            "AWS_ACCESS_KEY_ID=sua-access-key",
            "AWS_SECRET_ACCESS_KEY=sua-secret-key",
            "AWS_REGION=us-east-1",
            "S3_BACKUP_BUCKET=hospshop-backups",
            "",
            "# Effecti (se houver API key)",
            "EFFECTI_API_KEY=sua-api-key",
            "EFFECTI_API_URL=https://api.effecti.com.br",
        ]
        
        try:
            env_path = self.project_dir / '.env.example'
            with open(env_path, 'w') as f:
                f.write('\n'.join(env_vars))
            
            print(f"✅ .env.example criado\n")
            return True
        except Exception as e:
            print(f"❌ Erro ao gerar .env.example: {e}\n")
            return False
    
    def gerar_checklist_deploy(self) -> bool:
        """
        Gera checklist de deploy em produção
        """
        print("📝 GERANDO CHECKLIST DE DEPLOY\n")
        
        checklist = """# Checklist de Deploy em Produção - Hospshop

**Data**: {timestamp}

---

## 🔐 Segurança

- [ ] SECRET_KEY configurada (gerada aleatoriamente)
- [ ] Senhas de banco de dados fortes
- [ ] Credenciais AWS configuradas
- [ ] HTTPS/SSL ativo
- [ ] Firewall configurado
- [ ] Backup automático ativo

---

## 🗄️ Banco de Dados

- [ ] Migração SQLite → PostgreSQL (se aplicável)
- [ ] Backup inicial criado
- [ ] Índices criados nas tabelas principais
- [ ] Dados de teste removidos
- [ ] Conexão SSL ativa

---

## 🚀 Aplicação

- [ ] Todas as dependências instaladas
- [ ] Variáveis de ambiente configuradas
- [ ] Gunicorn configurado (workers, timeout)
- [ ] Logs configurados
- [ ] Monitoramento ativo

---

## 📧 Integrações

- [ ] SMTP configurado e testado
- [ ] WhatsApp API configurada
- [ ] Effecti integração testada
- [ ] AWS S3 backup testado
- [ ] Google Sheets (se aplicável)

---

## 🌐 Deploy

- [ ] Domínio configurado
- [ ] DNS apontando corretamente
- [ ] Certificado SSL instalado
- [ ] Railway/AWS configurado
- [ ] Variáveis de ambiente no servidor
- [ ] Build bem-sucedido

---

## ✅ Testes

- [ ] Teste de login
- [ ] Teste de captura Effecti
- [ ] Teste de notificações
- [ ] Teste de backup
- [ ] Teste de análise de concorrentes
- [ ] Teste de performance

---

## 📊 Monitoramento

- [ ] Logs centralizados
- [ ] Alertas configurados
- [ ] Métricas de performance
- [ ] Backup automático agendado
- [ ] Monitoramento de uptime

---

## 📚 Documentação

- [ ] README.md atualizado
- [ ] Documentação de API
- [ ] Manual de usuário
- [ ] Guia de troubleshooting
- [ ] Contatos de suporte

---

## 🎯 Pós-Deploy

- [ ] Teste completo em produção
- [ ] Treinamento da equipe
- [ ] Backup inicial verificado
- [ ] Monitoramento ativo
- [ ] Plano de rollback preparado

---

**Status**: 🔄 Em Preparação

**Responsável**: _____________

**Data Prevista**: _____________

""".format(timestamp=datetime.now().strftime('%d/%m/%Y %H:%M'))
        
        try:
            checklist_path = self.project_dir / 'CHECKLIST_DEPLOY.md'
            with open(checklist_path, 'w') as f:
                f.write(checklist)
            
            print(f"✅ CHECKLIST_DEPLOY.md criado\n")
            return True
        except Exception as e:
            print(f"❌ Erro ao gerar checklist: {e}\n")
            return False
    
    def gerar_documentacao_modulos(self) -> bool:
        """
        Gera documentação dos módulos desenvolvidos
        """
        print("📖 GERANDO DOCUMENTAÇÃO DOS MÓDULOS\n")
        
        doc = """# Documentação dos Módulos - Sistema Hospshop

**Versão**: 1.0  
**Data**: {timestamp}

---

## 📦 Módulos Desenvolvidos

### 1. effecti_integration.py - Integração Effecti

**Descrição**: Sistema de captura automática de licitações da plataforma Effecti.

**Principais Funcionalidades**:
- Busca de licitações por palavra-chave e estado
- Salvamento automático no banco de dados
- Validação de duplicatas
- Atualização de status

**Uso**:
```python
from effecti_integration import EffectiIntegration

effecti = EffectiIntegration()
resultado = effecti.capturar_e_salvar('hospitalar', estado='SP', limite=50)
```

---

### 2. api_analise.py - API de Análise de Concorrentes

**Descrição**: API REST para análise de concorrentes em licitações.

**Endpoints**:
- `GET /api/analise/metricas` - Métricas gerais
- `GET /api/analise/irregularidades` - Lista irregularidades
- `GET /api/analise/recursos` - Recursos gerados
- `GET /api/analise/licitacoes` - Licitações ativas

**Dashboard**: React integrado em `/static/dashboard/`

---

### 3. notifications.py - Sistema de Notificações

**Descrição**: Gerenciamento de notificações por e-mail e WhatsApp.

**Principais Funcionalidades**:
- Envio de e-mails via SMTP
- Integração WhatsApp Business API
- Templates HTML profissionais
- Notificações de eventos (nova licitação, prazo próximo)

**Uso**:
```python
from notifications import NotificationManager

manager = NotificationManager()
manager.notificar_nova_licitacao(
    email='usuario@example.com',
    licitacao=dados_licitacao
)
```

---

### 4. padronizacao.py - Padronização de Captação

**Descrição**: Sistema de filtros e validação de licitações.

**Principais Funcionalidades**:
- Configuração de estados prioritários
- Palavras-chave por categoria
- Tipos de cliente
- Sistema de score e priorização

**Uso**:
```python
from padronizacao import PadronizacaoCaptacao

padrao = PadronizacaoCaptacao()
resultado = padrao.validar_licitacao(licitacao)
# resultado['score'], resultado['prioridade'], resultado['valida']
```

---

### 5. sistema_backup_automatizado.py - Backup AWS S3

**Descrição**: Sistema de backup automático para AWS S3.

**Principais Funcionalidades**:
- Backup do banco de dados (dump comprimido)
- Backup da aplicação completa
- Upload para S3
- Limpeza de backups antigos

**Uso**:
```python
from sistema_backup_automatizado import BackupSystem

backup = BackupSystem()
resultado = backup.executar_backup_completo(upload_s3=True)
```

---

### 6. app.py - Aplicação Principal

**Descrição**: Aplicação Flask principal com todas as rotas e integrações.

**Principais Rotas**:
- `/` - Dashboard principal
- `/login` - Autenticação
- `/fornecedores` - CRUD fornecedores
- `/licitacoes` - CRUD licitações
- `/plataformas` - CRUD plataformas
- `/analise-concorrentes` - Dashboard de análise

---

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais

1. **usuarios** - Autenticação
2. **fornecedores** - Cadastro de fornecedores
3. **licitacoes** - Licitações cadastradas
4. **plataformas** - Plataformas de licitação
5. **licitacoes_effecti** - Licitações capturadas do Effecti
6. **config_filtros** - Configurações de filtros
7. **estados_prioritarios** - Estados prioritários
8. **tipos_cliente** - Tipos de cliente
9. **palavras_chave** - Palavras-chave para busca

---

## 🔧 Configuração

### Variáveis de Ambiente

Ver arquivo `.env.example` para lista completa.

### Dependências

Ver `requirements.txt` para lista completa de dependências Python.

---

## 📊 Métricas e Monitoramento

- Dashboard de Análise de Concorrentes: métricas em tempo real
- Logs: arquivo `hospshop.log` (configurar)
- Backup: diário às 2h (configurar cron)

---

**Desenvolvido por**: Equipe Hospshop  
**Última Atualização**: {timestamp}

""".format(timestamp=datetime.now().strftime('%d/%m/%Y %H:%M'))
        
        try:
            doc_path = self.project_dir / 'DOCUMENTACAO_MODULOS.md'
            with open(doc_path, 'w') as f:
                f.write(doc)
            
            print(f"✅ DOCUMENTACAO_MODULOS.md criado\n")
            return True
        except Exception as e:
            print(f"❌ Erro ao gerar documentação: {e}\n")
            return False
    
    def executar_preparacao_completa(self):
        """
        Executa preparação completa para produção
        """
        print("\n" + "="*60)
        print("🚀 PREPARAÇÃO PARA PRODUÇÃO - HOSPSHOP")
        print("="*60)
        
        # Verificar arquivos
        status_arquivos = self.verificar_arquivos_essenciais()
        
        # Gerar arquivos de configuração
        self.gerar_requirements_completo()
        self.gerar_env_exemplo()
        self.gerar_checklist_deploy()
        self.gerar_documentacao_modulos()
        
        # Resumo
        print("="*60)
        print("✅ PREPARAÇÃO CONCLUÍDA")
        print("="*60)
        print("\n📁 Arquivos Gerados:")
        print("   • requirements.txt (atualizado)")
        print("   • .env.example")
        print("   • CHECKLIST_DEPLOY.md")
        print("   • DOCUMENTACAO_MODULOS.md")
        print("\n📝 Próximos Passos:")
        print("   1. Revisar CHECKLIST_DEPLOY.md")
        print("   2. Configurar variáveis de ambiente (.env)")
        print("   3. Testar aplicação localmente")
        print("   4. Fazer deploy em produção")
        print("   5. Executar testes pós-deploy")
        print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    preparador = PreparadorProducao()
    preparador.executar_preparacao_completa()
