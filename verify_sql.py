import os
from sqlalchemy import text
from rich.console import Console
from rich.table import Table
from database.connection import engine

console = Console()

def print_table(name, rows, keys):
    table = Table(title=name)
    for key in keys:
        table.add_column(key)
    
    for row in rows:
        table.add_row(*[str(getattr(row, key, None) or row[idx]) for idx, key in enumerate(keys)])
        # Handling row access as object or tuple/dict depending on result proxy

    console.print(table)

def run_verification():
    console.print("[bold green]Running verification queries against database...[/bold green]")
    
    with engine.connect() as conn:
        tables = ["Departments", "Users", "ModelRegistry", "VerificationRequests"]
        
        for table_name in tables:
            try:
                result = conn.execute(text(f"SELECT * FROM {table_name}"))
                keys = result.keys()
                rows = result.fetchall()
                
                # Check directly accessing by index/key for rich
                # Rich expects strings usually for safe printing
                
                table = Table(title=table_name)
                for key in keys:
                    table.add_column(key, style="cyan")
                
                for row in rows:
                     # row is a Row object, can be unpacked
                    table.add_row(*[str(item) for item in row])

                console.print(table)
                console.print("\n")
            except Exception as e:
                console.print(f"[bold red]Error querying {table_name}: {e}[/bold red]")

if __name__ == "__main__":
    run_verification()
