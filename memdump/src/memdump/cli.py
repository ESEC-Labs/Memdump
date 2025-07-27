import click
import psutil


@click.group()
def main():
    ''' Memdump CLI memory dumping tool'''
    pass


@main.command(name="show")
def show():
    ''' 
    Show running processes. Shows in the order of pid, name 
    '''
    click.echo("Showing process...")
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        pid = proc.info['pid']
        name = proc.info['name']
        status = proc.info['status']

        if status == "running":
            color = "green"
        elif status == "idle":
            color = "yellow"
        elif status == "sleeping":
            color = "blue"
        else:
            color = "white"  

        click.secho(f"{pid} - {name} - {status}", fg=color)

@main.command()
@click.argument('pid', type=int)
def dump(pid):
    ''' Dump memory maps from a process ID. '''
    try: 
        click.echo("Dumping memory segments...")
    except PermissionError:
        click.echo("Permission deined. Please run as sudo.")

    


if __name__ == "__main__":
    main()
