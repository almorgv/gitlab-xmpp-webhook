DIR=$(dirname $0)
docker build "$DIR/.." -t gitlab-xmpp-webhook --build-arg APT_CACHE= --build-arg HTTPS_PROXY=