#!/usr/bin/env python3
"""
Script para mostrar estadísticas de contribuciones al repositorio.
Muestra cuántas líneas de código cada contribuidor ha agregado y eliminado.
"""
import subprocess
from typing import Dict, List


def get_contributors() -> List[str]:
    """Get list of all contributors to the repository."""
    try:
        result = subprocess.run(
            ['git', 'log', '--all', '--format=%aN'],
            capture_output=True,
            text=True,
            check=True
        )
        contributors = list(set(result.stdout.strip().split('\n')))
        return sorted(contributors)
    except subprocess.CalledProcessError as e:
        print(f"Error obteniendo contribuidores: {e}")
        return []


def get_contributor_stats(author: str) -> Dict[str, int]:
    """Get statistics for a specific contributor."""
    try:
        # Escape special regex characters in author name for git grep patterns
        # Use --fixed-strings to treat author name literally
        
        # Get additions and deletions
        result = subprocess.run(
            ['git', 'log', '--all', '--author=' + author, '--fixed-strings', '--pretty=tformat:', '--numstat'],
            capture_output=True,
            text=True,
            check=True
        )
        
        additions = 0
        deletions = 0
        
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        # Handle binary files (marked as '-')
                        add = int(parts[0]) if parts[0] != '-' else 0
                        dele = int(parts[1]) if parts[1] != '-' else 0
                        additions += add
                        deletions += dele
                    except ValueError:
                        continue
        
        # Get commit count
        commit_result = subprocess.run(
            ['git', 'log', '--all', '--author=' + author, '--fixed-strings', '--oneline'],
            capture_output=True,
            text=True,
            check=True
        )
        commits = len([line for line in commit_result.stdout.strip().split('\n') if line])
        
        return {
            'additions': additions,
            'deletions': deletions,
            'commits': commits,
            'total_changes': additions + deletions
        }
    except subprocess.CalledProcessError as e:
        print(f"Error obteniendo estadísticas para {author}: {e}")
        return {'additions': 0, 'deletions': 0, 'commits': 0, 'total_changes': 0}


def get_all_contributor_stats() -> List[Dict[str, any]]:
    """Get statistics for all contributors."""
    contributors = get_contributors()
    stats = []
    
    for contributor in contributors:
        contributor_stats = get_contributor_stats(contributor)
        stats.append({
            'author': contributor,
            **contributor_stats
        })
    
    # Sort by total changes (descending)
    stats.sort(key=lambda x: x['total_changes'], reverse=True)
    return stats


def print_stats(stats: List[Dict[str, any]] = None):
    """Print contributor statistics in a formatted table."""
    if stats is None:
        stats = get_all_contributor_stats()
    
    print("\n" + "="*80)
    print("ESTADÍSTICAS DE CONTRIBUCIONES AL REPOSITORIO")
    print("="*80)
    print(f"{'Contribuidor':<30} {'Commits':>10} {'Líneas +':>12} {'Líneas -':>12} {'Total':>12}")
    print("-"*80)
    
    total_commits = 0
    total_additions = 0
    total_deletions = 0
    
    for stat in stats:
        print(f"{stat['author']:<30} {stat['commits']:>10} {stat['additions']:>12} {stat['deletions']:>12} {stat['total_changes']:>12}")
        total_commits += stat['commits']
        total_additions += stat['additions']
        total_deletions += stat['deletions']
    
    print("-"*80)
    print(f"{'TOTAL':<30} {total_commits:>10} {total_additions:>12} {total_deletions:>12} {total_additions + total_deletions:>12}")
    print("="*80 + "\n")


if __name__ == "__main__":
    print_stats()
