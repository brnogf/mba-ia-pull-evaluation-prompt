"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        return False

    full_prompt_name = prompt_name if "/" in prompt_name else f"{username}/{prompt_name}"
    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")
    description = prompt_data.get("description", "")
    tags = list(prompt_data.get("tags", []))

    for tech in prompt_data.get("techniques_applied", []):
        slug = tech.lower().replace(" ", "-")
        if slug not in tags:
            tags.append(slug)

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt),
        ])

        client = Client()
        print(f"🚀 Fazendo push do prompt: {full_prompt_name}...")
        url = client.push_prompt(
            full_prompt_name,
            object=prompt,
            is_public=True,
            description=description,
            tags=tags,
        )
        print(f"✅ Prompt publicado com sucesso!")
        print(f"🔗 URL: {url}")
        return True

    except Exception as e:
        err_msg = str(e)
        if "nothing to commit" in err_msg.lower() or "no changes" in err_msg.lower():
            print(f"ℹ️  O prompt '{full_prompt_name}' já está atualizado no LangSmith Hub (sem alterações).")
            return True
        print(f"❌ Erro ao fazer push do prompt '{full_prompt_name}': {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    is_valid, errors = validate_prompt_structure(prompt_data)

    user_prompt = prompt_data.get("user_prompt", "").strip()
    if not user_prompt:
        errors.append("Campo obrigatório faltando ou vazio: user_prompt")
    elif "{bug_report}" not in user_prompt:
        errors.append("user_prompt deve conter a variável '{bug_report}'")

    return (len(errors) == 0, errors)


def main() -> int:
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    yaml_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    raw_data = load_yaml(str(yaml_path))
    if not raw_data:
        return 1

    prompt_key = "bug_to_user_story_v2"
    prompt_data = raw_data.get(prompt_key, raw_data)

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print(f"❌ Prompt '{prompt_key}' inválido:")
        for err in errors:
            print(f"   - {err}")
        return 1

    print(f"✓ Prompt '{prompt_key}' validado com sucesso.")
    success = push_prompt_to_langsmith(prompt_key, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

