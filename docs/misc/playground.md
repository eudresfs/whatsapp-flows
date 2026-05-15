# Playground

Source: https://developers.facebook.com/docs/whatsapp/flows/playground/

> **Crawl note — empty body:** The Playground documentation page is a client-rendered (JavaScript-only) shell. The static HTML returned to the WebFetch crawler contained no article content — only the site chrome (top nav, left-hand documentation sidebar, footer, language switcher, "Was this page helpful?" feedback widget, and the AI translation banner: "The content on this page has been translated from English into another language using AI").
>
> Multiple URL variants were tried, all yielded the same empty-body result or HTTP 404:
> - `https://developers.facebook.com/docs/whatsapp/flows/playground/` (original)
> - `https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/playground/` (canonical redirect target — empty body)
> - `https://developers.facebook.com/docs/whatsapp/flows/playground` (no trailing slash — empty body)
> - `https://developers.facebook.com/docs/whatsapp/cloud-api/flows/playground` — 404
> - `https://developers.facebook.com/community/whatsapp/flows/playground/` — 404
>
> The actual Playground tool itself lives at `https://business.facebook.com/wa/manage/flows/` and is **login-gated** ("Você deve se conectar para continuar." / "You must log in to continue."), so it cannot be crawled anonymously either.
>
> To capture the real article body, use a browser-based MCP (e.g. Chrome DevTools MCP) that can execute JavaScript and wait for hydration.

## Sidebar context captured from the page shell

Even though the article body was empty, the surrounding documentation navigation confirms this page lives under the WhatsApp Flows section of the Meta for Developers site. Sidebar links observed on this page:

### Getting Started
- Começar (Getting Started) — `/documentation/business-messaging/whatsapp/flows/gettingstarted/`
- Linha de crédito/cartão de crédito pré-aprovado — `/documentation/business-messaging/whatsapp/flows/gettingstarted/pre-approved-loan/`
- Cotação de seguro — `/documentation/business-messaging/whatsapp/flows/gettingstarted/health-insurance/`
- Oferta personalizada — `/documentation/business-messaging/whatsapp/flows/gettingstarted/personalised-offer/`
- Interesse na compra — `/documentation/business-messaging/whatsapp/flows/gettingstarted/purchase-intent/`

### Guides
- Como implementar ponto de extremidade para Flows — `/documentation/business-messaging/whatsapp/flows/guides/implementingyourflowendpoint/`
- Flow (Interactive Flow Messages) — `/documentation/business-messaging/whatsapp/flows/guides/interactive-flow-messages/`
- Modelos do Flows — `/documentation/business-messaging/whatsapp/flows/guides/flows-templates/`
- Como enviar um Flow — `/documentation/business-messaging/whatsapp/flows/guides/sendingaflow/`
- Recebimento da resposta do Flow — `/documentation/business-messaging/whatsapp/flows/guides/receiveflowresponse/`
- Integridade e monitoramento do Flow — `/documentation/business-messaging/whatsapp/flows/guides/healthmonitoring/`
- Boas práticas — `/documentation/business-messaging/whatsapp/flows/guides/bestpractices/`
- Teste e depuração — `/documentation/business-messaging/whatsapp/flows/guides/testingdebugging/`
- Exemplos — `/documentation/business-messaging/whatsapp/flows/guides/examples/`

### Resources / Reference
- Referência da API — `/documentation/business-messaging/whatsapp/flows/reference/`
- Componentes — `/documentation/business-messaging/whatsapp/flows/reference/components`
- Códigos de erro — `/documentation/business-messaging/whatsapp/flows/reference/error-codes`
- Flows JSON — `/documentation/business-messaging/whatsapp/flows/reference/flowjson`
- API de Flows — `/documentation/business-messaging/whatsapp/flows/reference/flowsapi`
- Criptografia do Flows — `/documentation/business-messaging/whatsapp/flows/guides/whatsapp-business-encryption`
- Ciclo de vida de um flow — `/documentation/business-messaging/whatsapp/flows/reference/lifecycle`
- Componentes de carregamento de mídia — `/documentation/business-messaging/whatsapp/flows/reference/media_upload`
- API de Métricas — `/documentation/business-messaging/whatsapp/flows/reference/metrics_api`
- Controle de versões — `/documentation/business-messaging/whatsapp/flows/reference/versioning`
- Webhooks — `/documentation/business-messaging/whatsapp/flows/reference/flowswebhooks`
- Registro de alterações — `/documentation/business-messaging/whatsapp/flows/changelog/`

### Additional Links
- Playground — `/documentation/business-messaging/whatsapp/flows/playground/` (this page)
- Ajuda (Support) — `/documentation/business-messaging/whatsapp/flows/support/`
- Documentação — `/docs`
- Visão geral — `/documentation/business-messaging/whatsapp/overview`

## Footer text captured

- "The content on this page has been translated from English into another language using AI."
- "Você achou esta página útil?" (Did you find this page helpful?) — with thumbs up / thumbs down feedback options.
