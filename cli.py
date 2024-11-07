# cli.py
import click
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict
from main import ReviewManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """RBRDCK - Advanced Code Review Tool"""
    pass

@cli.command()
@click.argument('repo', type=str)
@click.argument('pr_number', type=int)
@click.option('-o', '--output', type=click.Path(), help='Save review to file')
def review(repo: str, pr_number: int, output: str = None):
    """Review a specific pull request"""
    async def _review():
        try:
            review_manager = await ReviewManager.create()
            results = await review_manager.review_pr(repo, pr_number)
            
            if output:
                Path(output).write_text(json.dumps(results, indent=2))
                click.echo(f"Review saved to {output}")
            else:
                click.echo(json.dumps(results, indent=2))
                
        except Exception as e:
            logger.error(f"Error reviewing PR: {e}")
            click.echo(f"Error: {str(e)}", err=True)
            raise click.Abort()
    
    asyncio.run(_review())

@cli.command()
@click.argument('repo')
@click.option('--days', default=7, help='Number of days to analyze')
@click.option('--output', '-o', type=click.Path(),
              help='Save insights to file')
def insights(repo: str, days: int, output: str):
    """Generate insights report"""
    try:
        review_manager = ReviewManager()
        report = review_manager.get_insights(days)
        
        # Format report
        formatted_report = json.dumps(report, indent=2)
        
        # Output report
        if output:
            output_path = Path(output)
            output_path.write_text(formatted_report)
            click.echo(f"Insights saved to {output}")
        else:
            click.echo(formatted_report)
            
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('repo')
@click.option('--webhook-url', required=True,
              help='Webhook URL for notifications')
def setup(repo: str, webhook_url: str):
    """Setup integrations for a repository"""
    async def _setup():
        try:
            review_manager = await ReviewManager.create()
            results = await review_manager.setup_repository(repo, webhook_url)
            
            # Output results
            for integration, status in results.items():
                click.echo(f"{integration} integration setup: {status}")
                
        except Exception as e:
            logger.error(f"Error setting up repository: {e}")
            click.echo(f"Error: {str(e)}", err=True)
            raise click.Abort()
    
    asyncio.run(_setup())

@cli.command()
@click.argument('repo')
def status(repo: str):
    """Check status of integrations and services"""
    try:
        review_manager = ReviewManager()
        
        # Check integration status
        click.echo("Integration Status:")
        for integration, status in review_manager.integration_hub._integrations.items():
            click.echo(f"- {integration}: {'Active' if status else 'Inactive'}")
            
        # Check analytics status
        click.echo("\nAnalytics Status:")
        metrics = review_manager.usage_analytics.get_usage_statistics()
        click.echo(json.dumps(metrics, indent=2))
        
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

def main():
    try:
        asyncio.run(cli())
    except Exception as e:
        logger.error(f"CLI error: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()