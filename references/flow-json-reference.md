# WhatsApp Flows – Referência Completa do JSON (Frontend)

> Fontes:
> - https://developers.facebook.com/docs/whatsapp/flows/reference/flowjson
> - https://developers.facebook.com/docs/whatsapp/flows/reference/components
> - https://developers.facebook.com/docs/whatsapp/flows/reference/media_upload
>
> Revisão adversarial aplicada — v4 (validator-corrected).

---

## 1. Estrutura Top-Level do Flow JSON

```json
{
  "version": "7.3",
  "data_api_version": "3.0",
  "routing_model": {
    "SCREEN_A": ["SCREEN_B"]
  },
  "screens": [...]
}
```

| Propriedade | Obrigatório | Tipo | Descrição |
|---|---|---|---|
| `version` | ✅ | string | Versão do Flow JSON |
| `screens` | ✅ | array | Telas do fluxo |
| `routing_model` | Condicional | object | **Com endpoint**: obrigatório, cobre todas as rotas. **Sem endpoint**: omita — é auto-gerado. ⚠️ Se `data_api_version` estiver presente, `routing_model` é exigido. |
| `data_api_version` | Condicional | string | `"3.0"` — **apenas** quando há Data Endpoint. Sem endpoint, **omita este campo** |
| `data_channel_uri` | Não | string | URL do endpoint — **não suportado em v3.0+** (use `endpoint_uri` via Flows API) |

**Limite:** Tamanho máximo do Flow JSON: **10 MB**

---

## 2. Screens (Telas)

```json
{
  "id": "SCREEN_ONE",
  "title": "Título da Tela",
  "terminal": false,
  "success": true,
  "refresh_on_back": false,
  "sensitive": ["ssn", "credit_card"],
  "data": {
    "field1": {
      "type": "string",
      "__example__": "Exemplo"
    }
  },
  "layout": {
    "type": "SingleColumnLayout",
    "children": [...]
  }
}
```

| Propriedade | Obrigatório | Tipo | Descrição |
|---|---|---|---|
| `id` | ✅ | string | Identificador único. `"SUCCESS"` é reservado. **Somente letras e underscores — sem dígitos, sem hífens.** Ex.: `SCREEN_ONE` ✓, `SCREEN_1` ✗ |
| `layout` | ✅ | object | Composição da UI |
| `title` | ⚠️ **Efetivamente obrigatório** | string | Texto da barra de navegação superior — a spec diz "opcional", mas o validator **rejeita** telas sem `title` |
| `terminal` | Não | boolean | Marca fim do fluxo; requer Footer. Padrão: `false` |
| `success` | Não | boolean | Apenas em telas terminais. Padrão: `true` |
| `data` | Não | object | JSON Schema dos dados dinâmicos da tela |
| `refresh_on_back` | Não | boolean | `false`: carrega dados salvos anteriormente; `true`: dispara requisição ao endpoint com `action: "BACK"`. Padrão: `false`. Só funciona com endpoint. |
| `sensitive` | Não | array\<string\> | Nomes de campos a mascarar na conclusão — v5.1+ |

---

## 3. Campo `data` (JSON Schema)

```json
"data": {
  "campo_texto": {
    "type": "string",
    "__example__": "valor de exemplo"
  },
  "flag": {
    "type": "boolean",
    "__example__": true
  },
  "lista_simples": {
    "type": "array",
    "items": { "type": "string" },
    "__example__": ["a", "b"]
  },
  "lista_objetos": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id":          { "type": "string" },
        "title":       { "type": "string" },
        "description": { "type": "string" },
        "metadata":    { "type": "string" },
        "enabled":     { "type": "boolean" }
      }
    },
    "__example__": [
      { "id": "1", "title": "Item A", "description": "Desc", "metadata": "meta", "enabled": true }
    ]
  }
}
```

**Tipos suportados:** `string`, `number`, `boolean`, `object`, `array`

> ⚠️ `null` **não é suportado**. Use valores vazios: `""`, `0`, `false`, ou omita a propriedade.
>
> ℹ️ **`__example__`** pode ser string vazia `""` — é aceito pelo validator. Preferir valores reais para facilitar testes, mas `""` é válido quando o dado será sempre fornecido pelo servidor.
>
> ⚠️ **Ao usar `data-source` dinâmico** (ex.: `"data-source": "${data.paises}"`), o schema do array **deve declarar explicitamente as `properties` dos objetos**, incluindo `id`. Usar apenas `"items": { "type": "object" }` (sem `properties`) causa erro de validação — o validator precisa enxergar o campo `id` no schema.

---

## 4. Layout

Único tipo disponível: **SingleColumnLayout** (container flexbox vertical).

```json
{
  "type": "SingleColumnLayout",
  "children": [...]
}
```

**Limite:** Máximo de **50 componentes por tela**.

---

## 5. Referências Dinâmicas

### Sintaxe básica

```
${data.campo}        → dados da tela atual (vindos do servidor ou navigate)
${form.campo}        → valores do formulário da tela atual
```

### Referência global entre telas (v4.0+)

```
${screen.<nome_tela>.(form|data).<campo>}
```

Exemplo:
```json
{ "text": "${screen.SCREEN_ONE.data.field1}" }
```

### Expressões aninhadas com backtick (v6.0+)

Envolver a expressão em backticks habilita lógica condicional e operações.

> ⚠️ **Sintaxe de backtick — regra crítica:** Ao misturar texto estático com referências dinâmicas dentro de backtick, o texto estático **deve estar em single quotes**. Texto literal sem aspas dentro de backtick causa **parse error**.
>
> ```json
> // PADRÃO 1 — referência simples, sem backtick
> { "text": "${data.email}" }
>
> // PADRÃO 2 — tudo dentro do backtick, texto estático em single quotes
> { "label": "`'Já consultou na ' ${data.processadora}'?'`" }
> { "text": "`'Total: R$ ' ${data.valor}`" }
>
> // INVÁLIDO — texto sem single quotes dentro de backtick
> { "text": "`E-mail: ${data.email}`" }   // ':' sem quotes → parse error
> { "text": "`Olá ${form.nome}`" }          // texto sem quotes → parse error
> ```

**Operadores disponíveis:**

| Operador | Tipos | Retorno | Exemplo |
|---|---|---|---|
| `==`, `!=` | string / number / boolean (mesmo tipo) | boolean | `` `${form.x} != ${form.y}` `` |
| `<`, `<=`, `>`, `>=` | number | boolean | `` `${form.age} >= 18` `` |
| `&&`, `\|\|` | boolean | boolean | `` `${form.a} && ${form.b}` `` |
| `!` | boolean | boolean | `` `!${form.aceito}` `` |
| `+`, `-`, `/`, `%` | number | number | `` `${data.total} - ${form.desconto}` `` |
| Concatenação (espaço) | string / number / boolean | string | `` `'Olá ' ${form.nome}` `` |

> ⚠️ **Divisão por zero retorna `0`** (não NaN).

> ⚠️ **Escape de backtick literal** dentro de expressão: usar `\\\\` (quatro barras no JSON).
> Exemplo: `"`'Ana\\\\'s house'`"`

---

## 6. Sensitive Field Masking (v5.1+)

```json
{ "sensitive": ["ssn", "credit_card", "password"] }
```

| Componente | Comportamento |
|---|---|
| TextInput, TextArea, DatePicker, Dropdown, CheckboxGroup, RadioButtonsGroup | Mascarado como `••••` |
| Password, OTP (passcode) | Completamente oculto |
| DocumentPicker, PhotoPicker | Completamente oculto |
| OptIn | Exibido normalmente |

---

## 7. Routing Model

```json
{
  "routing_model": {
    "ITEM_CATALOG": ["ITEM_DETAILS", "CHECKOUT"],
    "ITEM_DETAILS": ["ITEM_CATALOG", "CHECKOUT"],
    "CHECKOUT": []
  }
}
```

**Regras:**
1. **Sem Data Endpoint: omita `routing_model` E `data_api_version` por completo.** O routing_model é auto-gerado. Se `data_api_version` estiver presente, o validator **exige** `routing_model`.
2. **Com Data Endpoint: inclua ambos** (`data_api_version: "3.0"` e `routing_model`). O routing_model deve cobrir **TODAS as rotas de navigate** — rotas faltando causam erro de validação.
3. Não pode rotear para a tela atual (exceto refresh/validação).
4. Navegação bidirecional implícita: A→B permite voltar B→A.
5. Apenas rotas forward são declaradas (sem arestas reversas).
6. Telas terminais têm arrays vazios.
7. Tela de entrada não tem arestas de entrada.
8. Todas as rotas terminam em tela terminal.
9. **Máximo de 10 branches por screen.**

---

## 8. Actions (Ações)

### `navigate`

Navega para a próxima tela; payload fica disponível como `${data.*}` na tela destino.

```json
{
  "on-click-action": {
    "name": "navigate",
    "next": { "type": "screen", "name": "NEXT_SCREEN" },
    "payload": {
      "name": "${form.first_name}",
      "lang": "${form.language}"
    }
  }
}
```

> ⚠️ **`next` deve ser sempre um objeto** — nunca uma string direta. O campo `name` pode ser estático ou dinâmico:
> ```json
> // Estático
> "next": { "type": "screen", "name": "CONFIRMACAO" }
> // Dinâmico (tela destino determinada pelo servidor)
> "next": { "type": "screen", "name": "${data.proximaTela}" }
> ```
>
> ⚠️ **Não usar `navigate` no Footer de tela terminal.**
>
> ⚠️ **Tela destino deve declarar o payload em `data`:** cada campo enviado no `payload` do navigate precisa ser declarado no `data` da tela destino, com `__example__` de valor real (não `""`):
>
> ```json
> // Tela origem — navigate com payload
> "payload": { "nome": "${form.nome}", "email": "${form.email}" }
>
> // Tela destino — data deve espelhar o payload (com exemplos reais)
> "data": {
>   "nome":  { "type": "string", "__example__": "João Silva" },
>   "email": { "type": "string", "__example__": "joao@example.com" }
> }
> ```

---

### `data_exchange`

Envia dados ao Data Endpoint (somente flows com endpoint configurado).

```json
{
  "on-click-action": {
    "name": "data_exchange",
    "payload": {
      "discount_code": "${data.discount_code}",
      "items": "${form.selected_items}"
    }
  }
}
```

---

### `complete`

Encerra o fluxo e submete resposta via webhook. **Usar apenas em telas terminais.**

```json
{
  "on-click-action": {
    "name": "complete",
    "payload": {
      "discount_code": "${data.discount_code}",
      "items": "${form.selected_items}"
    }
  }
}
```

> ⚠️ **Recomendação:** incluir apenas dados inseridos pelo usuário. Evitar imagens em base64 no payload.

---

### `update_data` (v6.0+)

Atualiza o estado da tela atual sem navegar. Suporta referências globais.

```json
{
  "on-click-action": {
    "name": "update_data",
    "payload": {
      "available_states": "${data.countries[${form.country_index}].states}"
    }
  }
}
```

---

### `open_url` (v6.0+)

Abre URL externa no navegador. **Disponível apenas em `EmbeddedLink` e `OptIn`.** Não aceita payload.

```json
{
  "on-click-action": {
    "name": "open_url",
    "url": "https://example.com/terms"
  }
}
```

---

## 9. Forms (Formulários)

A partir da v4.0, o componente Form é **opcional**.

> ⚠️ **Máximo de 1 Form por tela.** O validator rejeita telas com múltiplos componentes `Form`. Se precisar de vários campos interativos, agrupe todos dentro de um único Form, ou coloque-os fora de Form.

> ⚠️ **Regra crítica sobre `init-value` e `error-message`:**
> - **Dentro de Form:** essas propriedades **não existem** no componente filho. Use `init-values` (plural) e `error-messages` (plural) no próprio `Form`.
> - **Fora de Form:** use `init-value` (singular) e `error-message` (singular) diretamente no componente.
> Misturar os contextos resulta em erro de validação.

### Com Form

```json
{
  "type": "Form",
  "name": "meu_form",
  "init-values": {
    "first_name": "João",
    "language": "pt",
    "interests": ["tech", "art"]
  },
  "error-messages": {
    "email": "E-mail inválido",
    "age": "Deve ter 18 anos ou mais"
  },
  "children": [...]
}
```

**Tipos de `init-values` por componente:**

| Componente | Tipo | Exemplo |
|---|---|---|
| TextInput | String | `"first_name": "João"` |
| TextArea | String | `"message": ""` |
| Dropdown | String | `"country": "br"` |
| RadioButtonsGroup | **String** (seleção única) | `"gender": "M"` |
| CheckboxGroup | **Array\<String\>** (multi-seleção) | `"langs": ["pt", "en"]` |
| DatePicker | String | `"birth": "2000-01-15"` |
| OptIn | boolean | (apenas fora de Form via `init-value`) |

### Sem Form (v4.0+)

Usar `init-value` (singular) e `error-message` (singular) diretamente no componente:

```json
{
  "type": "TextInput",
  "name": "first_name",
  "label": "Nome",
  "init-value": "${data.first_name}",
  "error-message": "${data.error_messages.first_name}"
}
```

---

## 10. Componentes – Referência Completa

### 10.1 TextHeading

```json
{
  "type": "TextHeading",
  "text": "Título principal",
  "visible": true
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `text` | ✅ | string (dinâmico) | máx. 80 chars; não pode ser vazio |
| `visible` | Não | boolean (dinâmico) | padrão: `true` |

---

### 10.2 TextSubheading

```json
{
  "type": "TextSubheading",
  "text": "Subtítulo",
  "visible": true
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `text` | ✅ | string (dinâmico) | máx. 80 chars; não pode ser vazio |
| `visible` | Não | boolean (dinâmico) | padrão: `true` |

---

### 10.3 TextBody

```json
{
  "type": "TextBody",
  "text": "Corpo do texto",
  "font-weight": "bold",
  "strikethrough": false,
  "markdown": false,
  "visible": true
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `text` | ✅ | string (dinâmico) | máx. 4096 chars; não pode ser vazio |
| `font-weight` | Não | enum | `bold`, `italic`, `bold_italic`, `normal` |
| `strikethrough` | Não | boolean (dinâmico) | — |
| `markdown` | Não | boolean | padrão: `false`; requer v5.1+ |
| `visible` | Não | boolean | padrão: `true` |

---

### 10.4 TextCaption

```json
{
  "type": "TextCaption",
  "text": "Legenda",
  "font-weight": "italic",
  "strikethrough": false,
  "markdown": false,
  "visible": true
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `text` | ✅ | string (dinâmico) | máx. 409 chars; não pode ser vazio |
| `font-weight` | Não | enum | `bold`, `italic`, `bold_italic`, `normal` |
| `strikethrough` | Não | boolean (dinâmico) | — |
| `markdown` | Não | boolean | padrão: `false`; v5.1+ |
| `visible` | Não | boolean | padrão: `true` |

---

### 10.5 RichText (v5.1+)

```json
{
  "type": "RichText",
  "text": "## Título\n\nParágrafo com **negrito** e *itálico*.",
  "visible": true
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `text` | ✅ | string \| string[] (dinâmico) | — |
| `visible` | Não | boolean | padrão: `true` |

**Markdown suportado:** h1, h2, **negrito**, *itálico*, ~~tachado~~, listas (ordenadas e não-ordenadas), links, tabelas, imagens inline base64 (PNG, JPG, JPEG, WEBP).

**Restrições:**
- Máximo **1 por tela**.
- Até v6.2: componente standalone — não pode combinar com outros.
- **v6.3+:** pode coexistir apenas com `Footer`.

---

### 10.6 TextInput

**Fora de Form** (init-value e error-message direto no componente):
```json
{
  "type": "TextInput",
  "name": "telefone",
  "label": "Telefone",
  "label-variant": "large",
  "input-type": "number",
  "required": true,
  "min-chars": 8,
  "max-chars": 15,
  "helper-text": "Somente números",
  "enabled": true,
  "visible": true,
  "init-value": "${data.telefone}",
  "error-message": "${data.error_messages.telefone}"
}
```

**Dentro de Form** (init-value e error-message ficam no Form, não no componente):
```json
{
  "type": "Form",
  "name": "meu_form",
  "init-values": { "telefone": "11999999999" },
  "error-messages": { "telefone": "Número inválido" },
  "children": [
    {
      "type": "TextInput",
      "name": "telefone",
      "label": "Telefone",
      "input-type": "number",
      "required": true
    }
  ]
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | — |
| `label` | ✅ | string (dinâmico) | máx. 20 chars |
| `label-variant` | Não | enum | `"large"` — v7.0+ |
| `input-type` | Não | enum | `text`, `number`, `password`, `passcode`, `email`, `phone` — ⚠️ `date` **não existe** (use `DatePicker`) |
| `pattern` | Não | string (regex) | v6.2+; exige `helper-text` quando presente |
| `required` | Não | boolean (dinâmico) | — |
| `min-chars` | Não | **number** ou `"${data.x}"` | ⚠️ estático = número (`5`, não `"5"`) |
| `max-chars` | Não | **number** ou `"${data.x}"` | ⚠️ estático = número (`80`, não `"80"`); padrão: 80 |
| `helper-text` | Não | string (dinâmico) | máx. 80 chars |
| `enabled` | Não | boolean (dinâmico) | — |
| `visible` | Não | boolean | padrão: `true` |
| `init-value` | Não | string | ⚠️ **PROIBIDO dentro de Form** — fora de Form apenas (v4.0+) |
| `error-message` | Não | string | ⚠️ **PROIBIDO dentro de Form** — fora de Form apenas; máx. 30 chars |

> ⚠️ `date` **não existe** em `input-type`. Use `DatePicker` para datas. `email` e `phone` são válidos.
> ⚠️ `init-value` e `error-message` no componente causam erro de validação quando o TextInput está dentro de um `Form`. Nesse caso, use `init-values` e `error-messages` no próprio Form.

---

### 10.7 TextArea

```json
{
  "type": "TextArea",
  "name": "observacoes",
  "label": "Observações",
  "label-variant": "large",
  "required": false,
  "max-length": 300,
  "helper-text": "Máx. 300 caracteres",
  "enabled": true,
  "visible": true,
  "init-value": "${data.observacoes}",
  "error-message": "${data.error_messages.observacoes}"
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | — |
| `label` | ✅ | string (dinâmico) | máx. 20 chars |
| `label-variant` | Não | enum | `"large"` — v7.0+ |
| `required` | Não | boolean (dinâmico) | — |
| `max-length` | Não | **number** ou `"${data.x}"` | ⚠️ estático = número (`300`, não `"300"`); padrão: 600 |
| `helper-text` | Não | string (dinâmico) | máx. 80 chars |
| `enabled` | Não | boolean (dinâmico) | — |
| `visible` | Não | boolean | padrão: `true` |
| `init-value` | Não | string | ⚠️ **PROIBIDO dentro de Form** — fora de Form apenas (v4.0+) |
| `error-message` | Não | string | ⚠️ **PROIBIDO dentro de Form** — fora de Form apenas; máx. 30 chars |

---

### 10.8 CheckboxGroup

```json
{
  "type": "CheckboxGroup",
  "name": "frutas",
  "label": "Escolha suas frutas",
  "description": "Selecione uma ou mais opções",
  "required": true,
  "min-selected-items": 1,
  "max-selected-items": 3,
  "enabled": true,
  "visible": true,
  "media-size": "regular",
  "data-source": [
    {
      "id": "1",
      "title": "Maçã",
      "description": "Fruta vermelha",
      "metadata": "meta",
      "enabled": true,
      "image": "<base64>",
      "alt-text": "Maçã",
      "color": "#FF0000",
      "on-select-action": { "name": "update_data", "payload": {} },
      "on-unselect-action": { "name": "update_data", "payload": {} }
    }
  ],
  "on-select-action": { "name": "data_exchange", "payload": {} },
  "on-unselect-action": { "name": "update_data", "payload": {} },
  "init-value": ["1"],
  "error-message": "${data.error_messages.frutas}"
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | — |
| `data-source` | ✅ | array (dinâmico: `${data.data_source}`) | mín. 1, máx. 20 opções |
| `label` | ✅ a partir de v4.0 | string (dinâmico) | máx. 30 chars |
| `description` | Não | string (dinâmico) | v4.0+; máx. 300 chars |
| `min-selected-items` | Não | int (dinâmico) | — |
| `max-selected-items` | Não | int (dinâmico) | — |
| `enabled` | Não | boolean (dinâmico) | — |
| `required` | Não | boolean (dinâmico) | — |
| `visible` | Não | boolean | padrão: `true` |
| `media-size` | Não | enum | `regular`, `large` — v5.0+ |
| `on-select-action` | Não | action | `data_exchange`, `update_data` — v6.0+ |
| `on-unselect-action` | Não | action | apenas `update_data` — v6.0+ |
| `init-value` | Não | **Array\<string\>** | fora de Form — v4.0+ |
| `error-message` | Não | string | fora de Form — v4.0+ |

**Limites do `data-source`:**

| Campo | Limite |
|---|---|
| `title` | 30 chars |
| `description` | 300 chars |
| `metadata` | 20 chars |
| `image` | 300KB (v5.x), **100KB (v6.0+)** |
| `color` | hex 6 dígitos (v5.0+) |

> ⚠️ **WebP não é suportado em iOS < 14.**

---

### 10.9 RadioButtonsGroup

Estrutura idêntica ao `CheckboxGroup`, com as seguintes diferenças:

- **Seleção única** (não múltipla).
- `init-value` é **`String`** (não Array) — corresponde ao `id` da opção selecionada.
- `on-unselect-action`: apenas `update_data`.
- **`helper-text` NÃO existe** em `RadioButtonsGroup` — o validator rejeita. (Existe em TextInput, TextArea, DatePicker, CalendarPicker, mas não em RadioButtonsGroup nem Dropdown.)
- **`init-value` direto no componente NÃO é permitido** quando dentro de Form — use `init-values` no Form. Fora de Form, use `init-value` no componente.

> ⚠️ Não use `Array` em `init-value` do RadioButtonsGroup. Esse é o erro mais comum ao copiar de CheckboxGroup.

---

### 10.10 Dropdown

```json
{
  "type": "Dropdown",
  "name": "pais",
  "label": "País",
  "required": true,
  "enabled": true,
  "visible": true,
  "data-source": "${data.paises}",
  "on-select-action": { "name": "update_data", "payload": {} },
  "on-unselect-action": { "name": "update_data", "payload": {} },
  "init-value": "${data.pais}",
  "error-message": "${data.error_messages.pais}"
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | — |
| `label` | ✅ | string | máx. 20 chars |
| `data-source` | ✅ | array (dinâmico) | mín. 1, máx. **200** (sem imagens) ou **100** (com imagens) |
| `required` | Não | boolean | — |
| `enabled` | Não | boolean (dinâmico) | — |
| `visible` | Não | boolean | padrão: `true` |
| `on-select-action` | Não | action | `data_exchange`, `update_data` — v6.0+ |
| `on-unselect-action` | Não | action | apenas `update_data` — v6.0+ |
| `init-value` | Não | **String** | fora de Form |
| `error-message` | Não | string | fora de Form |

**Limites do `data-source`:** Igual ao CheckboxGroup (title 30, description 300, metadata 20, image 300KB/100KB).

> ⚠️ **WebP não é suportado em iOS < 14.**
> ⚠️ **`helper-text` NÃO existe em Dropdown** — o validator rejeita. Igual ao RadioButtonsGroup.

---

### 10.11 Footer

```json
{
  "type": "Footer",
  "label": "Continuar",
  "left-caption": "Voltar",
  "right-caption": "Pular",
  "enabled": true,
  "on-click-action": {
    "name": "navigate",
    "next": { "type": "screen", "name": "NEXT_SCREEN" },
    "payload": {}
  }
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `label` | ✅ | string (dinâmico) | máx. 35 chars |
| `on-click-action` | ✅ | action | qualquer tipo |
| `left-caption` | Não | string (dinâmico) | máx. 15 chars |
| `center-caption` | Não | string (dinâmico) | máx. 15 chars |
| `right-caption` | Não | string (dinâmico) | máx. 15 chars |
| `enabled` | Não | boolean (dinâmico) | — |

**Posicionamento — padrão confirmado em produção:**
O Footer deve ser o **último filho do `Form`** (não colocado fora do Form, diretamente no layout):
```json
{
  "type": "Form",
  "name": "form",
  "children": [
    ...outros componentes...,
    { "type": "Footer", "label": "Continuar", ... }
  ]
}
```

**Restrições:**
- **Máximo 1 Footer por tela.**
- Pode definir `left` + `right` OU apenas `center` — nunca os três.
- Dentro de `If`: se Footer em `then`, é obrigatório em `else` (e vice-versa).
- Footer dentro de `If` só pode estar no primeiro nível (não aninhado).

---

### 10.12 OptIn

```json
{
  "type": "OptIn",
  "name": "aceitar_termos",
  "label": "Aceito os termos de uso",
  "required": true,
  "visible": true,
  "on-click-action": {
    "name": "open_url",
    "url": "https://example.com/terms"
  },
  "on-select-action": { "name": "update_data", "payload": {} },
  "on-unselect-action": { "name": "update_data", "payload": {} },
  "init-value": false
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | — |
| `label` | ✅ | string (dinâmico) | máx. 120 chars |
| `required` | Não | boolean (dinâmico) | — |
| `visible` | Não | boolean | padrão: `true` |
| `on-click-action` | Não | action | `data_exchange`, `navigate`, `open_url` (v6.0+) |
| `on-select-action` | Não | action | apenas `update_data` — v6.0+ |
| `on-unselect-action` | Não | action | apenas `update_data` — v6.0+ |
| `init-value` | Não | boolean | fora de Form — v4.0+ |

**Limite:** Máximo de **5 OptIn por tela.**

---

### 10.13 DatePicker

```json
{
  "type": "DatePicker",
  "name": "data_nascimento",
  "label": "Data de nascimento",
  "min-date": "1990-01-01",
  "max-date": "2010-12-31",
  "unavailable-dates": ["2000-01-01"],
  "helper-text": "Formato: AAAA-MM-DD",
  "enabled": true,
  "visible": true,
  "on-select-action": { "name": "data_exchange", "payload": {} },
  "init-value": "${data.data_nascimento}",
  "error-message": "Data inválida"
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | — |
| `label` | ✅ | string (dinâmico) | máx. 40 chars |
| `min-date` | Não | string (dinâmico) | `YYYY-MM-DD` (v5.0+); antes: milissegundos |
| `max-date` | Não | string (dinâmico) | `YYYY-MM-DD` (v5.0+); antes: milissegundos |
| `unavailable-dates` | Não | array\<string\> (dinâmico) | `YYYY-MM-DD` (v5.0+); antes: milissegundos |
| `helper-text` | Não | string (dinâmico) | máx. 80 chars |
| `enabled` | Não | boolean | padrão: `true` |
| `visible` | Não | boolean | padrão: `true` |
| `on-select-action` | Não | action | **apenas `data_exchange`** |
| `init-value` | Não | string | fora de Form — v4.0+ |
| `error-message` | Não | string | fora de Form — máx. 80 chars |

> ⚠️ **Antes da v5.0:** datas em milissegundos (timestamp); empresa e usuário devem estar no mesmo fuso horário.
> **v5.0+:** strings `YYYY-MM-DD`, independente de timezone.

---

### 10.14 CalendarPicker (v6.1+)

O comportamento das propriedades **muda completamente** entre `mode: "single"` e `mode: "range"`. Elas são praticamente dois componentes distintos.

**Modo `single`:**
```json
{
  "type": "CalendarPicker",
  "name": "data_entrega",
  "label": "Data de entrega",
  "helper-text": "Selecione uma data disponível",
  "mode": "single",
  "min-date": "2026-01-01",
  "max-date": "2026-12-31",
  "unavailable-dates": ["2026-07-04"],
  "include-days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
  "required": false,
  "enabled": true,
  "visible": true,
  "on-select-action": { "name": "data_exchange", "payload": {} },
  "init-value": "2026-05-10",
  "error-message": "Data inválida"
}
```

**Modo `range`:**
```json
{
  "type": "CalendarPicker",
  "name": "periodo",
  "title": "Período da viagem",
  "description": "Selecione as datas de check-in e check-out",
  "label": "Período",
  "helper-text": "Selecione check-in e check-out",
  "mode": "range",
  "min-date": "2026-01-01",
  "max-date": "2026-12-31",
  "unavailable-dates": ["2026-07-04"],
  "include-days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  "min-days": 2,
  "max-days": 30,
  "required": true,
  "enabled": true,
  "visible": true,
  "on-select-action": { "name": "data_exchange", "payload": {} },
  "init-value": { "start-date": "2026-03-01", "end-date": "2026-03-10" }
}
```

> ⚠️ **`error-message` NÃO EXISTE** no componente CalendarPicker (nem em single, nem em range).

| Propriedade | Modo `single` | Modo `range` |
|---|---|---|
| `name` | string ✅ | string ✅ |
| `label` | string (máx. 40 chars) | string (máx. 40 chars) — **NÃO é objeto** |
| `title` | — não existe | string (dinâmico); máx. 80 chars |
| `description` | — não existe | string (dinâmico); máx. 300 chars |
| `helper-text` | string (máx. 80 chars) | string (máx. 80 chars) — **NÃO é objeto** |
| `mode` | `"single"` (padrão) | `"range"` |
| `min-date` | string `YYYY-MM-DD` | string `YYYY-MM-DD` |
| `max-date` | string `YYYY-MM-DD` | string `YYYY-MM-DD` |
| `unavailable-dates` | array\<string\> `YYYY-MM-DD` | array\<string\> `YYYY-MM-DD` |
| `include-days` | array\<enum\> | array\<enum\> |
| `min-days` | — não existe | int |
| `max-days` | — não existe | int |
| `required` | boolean | boolean — **NÃO é objeto** |
| `enabled` | boolean | boolean |
| `visible` | boolean | boolean |
| `on-select-action` | apenas `data_exchange` | apenas `data_exchange` |
| `init-value` | string `"YYYY-MM-DD"` | `{"start-date": "YYYY-MM-DD", "end-date": "YYYY-MM-DD"}` |
| `error-message` | ❌ **não existe** | ❌ **não existe** |

**Payload recebido:**
- Modo `single`: `"YYYY-MM-DD"`
- Modo `range`: `{"start-date": "YYYY-MM-DD", "end-date": "YYYY-MM-DD"}`

> ⚠️ **Em navigate payload, não passe o objeto CalendarPicker range inteiro.** Passar `"${form.periodo}"` no payload do navigate falha na validação de schema. Passe `start-date` e `end-date` como campos separados:
>
> ```json
> // CORRETO
> "payload": {
>   "checkin":  "${form.periodo.start-date}",
>   "checkout": "${form.periodo.end-date}"
> }
>
> // Tela destino — campos como strings separadas
> "data": {
>   "checkin":  { "type": "string", "__example__": "2026-06-01" },
>   "checkout": { "type": "string", "__example__": "2026-06-05" }
> }
>
> // ERRADO — passa o objeto inteiro
> "payload": { "periodo": "${form.periodo}" }
> ```

---

### 10.15 Image

```json
{
  "type": "Image",
  "src": "<base64>",
  "width": 400,
  "height": 300,
  "scale-type": "contain",
  "aspect-ratio": 1.33,
  "alt-text": "Descrição da imagem"
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `src` | ✅ | string base64 (dinâmico) | PNG ou JPEG |
| `width` | Não | int (dinâmico) | — |
| `height` | Não | int (dinâmico) | — |
| `scale-type` | Não | enum | `cover`, `contain` (padrão) |
| `aspect-ratio` | Não | number (dinâmico) | padrão: `1` |
| `alt-text` | Não | string (dinâmico) | acessibilidade |

**Limites:**
- Máximo **3 imagens por tela**
- Tamanho recomendado: até **300KB**
- Payload total: máx. **1MB**
- Formatos: JPEG, PNG

**Scale types:**
- **`cover`:** Imagem recortada para preencher o container (full width padrão).
- **`contain`:** Mantém proporção original. ⚠️ **No Android, requer `height` explícito.**

---

### 10.16 EmbeddedLink

```json
{
  "type": "EmbeddedLink",
  "text": "Saiba mais",
  "visible": true,
  "on-click-action": {
    "name": "open_url",
    "url": "https://example.com"
  }
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `text` | ✅ | string (dinâmico) | máx. 25 chars; não pode ser vazio/branco |
| `on-click-action` | ✅ | action | `data_exchange`, `navigate`, `open_url` (v6.0+) |
| `visible` | Não | boolean | padrão: `true` |

**Limite:** Máximo **2 por tela.**

---

### 10.17 If Component (v4.0+)

```json
{
  "type": "If",
  "condition": "${data.mostrar_campo}",
  "then": [
    { "type": "TextInput", "name": "campo", "label": "Campo" }
  ],
  "else": [
    { "type": "TextBody", "text": "Campo não disponível" }
  ]
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `condition` | ✅ | string | expressão booleana; requer ao menos um valor dinâmico |
| `then` | ✅ | array | **não pode ser array vazio** |
| `else` | Não | array | **não pode ser array vazio** se declarado |

**Operadores suportados:** `()`, `==`, `!=`, `&&`, `||`, `!`, `>`, `>=`, `<`, `<=`

**Componentes permitidos dentro de If:**
TextHeading, TextSubheading, TextBody, TextCaption, CheckboxGroup, DatePicker, Dropdown, EmbeddedLink, Footer, Image, OptIn, RadioButtonsGroup, Switch, TextArea, TextInput, If (até **3 níveis** de aninhamento), ChipsSelector (v7.1+)

**Regras do Footer dentro de If:**
- Apenas no **primeiro nível** (não aninhado).
- Se Footer está em `then`, é **obrigatório** em `else` também.
- Não pode coexistir com Footer fora do If na mesma tela.

---

### 10.18 Switch Component (v4.0+)

```json
{
  "type": "Switch",
  "value": "${data.animal}",
  "cases": {
    "dog": [
      { "type": "TextBody", "text": "Você selecionou cachorro" }
    ],
    "cat": [
      { "type": "TextBody", "text": "Você selecionou gato" }
    ]
  }
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `value` | ✅ | string | expressão dinâmica |
| `cases` | ✅ | object | mapa chave → array de componentes; **mínimo 1 case**; suporta chave `"default"` |

A chave `"default"` (array vazio `[]` permitido) é o fallback quando nenhum case corresponde:
```json
"cases": {
  "tipo_a": [ { "type": "Footer", "label": "Ação A", ... } ],
  "tipo_b": [ { "type": "Footer", "label": "Ação B", ... } ],
  "default": []
}
```

**Componentes permitidos dentro de Switch:**
TextHeading, TextSubheading, TextBody, TextCaption, CheckboxGroup, DatePicker, Dropdown, EmbeddedLink, Footer, Image, OptIn, RadioButtonsGroup, TextArea, TextInput, ChipsSelector (v7.1+)

---

### 10.19 NavigationList (v6.2+)

```json
{
  "type": "NavigationList",
  "name": "lista_produtos",
  "label": "Produtos",
  "description": "Selecione um produto",
  "media-size": "regular",
  "list-items": "${data.lista_produtos}",
  "on-click-action": {
    "name": "navigate",
    "next": { "type": "screen", "name": "PRODUTO_DETAIL" },
    "payload": {}
  }
}
```

`list-items` pode ser estático ou dinâmico via `"${data.list_items}"`. Estrutura de cada item:

```json
{
  "main-content": {
    "title": "Produto A",
    "description": "Descrição curta",
    "metadata": "SKU-001"
  },
  "start": {
    "image": "<base64>",
    "alt-text": "Produto A"
  },
  "end": {
    "title": "R$ 99",
    "description": "Em estoque",
    "metadata": "qtd"
  },
  "badge": "Novo",
  "tags": ["promoção", "destaque"],
  "on-click-action": {
    "name": "navigate",
    "next": { "type": "screen", "name": "DETAIL" },
    "payload": { "id": "produto_a" }
  }
}
```

| Propriedade do componente | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | — |
| `list-items` | ✅ | array (dinâmico) | 1–20 itens |
| `label` | Não | string (dinâmico) | máx. 80 chars |
| `description` | Não | string (dinâmico) | máx. 300 chars |
| `media-size` | Não | enum | `regular` (padrão), `large` |
| `on-click-action` | Condicional | action | `data_exchange`, `navigate`; **não pode definir no componente E no item simultaneamente** |

**Limites por campo do item:**

| Campo | Limite |
|---|---|
| `main-content.title` | **obrigatório**; máx. 30 chars |
| `main-content.description` | máx. 20 chars |
| `main-content.metadata` | máx. 80 chars |
| `start.image` | **obrigatório**; base64; máx. 100KB |
| `end.title` / `.description` / `.metadata` | máx. 10 chars cada |
| `badge` | máx. 15 chars; **máx. 1 badge por lista** |
| `tags[]` | máx. 15 chars por tag; máx. 3 tags |

**Restrições:**
- Não pode ser usado em tela terminal.
- Máximo **2 por tela**.
- Não pode combinar com outros componentes na mesma tela.
- `end` incompatível com `media-size: "large"`.
- `start` é **obrigatório** em cada item.
- ⚠️ **WebP não é suportado em iOS < 14.**

---

### 10.20 ChipsSelector (v6.3+)

```json
{
  "type": "ChipsSelector",
  "name": "interesses",
  "label": "Seus interesses",
  "description": "Selecione tudo que se aplica",
  "required": false,
  "enabled": true,
  "visible": true,
  "min-selected-items": 1,
  "max-selected-items": 5,
  "data-source": "${data.interesses}",
  "on-select-action": { "name": "data_exchange", "payload": {} },
  "on-unselect-action": { "name": "update_data", "payload": {} },
  "init-value": ["tech"],
  "error-message": "Selecione ao menos 1"
}
```

Estrutura de cada item do `data-source`:
```json
{
  "id": "tech",
  "title": "Tecnologia",
  "enabled": true,
  "on-select-action": { "name": "update_data", "payload": {} },
  "on-unselect-action": { "name": "update_data", "payload": {} }
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | — |
| `data-source` | ✅ | array (dinâmico) | mín. **2**, máx. 20 opções |
| `label` | ✅ | string (dinâmico) | máx. 80 chars |
| `description` | Não | string (dinâmico) | máx. 300 chars |
| `min-selected-items` | Não | int (dinâmico) | — |
| `max-selected-items` | Não | int (dinâmico) | — |
| `enabled` | Não | boolean (dinâmico) | — |
| `required` | Não | boolean (dinâmico) | — |
| `visible` | Não | boolean | padrão: `true` |
| `on-select-action` | Não | action | `data_exchange`, `update_data` (v7.1+) |
| `on-unselect-action` | Não | action | apenas `update_data` (v7.1+) |
| `init-value` | Não | Array\<string\> | fora de Form |
| `error-message` | Não | string | fora de Form |

> ⚠️ Se `on-unselect-action` não for definido, **`on-select-action` trata ambos os eventos** (seleção e desseleção).

---

### 10.21 ImageCarousel (v7.1+)

```json
{
  "type": "ImageCarousel",
  "aspect-ratio": "16:9",
  "scale-type": "cover",
  "images": "${data.imagens}"
}
```

`images` pode ser dinâmico via `"${data.imagens}"`. Estrutura de cada item:

```json
{ "src": "<base64>", "alt-text": "Imagem 1" }
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `images` | ✅ | array (dinâmico) | mín. 1, máx. 3 |
| `images[].src` | ✅ | string base64 | — |
| `images[].alt-text` | ✅ | string | acessibilidade |
| `aspect-ratio` | Não | enum | `4:3` (padrão), `16:9` |
| `scale-type` | Não | enum | `contain` (padrão), `cover` |

**Limites:**
- Máximo **2 ImageCarousel por tela**
- Máximo **3 ImageCarousel por Flow**
- ⚠️ **WebP não é suportado em iOS < 14.**

---

## 11. Media Upload Components

### 11.1 PhotoPicker (v4.0+)

```json
{
  "type": "PhotoPicker",
  "name": "foto_perfil",
  "label": "${data.label}",
  "description": "${data.description}",
  "photo-source": "camera_gallery",
  "max-file-size-kb": 5120,
  "min-uploaded-photos": 1,
  "max-uploaded-photos": 3,
  "enabled": "${data.is_enabled}",
  "visible": "${data.is_visible}",
  "error-message": "Erro ao enviar foto"
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | único por tela |
| `label` | ✅ | string (dinâmico) | máx. 80 chars |
| `description` | Não | string (dinâmico) | máx. 300 chars |
| `photo-source` | Não | enum | `camera_gallery` (padrão), `camera`, `gallery` |
| `max-file-size-kb` | Não | int | padrão: 25600 (25 MiB); range [1, 25600] |
| `min-uploaded-photos` | Não | int | padrão: 0 (opcional); range [0, 30] |
| `max-uploaded-photos` | Não | int | padrão: 30; range [1, 30] |
| `enabled` | Não | boolean / string dinâmico | padrão: `true` |
| `visible` | Não | boolean / string dinâmico | padrão: `true` |
| `error-message` | Não | string **ou** object | string = genérico; object = `{ "<media_id>": "mensagem" }` |

**Referências dinâmicas suportadas:** `${data.label}`, `${data.description}`, `${data.is_enabled}`, `${data.is_visible}`, `${screen.<id>.data.*}`

**Restrições:**
- `min-uploaded-photos` não pode exceder `max-uploaded-photos`.
- **Não pode ser inicializado via `init-values` do Form.**
- Máximo **1 PhotoPicker por tela.**
- **Não pode coexistir com DocumentPicker** na mesma tela.
- **Não permitido** no payload de `navigate`.
- Permitido apenas no **nível superior** de payloads `data_exchange` ou `complete`.
- Valores **não acessíveis entre telas** via referência direta; usar Global Dynamic Referencing.

---

### 11.2 DocumentPicker (v4.0+)

```json
{
  "type": "DocumentPicker",
  "name": "documento",
  "label": "Documento",
  "description": "Envie seu comprovante",
  "allowed-mime-types": ["application/pdf", "image/jpeg"],
  "max-file-size-kb": 10240,
  "min-uploaded-documents": 1,
  "max-uploaded-documents": 5,
  "enabled": true,
  "visible": true,
  "error-message": { "media_id_xyz": "Arquivo corrompido" }
}
```

| Propriedade | Obrigatório | Tipo | Detalhe |
|---|---|---|---|
| `name` | ✅ | string | único por tela |
| `label` | ✅ | string (dinâmico) | máx. 80 chars |
| `description` | Não | string (dinâmico) | máx. 300 chars |
| `allowed-mime-types` | Não | array\<string\> | filtra tipos selecionáveis; padrão: todos os suportados |
| `max-file-size-kb` | Não | int | padrão: 25600; range [1, 25600] |
| `min-uploaded-documents` | Não | int | padrão: 0; range [0, 30] |
| `max-uploaded-documents` | Não | int | padrão: 30; range [1, 30] |
| `enabled` | Não | boolean / string dinâmico | padrão: `true` |
| `visible` | Não | boolean / string dinâmico | padrão: `true` |
| `error-message` | Não | string **ou** object | string = genérico; object = `{ "<media_id>": "mensagem" }` |

**MIME types suportados (lista completa):**

| Tipo | MIME type |
|---|---|
| PDF | `application/pdf` |
| Word (.doc) | `application/msword` |
| Word (.docx) | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| Excel (.xls) | `application/vnd.ms-excel` |
| Excel (.xlsx) | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| PowerPoint (.ppt) | `application/vnd.ms-powerpoint` |
| PowerPoint (.pptx) | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |
| ODP | `application/vnd.oasis.opendocument.presentation` |
| ODS | `application/vnd.oasis.opendocument.spreadsheet` |
| ODT | `application/vnd.oasis.opendocument.text` |
| ZIP | `application/zip` |
| 7z | `application/x-7z-compressed` |
| GZIP | `application/gzip` |
| JPEG | `image/jpeg` ⚠️ também ativa seleção de fotos da galeria |
| PNG | `image/png` |
| GIF | `image/gif` |
| WebP | `image/webp` |
| HEIC | `image/heic` |
| HEIF | `image/heif` |
| AVIF | `image/avif` |
| TIFF | `image/tiff` |
| MP4 | `video/mp4` |
| MPEG | `video/mpeg` |
| Texto | `text/plain` |

**Restrições (idênticas ao PhotoPicker):**
- Máximo **1 DocumentPicker por tela.**
- **Não pode coexistir com PhotoPicker** na mesma tela.
- **Não permitido** no payload de `navigate`.
- Permitido apenas no **nível superior** de payloads `data_exchange` ou `complete`.
- **Não pode ser inicializado via `init-values` do Form.**

> ⚠️ Alguns Android/iOS antigos podem não reconhecer todos os MIME types e permitir seleção alternativa.

---

### 11.3 Limites Globais de Upload

| Escopo | Arquivos | Tamanho |
|---|---|---|
| Resposta final (mensagem Cloud API) | máx. 10 | máx. 100 MiB agregado |
| Envio via `data_exchange` | máx. 30 | máx. 25.600 KB por arquivo |
| Retenção no CDN WhatsApp | — | até **20 dias** |

---

### 11.4 Payload Enviado ao Data Endpoint

```json
{
  "photo_picker": [
    {
      "media_id": "790aba14-5f4a-4dbd-aa9e-0d75401da14b",
      "cdn_url": "https://mmg.whatsapp.net/v/redacted",
      "file_name": "IMG_5237.jpg",
      "encryption_metadata": {
        "encrypted_hash": "/QvkBvpBED2q2AHPIFuhXfLpkn22zj2kO6ggzjvhHv0=",
        "iv": "5SHjLrrsfPXTSJTcbrVSkg==",
        "encryption_key": "lPa4SXcWbk3sy2so3OxjyXmpV4aE6CcIKd+4byr5hBw=",
        "hmac_key": "15l+E9Z5gcL15WH9OQ8GgK7VVCKkfbVigoSiM9djvGU=",
        "plaintext_hash": "AOF2dHXVEpm9efk9udNy3R1cUJWnpjFwQKGBEdALqXI="
      }
    }
  ]
}
```

**Campos de `encryption_metadata`:**

| Campo | Significado |
|---|---|
| `encrypted_hash` | SHA256 do `cdn_file` completo — valida integridade do arquivo criptografado |
| `iv` | Initialization vector para AES-256-CBC |
| `encryption_key` | Chave AES-256 para descriptografia |
| `hmac_key` | Chave para validação HMAC-SHA256 |
| `plaintext_hash` | SHA256 do arquivo já descriptografado — valida integridade final |

---

### 11.5 Algoritmo de Descriptografia

Estrutura do arquivo no CDN: `cdn_file = ciphertext + hmac10`
(os últimos 10 bytes são os primeiros 10 bytes do HMAC-SHA256)

**Passos:**
1. Download de `cdn_url` → `cdn_file`
2. Verificar: `SHA256(cdn_file) == encrypted_hash`
3. Extrair `ciphertext = cdn_file[:-10]` e `hmac10 = cdn_file[-10:]`
4. Calcular `HMAC-SHA256(hmac_key, iv + ciphertext)` → comparar primeiros 10 bytes com `hmac10`
5. Descriptografar com `AES-256-CBC(encryption_key, iv, ciphertext)` → remover padding PKCS7
6. Verificar: `SHA256(decrypted_media) == plaintext_hash`

---

### 11.6 Resposta via Cloud API (após submissão)

```json
{
  "nfm_reply": {
    "response_json": {
      "photo_picker": [
        {
          "file_name": "IMG_5237.jpg",
          "mime_type": "image/jpeg",
          "sha256": "PqHgadp8cJ/N6mvAYGNMxhs9Ra5hbZFcctCtCClXsMU=",
          "id": "3631120727156756"
        }
      ],
      "flow_token": "xyz",
      "name": "John"
    }
  }
}
```

Download segue o mesmo processo de mensagens de imagem/documento comuns da Cloud API.

---

### 11.7 Payload de Mídia: Válido vs. Inválido

**✅ Válido:**
```json
{
  "on-click-action": {
    "name": "data_exchange",
    "payload": { "media": "${form.photo_picker}" }
  }
}
```

**❌ Inválido — aninhado em objeto:**
```json
{
  "on-click-action": {
    "name": "data_exchange",
    "payload": { "media": { "photo": "${form.photo_picker}" } }
  }
}
```

**❌ Inválido — usando `navigate`:**
```json
{
  "on-click-action": {
    "name": "navigate",
    "payload": { "foto": "${form.photo_picker}" }
  }
}
```

**❌ Inválido — `init-values` do Form:**
```json
{
  "type": "Form",
  "init-values": { "photo_picker": "IMG_001.jpg" }
}
```

---

## 12. Versões – Histórico de Funcionalidades

| Versão | Funcionalidades Adicionadas |
|---|---|
| v2.1 | Base; `data_channel_uri` |
| v3.0+ | `data_channel_uri` migrado para `endpoint_uri` via Flows API |
| v4.0 | Form opcional; `init-value`/`error-message` singulares; referência global (`${screen.*}`); componentes `If` e `Switch` |
| v5.0 | DatePicker timezone-agnostic (`YYYY-MM-DD`); imagens em CheckboxGroup / RadioButtonsGroup / Dropdown |
| v5.1 | Campo `sensitive`; `RichText`; Markdown em TextBody e TextCaption |
| v6.0 | Expressões aninhadas (backtick); `update_data`; `open_url`; `on-select-action` e `on-unselect-action` em componentes |
| v6.1 | `CalendarPicker` |
| v6.2 | `NavigationList`; `pattern` em TextInput; `RichText` pode coexistir com Footer (corrigido: **v6.3**) |
| v6.3 | `ChipsSelector`; `RichText` compatível com Footer |
| v7.0 | `label-variant: "large"` em TextInput e TextArea |
| v7.1 | `ImageCarousel`; `ChipsSelector` dentro de If/Switch; `on-select-action` em ChipsSelector |

---

## 13. Exemplo Completo de Flow JSON

```json
{
  "version": "6.3",
  "data_api_version": "3.0",
  "routing_model": {
    "DADOS_PESSOAIS": ["CONFIRMACAO"],
    "CONFIRMACAO": []
  },
  "screens": [
    {
      "id": "DADOS_PESSOAIS",
      "title": "Seus dados",
      "data": {
        "paises": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id":    { "type": "string" },
              "title": { "type": "string" }
            }
          },
          "__example__": [{ "id": "br", "title": "Brasil" }]
        },
        "nome_inicial": { "type": "string", "__example__": "" }
      },
      "layout": {
        "type": "SingleColumnLayout",
        "children": [
          { "type": "TextHeading", "text": "Informações pessoais" },
          { "type": "TextBody", "text": "Preencha os campos abaixo" },
          {
            "type": "TextInput",
            "name": "nome",
            "label": "Nome completo",
            "input-type": "text",
            "required": true,
            "init-value": "${data.nome_inicial}"
          },
          {
            "type": "TextInput",
            "name": "email",
            "label": "E-mail",
            "input-type": "text",
            "required": true,
            "helper-text": "Ex: joao@exemplo.com"
          },
          {
            "type": "Dropdown",
            "name": "pais",
            "label": "País",
            "required": true,
            "data-source": "${data.paises}"
          },
          {
            "type": "If",
            "condition": "${form.pais} == 'br'",
            "then": [
              { "type": "TextBody", "text": "Bem-vindo, brasileiro!" }
            ],
            "else": [
              { "type": "TextBody", "text": "Welcome, international user!" }
            ]
          },
          {
            "type": "OptIn",
            "name": "aceitar_termos",
            "label": "Aceito os termos de uso",
            "required": true,
            "on-click-action": {
              "name": "open_url",
              "url": "https://example.com/terms"
            }
          },
          {
            "type": "Footer",
            "label": "Continuar",
            "on-click-action": {
              "name": "navigate",
              "next": { "type": "screen", "name": "CONFIRMACAO" },
              "payload": {
                "nome": "${form.nome}",
                "email": "${form.email}",
                "pais": "${form.pais}"
              }
            }
          }
        ]
      }
    },
    {
      "id": "CONFIRMACAO",
      "title": "Confirmação",
      "terminal": true,
      "success": true,
      "data": {
        "nome": { "type": "string", "__example__": "João Silva" },
        "email": { "type": "string", "__example__": "joao@example.com" },
        "pais": { "type": "string", "__example__": "br" }
      },
      "layout": {
        "type": "SingleColumnLayout",
        "children": [
          { "type": "TextHeading", "text": "Confirme seus dados" },
          { "type": "TextBody", "text": "`'Nome: ' ${data.nome}`" },
          { "type": "TextBody", "text": "`'E-mail: ' ${data.email}`" },
          {
            "type": "Footer",
            "label": "Confirmar",
            "on-click-action": {
              "name": "complete",
              "payload": {
                "nome": "${data.nome}",
                "email": "${data.email}",
                "pais": "${data.pais}"
              }
            }
          }
        ]
      }
    }
  ]
}
```
