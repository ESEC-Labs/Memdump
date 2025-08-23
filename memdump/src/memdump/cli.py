import os
import sys
import click
import psutil
from . import categorize_memory_regions

'''
--- Supporting functions ---
'''

def map_file(file_name, exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec):
    '''Given a file name match a regex expression and get each readable string from a mmapped file'''  
    with open(file_name, 'r') as f:
        file_content = f.readlines()

        categorize_memory_regions.group_regions(file_content, exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec) 

def dump_memory(pid, exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec):
    """Handles the actual memory dumping logic."""

    click.echo(f"Dumping memory segments for PID {pid}...\n")
    try:
        process_maps = f"/proc/{pid}/maps"
        map_file(process_maps, exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec)
        click.echo("Memory map has been dumped!\n")
    except PermissionError:
        click.echo("Permission denied. Please run as sudo.")
    except FileNotFoundError:
        click.echo("Process file not found. Please run 'memdump show' to look for another process.")

'''
--- Commands ---
'''
@click.group()
def main():
    ''' Memdump CLI memory dumping tool'''
    pass

@main.group(name="dump")
def dump():
    ''' Dump memory maps from a process ID or self. '''
    pass

@main.command(name="show")
@click.option('--owner', help="Filter by the owner name.")
def show(owner):
    ''' 
    Show running processes. Shows in the order of pid, name 
    '''

    click.echo("Showing process...")
    for proc in psutil.process_iter(['pid', 'name', 'status', 'username']):
        pid = proc.info['pid']
        name = proc.info['name']
        status = proc.info['status']
        owner = proc.info['username']

        if status == "running":
            color = "green"
        elif status == "idle":
            color = "yellow"
        elif status == "sleeping":
            color = "blue"
        else:
            color = "white"  

        click.secho(f"PID: {pid} - Name: {name} - Status: {status} - Owner: {owner}", fg=color)


@dump.command(name="pid")
@click.argument('pid', type=int, required=False)
@click.option('--self', 'dump_self', is_flag=True, help="Dump the current process.")
@click.option('--all', 'all_sec', is_flag=True, help="Dump all memory sections.")
@click.option('-e', 'exec_sec', is_flag=True, help="Dump only executable sections.")
@click.option('-sl', 'slib_sec', is_flag=True, help="Dump only shared library sections.")
@click.option('-h', 'he_sec', is_flag=True, help="Dump only heap sections.")
@click.option('-st', 'st_sec', is_flag=True, help="Dump only stack sections.")
@click.option('-vv', 'vvar_sec', is_flag=True, help="Dump only vvar sections.")
@click.option('-vs', 'vsys_sec', is_flag=True, help="Dump only vsys sections.")
@click.option('-vd', 'vdso_sec', is_flag=True, help="Dump only vdso sections.")
@click.option('-no', 'none_sec', is_flag=True, help="Dump only none sections.")
def dump_pid(pid, dump_self, exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec):
    ''' Dumps memory maps from a given process ID or the current process. '''
    # Check if a flag has been provided
    if not dump_self and not pid and not any([exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec]):
        click.echo("Error: Please provide a flag or a PID. Use --help for more.")
        sys.exit(1)
    
    if dump_self and not pid and not any([exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec]):
        click.echo("Error: Please provide a flag or a PID. Use --help for more.")
        sys.exit(1)
 
    if all_sec:
        exec_sec = True
        slib_sec = True
        he_sec = True
        st_sec = True
        vvar_sec = True 
        vsys_sec = True 
        vdso_sec = True 
        none_sec = True
    elif exec_sec or slib_sec or he_sec or st_sec or vvar_sec or vsys_sec or vdso_sec or none_sec:
        all_sec = False

    if pid is not None and dump_self:
        click.echo("Error: Cannot provide both a PID and the --self flag.")
        sys.exit(1)

    # Determine the target PID
    if dump_self:
        target_pid = os.getpid()
    elif pid is not None:
        target_pid = pid
    else:
        click.echo("Error: A PID or --self flag is required for this command.")
        sys.exit(1)

    dump_memory(target_pid, exec_sec, slib_sec, all_sec, he_sec, st_sec, vvar_sec, vsys_sec, vdso_sec, none_sec)

if __name__ == "__main__":
    main()
