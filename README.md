# datadogEventWrap

A simple utility used to create Datadog events when the given command/process starts and stops

## Configuration
### Datadog API/App Keys
You must have the following variables configured for the utility to work:
* `datadog_api_key` - An API key for your Datadog account
* `datadog_app_key` - An App key for your Datadog account

Those variables will work in a configuration file, or as environment variables. If using both, the config files values will override the environment variables

### Event Creation Errors
You can choose to ignore if an error occurs during event creation. For example if your Datadog credentials are not correct then the script can continue to run the command being passed in.

Use either the `--ignore-event-errors` flag at runtime or set `ignore_event_errors` to a boolean value in your configuration file

### Configuring Tags
You can either define tags as parameters passed to the script (see Usage below) or by creating a config file.

There are 3 supported 'types' of tags:
* Start Tags - These get sent with the start event
* End Tags - These get sent with the end event
* Event Tags (or simply Tags) - These get sent with all events

See the `datadogEventWrap.yaml.example` file for an example configuration file

## Usage
```
Datadog Event Wrapper
	Logs events using the DataDog API when the given command starts and finishes

Usage:
	ddEventWrap <options> <command>

Options:
	-c=/some/config.yaml, --config=/some/config.yaml - Path to the configuration file. Defaults to ./ddWrap.yaml
	-t=sometag:somevalue, --eventtag=sometag:somevalue - Additional tag to include for all the events triggered
	-s=sometag:somevalue, --starttag=sometag:somevalue - Additional tag to include for the start event triggered
	-e=sometag:somevalue, --endtag=sometag:somevalue - Additional tag to include for the end event triggered
	-d, --debug - Enable debug mode
	--dryrun - Enable debug mode and skip event creation
	--ignore-event-errors - Ignore errors that happen during event creation
```
