# Integration StackSpot AI with Home Assistan

![banner_dark.png](.docs/banner_dark.png)


## 📢 DOCUMENTAÇÃO EM DESENVOLVIMENTO

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alves-dev&repository=stackspot-homeassistant&category=integration)


### O que é
Está é uma integração do Home Assistant para conectar-se à plataforma [StackSpot AI](https://ai.stackspot.com/?campaignCode=01JXZTS2JEQA9H6Z5Y7X52YGR9), 
que é uma plataforma de AI, onde você pode criar com facilidade seus agentes customizados com vários modelos distintos.

### Requisito

Você apenas deve ter uma conta na plataforma StackSpot: [criar conta freemium com 2M de tokens](https://ai.stackspot.com/?campaignCode=01JXZTS2JEQA9H6Z5Y7X52YGR9)

### Funcionalidades
No momento a integração cria um `Conversation agent` o que te permite interagir com seu agente da StackSpot por meio da 
interface do Home Assistant.

![interaction.png](.docs/interaction.png)

### Instalação
A integração está em processo para ser adicionada por padrão no HACS, mas você pode adicionar ela adicionando o repositório
diretamente ao seu HACS, basta clicar no botão a seguir:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alves-dev&repository=stackspot-homeassistant&category=integration)


### Configuração
Após adicionar e instalar a integração, configure com:

![config.png](.docs/config.png)

- `realm`: (ex: stackspot-freemium)
- `client_id` e `client_key`: são credenciais para acessar sua conta, e podem ser adquiridas [aqui](https://myaccount.stackspot.com/profile/access-token).
- `agent`: ID do agente que deseja usar, [aqui](https://www.linkedin.com/pulse/seu-agente-de-ia-do-jeito-igor-moreira-nhu6f/) pode ver como criar um.

Então tera algo como:

![integration_added.png](.docs/integration_added.png)

Agora vá até o `Assistants` e clique em `+ ADD ASSISTANT`:

[![Open your Home Assistant instance and show your voice assistants.](https://my.home-assistant.io/badges/voice_assistants.svg)](https://my.home-assistant.io/redirect/voice_assistants/)

Veja que pode definir um nome para seu assistant, e em `Conversation agent` você terá uma nova opção:

![add_asistant.png](.docs/add_asistant.png)

Após criado basta utilizar o atalho `a` que a interface de conversação será aberta:

![interaction.png](.docs/interaction.png)


### Limitações

No momento a integração ainda não é capaz de acessar suas entidades, assim como não será capaz de alterar status de suas entidades.