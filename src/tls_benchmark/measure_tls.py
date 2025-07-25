#!/usr/bin/env python3
"""
TLS 1.3 Hybrid Benchmark Tool

Mesure les performances de handshake TLS 1.3 avec et sans cryptographie post-quantique.
Utilise OpenSSL 3.5 avec OQS Provider pour l'hybridation X25519+ML-KEM-768.

Usage:
    python measure_tls.py [--iterations N] [--target HOST:PORT] [--output DIR]

Author: SeifB13
Date: Juillet 2025
"""

import subprocess
import os
import time
import pandas as pd
import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import json


class TLSBenchmark:
    """Classe principale pour les benchmarks TLS hybrides."""
    
    def __init__(self, openssl_path: str = None, target: str = "localhost:4433", 
                 output_dir: str = "data/output"):
        """
        Initialise le benchmark TLS.
        
        Args:
            openssl_path: Chemin vers l'exécutable OpenSSL (détection auto si None)
            target: Serveur cible (host:port)
            output_dir: Répertoire de sortie pour les résultats
        """
        self.target = target 
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration OpenSSL
        self.openssl_path = openssl_path or self._find_openssl()
        self.env = self._setup_environment()
        
        # Configuration logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _find_openssl(self) -> str:
        """Détecte automatiquement le chemin OpenSSL."""
        possible_paths = [
            os.path.expanduser("~/ossl-3.5/bin/openssl"),
            "/usr/local/bin/openssl",
            "/usr/bin/openssl"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        raise RuntimeError("OpenSSL non trouvé. Veuillez spécifier le chemin.")
        
    def _setup_environment(self) -> Dict[str, str]:
        """Configure l'environnement pour OpenSSL + OQS."""
        base_dir = os.path.expanduser("~/ossl-3.5")
        
        env = {
            **os.environ,
            "LD_LIBRARY_PATH": f"{base_dir}/lib64",
            "OPENSSL_CONF": f"{base_dir}/ssl/openssl.cnf", 
            "OPENSSL_MODULES": f"{base_dir}/lib64/ossl-modules",
        }
        
        return env
        
    def measure_latency(self, group: str, timeout: int = 5) -> Optional[float]:
        """
        Mesure la latence d'un handshake TLS.
        
        Args:
            group: Groupe cryptographique (ex: "X25519" ou "X25519MLKEM768")
            timeout: Timeout en secondes
            
        Returns:
            Latence en millisecondes ou None en cas d'échec
        """
        cmd = [
            self.openssl_path, "s_client",
            "-connect", self.target,
            "-groups", group,
            "-brief",
            "-tls1_3"
        ]
        
        try:
            start_time = time.perf_counter()
            result = subprocess.run(
                cmd, 
                input=b"",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=self.env,
                timeout=timeout,
                check=True
            )
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            return latency_ms if latency_ms >= 0 else None
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.logger.warning(f"Échec handshake {group}: {e}")
            return None
            
    def run_benchmark(self, iterations: int = 1000) -> pd.DataFrame:
        """
        Exécute le benchmark complet.
        
        Args:
            iterations: Nombre d'itérations par configuration
            
        Returns:
            DataFrame avec les résultats
        """
        self.logger.info(f"Démarrage benchmark - {iterations} itérations par configuration")
        
        # Mesures classiques
        self.logger.info("Mesure handshakes classiques (X25519)...")
        classic_latencies = []
        for _ in tqdm.tqdm(range(iterations), desc="Classique"):
            latency = self.measure_latency("X25519")
            if latency is not None:
                classic_latencies.append(latency)
                
        # Pause entre les mesures
        time.sleep(2)
        
        # Mesures hybrides
        self.logger.info("Mesure handshakes hybrides (X25519+ML-KEM-768)...")
        hybrid_latencies = []
        for _ in tqdm.tqdm(range(iterations), desc="Hybride"):
            latency = self.measure_latency("X25519MLKEM768")
            if latency is not None:
                hybrid_latencies.append(latency)
                
        # Création du DataFrame
        min_len = min(len(classic_latencies), len(hybrid_latencies))
        if min_len == 0:
            raise RuntimeError("Aucune mesure valide obtenue")
            
        df = pd.DataFrame({
            "classic_ms": classic_latencies[:min_len],
            "hybrid_ms": hybrid_latencies[:min_len],
            "timestamp": [datetime.now().isoformat()] * min_len
        })
        
        self.logger.info(f"Benchmark terminé: {len(classic_latencies)} classiques, "
                        f"{len(hybrid_latencies)} hybrides")
        
        return df
        
    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse statistique des résultats.
        
        Args:
            df: DataFrame des résultats
            
        Returns:
            Dictionnaire des statistiques
        """
        stats = df[["classic_ms", "hybrid_ms"]].describe(percentiles=[0.5, 0.95, 0.99])
        
        # Calcul des différences
        mean_classic = df["classic_ms"].mean()
        mean_hybrid = df["hybrid_ms"].mean()
        delta_percent = 100 * (mean_hybrid - mean_classic) / mean_classic
        
        analysis = {
            "summary": {
                "classic_mean_ms": round(mean_classic, 2),
                "hybrid_mean_ms": round(mean_hybrid, 2),
                "delta_percent": round(delta_percent, 2),
                "sample_size": len(df)
            },
            "statistics": stats.to_dict(),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "target": self.target,
                "openssl_path": self.openssl_path
            }
        }
        
        return analysis
        
    def generate_plots(self, df: pd.DataFrame, output_path: str = None) -> str:
        """
        Génère les graphiques de visualisation.
        
        Args:
            df: DataFrame des résultats
            output_path: Chemin de sortie (auto si None)
            
        Returns:
            Chemin du fichier généré
        """
        if output_path is None:
            output_path = self.output_dir / "handshake_violinplot.pdf"
            
        # Filtrage des outliers pour l'affichage
        df_filtered = df[(df["classic_ms"] < 300) & (df["hybrid_ms"] < 300)]
        
        # Reshape pour seaborn
        df_melted = df_filtered.rename(columns={
            "classic_ms": "Classique",
            "hybrid_ms": "Hybride"
        }).melt(
            id_vars=["timestamp"],
            var_name="Type", 
            value_name="Latence (ms)"
        )
        
        # Génération du plot
        plt.figure(figsize=(8, 6))
        
        # Violin plot
        sns.violinplot(
            data=df_melted, 
            x="Type", 
            y="Latence (ms)",
            inner="box",
            palette=["#a6cee3", "#fdbf6f"]
        )
        
        # Points de moyenne
        sns.pointplot(
            data=df_melted,
            x="Type", 
            y="Latence (ms)",
            estimator='mean',
            color="darkgreen",
            markers='D',
            linestyles='',
            label="Moyenne"
        )
        
        plt.title("Latence Handshake TLS 1.3 - Classique vs Hybride", fontsize=14)
        plt.ylabel("Latence (ms)", fontsize=12)
        plt.xlabel("Configuration Cryptographique", fontsize=12)
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        plt.legend(loc="upper right")
        plt.tight_layout()
        
        # Sauvegarde
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Graphique sauvegardé: {output_path}")
        return str(output_path)
        
    def save_results(self, df: pd.DataFrame, analysis: Dict[str, Any], 
                    filename_prefix: str = "tls_benchmark") -> Dict[str, str]:
        """
        Sauvegarde tous les résultats.
        
        Args:
            df: DataFrame des données brutes
            analysis: Dictionnaire d'analyse
            filename_prefix: Préfixe des fichiers
            
        Returns:
            Dictionnaire des chemins de fichiers créés
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files = {}
        
        # Données brutes CSV
        csv_path = self.output_dir / f"{filename_prefix}_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        files["raw_data"] = str(csv_path)
        
        # Statistiques JSON
        json_path = self.output_dir / f"{filename_prefix}_analysis_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        files["analysis"] = str(json_path)
        
        # Graphique
        plot_path = self.generate_plots(df, 
            self.output_dir / f"{filename_prefix}_plot_{timestamp}.pdf")
        files["plot"] = plot_path
        
        # Rapport Markdown
        report_path = self.output_dir / f"{filename_prefix}_report_{timestamp}.md"
        self._generate_markdown_report(analysis, report_path)
        files["report"] = str(report_path)
        
        return files
        
    def _generate_markdown_report(self, analysis: Dict[str, Any], 
                                 output_path: str):
        """Génère un rapport Markdown des résultats."""
        summary = analysis["summary"]
        
        report = f"""# TLS 1.3 Hybrid Benchmark Report

Generated: {analysis["metadata"]["timestamp"]}
Target: {analysis["metadata"]["target"]}

## Summary

- **Classic (X25519)**: {summary["classic_mean_ms"]} ms (moyenne)
- **Hybrid (X25519+ML-KEM-768)**: {summary["hybrid_mean_ms"]} ms (moyenne)
- **Performance Impact**: {summary["delta_percent"]}%
- **Sample Size**: {summary["sample_size"]} measurements

## Interpretation

"""
        
        if abs(summary["delta_percent"]) < 5:
            report += "✅ **No significant performance impact** - Hybrid PQC ready for production\n"
        elif summary["delta_percent"] > 0:
            report += f"⚠️ **Performance degradation** of {summary['delta_percent']}% detected\n"
        else:
            report += f"🚀 **Performance improvement** of {abs(summary['delta_percent'])}% observed\n"
            
        with open(output_path, 'w') as f:
            f.write(report)


def main():
    """Fonction principale CLI."""
    parser = argparse.ArgumentParser(
        description="TLS 1.3 Hybrid Benchmark Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--iterations", "-n", 
        type=int, 
        default=1000,
        help="Nombre d'itérations par configuration"
    )
    
    parser.add_argument(
        "--target", "-t",
        default="localhost:4433",
        help="Serveur cible (host:port)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="data/output",
        help="Répertoire de sortie"
    )
    
    parser.add_argument(
        "--openssl",
        help="Chemin vers OpenSSL (détection auto si non spécifié)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialisation
        benchmark = TLSBenchmark(
            openssl_path=args.openssl,
            target=args.target,
            output_dir=args.output
        )
        
        # Exécution
        df = benchmark.run_benchmark(args.iterations)
        analysis = benchmark.analyze_results(df)
        
        # Sauvegarde
        files = benchmark.save_results(df, analysis)
        
        # Résumé
        print("\n" + "="*60)
        print("RÉSULTATS DU BENCHMARK")
        print("="*60)
        
        summary = analysis["summary"]
        print(f"Classique (X25519):           {summary['classic_mean_ms']} ms")
        print(f"Hybride (X25519+ML-KEM-768): {summary['hybrid_mean_ms']} ms") 
        print(f"Impact performance:           {summary['delta_percent']:+.1f}%")
        print(f"Échantillon:                  {summary['sample_size']} mesures")
        
        print(f"\nFichiers générés:")
        for file_type, path in files.items():
            print(f"  {file_type}: {path}")
            
    except Exception as e:
        logging.error(f"Erreur during benchmark: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())
