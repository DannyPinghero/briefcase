import inspect

from .exceptions import BriefcaseConfigError
from .config import parse_config, AppConfig


class BaseCommand:
    def __init__(self, platform, output_format, parser, extra):
        self.platform = platform
        self.output_format = output_format

        self.add_options(parser)

        # Extract the set of command line options that have default values.
        self.default_options = {
            action.dest
            for action in parser._actions
            if action.default
        }
        # Parse the full set of command line options from the content
        # remaining after the basic command/platform/output format
        # has been extracted.
        self.options = parser.parse_args(extra)

    def add_options(self, parser):
        """
        Add any options that this command needs to parse from the command line.

        :param parser: a stub argparse parser for the command.
        """
        pass

    @property
    def config_options(self):
        "Return the set of option names that augment application configuration."
        return set()

    def parse_config(self, filename):
        try:
            with open(filename) as config_file:
                # Parse the content of the pyproject.toml file, extracting
                # any platform and output format configuration for each app,
                # creating a single set of configuration options.
                app_configs = parse_config(
                    config_file,
                    platform=self.platform,
                    output_format=self.output_format
                )

                self.apps = {}
                for app_name, parsed_config in app_configs.items():
                    # Start the application configuration with all the
                    # values that have default values.
                    app_config = {
                        option: getattr(self.options, option)
                        for option in self.config_options
                        if option in self.default_options
                    }

                    # Override those default values with values provided
                    # in the configuration file.
                    app_config.update(parsed_config)

                    # Augment the config file values with any options that
                    # were passed in at the command line that have *explicit*
                    # values.
                    app_config.update({
                        option: getattr(self.options, option)
                        for option in self.config_options
                        if option not in self.default_options
                    })

                    # We now have the final state of all the options.
                    # Construct an AppConfig object with the final set of
                    # configuration options for the app.
                    try:
                        self.apps[app_name] = AppConfig(**app_config)
                    except TypeError:
                        # Inspect the AppConfig constructor to find which
                        # parameters are required and don't have a default
                        # value.
                        required_args = {
                            name
                            for name, param in inspect.signature(AppConfig.__init__).parameters.items()
                            if param.default == inspect._empty
                            and name not in {'self', 'kwargs'}
                        }
                        missing_args = required_args - app_config.keys()
                        missing = ', '.join(
                            "'{arg}'".format(arg=arg)
                            for arg in missing_args
                        )
                        raise BriefcaseConfigError(
                            "Configuration for '{app_name}' is incomplete (missing {missing})".format(
                                app_name=app_name,
                                missing=missing
                            )
                        )

        except FileNotFoundError:
            raise BriefcaseConfigError('configuration file not found')


class CreateCommand(BaseCommand):
    def __call__(self):
        self.verify_tools()
        print("CREATE:", self.description)

    def verify_tools(self):
        "Verify that the tools needed to run this command exist"


class UpdateCommand(BaseCommand):
    def __call__(self):
        print("UPDATE:", self.description)


class BuildCommand(BaseCommand):
    def __call__(self):
        print("BUILD:", self.description)


class RunCommand(BaseCommand):
    def __call__(self):
        print("RUN:", self.description)


class PublishCommand(BaseCommand):
    def __call__(self):
        print("PUBLISH:", self.description)
