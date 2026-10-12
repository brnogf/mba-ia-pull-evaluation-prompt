"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

DICAS DE IMPLEMENTAÇÃO:

- O pull é feito pelo cliente do LangSmith:

      from langsmith import Client
      client = Client()
      prompt = client.pull_prompt(
          "leonanluppi/bug_to_user_story_v1",
          dangerously_pull_public_prompt=True,
      )

- O parâmetro `dangerously_pull_public_prompt=True` é obrigatório sempre que o
  identificador tem dono explícito ("owner/nome"). O LangSmith bloqueia esse pull
  por padrão porque um prompt do Hub é um objeto LangChain serializado, que pode
  vir de terceiros. Aqui o prompt é o do desafio, então o risco é conhecido.

- O retorno é um ChatPromptTemplate. Para extrair o conteúdo das mensagens,
  use a serialização nativa do LangChain (`prompt.messages`, e o atributo
  `.prompt.template` de cada mensagem).

- Use `save_yaml` de utils.py para gravar o resultado no arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def pull_prompts_from_langsmith() -> bool:
    """
    Conecta ao LangSmith, faz pull do prompt inicial (v1) e salva em YAML.

    Returns:
        True se o pull e gravação ocorreram com sucesso, False caso contrário.
    """
    prompt_identifier = "leonanluppi/bug_to_user_story_v1"
    output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"

    try:
        print(f"🔍 Fazendo pull do prompt: {prompt_identifier}...")
        client = Client()
        prompt = client.pull_prompt(
            prompt_identifier,
            dangerously_pull_public_prompt=True,
        )

        system_prompt = ""
        user_prompt = "{bug_report}"

        for msg in getattr(prompt, "messages", []):
            template = getattr(getattr(msg, "prompt", None), "template", "")
            msg_class = msg.__class__.__name__.lower()
            if "system" in msg_class:
                system_prompt = template
            elif "human" in msg_class or "user" in msg_class:
                user_prompt = template

        if not system_prompt and getattr(prompt, "messages", []):
            first_msg = prompt.messages[0]
            system_prompt = getattr(getattr(first_msg, "prompt", None), "template", "")

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        if save_yaml(prompt_data, str(output_path)):
            print(f"✅ Prompt salvo com sucesso em: {output_path}")
            return True

        print(f"❌ Falha ao salvar o prompt em: {output_path}")
        return False

    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt '{prompt_identifier}': {e}")
        return False


def main() -> int:
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

