# GitLab Topics Cleaner

Simple CLI tool that helps you to cleanup your GitLab topics
and make them manageable and easier to use. This tool can:
- identify similar topics, that could be merged into one
- remove unused topics
- migrate synonyms / similar topics into their primary form topic

This tools is not aimed to manage available topics, for such case
you can use [GitLab Terraform Provider](https://registry.terraform.io/providers/gitlabhq/gitlab/latest/docs/resources/topic).

## 🚀 How to use

You can use either CLI or provided `gcr.io/filipowm/gitlab-topics-cleaner` Docker image.

In order to use it, you need to:
1. Use at least `Python 3.6`
1. [optional] Clone this repo (only when using CLI; package in pip will be created in future) 
    and execute `pip install -r requirements.txt` to install necessary libraries
1. Create [GitLab Private Access Token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) with `api` scope
1. Set up `GITLAB_TOKEN` environment variable with created token
1. [optional] Set up `GITLAB_URL` environment variable with full URL to GitLab (defaults to `https://gitlab.com`)

**Important:** applying `cleanup` operations require admin access token! For dry-run, admin access may not be required.

When using CLI:
```
Usage: gitlab-cleaner.py [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  Enable debug mode  [default: False]
  --help   Show this message and exit.

Commands:
  cleanup       Cleanup unused topics and/or migrate synonyms to their...
  find-similar  Identify similar or mis-spelled topics.
```

When using Docker image same commands and options/args are available as in CLI.
```bash
docker run -e GITLAB_TOKEN=<PRIVATE_ACCESS_TOKEN> gcr.io/filipowm/gitlab-topics-cleaner [OPTIONS] COMMAND [ARGS]...
```

### Identifying similar topics

```
Usage: gitlab-cleaner.py find-similar [OPTIONS]

  Identify similar or mis-spelled topics.

Options:
  -o, --output PATH  Path where results will be written as CSV (not yet working)
  --help             Show this message and exit.
```

**Important:** This command is safe and does not modify any resources in GitLab.

Example output:
```
Finding similar / mis-spelled topics...
Found 5 similar topics groups

['not-validated', 'non-validated', 'not validated', 'not-Validate', 'nor-validated']
['backend', 'back-end']
['frontend', 'front-end', 'frontent']
['cicd', 'ci/cd']
['data-pattern', 'datapattern', 'data patterns']
```

### Cleaning up

**Important:** applying `cleanup` operations require admin access token! For dry-run, admin access may not be required.

```
Usage: gitlab-cleaner.py cleanup [OPTIONS]

  Cleanup unused topics and/or migrate synonyms to their primary form.
  Requires additional configuration.

Options:
  -a, --apply                  Use to apply changes. Without this flag, no
                               changes will be done on remote GitLab.
                               [default: False]
  -m, --migrate-synonyms PATH  Migrate synonyms to their primary form. Provide
                               path to topics configuration file.
  -r, --remove-unused          Remove unused topics  [default: False]
  --help                       Show this message and exit.
```

**Important:** By default not changes are applied and tool works in dry-run mode,
unless `-a/-apply` flag is provided.

You can execute both migration and cleanup operations at once by providing both `-r` and `-m` flags.

#### Migrating topics

Synonymous topics in all projects containing them will be migrated to primary form,
and then those synonyms would be removed.

First, you need to define topics and their synonyms in either JSON or YAML files:

```yaml
- topic: machine-learning
  synonyms:
    - 'ml'
    - 'machinelearning'
```

```json
[
  {
    "topic": "machine-learning",
    "synonyms": ["ml", "machinelearning"]
  }
]
```

Then you can use `cleanup` command with provided configuration file to perform migration
```shell
python gitlab-cleaner.py cleanup -m my_config_file.yaml
```

Example output (without `apply` flag):
```
Running in dry run mode. No changes will be applied. To apply changes, use -a/--apply flag.

Synonymous topics will be migrated to their primary form.
2 synonyms were identified.

Migrating synonym 'ml' to 'machine-learning' in 100 projects
Synonym 'ml' was migrated to 'machine-learning' in all 100 projects
Topic 'ml' would be removed, but in dry-run mode

Migrating synonym 'machinelearning' to 'machine-learning' in 5 projects
Synonym 'machinelearning' was migrated to 'machine-learning' in all 5 projects
Topic 'machinelearning' would be removed, but in dry-run mode

2 synonyms were migrated!
```

In case you use provided Docker image, you simply can use (assuming in your `pwd` you have `my_config.yaml`
file with aforementioned topics configuration):
```bash
docker run -d -v $(PWD):/config/ filipowm/gitlab-topic-cleaner cleanup -m /config/my_config.yaml -a
```

#### Removing unused topics

```bash
python gitlab-cleaner.py cleanup -r
```

To apply changes, add `-a/--apply` flag:
```bash
python gitlab-cleaner.py cleanup -r -a
```

In case you use provided Docker image, you simply can use:
```bash
docker run -d filipowm/gitlab-topic-cleaner cleanup -r -a
```

Example output (without `apply` flag):
```
Running in dry run mode. No changes will be applied. To apply changes, use -a/--apply flag.

Unused topics will be removed
5 topics are not connected with any project and will be removed
Topic 'rancher' would be removed, but in dry-run mode
Topic 'GitLab CI/CD templates' would be removed, but in dry-run mode
Topic 'ml' would be removed, but in dry-run mode
Topic 'docs-content' would be removed, but in dry-run mode
Topic 'argo' would be removed, but in dry-run mode
5 topics would be removed, but running in dry-run mode.
```

## Contributions

As always - contributions are more than welcome :-) Don't hesitate
to drop an issue or send a PR.