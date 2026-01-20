import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
import os
from pathlib import Path
from sentinel.core.runtime import SecureRuntime
from sentinel.storage.ipfs import IPFSStorage
from sentinel.core.proof import ProofGenerator

app = typer.Typer(help="Argus: Decentralised AI Exec Proofs")
console = Console()

@app.command()
def run(
    model_path: str = typer.Argument(..., help="Path to the model file"),
    input_data: str = typer.Argument(..., help="Input prompt/data for the model"),
    store: bool = typer.Option(True, help="Store proof to IPFS"),
    simulate_tamper: bool = typer.Option(False, help="Simulate a man-in-the-middle attack for demo"),
    demo_privacy: bool = typer.Option(False, help="Enable Privacy/ZKP mode for demo")
):
    """
    Execute an AI task securely and generate a proof.
    """
    if not os.path.exists(model_path):
        console.print(f"[bold red]Error:[/bold red] Model file not found at {model_path}")
        raise typer.Exit(code=1)

    console.print(Panel(f"[bold green]Argus Secure Runtime[/bold green]\nTarget Model: {model_path}\nInput: {input_data}", border_style="green"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        
        task1 = progress.add_task(description="Initializing Secure Runtime...", total=None)
        # Initialize Runtime
        runtime = SecureRuntime(model_path)
        progress.update(task1, completed=True)
        
        task2 = progress.add_task(description="Executing Model & Generating Proof...", total=None)
        # Execute
        constraints = {"max_input_length": 2048}
        
        if demo_privacy:
            constraints["privacy"] = {
                "min_score": 700,
                "min_income": 40000,
                "age_limit": 18
            }
            
        proof = runtime.execute(input_data, constraints)
        progress.update(task2, completed=True)

    if simulate_tamper:
        console.print("[bold yellow]![/bold yellow] Simulating Tampering Attack...", style="yellow")
        proof['credentialSubject']['executionTrace']['output'] = "Evildoer was here"
        # Note: We modified the trace content but NOT the trace_hash in the proof wrapping
        # This will cause verification to fail because hash(trace) != proof.trace_hash

    # Display Proof
    console.print("\n[bold cyan]Execution Complete. Proof Generated:[/bold cyan]")
    console.print(JSON(json.dumps(proof, indent=2)))

    if store:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]Uploading to IPFS..."), transient=True) as p:
            p.add_task("upload", total=None)
            storage = IPFSStorage()
            cid = storage.save_proof(proof)
        
        console.print(Panel(f"[bold white]Proof Stored on IPFS[/bold white]\nCID: [bold yellow]{cid}[/bold yellow]", border_style="blue"))
        
        # BROADCAST TO LOCAL SERVER IF AVAILABLE
        try:
            import requests
            payload = {"cid": cid, "model_hash": proof['credentialSubject']['executionTrace']['model_hash'], "type": "execution_proof"}
            try:
                requests.post("http://127.0.0.1:8000/api/broadcast", json=payload, timeout=0.1)
                # console.print("[dim]Broadcasted to Live Dashboard[/dim]")
            except:
                pass # Fail silently if dashboard is not running
        except ImportError:
            pass

        # QR CODE DISPLAY
        try:
            import qrcode
            import io
            import socket
            
            # Auto-detect local IP for mobile scanning
            # This allows a phone on the same WiFi to reach the laptop
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except:
                local_ip = "127.0.0.1"

            # Point to the Web Dashboard (User Interface), not the raw API JSON
            qr_data = f"http://{local_ip}:8000/?cid={cid}" 
            
            qr = qrcode.QRCode()
            qr.add_data(qr_data)
            f = io.StringIO()
            # invert=True is often better for dark terminal backgrounds
            qr.print_ascii(out=f, invert=True)
            f.seek(0)
            
            # Print URL explicitly for backup
            console.print(Panel(
                f"[bold]Mobile Verification[/bold]\n"
                f"Scan the code below or visit:\n[bold blue]{qr_data}[/bold blue]\n\n"
                f"{f.read()}", 
                border_style="white", 
                expand=False
            ))
        except ImportError:
            pass
        
@app.command()
def verify(cid: str = typer.Argument(..., help="IPFS CID or Path to proof JSON")):
    """
    Verify an execution proof from IPFS or local file.
    """
    proof = None
    
    # Try fetching from IPFS first
    storage = IPFSStorage()
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]Fetching Proof..."), transient=True) as p:
        p.add_task("fetch")
        # Check if it looks like a file path
        if os.path.exists(cid):
             with open(cid, 'r') as f:
                 proof = json.load(f)
        else:
            proof = storage.get_proof(cid)

    if not proof:
        console.print(f"[bold red]Error:[/bold red] Could not retrieve proof for CID/Path: {cid}")
        raise typer.Exit(code=1)

    console.print(f"[bold]Verifying Proof...[/bold]")
    
    # Verification Logic
    is_valid = ProofGenerator.verify_proof(proof)
    
    table = Table(title="Verification Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="bold")
    
    if is_valid:
        table.add_row("Integrity Check (Hash Match)", "[green]PASS[/green]")
        console.print(table)
        console.print(Panel("[bold green]VERIFICATION SUCCESSFUL[/bold green]\nThe execution trace is authentic and has not been tampered with.", border_style="green"))
    else:
        table.add_row("Integrity Check (Hash Match)", "[red]FAIL[/red]")
        console.print(table)
        console.print(Panel("[bold red]VERIFICATION FAILED[/bold red]\nThe proof signature does not match the content. Data may have been tampered with.", border_style="red"))

if __name__ == "__main__":
    app()
