# Documentação dos Módulos - Sistema Hospshop

**Versão**: 1.0  
**Data**: 01/12/2025 09:04

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
**Última Atualização**: 01/12/2025 09:04

