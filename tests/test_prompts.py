"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

PROMPT_V2_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def get_v2_prompt_data() -> dict:
    """Retorna o dicionário do prompt bug_to_user_story_v2."""
    assert PROMPT_V2_PATH.exists(), f"Arquivo não encontrado: {PROMPT_V2_PATH}"
    data = load_prompts(str(PROMPT_V2_PATH))
    assert isinstance(data, dict), "Conteúdo do YAML deve ser um dicionário"
    return data.get("bug_to_user_story_v2", data)


class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt_data = get_v2_prompt_data()
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' ausente no YAML"
        system_prompt = prompt_data["system_prompt"]
        assert isinstance(system_prompt, str) and len(system_prompt.strip()) > 0, (
            "Campo 'system_prompt' não pode estar vazio"
        )
        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, f"Falha na validação estrutural: {errors}"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_data = get_v2_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "").lower()
        role_keywords = [
            "você é um product manager",
            "product manager",
            "especialista em engenharia de requisitos",
            "product owner",
        ]
        assert any(kw in system_prompt for kw in role_keywords), (
            "O system_prompt deve definir claramente uma persona (Role Prompting)"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_data = get_v2_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "").lower()
        has_markdown_or_us = "markdown" in system_prompt or "user story" in system_prompt
        has_template_parts = (
            "como " in system_prompt
            and "eu quero" in system_prompt
            and "para que" in system_prompt
            and "critérios de aceitação" in system_prompt
        )
        assert has_markdown_or_us and has_template_parts, (
            "O prompt deve exigir o formato Markdown/User Story padrão (Como... eu quero... para que... + Critérios de Aceitação)"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_data = get_v2_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "").lower()
        assert "exemplo" in system_prompt, "O prompt deve conter exemplos (Few-shot)"
        assert "entrada:" in system_prompt and "saída esperada:" in system_prompt, (
            "O prompt deve conter pares explícitos de Entrada e Saída Esperada"
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_data = get_v2_prompt_data()
        full_text = yaml.dump(prompt_data, allow_unicode=True)
        assert "[TODO]" not in full_text and "TODO" not in full_text, (
            "O prompt não pode conter marcações [TODO] ou TODO pendentes"
        )

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_data = get_v2_prompt_data()
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list), "'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Esperado pelo menos 2 técnicas em 'techniques_applied', encontrado: {len(techniques)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])