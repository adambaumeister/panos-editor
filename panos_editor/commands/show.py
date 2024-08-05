import typer

app = typer.Typer()


@app.command()
def show(query: str):
    print("here")
