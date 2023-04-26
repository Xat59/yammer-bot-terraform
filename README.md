# yammer-bot-terraform

Python3 app that keeps you informed about `terraform` topics by scanning relevant sources, then pushing them to a Yammer group.

Here are the following topics:
- terraform providers releases from the [official Github hashicorp organization](https://github.com/hashicorp/)
- terraform releases from the [official terraform repository](https://github.com/hashicorp/terraform)
- terraform blog articles from the [official hashicorp terraform blog](https://www.hashicorp.com/blog/products/terraform)

## Why this app

There are a lot of source of information to be kept informed regarding `terraform` topics.
Checking the terraform blog, terraform binary repository and official providers takes so much time and is annoying.

So I've decided to create this app to automatically retrieve new information and push them to a Yammer group.

## Installation

### Classic installation

Use the `requirements.txt` file to install python packages locally:

```bash
pip install -r requirements.txt
```

### Docker installation

A `Dockerfile` has been provided to run the app as container.

## Usage

### Configuration

Copy the `config.ini.example` file:

```bash
cp config.ini.example config.ini
```

The `config.ini` file looks like the following, please replace with your own information:

```ìni
[yammer]
api_endpoint = https://www.yammer.com/api/v1/messages.json
access_token = <REPLACE_WITH_YAMMER_TOKEN>
group_id = <REPLACE_WITH_YAMMER_GROUP_IDENTIFIER>
```

- `yammer.api_endpoint`: if you really need to change you Yammer API endpoint, feel free to change it.
- `yammer.access_token`: the Yammer access token allows the app to push information in your Yammer group.
- `yammer.group_id`: the group identifier of your Yammer group you want to push information to.

### Usage with classic installation

To run the `blog` app, execute the following:

```bash
./app/blog.py
```

To run the `github` app, execute the following:

```bash
./app/github.py
```

### Usage with Docker

To run the `blog` app, execute the following:

```bash
docker run -v <CONFIG_PATH>:/config.ini -v <DB_PATH>:/db yammer-bot-terraform python blog.py
```

To run the `github` app, execute the following:

```bash
docker run -v <CONFIG_PATH>:/config.ini -v <DB_PATH>:/db yammer-bot-terraform python github.py
```

> **NOTE**: Make sure you have replaced `<CONFIG_PATH>` and `<DB_PATH>`

## Future improvments

- provide a way to provide Github authentication to avoid Github API rate limits.
- possibility to push information to any social network.
- add new source of information (please create an issue).
- on first run, do not push any information, but create the DB files instead.