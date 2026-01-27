#!/usr/bin/env python3
"""
DVC Automatizado para Machine Learning Engineering

"""

import os
import sys
import subprocess
import shutil
import time
import argparse
from pathlib import Path
from typing import Optional, List
import json

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # Fallback se colorama não estiver instalado
    class Fore:
        GREEN = RED = YELLOW = CYAN = MAGENTA = BLUE = WHITE = ""
    class Style:
        RESET_ALL = BRIGHT = ""

# =============================================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================================

PROJECT_NAME = "projeto-ibovespa"
REMOTE_STORAGE_PATH = "/tmp/dvc-storage"
TEMP_COLLAB_PATH = "/tmp/projeto-colaborador"

# =============================================================================
# CLASSES AUXILIARES
# =============================================================================

class Logger:
    """Logger colorido """
    
    @staticmethod
    def info(msg: str):
        print(f"{Fore.CYAN}ℹ  {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def success(msg: str):
        print(f"{Fore.GREEN} {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def warning(msg: str):
        print(f"{Fore.YELLOW}  {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def error(msg: str):
        print(f"{Fore.RED} {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def section(msg: str):
        print(f"\n{Fore.MAGENTA}{'='*70}")
        print(f"  {msg}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
    
    @staticmethod
    def step(num: int, msg: str):
        print(f"{Fore.BLUE} Passo {num}: {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def command(cmd: str):
        print(f"{Fore.WHITE}   $ {cmd}{Style.RESET_ALL}")


class CommandRunner:
    """Executor de comandos com logging"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def run(self, cmd: str, cwd: Optional[str] = None, 
            show_output: bool = True) -> subprocess.CompletedProcess:
        """
        Executa comando shell e retorna resultado
        
        Args:
            cmd: Comando a executar
            cwd: Diretório de trabalho
            show_output: Se deve mostrar output do comando
        """
        if self.debug:
            Logger.command(cmd)
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if show_output and result.stdout:
                print(f"{Fore.WHITE}{result.stdout}{Style.RESET_ALL}")
            
            return result
            
        except subprocess.CalledProcessError as e:
            Logger.error(f"Comando falhou: {cmd}")
            if e.stderr:
                print(f"{Fore.RED}{e.stderr}{Style.RESET_ALL}")
            raise


class DVCTutorial:
    """Classe principal do tutorial DVC"""
    
    def __init__(self, interactive: bool = True, debug: bool = False):
        self.interactive = interactive
        self.debug = debug
        self.runner = CommandRunner(debug=debug)
        self.project_path = Path.cwd() / PROJECT_NAME
        
    def pause(self, msg: str = "Pressione ENTER para continuar..."):
        """Pausa execução em modo interativo"""
        if self.interactive:
            input(f"\n{Fore.YELLOW}{msg}{Style.RESET_ALL}\n")
    
    def check_prerequisites(self):
        """Verifica pré-requisitos do sistema"""
        Logger.section("VERIFICANDO PRÉ-REQUISITOS")
        
        requirements = {
            "python3": "python3 --version",
            "git": "git --version",
            "pip": "pip --version"
        }
        
        all_ok = True
        
        for name, cmd in requirements.items():
            try:
                result = self.runner.run(cmd, show_output=False)
                version = result.stdout.strip()
                Logger.success(f"{name}: {version}")
            except Exception:
                Logger.error(f"{name} não encontrado!")
                all_ok = False
        
        if not all_ok:
            Logger.error("Instale os pré-requisitos antes de continuar")
            sys.exit(1)
        
        # Verificar/instalar DVC
        try:
            result = self.runner.run("dvc version", show_output=False)
            Logger.success(f"DVC: {result.stdout.strip()}")
        except Exception:
            Logger.warning("DVC não encontrado. Instalando...")
            self.runner.run("pip install dvc pandas")
            Logger.success("DVC instalado com sucesso!")
        
        self.pause()
    
    def module_1_setup(self):
        """Módulo 1: Configuração Inicial"""
        Logger.section("MÓDULO 1: CONFIGURAÇÃO INICIAL DO AMBIENTE")
        
        # Limpar projeto anterior se existir
        if self.project_path.exists():
            Logger.warning(f"Removendo projeto anterior em {self.project_path}")
            shutil.rmtree(self.project_path)
        
        Logger.step(1, "Criando diretório do projeto")
        self.project_path.mkdir(parents=True)
        Logger.success(f"Projeto criado em: {self.project_path}")
        
        Logger.step(2, "Inicializando Git")
        self.runner.run("git init", cwd=self.project_path)
        self.runner.run('git config user.name "DVC Tutorial"', cwd=self.project_path)
        self.runner.run('git config user.email "tutorial@dvc.org"', cwd=self.project_path)
        Logger.success("Git inicializado")
        
        Logger.step(3, "Inicializando DVC")
        self.runner.run("dvc init", cwd=self.project_path)
        Logger.success("DVC inicializado")
        
        Logger.step(4, "Commitando configuração inicial")
        self.runner.run("git add .dvc .dvcignore", cwd=self.project_path)
        self.runner.run('git commit -m "Initialize DVC"', cwd=self.project_path)
        Logger.success("Configuração inicial commitada")
        
        # Mostrar estrutura criada
        Logger.info("Estrutura do projeto:")
        self.runner.run("tree -a -L 2 2>/dev/null || ls -laR", cwd=self.project_path)
        
        self.pause()
    
    def module_2_versioning(self):
        """Módulo 2: Versionamento de Dataset"""
        Logger.section("MÓDULO 2: VERSIONAMENTO DE DATASET")
        
        Logger.step(1, "Criando estrutura de diretórios")
        data_dirs = ["data/raw", "data/processed", "data/features", "models", "metrics"]
        for dir_path in data_dirs:
            (self.project_path / dir_path).mkdir(parents=True, exist_ok=True)
        Logger.success("Diretórios criados")
        
        Logger.step(2, "Criando dataset IBOVESPA de exemplo")
        dataset_content = """data,abertura,maxima,minima,fechamento,volume
2024-01-02,118000,119500,117800,118900,15000000
2024-01-03,118900,120200,118500,119800,16200000
2024-01-04,119800,120500,119200,120100,14800000
2024-01-05,120100,121000,119900,120600,15500000
2024-01-08,120600,121500,120300,121200,16000000"""
        
        dataset_file = self.project_path / "data/raw/ibovespa_v1.csv"
        dataset_file.write_text(dataset_content)
        Logger.success(f"Dataset criado: {dataset_file.name} ({len(dataset_content)} bytes)")
        
        Logger.step(3, "Adicionando dataset ao DVC")
        self.runner.run("dvc add data/raw/ibovespa_v1.csv", cwd=self.project_path)
        Logger.success("Dataset adicionado ao DVC")
        
        Logger.step(4, "Examinando arquivo .dvc gerado")
        dvc_file = self.project_path / "data/raw/ibovespa_v1.csv.dvc"
        if dvc_file.exists():
            Logger.info("Conteúdo do arquivo .dvc:")
            print(f"{Fore.WHITE}{dvc_file.read_text()}{Style.RESET_ALL}")
        
        Logger.step(5, "Examinando .gitignore gerado")
        gitignore_file = self.project_path / "data/raw/.gitignore"
        if gitignore_file.exists():
            Logger.info("Conteúdo do .gitignore:")
            print(f"{Fore.WHITE}{gitignore_file.read_text()}{Style.RESET_ALL}")
        
        Logger.step(6, "Commitando metadados no Git")
        self.runner.run("git add data/raw/ibovespa_v1.csv.dvc data/raw/.gitignore", 
                       cwd=self.project_path)
        self.runner.run('git commit -m "Add IBOVESPA dataset v1"', cwd=self.project_path)
        self.runner.run('git tag -a v1.0 -m "Dataset version 1.0"', cwd=self.project_path)
        Logger.success("Metadados commitados e tag v1.0 criada")
        
        self.pause()
    
    def module_3_remote_storage(self):
        """Módulo 3: Configuração de Storage Remoto"""
        Logger.section("MÓDULO 3: CONFIGURAÇÃO DE STORAGE REMOTO")
        
        Logger.step(1, "Criando diretório de storage remoto")
        remote_path = Path(REMOTE_STORAGE_PATH)
        remote_path.mkdir(parents=True, exist_ok=True)
        Logger.success(f"Storage remoto criado em: {remote_path}")
        
        Logger.step(2, "Configurando remote no DVC")
        self.runner.run(f"dvc remote add -d myremote {REMOTE_STORAGE_PATH}", 
                       cwd=self.project_path)
        Logger.success("Remote configurado")
        
        Logger.step(3, "Verificando configuração")
        config_file = self.project_path / ".dvc/config"
        if config_file.exists():
            Logger.info("Conteúdo do .dvc/config:")
            print(f"{Fore.WHITE}{config_file.read_text()}{Style.RESET_ALL}")
        
        Logger.step(4, "Commitando configuração")
        self.runner.run("git add .dvc/config", cwd=self.project_path)
        self.runner.run('git commit -m "Configure remote storage"', cwd=self.project_path)
        Logger.success("Configuração commitada")
        
        Logger.step(5, "Fazendo push dos dados para remote")
        self.runner.run("dvc push", cwd=self.project_path)
        Logger.success("Dados enviados para remote storage")
        
        Logger.step(6, "Verificando arquivos no remote")
        self.runner.run(f"ls -R {REMOTE_STORAGE_PATH}")
        
        self.pause()
    
    def module_4_update_dataset(self):
        """Módulo 4: Atualização de Dataset"""
        Logger.section("MÓDULO 4: ATUALIZAÇÃO DE DATASET (NOVA VERSÃO)")
        
        Logger.step(1, "Adicionando novos dados ao dataset")
        additional_data = """2024-01-09,121200,122000,121000,121800,15800000
2024-01-10,121800,122500,121500,122200,16500000
2024-01-11,122200,123000,121900,122700,17000000"""
        
        dataset_file = self.project_path / "data/raw/ibovespa_v1.csv"
        with open(dataset_file, 'a') as f:
            f.write('\n' + additional_data)
        
        Logger.success("Novos dados adicionados (3 linhas)")
        
        Logger.step(2, "Atualizando versionamento no DVC")
        self.runner.run("dvc add data/raw/ibovespa_v1.csv", cwd=self.project_path)
        Logger.success("DVC recalculou hash do dataset")
        
        Logger.step(3, "Examinando mudanças no arquivo .dvc")
        dvc_file = self.project_path / "data/raw/ibovespa_v1.csv.dvc"
        Logger.info("Novo conteúdo do .dvc (observe hash e size):")
        print(f"{Fore.WHITE}{dvc_file.read_text()}{Style.RESET_ALL}")
        
        Logger.step(4, "Commitando nova versão")
        self.runner.run("git add data/raw/ibovespa_v1.csv.dvc", cwd=self.project_path)
        self.runner.run('git commit -m "Update dataset: add 3 more days"', 
                       cwd=self.project_path)
        self.runner.run('git tag -a v1.1 -m "Dataset version 1.1"', cwd=self.project_path)
        Logger.success("Nova versão commitada e tag v1.1 criada")
        
        Logger.step(5, "Push da nova versão para remote")
        self.runner.run("dvc push", cwd=self.project_path)
        Logger.success("Nova versão enviada para remote")
        
        Logger.step(6, "Visualizando histórico")
        self.runner.run("git log --oneline --graph --all --tags", cwd=self.project_path)
        
        self.pause()
    
    def module_5_version_recovery(self):
        """Módulo 5: Recuperação de Versão Anterior"""
        Logger.section("MÓDULO 5: RECUPERAÇÃO DE VERSÃO ANTERIOR")
        
        Logger.step(1, "Verificando estado atual")
        result = self.runner.run("wc -l data/raw/ibovespa_v1.csv", 
                                cwd=self.project_path, show_output=False)
        Logger.info(f"Linhas no dataset atual: {result.stdout.strip()}")
        
        Logger.step(2, "Voltando para versão v1.0")
        self.runner.run("git checkout v1.0", cwd=self.project_path)
        Logger.success("Git revertido para v1.0")
        
        Logger.step(3, "Restaurando dados da versão v1.0")
        self.runner.run("dvc checkout", cwd=self.project_path)
        Logger.success("Dados restaurados")
        
        Logger.step(4, "Verificando dados restaurados")
        result = self.runner.run("wc -l data/raw/ibovespa_v1.csv", 
                                cwd=self.project_path, show_output=False)
        Logger.info(f"Linhas no dataset v1.0: {result.stdout.strip()}")
        
        Logger.step(5, "Retornando para versão mais recente")
        self.runner.run("git checkout main 2>/dev/null || git checkout master", 
                       cwd=self.project_path)
        self.runner.run("dvc checkout", cwd=self.project_path)
        Logger.success("Retornado para versão mais recente")
        
        Logger.step(6, "Verificando estado final")
        result = self.runner.run("wc -l data/raw/ibovespa_v1.csv", 
                                cwd=self.project_path, show_output=False)
        Logger.info(f"Linhas no dataset atual: {result.stdout.strip()}")
        
        self.pause()
    
    def module_6_collaboration(self):
        """Módulo 6: Colaboração em Equipe"""
        Logger.section("MÓDULO 6: COLABORAÇÃO EM EQUIPE (SIMULAÇÃO)")
        
        # Limpar diretório de colaboração anterior
        collab_path = Path(TEMP_COLLAB_PATH)
        if collab_path.exists():
            shutil.rmtree(collab_path)
        
        Logger.step(1, "Simulando clone do projeto por colega")
        parent_dir = collab_path.parent
        self.runner.run(
            f"git clone {self.project_path} {collab_path.name}", 
            cwd=parent_dir
        )
        Logger.success(f"Projeto clonado em: {collab_path}")
        
        Logger.step(2, "Configurando DVC no projeto clonado")
        self.runner.run(
            f"dvc remote modify myremote url {REMOTE_STORAGE_PATH}", 
            cwd=collab_path
        )
        Logger.success("Remote configurado")
        
        Logger.step(3, "Baixando dados do remote")
        self.runner.run("dvc pull", cwd=collab_path)
        Logger.success("Dados baixados do remote storage")
        
        Logger.step(4, "Verificando dados restaurados")
        self.runner.run("ls -lh data/raw/", cwd=collab_path)
        result = self.runner.run("head -5 data/raw/ibovespa_v1.csv", 
                                cwd=collab_path, show_output=False)
        Logger.info("Primeiras linhas do dataset:")
        print(f"{Fore.WHITE}{result.stdout}{Style.RESET_ALL}")
        
        Logger.success("Colaboração simulada com sucesso!")
        Logger.info(f"Projeto do colaborador em: {collab_path}")
        
        self.pause()
    
    def module_7_pipeline(self):
        """Módulo 7: Pipeline com DVC"""
        Logger.section("MÓDULO 7: PIPELINE SIMPLES COM DVC")
        
        Logger.step(1, "Criando arquivo dvc.yaml")
        pipeline_config = """stages:
  preprocess:
    cmd: python src/preprocess.py
    deps:
      - data/raw/ibovespa_v1.csv
      - src/preprocess.py
    outs:
      - data/processed/ibovespa_clean.csv
"""
        pipeline_file = self.project_path / "dvc.yaml"
        pipeline_file.write_text(pipeline_config)
        Logger.success("Pipeline configurado em dvc.yaml")
        
        Logger.step(2, "Criando script de pré-processamento")
        preprocess_script = '''import pandas as pd
import sys

print(" Iniciando pré-processamento...")

# Carregar dados
df = pd.read_csv('data/raw/ibovespa_v1.csv')
print(f"   Dados carregados: {len(df)} registros")

# Processamento
df['data'] = pd.to_datetime(df['data'])
df = df.sort_values('data')
df['retorno'] = df['fechamento'].pct_change()

# Estatísticas
print(f"   Período: {df['data'].min()} até {df['data'].max()}")
print(f"   Retorno médio: {df['retorno'].mean():.4f}")

# Salvar
df.to_csv('data/processed/ibovespa_clean.csv', index=False)
print(f" Processamento concluído: {len(df)} registros salvos")
'''
        
        src_dir = self.project_path / "src"
        src_dir.mkdir(exist_ok=True)
        preprocess_file = src_dir / "preprocess.py"
        preprocess_file.write_text(preprocess_script)
        Logger.success("Script preprocess.py criado")
        
        Logger.step(3, "Executando pipeline")
        self.runner.run("dvc repro", cwd=self.project_path)
        Logger.success("Pipeline executado")
        
        Logger.step(4, "Examinando dvc.lock gerado")
        lock_file = self.project_path / "dvc.lock"
        if lock_file.exists():
            Logger.info("Primeiras linhas do dvc.lock:")
            lines = lock_file.read_text().split('\n')[:15]
            print(f"{Fore.WHITE}{chr(10).join(lines)}{Style.RESET_ALL}")
        
        Logger.step(5, "Commitando pipeline")
        self.runner.run("git add dvc.yaml dvc.lock src/preprocess.py data/processed/.gitignore", 
                       cwd=self.project_path)
        self.runner.run('git commit -m "Add preprocessing pipeline"', cwd=self.project_path)
        Logger.success("Pipeline commitado")
        
        Logger.step(6, "Testando re-execução (sem mudanças)")
        Logger.info("Executando novamente sem modificações...")
        self.runner.run("dvc repro", cwd=self.project_path)
        Logger.success("DVC detectou que nada mudou e pulou execução!")
        
        self.pause()
    
    def module_8_dag_visualization(self):
        """Módulo 8: Visualização do Pipeline"""
        Logger.section("MÓDULO 8: VISUALIZAÇÃO E MANUTENÇÃO")
        
        Logger.step(1, "Visualizando DAG do pipeline")
        self.runner.run("dvc dag", cwd=self.project_path)
        
        Logger.step(2, "Verificando status do DVC")
        self.runner.run("dvc status", cwd=self.project_path)
        
        Logger.step(3, "Estatísticas do cache")
        self.runner.run("du -sh .dvc/cache 2>/dev/null || echo 'Cache vazio'", 
                       cwd=self.project_path)
        
        Logger.step(4, "Resumo final do projeto")
        Logger.info("Estrutura final do projeto:")
        self.runner.run(
            "tree -L 3 -a 2>/dev/null || find . -maxdepth 3 -print | sed 's|[^/]*/| |g'", 
            cwd=self.project_path
        )
        
        self.pause()
    
    def generate_summary(self):
        """Gera resumo final"""
        Logger.section("RESUMO")
        
        summary = f"""
{Fore.GREEN} CONCLUÍDO COM SUCESSO!{Style.RESET_ALL}

{Fore.CYAN} Projeto criado em:{Style.RESET_ALL}
   {self.project_path}

{Fore.CYAN} Storage remoto em:{Style.RESET_ALL}
   {REMOTE_STORAGE_PATH}

{Fore.CYAN} Projeto colaborador em:{Style.RESET_ALL}
   {TEMP_COLLAB_PATH}

