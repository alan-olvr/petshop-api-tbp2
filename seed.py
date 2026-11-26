from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    Animal,
    AplicacaoVacina,
    Atendimento,
    AtendimentoServico,
    HistoricoTutela,
    Microchip,
    Servico,
    Tutor,
    Vacina,
    Veterinario,
)


def dias(n: int) -> date:
   
    return date.today() - timedelta(days=n)



TUTORES = [
    ("Maria Oliveira", "88999010001", "maria.oliveira@example.com", True),
    ("JoÃ£o Pereira", "88999010002", "joao.pereira@example.com", True),
    ("Ana Souza", "88999010003", "ana.souza@example.com", True),
    ("Carlos Lima", "88999010004", "carlos.lima@example.com", True),
    ("Fernanda Costa", "88999010005", "fernanda.costa@example.com", True),
    ("Paulo Alves", "88999010006", "paulo.alves@example.com", True),
    ("Beatriz Rocha", "88999010007", "beatriz.rocha@example.com", True),
    ("Ricardo Mendes", "88999010008", "ricardo.mendes@example.com", False),
]


VETERINARIOS = [
    ("Dra. Helena Martins", "CRMV-CE 1001", "ClÃ­nica Geral", True),
    ("Dr. Rafael Torres", "CRMV-CE 1002", "Cirurgia", True),
    ("Dra. Camila Duarte", "CRMV-CE 1003", "Dermatologia", True),
    ("Dr. Marcelo Freitas", "CRMV-CE 1004", "Animais Silvestres", True),
    ("Dra. Juliana Prado", "CRMV-CE 1005", "ClÃ­nica Geral", False),
]


SERVICOS = [
    ("Consulta clÃ­nica", "120.00", True),
    ("Exame de sangue", "95.00", True),
    ("Ultrassonografia", "180.00", True),
    ("Raio-X", "140.00", True),
    ("Limpeza de tÃ¡rtaro", "250.00", True),
    ("CastraÃ§Ã£o", "450.00", True),
    ("Banho e tosa higiÃªnica", "70.00", True),
    ("Consulta domiciliar", "200.00", False),
]


VACINAS = [
    ("AntirrÃ¡bica", "Zoetis", 365),
    ("V10 (MÃºltipla Canina)", "MSD SaÃºde Animal", 21),
    ("V4 (QuÃ¡drupla Felina)", "MSD SaÃºde Animal", 21),
    ("GiÃ¡rdia", "Zoetis", 21),  # fica no catÃ¡logo sem nenhuma aplicaÃ§Ã£o
]


ANIMAIS = [
    ("Thor", "Cachorro", "Labrador", "M", date(2020, 3, 10), 32.5, 0, True),
    ("Mia", "Gato", "SiamÃªs", "F", date(2021, 7, 1), 4.2, 0, True),
    ("Bob", "Cachorro", "Poodle", "M", date(2019, 11, 20), 7.8, 1, True),
    ("Luna", "Gato", "Persa", "F", date(2022, 2, 14), 3.9, 1, True),
    ("Nina", "Cachorro", "Vira-lata", "F", date(2018, 5, 5), 14.0, 2, True),
    ("Simba", "Gato", "Maine Coon", "M", date(2023, 1, 15), 5.1, 2, True),
    ("Rex", "Cachorro", "Pastor AlemÃ£o", "M", date(2017, 9, 9), 38.0, 3, True),
    ("Mel", "Cachorro", "Golden Retriever", "F", date(2021, 12, 1), 27.3, 3, True),
    ("Pipoca", "Coelho", "Mini Lop", "F", date(2023, 6, 10), 1.6, 4, True),
    ("Tobby", "Cachorro", "Beagle", "M", date(2022, 8, 18), 11.2, 4, True),
    ("Cleo", "Gato", "SRD", "F", date(2020, 10, 30), 4.5, 5, True),
    ("Zeca", "Cachorro", "Shih Tzu", "M", date(2019, 4, 22), 6.9, 5, True),
    ("Amora", "Gato", "Bengal", "F", date(2024, 3, 3), 3.2, 6, True),
    ("Fred", "Cachorro", "Bulldog FrancÃªs", "M", date(2021, 5, 25), 12.4, 6, False),
]


MICROCHIPS = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10]


TRANSFERENCIAS = [
    (2, 4, 45, "transferencia"),  
    (6, 2, 90, "adocao"),        
    (10, 6, 30, "adocao"),       
]



APLICACOES = [
    (0, 0, 1, "aplicada", 200, 0), (0, 0, 2, "prevista", 165, None),
    (0, 1, 1, "aplicada", 150, 0), (0, 1, 2, "aplicada", 120, 0),
    (1, 2, 1, "aplicada", 40, 0),  (1, 2, 2, "aplicada", 15, 0),
    (1, 0, 1, "aplicada", 40, 0),  (1, 0, 2, "prevista", 325, None),
    (2, 1, 1, "aplicada", 60, 1),  (2, 1, 2, "aplicada", 38, 1),
    (3, 2, 1, "aplicada", 25, 0),  (3, 2, 2, "prevista", -4, None),
    (4, 0, 1, "aplicada", 100, 2), (4, 0, 2, "prevista", 265, None),
    (4, 1, 1, "aplicada", 10, 2),  (4, 1, 2, "prevista", 11, None),
    (5, 2, 1, "aplicada", 5, 0),   (5, 2, 2, "prevista", 16, None),
    (6, 0, 1, "aplicada", 300, 1), (6, 0, 2, "prevista", 65, None),
    (7, 1, 1, "aplicada", 90, 0),  (7, 1, 2, "aplicada", 65, 0),
    (9, 0, 1, "prevista", 7, None),
]


ATENDIMENTOS = [
    (2, 0, 70, "Coceira intensa e vermelhidÃ£o", "Evitar banhos por 5 dias", [0]),
    (2, 2, 20, "Retorno de dermatite", "Manter medicaÃ§Ã£o por 7 dias", [0, 1]),
    (6, 1, 120, "ClaudicaÃ§Ã£o na pata traseira", "Repouso por 10 dias", [0, 3]),
    (6, 0, 30, "Check-up geral", "Dieta para controle de peso", [0, 1]),
    (10, 0, 50, "VÃ´mitos recorrentes", "AlimentaÃ§Ã£o leve e hidrataÃ§Ã£o", [0, 1, 2]),
    (10, 0, 10, "Retorno gastrointestinal", "Retomar a raÃ§Ã£o gradualmente", [0]),
    (0, 0, 14, "Consulta de rotina", "Manter a vacinaÃ§Ã£o em dia", [0]),
    (1, 0, 8, "Perda de apetite", "Observar por 48 horas", [0, 1]),
    (3, 2, 3, "Queda de pelos", "SuplementaÃ§Ã£o indicada", [0, 1]),
    (4, 1, 45, "TÃ¡rtaro e mau hÃ¡lito", "EscovaÃ§Ã£o dental diÃ¡ria", [0, 4]),
    (5, 0, 12, "Consulta de filhote", "VermifugaÃ§Ã£o em 15 dias", [0]),
    (7, 1, 33, "CastraÃ§Ã£o eletiva", "Repouso e colar elisabetano", [0, 5]),
    (8, 3, 18, "AvaliaÃ§Ã£o de coelho", "Feno Ã  vontade", [0]),
    (9, 0, 6, "Otite", "Limpeza do ouvido diÃ¡ria", [0]),
    (11, 2, 27, "Alergia de pele", "Shampoo medicado", [0, 6]),
    (13, 4, 80, "Dificuldade respiratÃ³ria", "Evitar calor e exercÃ­cio", [0, 3]),
    (12, 0, 2, "Primeira consulta", "Agendar vacinaÃ§Ã£o", [0]),
]


def tutor_da_epoca(vinculos: list[HistoricoTutela], quando: date) -> int:
    """Tutor que tinha a tutela do animal na data informada."""
    for v in vinculos:
        if v.data_inicio <= quando and (v.data_fim is None or quando < v.data_fim):
            return v.tutor.id
    return vinculos[-1].tutor.id


def popular(db: Session) -> None:
    tutores = [
        Tutor(nome=n, telefone=t, email=e, ativo=a) for n, t, e, a in TUTORES
    ]
    veterinarios = [
        Veterinario(nome=n, crmv=c, especialidade=esp, ativo=a)
        for n, c, esp, a in VETERINARIOS
    ]
    servicos = [
        Servico(nome=n, valor_padrao=Decimal(v), ativo=a) for n, v, a in SERVICOS
    ]
    vacinas = [
        Vacina(nome=n, fabricante=f, dias_reforco=d, ativo=True) for n, f, d in VACINAS
    ]
    db.add_all(tutores + veterinarios + servicos + vacinas)
    db.flush()

    animais = [
        Animal(
            nome=nome, especie=especie, raca=raca, sexo=sexo,
            data_nasc_aprox=nasc, peso_kg=peso, ativo=ativo, tutor=tutores[ti],
        )
        for nome, especie, raca, sexo, nasc, peso, ti, ativo in ANIMAIS
    ]
    db.add_all(animais)
    db.flush()

    # Primeiro vÃ­nculo de tutela de cada animal
    vinculos: dict[int, list[HistoricoTutela]] = {}
    for i, animal in enumerate(animais):
        v = HistoricoTutela(
            animal=animal, tutor=animal.tutor, data_inicio=dias(400), motivo="adocao"
        )
        vinculos[i] = [v]
        db.add(v)
    db.flush()

    # TransferÃªncias: fecha o vÃ­nculo vigente e abre o novo
    for i, novo_tutor_i, atras, motivo in TRANSFERENCIAS:
        data_transf = dias(atras)
        vinculos[i][-1].data_fim = data_transf
        novo = HistoricoTutela(
            animal=animais[i], tutor=tutores[novo_tutor_i],
            data_inicio=data_transf, motivo=motivo,
        )
        vinculos[i].append(novo)
        animais[i].tutor = tutores[novo_tutor_i]
        db.add(novo)
        db.flush()

    for n, i in enumerate(MICROCHIPS, start=1):
        db.add(Microchip(
            numero=f"98511200000{n:04d}",  # 15 dÃ­gitos
            data_implantacao=dias(200 + n * 5),
            animal=animais[i],
        ))

    for animal_i, vacina_i, dose, status, d, vet_i in APLICACOES:
        if status == "aplicada":
            data_aplicacao, data_prevista = dias(d), dias(d)
        else:
            data_aplicacao, data_prevista = None, dias(-d)
        db.add(AplicacaoVacina(
            dose=dose,
            status=status,
            data_prevista=data_prevista,
            data_aplicacao=data_aplicacao,
            animal_id=animais[animal_i].id,
            vacina_id=vacinas[vacina_i].id,
            veterinario_id=None if vet_i is None else veterinarios[vet_i].id,
        ))

    for n, (animal_i, vet_i, atras, situacao, orientacoes, servicos_i) in enumerate(ATENDIMENTOS):
        data = dias(atras)
        db.add(Atendimento(
            data_hora=datetime.combine(data, time(8 + n % 9, 30)),
            situacao=situacao,
            orientacoes=orientacoes,
            animal_id=animais[animal_i].id,
            veterinario_id=veterinarios[vet_i].id,
            tutor_id_epoca=tutor_da_epoca(vinculos[animal_i], data),
            servicos=[
                AtendimentoServico(
                    servico_id=servicos[s].id,
                    quantidade=1,
                    valor_cobrado=servicos[s].valor_padrao,
                )
                for s in servicos_i
            ],
        ))


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(Tutor)):
            print("O banco jÃ¡ possui dados; nada foi inserido.")
            return
        popular(db)
        db.commit()

        print("Povoamento concluÃ­do:")
        for modelo in (
            Tutor, Veterinario, Animal, Microchip, HistoricoTutela, Servico,
            Vacina, AplicacaoVacina, Atendimento, AtendimentoServico,
        ):
            total = db.scalar(select(func.count()).select_from(modelo))
            print(f"  {modelo.__tablename__}: {total}")


if __name__ == "__main__":
    main()
