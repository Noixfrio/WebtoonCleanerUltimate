# 🔒 Política de Segurança

## Versões Suportadas

Versões que recebem atualizações de segurança:

| Versão | Suportada | Status |
|--------|-----------|--------|
| 0.9.9+ | ✅ Sim | Latest |
| 0.9.8 | ✅ Sim | LTS |
| < 0.9.8 | ❌ Não | EOL |

---

## Reportar Vulnerabilidade

### ⚠️ NÃO crie uma issue pública para vulnerabilidades de segurança!

Se você descobrir uma vulnerabilidade de segurança, por favor:

1. **NÃO** divulgue publicamente
2. **NÃO** abra issue pública
3. **NÃO** discussões públicas

### ✅ Reporte Seguramente

Envie um relatório via **GitHub Security Advisory**:

1. Vá para: https://github.com/Noixfrio/WebtoonCleanerUltimate/security/advisories/new
2. Forneça detalhes da vulnerabilidade
3. Incluir PoC (Proof of Concept) se possível
4. Especificar versões afetadas

Ou envie um email para: **security@webtoon-cleaner.local** (substitua pelo email real)

---

## Informações Esperadas

Ao reportar, inclua:

- **Descrição:** O que é a vulnerabilidade?
- **Severidade:** Critical / High / Medium / Low
- **Afetadas:** Quais versões/componentes?
- **PoC:** Passos para reproduzir (se seguro)
- **Impacto:** O que um atacante poderia fazer?
- **Solução:** Você tem uma correção sugerida?

---

## Processo de Resposta

1. **Reconhecimento:** Resposta em até 48 horas
2. **Investigação:** Confirmamos a vulnerabilidade
3. **Correção:** Desenvolvemos e testamos o patch
4. **Divulgação:** Publicamos GHSA (GitHub Security Advisory)
5. **Release:** Lançamos versão corrigida
6. **Crédito:** Você é creditado (se desejar)

---

## Práticas de Segurança

### Dados de Usuário
- ✅ Processamento local (sem envio para nuvem)
- ✅ Sem telemetria invasiva
- ✅ Sem coleta de dados pessoais

### Modelos de IA
- ✅ Modelos verificados (HuggingFace)
- ✅ Checksums validados
- ✅ Armazenamento seguro local

### Dependências
- ✅ Pinned versions controladas
- ✅ Verificações de vulnerabilidades
- ✅ Updates regulares

### Código
- ✅ Code review em PRs
- ✅ Testes de segurança
- ✅ Análise estática

---

## Recomendações de Segurança para Usuários

### Instalação
```bash
# ✅ Clonar de HTTPS (verificado)
git clone https://github.com/Noixfrio/WebtoonCleanerUltimate.git

# ✅ Verificar commit assinado
git log --show-signature
```

### Execução
- ✅ Usar ambiente Python isolado (`venv`)
- ✅ Não executar como admin/root desnecessariamente
- ✅ Manter Python atualizado
- ✅ Manter dependências atualizadas: `pip install -U -r requirements.txt`

### Dados
- ✅ Fazer backup de imagens importantes
- ✅ Verificar resultados antes de sobrescrever originais
- ✅ Usar versão de controle com suas imagens

---

## Conformidade

Este projeto está comprometido em:

- ✅ Proteger a privacidade do usuário
- ✅ Manter código seguro
- ✅ Responder rapidamente a vulnerabilidades
- ✅ Praticar responsible disclosure
- ✅ Fornecer atualizações regulares

---

## Contato

- 🐛 **Bugs Públicos:** [Issues](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues)
- 🔒 **Segurança:** [GitHub Security Advisory](https://github.com/Noixfrio/WebtoonCleanerUltimate/security/advisories)
- 💬 **Discussões:** [Discussions](https://github.com/Noixfrio/WebtoonCleanerUltimate/discussions)

---

**Obrigado por ajudar a manter o projeto seguro! 🙏**
