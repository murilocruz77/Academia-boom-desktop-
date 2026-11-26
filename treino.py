import json
import os
from dataclasses import dataclass, asdict

DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
ARQUIVO = "cronograma_treino.json"
NOME_ACADEMIA = "Academia Boom"


@dataclass
class Exercicio:
    nome: str
    series: int
    repeticoes: int
    carga: float = 0.0  # em kg

    def __str__(self):
        carga = f" | {self.carga:.1f} kg" if self.carga else ""
        return f"{self.nome}: {self.series}x{self.repeticoes}{carga}"


class Treino:
    def __init__(self, nome, exercicios=None):
        self.nome = nome
        self.exercicios = exercicios or []

    def adicionar(self, exercicio):
        self.exercicios.append(exercicio)

    def remover(self, indice):
        self.exercicios.pop(indice)

    def to_dict(self):
        return {"nome": self.nome, "exercicios": [asdict(e) for e in self.exercicios]}

    @classmethod
    def from_dict(cls, data):
        return cls(data["nome"], [Exercicio(**e) for e in data["exercicios"]])

    def __str__(self):
        linhas = [f"  Treino {self.nome}"]
        linhas += [f"    {i}. {e}" for i, e in enumerate(self.exercicios, 1)]
        return "\n".join(linhas)


class Cronograma:
    def __init__(self):
        self.dias = {dia: None for dia in DIAS_SEMANA}

    def definir_treino(self, dia, treino):
        self.dias[dia] = treino

    def limpar_dia(self, dia):
        self.dias[dia] = None

    def to_dict(self):
        return {dia: (t.to_dict() if t else None) for dia, t in self.dias.items()}

    @classmethod
    def from_dict(cls, data):
        cronograma = cls()
        for dia, t in data.items():
            cronograma.dias[dia] = Treino.from_dict(t) if t else None
        return cronograma

    def __str__(self):
        linhas = ["\n=== Cronograma semanal ==="]
        for dia, treino in self.dias.items():
            linhas.append(f"\n{dia}:")
            linhas.append(str(treino) if treino else "  Descanso")
        return "\n".join(linhas)


class Armazenamento:
    def __init__(self, arquivo=ARQUIVO):
        self.arquivo = arquivo

    def salvar(self, cronograma):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(cronograma.to_dict(), f, ensure_ascii=False, indent=2)

    def carregar(self):
        if not os.path.exists(self.arquivo):
            return Cronograma()
        with open(self.arquivo, "r", encoding="utf-8") as f:
            return Cronograma.from_dict(json.load(f))


class App:
    def __init__(self):
        self.armazenamento = Armazenamento()
        self.cronograma = self.armazenamento.carregar()

    def salvar(self):
        self.armazenamento.salvar(self.cronograma)

    def escolher_dia(self):
        for i, dia in enumerate(DIAS_SEMANA, 1):
            print(f"  {i}. {dia}")
        try:
            return DIAS_SEMANA[int(input("Escolha o dia: ")) - 1]
        except (ValueError, IndexError):
            print("Opção inválida.")
            return None

    def ver_cronograma(self):
        print(self.cronograma)

    def definir_treino(self):
        dia = self.escolher_dia()
        if not dia:
            return

        treino = Treino(input("Nome do treino (ex: A - Peito e Tríceps): ").strip())
        print("Adicione os exercícios (deixe o nome vazio para terminar).")

        while True:
            nome = input("\nExercício: ").strip()
            if not nome:
                break
            try:
                series = int(input("  Séries: "))
                repeticoes = int(input("  Repetições: "))
                carga = float(input("  Carga em kg (0 se não aplicável): ").replace(",", "."))
            except ValueError:
                print("  Valor inválido, exercício ignorado.")
                continue
            treino.adicionar(Exercicio(nome, series, repeticoes, carga))

        self.cronograma.definir_treino(dia, treino)
        self.salvar()
        print(f"Treino de {dia} salvo!")

    def remover_exercicio(self):
        dia = self.escolher_dia()
        treino = self.cronograma.dias.get(dia) if dia else None
        if not treino or not treino.exercicios:
            print("Não há exercícios para remover nesse dia.")
            return

        print(treino)
        try:
            indice = int(input("Número do exercício a remover: ")) - 1
            treino.remover(indice)
        except (ValueError, IndexError):
            print("Opção inválida.")
            return
        self.salvar()
        print("Exercício removido!")

    def limpar_dia(self):
        dia = self.escolher_dia()
        if dia:
            self.cronograma.limpar_dia(dia)
            self.salvar()
            print(f"{dia} agora é dia de descanso.")

    def run(self):
        acoes = {
            "1": self.ver_cronograma,
            "2": self.definir_treino,
            "3": self.remover_exercicio,
            "4": self.limpar_dia,
        }
        while True:
            print(f"\n=== {NOME_ACADEMIA} ===")
            print("1 - Ver cronograma")
            print("2 - Definir treino de um dia")
            print("3 - Remover exercício")
            print("4 - Limpar dia (descanso)")
            print("0 - Sair")
            opcao = input("Escolha: ").strip()

            if opcao == "0":
                print("Bons treinos! 💪")
                break
            acao = acoes.get(opcao)
            if acao:
                acao()
            else:
                print("Opção inválida.")


if __name__ == "__main__":
    App().run()
