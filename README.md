# Hans-On- Aula 01 

## Objetivos de Aprendizagem

Ao concluir este tutorial, você será capaz de:

1. Configurar ambiente integrado Git + DVC
2. Versionar datasets de forma eficiente
3. Configurar storage remoto (local/cloud)
4. Gerenciar múltiplas versões de dados
5. Criar pipelines reproduzíveis
6. Colaborar em equipe com versionamento de dados

##  Pré-requisitos

- Python 3.8 ou superior
- Git 2.30 ou superior
- pip 21.0 ou superior

##  Instalação Rápida

### Opção 1: Execução Automatizada (Recomendado)
```bash
# Clonar repositório
git clone 
cd dvc-mlops-tutorial

# Instalar dependências
pip install -r requirements.txt

# Executar tutorial automatizado
python setup_dvc_tutorial.py
```

### Módulos Práticos

1. **Configuração Inicial** - Setup do ambiente Git + DVC
2. **Versionamento de Dados** - Adicionar datasets ao DVC
3. **Storage Remoto** - Configurar compartilhamento de dados
4. **Versionamento Incremental** - Gerenciar múltiplas versões
5. **Recuperação de Versões** - Time travel nos dados
6. **Colaboração** - Simular trabalho em equipe
7. **Pipelines DVC** - Criar workflows automatizados
8. **Execução Inteligente** - Cache e otimização


### Modo Interativo (Passo a Passo)
```bash
python setup_dvc_tutorial.py --interactive
```

### Modo Automatizado (Sem Paradas)
```bash
python setup_dvc_tutorial.py --auto
```

### Modo Debug (Ver Todos os Comandos)
```bash
python setup_dvc_tutorial.py --debug
```

### Executar Apenas Módulo Específico
```bash
# Apenas configuração inicial
python setup_dvc_tutorial.py --module setup

# Apenas pipeline
python setup_dvc_tutorial.py --module pipeline

# Apenas colaboração
python setup_dvc_tutorial.py --module collab
```

## Documentação Completa

Acesse a [documentação detalhada](docs/tutorial_completo.md) para explicações teóricas e conceitos aprofundados.

##  Casos de Uso Reais

Este tutorial é baseado em casos reais de implementação de DVC em:

-  **VSCO** - Versionamento de milhões de imagens para visão computacional
- **Banco Inter** - Compliance regulatório em modelos de crédito
-  **NASA JPL** - Datasets de sensoriamento remoto e imagens de satélite


##  Licença

Este projeto está sob licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.



##  Referências

- [Documentação Oficial do DVC](https://dvc.org/doc)
- [MLOps Best Practices](https://ml-ops.org/)
- [Google Cloud MLOps Guide](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

