# 📖 Manual do Usuário - Sistema Hospshop

## 🎯 Bem-vindo ao Sistema Hospshop!

Este manual irá guiá-lo através de todas as funcionalidades do sistema de gestão de licitações e fornecimento hospitalar.

---

## 🔐 1. Primeiro Acesso

### 1.1 Login

1. Acesse o sistema em: http://localhost:3000
2. Digite suas credenciais:
   - **Username**: fornecido pelo administrador
   - **Senha**: fornecida pelo administrador
3. Clique em **Entrar**

### 1.2 Alterar Senha (Recomendado)

1. Após o primeiro login, clique em **Configurações** no canto superior direito
2. Selecione **Alterar Senha**
3. Digite a senha atual e a nova senha
4. Clique em **Salvar**

---

## 📊 2. Dashboard Principal

O Dashboard é a tela inicial do sistema e apresenta:

### 2.1 KPIs Principais

- **Licitações Ativas**: Quantidade de licitações em andamento
- **Valor Total Contratos**: Soma de todos os contratos ativos
- **Economia Gerada**: Economia obtida através de análise de concorrentes
- **Taxa de Sucesso**: Percentual de propostas vencedoras

### 2.2 Módulos do Sistema

Acesse os 9 módulos principais clicando nos cards:

1. **Licitações** - Gerenciar licitações
2. **Análise Concorrentes** - Ver irregularidades
3. **Cotações** - Sistema de cotações
4. **Contratos** - Gestão de contratos
5. **Financeiro** - Controle financeiro
6. **Logística** - Entregas e rastreamento
7. **Fornecedores** - Gestão de fornecedores
8. **Notificações** - Email e WhatsApp
9. **Relatórios** - Relatórios gerenciais

### 2.3 Atividade Recente

Visualize as últimas 5 atividades do sistema em tempo real.

### 2.4 Ações Rápidas

Acesso rápido às funções mais utilizadas:
- Importar Licitações
- Nova Proposta
- Enviar Notificação
- Gerar Relatório
- Ver Análises

---

## 📄 3. Módulo de Licitações

### 3.1 Visualizar Licitações

1. Clique em **Licitações** no Dashboard
2. Veja a lista de todas as licitações
3. Use a **barra de busca** para encontrar licitações específicas
4. Use os **filtros** para filtrar por status:
   - Aberta
   - Em análise
   - Proposta enviada
   - Vencida
   - Perdida

### 3.2 Capturar Novas Licitações

1. Clique no botão **Capturar do Effecti**
2. O sistema buscará automaticamente novas licitações
3. Aguarde a confirmação de sucesso
4. As novas licitações aparecerão na lista

### 3.3 Detalhes da Licitação

Cada card de licitação mostra:
- **Número do edital**
- **Órgão contratante**
- **Objeto da licitação**
- **Valor estimado**
- **Data de abertura**
- **Estado**
- **Status** (badge colorido)

### 3.4 Ações Disponíveis

- **Criar Proposta**: Iniciar nova proposta para esta licitação
- **Baixar Edital**: Download do PDF do edital

---

## 💰 4. Módulo de Cotações

### 4.1 Visualizar Cotações

1. Acesse **Cotações** no Dashboard
2. Veja todas as solicitações de cotação
3. Use filtros por status:
   - Aguardando propostas
   - Em análise
   - Concluída

### 4.2 Criar Nova Cotação

1. Clique em **Nova Cotação**
2. Preencha os dados:
   - Número do edital
   - Descrição
   - Itens (descrição, quantidade, unidade)
   - Prazo de resposta
3. Clique em **Criar**

### 4.3 Comparar Propostas

1. Clique em **Comparar** em uma cotação
2. Veja a comparação automática:
   - Menor preço
   - Maior preço
   - Preço médio
   - Economia potencial
3. Selecione a proposta vencedora

---

## 💵 5. Módulo Financeiro

### 5.1 Visão Geral

O módulo financeiro apresenta:
- **Saldo Atual**
- **Total de Receitas**
- **Total de Despesas**
- **Resultado (Receitas - Despesas)**

### 5.2 Gráficos

- **Gráfico de Barras**: Receitas vs Despesas mensais
- **Gráfico de Linhas**: Evolução do saldo

### 5.3 Registrar Receita

1. Clique em **Nova Receita**
2. Preencha:
   - Descrição
   - Valor
   - Categoria
   - Data
3. Clique em **Salvar**

### 5.4 Registrar Despesa

1. Clique em **Nova Despesa**
2. Preencha os mesmos campos da receita
3. Clique em **Salvar**

### 5.5 Contas a Receber/Pagar

Visualize:
- **Contas a Receber**: Valores que você vai receber
- **Contas a Pagar**: Valores que você deve pagar
- **Vencimento**: Data de vencimento de cada conta

---

## 🚚 6. Módulo de Logística

### 6.1 Visualizar Entregas

1. Acesse **Logística**
2. Veja todas as entregas
3. Filtros disponíveis:
   - Pendente
   - Em trânsito
   - Agendada
   - Entregue

### 6.2 Criar Pedido

1. Clique em **Novo Pedido**
2. Preencha:
   - Número do pedido
   - Destino
   - Itens
   - Peso total
3. Clique em **Criar**

### 6.3 Agendar Entrega

1. Clique em **Agendar** em um pedido
2. Selecione:
   - Data da entrega
   - Motorista
   - Veículo
3. Clique em **Confirmar**

### 6.4 Rastreamento

1. Clique em **Rastrear** em uma entrega
2. Veja o histórico completo:
   - Pedido criado
   - Em separação
   - Em trânsito
   - Entregue
3. Cada evento mostra data, hora e localização

---

## 📝 7. Módulo de Contratos

### 7.1 Visualizar Contratos

1. Acesse **Contratos**
2. Veja todos os contratos
3. Status disponíveis:
   - Ativo
   - Próximo ao vencimento
   - Encerrado
   - Suspenso

### 7.2 Gerar Novo Contrato

1. Clique em **Novo Contrato**
2. Selecione o tipo:
   - Fornecimento
   - Prestação de Serviços
   - Locação
3. Preencha os dados
4. Clique em **Gerar PDF**

### 7.3 Termo Aditivo

1. Clique em **Gerar Aditivo** em um contrato
2. Preencha as alterações
3. Clique em **Gerar**

---

## 💳 8. Módulo de Pagamentos

### 8.1 Visualizar Pagamentos

1. Acesse **Pagamentos**
2. Veja todos os pagamentos parcelados
3. Cada pagamento mostra:
   - Descrição
   - Valor total
   - Parcelas (pagas/total)
   - Próxima parcela
   - Barra de progresso

### 8.2 Criar Pagamento

1. Clique em **Novo Pagamento**
2. Preencha:
   - Descrição
   - Valor total
   - Número de parcelas
   - Data de vencimento da primeira parcela
3. Clique em **Criar**

### 8.3 Registrar Pagamento de Parcela

1. Clique em **Pagar** na próxima parcela
2. Confirme o pagamento
3. A parcela será marcada como paga

---

## 👥 9. Módulo de Fornecedores

### 9.1 Visualizar Fornecedores

1. Acesse **Fornecedores**
2. Veja todos os fornecedores em cards
3. Cada card mostra:
   - Nome
   - Email e telefone
   - Localização
   - Avaliação (estrelas)
   - Status (ativo/pendente)

### 9.2 Buscar Fornecedores

Use a barra de busca para encontrar fornecedores por:
- Nome
- Email
- Localização

### 9.3 Filtrar por Status

- **Todos**
- **Ativos**
- **Pendentes**

### 9.4 Aprovar Fornecedor Pendente

1. Clique em **Aprovar** em um fornecedor pendente
2. O fornecedor será ativado

---

## 🔔 10. Módulo de Notificações

### 10.1 Enviar Email

1. Acesse **Notificações**
2. Selecione tipo **Email**
3. Escolha um template ou escreva personalizado
4. Preencha:
   - Destinatário
   - Assunto
   - Mensagem
5. Clique em **Enviar**

### 10.2 Enviar WhatsApp

1. Selecione tipo **WhatsApp**
2. Escolha um template
3. Preencha:
   - Telefone (com código do país)
   - Mensagem
4. Clique em **Enviar**

### 10.3 Templates Disponíveis

- Nova Licitação
- Prazo Próximo
- Proposta Enviada
- Pagamento Recebido

### 10.4 Histórico

Veja todas as notificações enviadas com:
- Data e hora
- Destinatário
- Status (enviado/pendente/falha)

---

## 📊 11. Módulo de Relatórios

### 11.1 Tipos de Relatórios

1. **Licitações**: Resumo de todas as licitações
2. **Financeiro**: Receitas, despesas e saldo
3. **Logística**: Entregas e rastreamento
4. **Fornecedores**: Avaliação e contratos
5. **Executivo**: Visão geral de todos os módulos

### 11.2 Gerar Relatório

1. Acesse **Relatórios**
2. Selecione o tipo de relatório
3. Escolha o período:
   - Última semana
   - Último mês
   - Último trimestre
   - Último ano
4. Clique em **Gerar**

### 11.3 Exportar

- **PDF**: Clique em **Exportar PDF**
- **Excel**: Clique em **Exportar Excel**

### 11.4 Histórico

Veja todos os relatórios gerados anteriormente.

---

## 👑 12. Painel de Administração (Apenas Admins)

### 12.1 Acessar

1. Clique no botão **Admin** no header (visível apenas para admins)
2. Ou acesse diretamente: /admin

### 12.2 Criar Usuário

1. Clique em **Novo Usuário**
2. Preencha:
   - Username
   - Email
   - Nome completo
   - Senha
   - Nível de acesso (Admin/Operador/Visualizador)
3. Clique em **Criar Usuário**

### 12.3 Gerenciar Usuários

- **Buscar**: Use a barra de busca
- **Ver detalhes**: Clique no usuário
- **Desativar**: Clique em ⋮ > Desativar

### 12.4 Logs de Acesso

Visualize todas as atividades:
- Logins bem-sucedidos
- Tentativas de login falhadas
- Criação de usuários
- Alterações de senha
- Logout

Cada log mostra:
- Usuário
- Ação
- Data e hora
- Endereço IP

---

## ⚙️ 13. Configurações

### 13.1 Alterar Senha

1. Clique em **Configurações** > **Alterar Senha**
2. Digite senha atual
3. Digite nova senha
4. Confirme nova senha
5. Clique em **Salvar**

### 13.2 Preferências

Configure:
- Idioma
- Tema (claro/escuro)
- Notificações
- Formato de data

---

## 🆘 14. Suporte

### 14.1 Problemas Comuns

**Não consigo fazer login**
- Verifique username e senha
- Verifique se usuário está ativo
- Contate o administrador

**Página não carrega**
- Verifique conexão com internet
- Limpe cache do navegador
- Tente outro navegador

**Erro ao enviar notificação**
- Verifique configurações de email/WhatsApp
- Contate o administrador

### 14.2 Contato

- **Email**: suporte@hospshop.com
- **Telefone**: (11) 9999-9999
- **Horário**: Segunda a Sexta, 9h às 18h

---

## 📱 15. Dicas e Atalhos

### 15.1 Atalhos de Teclado

- `Ctrl + K`: Busca rápida
- `Ctrl + /`: Ajuda
- `Esc`: Fechar modal

### 15.2 Dicas de Uso

1. **Use filtros** para encontrar informações rapidamente
2. **Favorite** licitações importantes
3. **Configure notificações** para não perder prazos
4. **Gere relatórios** regularmente para análise
5. **Mantenha dados atualizados** para melhor precisão

---

## ✅ 16. Checklist de Uso Diário

- [ ] Verificar Dashboard para KPIs atualizados
- [ ] Capturar novas licitações do Effecti
- [ ] Revisar licitações em análise
- [ ] Verificar cotações pendentes
- [ ] Conferir entregas do dia
- [ ] Verificar parcelas vencendo
- [ ] Revisar notificações enviadas
- [ ] Gerar relatório semanal (sexta-feira)

---

**Sistema Hospshop - Versão 1.0.0**  
**Desenvolvido em 01/12/2025**  
**© 2024 - Todos os direitos reservados**
