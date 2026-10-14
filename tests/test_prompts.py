"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


PROMPT_V2_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


@pytest.fixture(scope="module")
def prompt_v2_data() -> dict:
    """Fixture que carrega o YAML bug_to_user_story_v2 uma única vez em memória para a suíte de testes."""
    assert PROMPT_V2_PATH.exists(), f"Arquivo não encontrado: {PROMPT_V2_PATH}"
    data = load_prompts(str(PROMPT_V2_PATH))
    assert isinstance(data, dict), "Conteúdo do YAML deve ser um dicionário"
    return data.get("bug_to_user_story_v2", data)


def get_v2_prompt_data() -> dict:
    """Retorna o dicionário do prompt bug_to_user_story_v2 (mantido para compatibilidade)."""
    assert PROMPT_V2_PATH.exists(), f"Arquivo não encontrado: {PROMPT_V2_PATH}"
    data = load_prompts(str(PROMPT_V2_PATH))
    assert isinstance(data, dict), "Conteúdo do YAML deve ser um dicionário"
    return data.get("bug_to_user_story_v2", data)


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_v2_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_v2_data, "Campo 'system_prompt' ausente no YAML"
        system_prompt = prompt_v2_data["system_prompt"]
        assert isinstance(system_prompt, str) and len(system_prompt.strip()) > 0, (
            "Campo 'system_prompt' não pode estar vazio"
        )
        is_valid, errors = validate_prompt_structure(prompt_v2_data)
        assert is_valid, f"Falha na validação estrutural: {errors}"

    def test_prompt_has_role_definition(self, prompt_v2_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_v2_data.get("system_prompt", "").lower()
        role_keywords = [
            "você é um product manager",
            "product manager",
            "especialista em engenharia de requisitos",
            "product owner",
        ]
        assert any(kw in system_prompt for kw in role_keywords), (
            "O system_prompt deve definir claramente uma persona (Role Prompting)"
        )

    def test_prompt_mentions_format(self, prompt_v2_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_v2_data.get("system_prompt", "").lower()
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

    def test_prompt_has_few_shot_examples(self, prompt_v2_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_v2_data.get("system_prompt", "").lower()
        assert "exemplo" in system_prompt, "O prompt deve conter exemplos (Few-shot)"
        assert "entrada:" in system_prompt and "saída esperada:" in system_prompt, (
            "O prompt deve conter pares explícitos de Entrada e Saída Esperada"
        )

    def test_prompt_no_todos(self, prompt_v2_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        full_text = yaml.dump(prompt_v2_data, allow_unicode=True)
        assert "[TODO]" not in full_text and "TODO" not in full_text, (
            "O prompt não pode conter marcações [TODO] ou TODO pendentes"
        )

    def test_minimum_techniques(self, prompt_v2_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_v2_data.get("techniques_applied", [])
        assert isinstance(techniques, list), "'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Esperado pelo menos 2 técnicas em 'techniques_applied', encontrado: {len(techniques)}"
        )

    def test_prompt_strict_system_user_separation(self, prompt_v2_data):
        """Garante que a variável {bug_report} está presente em user_prompt e terminantemente ausente de system_prompt."""
        system_prompt = prompt_v2_data.get("system_prompt", "")
        user_prompt = prompt_v2_data.get("user_prompt", "")

        assert "user_prompt" in prompt_v2_data and isinstance(user_prompt, str) and len(user_prompt.strip()) > 0, (
            "Campo 'user_prompt' ausente ou vazio no YAML"
        )
        assert "{bug_report}" in user_prompt, (
            "A variável '{bug_report}' deve estar presente no user_prompt"
        )
        assert "{bug_report}" not in system_prompt, (
            "A variável '{bug_report}' não deve estar presente no system_prompt (elimina duplicação e risco de injeção do v1)"
        )

    def test_prompt_langchain_compilation(self, prompt_v2_data):
        """Valida que o prompt instancia ChatPromptTemplate.from_messages e formata uma mensagem de teste sem erros."""
        assert "system_prompt" in prompt_v2_data, "Campo 'system_prompt' ausente no YAML"
        assert "user_prompt" in prompt_v2_data, "Campo 'user_prompt' ausente no YAML"
        system_prompt = prompt_v2_data["system_prompt"]
        user_prompt = prompt_v2_data["user_prompt"]

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt),
        ])

        assert prompt_template.input_variables == ["bug_report"], (
            f"O template deve ter exatamente ['bug_report'] como variável de entrada, encontrado: {prompt_template.input_variables}"
        )

        test_input = "Botão de login não responde na versão mobile iOS."
        messages = prompt_template.format_messages(bug_report=test_input)

        assert len(messages) == 2, "ChatPromptTemplate deve gerar exatamente 2 mensagens (System e Human)"
        assert isinstance(messages[0], SystemMessage), "Primeira mensagem deve ser uma SystemMessage"
        assert isinstance(messages[1], HumanMessage), "Segunda mensagem deve ser uma HumanMessage"
        assert messages[0].content == system_prompt, "Conteúdo da SystemMessage deve corresponder ao system_prompt"
        assert test_input in messages[1].content, "Conteúdo da HumanMessage deve conter o bug_report interpolado"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
