# gitlab-xmpp-webhook

gitlab-xmpp-webhook is [GitLab](https://about.gitlab.com/)
[web hook](https://docs.gitlab.com/ce/user/project/integrations/webhooks.html) handler
for XMPP multi-user chat notifications about repository events written in Python.


## Configuration

Before run gitlab-xmpp-webhook, you migth want to create a configuration file. You could use
provided `config/config.default.json` as example. Create `config/config.json` and change XMPP
account JID/password according to your preferences.

Also configuration can be passed with the following ENV variables:
- `XMPP_HOST`
- `XMPP_PORT`
- `BOT_JID`
- `BOT_PASS`
- `BOT_NICK`

## Build

Before build specify APT_CACHE and HTTP_PROXY variables for build purpose.
You could use example script provided in `bin/docker-build.sh` to build docker image

## Run

Run gitlab-xmpp-webhook within docker container with `bin/docker-run.sh` script.
Servise should start listing on `0.0.0.0:8080`.
Additionally you could mount `config` and `app/templates` volumes to change configuration and add or change templates on the fly.