from pydio.api import Provider

from bumpify.context import Context

from . import api, config, filesystem, semver, prompt

provider = Provider()
provider.attach(api.provider)
provider.attach(config.provider)
provider.attach(semver.provider)
provider.attach(filesystem.provider)
provider.attach(prompt.provider)


@provider.provides(Context)
def make_context():
    # NOTE: Context is created by injector to ensure that all providers will
    # use same instance of it. It must be initialized shortly after creation.
    return Context()