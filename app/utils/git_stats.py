"""
Git statistics utility for analyzing contributor code contributions.
"""
import subprocess
from typing import Dict, List, Tuple


class GitStats:
    """Utility class for analyzing git repository statistics."""
    
    @staticmethod
    def get_contributors() -> List[str]:
        """
        Get list of all contributors to the repository.
        
        Returns:
            List of contributor names
        """
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
            print(f"Error getting contributors: {e}")
            return []
    
    @staticmethod
    def get_contributor_stats(author: str) -> Dict[str, int]:
        """
        Get statistics for a specific contributor.
        
        Args:
            author: Name of the contributor
            
        Returns:
            Dictionary with 'additions', 'deletions', and 'commits' counts
        """
        try:
            # Get additions and deletions
            result = subprocess.run(
                ['git', 'log', '--all', '--author=' + author, '--pretty=tformat:', '--numstat'],
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
                ['git', 'log', '--all', '--author=' + author, '--oneline'],
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
            print(f"Error getting stats for {author}: {e}")
            return {'additions': 0, 'deletions': 0, 'commits': 0, 'total_changes': 0}
    
    @staticmethod
    def get_all_contributor_stats() -> List[Dict[str, any]]:
        """
        Get statistics for all contributors.
        
        Returns:
            List of dictionaries containing contributor stats
        """
        contributors = GitStats.get_contributors()
        stats = []
        
        for contributor in contributors:
            contributor_stats = GitStats.get_contributor_stats(contributor)
            stats.append({
                'author': contributor,
                **contributor_stats
            })
        
        # Sort by total changes (descending)
        stats.sort(key=lambda x: x['total_changes'], reverse=True)
        return stats
    
    @staticmethod
    def print_stats(stats: List[Dict[str, any]] = None):
        """
        Print contributor statistics in a formatted table.
        
        Args:
            stats: Optional list of stats, if not provided will fetch all stats
        """
        if stats is None:
            stats = GitStats.get_all_contributor_stats()
        
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
    # When run as a script, print all contributor statistics
    GitStats.print_stats()
