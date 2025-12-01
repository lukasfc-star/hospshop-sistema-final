# Checklist de Deploy em Produção - Hospshop

**Data**: 01/12/2025 09:04

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

