import click
from src.db import Database
from src.repositories import ApplicationRepository
from src.crawler import Crawler

@click.group()
def cli():
    """IT Issue Tracker Crawler CLI"""
    pass

@cli.command()
@click.option('--app', 'app_name', help='Crawl specific application by name')
def crawl(app_name: str | None):
    """Crawl sources for IT issues."""
    db = Database()
    try:
        crawler = Crawler(db)

        if app_name:
            # Find app by name
            apps = ApplicationRepository(db).list_all()
            app = next((a for a in apps if a['name'].lower() == app_name.lower()), None)
            if not app:
                click.echo(f"Application not found: {app_name}")
                return
            count = crawler.crawl_application(app['id'])
        else:
            count = crawler.crawl_all()

        click.echo(f"\nDone! Added {count} new issues.")
    finally:
        db.close()

@cli.command('list-apps')
def list_apps():
    """List all monitored applications."""
    db = Database()
    try:
        repo = ApplicationRepository(db)
        apps = repo.list_all()

        if not apps:
            click.echo("No applications configured.")
            return

        click.echo("\nMonitored Applications:")
        click.echo("-" * 50)
        for app in apps:
            keywords = ", ".join(app['keywords'][:3])
            click.echo(f"  {app['name']} ({app['vendor'] or 'Unknown vendor'})")
            click.echo(f"    Keywords: {keywords}")
    finally:
        db.close()

@cli.command('add-app')
@click.option('--name', required=True, help='Application name')
@click.option('--vendor', help='Vendor name')
@click.option('--keywords', required=True, help='Comma-separated search keywords')
def add_app(name: str, vendor: str | None, keywords: str):
    """Add a new application to monitor."""
    db = Database()
    try:
        repo = ApplicationRepository(db)
        keyword_list = [k.strip() for k in keywords.split(',')]
        app = repo.create(name, vendor, keyword_list)
        click.echo(f"Added: {app['name']} (id: {app['id']})")
    finally:
        db.close()

if __name__ == '__main__':
    cli()
