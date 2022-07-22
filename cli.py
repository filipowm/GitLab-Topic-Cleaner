import logging

import click

import logger
from configurer import configure_gitlab, configure_synonyms_identifier, configure_cleaner

gitlab = None


@click.group()
@click.option('--debug/--no-debug', default=False, show_default=True)
def cli(debug):
    logging_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=logging_level)
    if debug:
        logger.warn('Turning on debug mode')


@cli.command()
@click.option('-a', '--apply',
              help='Use to apply changes. Without this flag, no changes will be done on remote GitLab.',
              is_flag=True,
              default=False,
              show_default=True)
@click.option('-m', '--migrate-synonyms', 'topics_config_path',
              help='Migrate synonyms to their primary form. Provide path to topics configuration file.',
              type=click.Path(exists=True))
@click.option('-r', '--remove-unused',
              help='Remove unused topics',
              is_flag=True,
              default=False,
              show_default=True)
def cleanup(apply, topics_config_path, remove_unused):
    if topics_config_path is None and not remove_unused:
        logger.error('None of -m/--migrate-synonyms or -r/--remove-unused flags were set!')
        return

    if not apply:
        logger.warn('Running in dry run mode. No changes will be applied. To apply changes, use -a/--apply flag.')

    cleaner = configure_cleaner(gitlab, config_path=topics_config_path, apply=apply)

    if topics_config_path is not None:
        logger.info()
        cleaner.migrate_synonyms()

    if remove_unused:
        logger.info()
        cleaner.remove_empty()


@cli.command()
@click.option('-o', '--output', help='Path of file to output results as CSV',
              type=click.Path(exists=False, writable=True))
def find_similar(output):
    synonyms_identifier = configure_synonyms_identifier(gitlab)
    identified_groups = synonyms_identifier.identify()
    logger.info()
    for group in identified_groups:
        mapped = list(map(lambda topic: topic.title, group))
        logger.info(mapped)


def _banner():
    banner = f"""{logger.YELLOW} 
  __                    ___                   _                      
 /__ o _|_ |   _. |_     |  _  ._  o  _  _   /  |  _   _. ._   _  ._ 
 \_| |  |_ |_ (_| |_)    | (_) |_) | (_ _>   \_ | (/_ (_| | | (/_ |  
            _                  |                                     
 |_       _|_ o | o ._   _       ._ _                                
 |_) \/    |  | | | |_) (_) \/\/ | | |                               
     /              |                                                
    {logger.NC}"""
    click.echo(banner, color=True)


if __name__ == '__main__':
    try:
        _banner()
        gitlab = configure_gitlab()
        cli()
    except:
        pass  # terrible practice, but discard for now
