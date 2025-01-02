# Developer Guide

## Structure

## Commans

## How to Add a new API?

### Routes

### Controllers

### Models

## Modules

### How to use log?

This project uses oslo.log as default logger. Log is already intitialized during startup, you can use it easily. By default, log level is info.

```
from oslo_log import log

LOG = log.getLogger(__name__)

LOG.debug("debug message")
LOG.info("some message")
```

### How to use config file?

This project uses oslo.cfg as default config management library. For more samples please check samples directory.

To define and use oslo.cfg please follow steps:

1. Define microservice config groups and options

Based on our code structure, each directory is a microservices(except conf/common), whether is api or daemon worker. Under each microservice, there is a file named conf.py, we should define our group and options here. For example:

The group name should be the name of microservices.

```
opts = [
    cfg.StrOpt("listen_address",
               default="0.0.0.0",
               help="Api service listen address, example: 0.0.0.0."),
    cfg.PortOpt("listen_port",
                default=5000,
                help="Api service listen port, example: 5000"),
    cfg.PortOpt("use_ssl",
                default=False,
                help="If enable https for api service"),
    cfg.BoolOpt("setup_api_doc",
                default=True,
                help=""),
]
```

2. Define DEFAULT options

The default options define is in conf/default.py.

3. Use config in application

Import conf directly and access options with group name. Example:

```
# import conf
from atomy import conf

# get conf object
CONF = conf.CONF

# access option from conf
port = CONF.api.listen_port
```

### How to use i18n?

Use pybabel to help generate i18n files.

#### How to generate translation files?

    $ cd atomy
    $ pybabel extract -F babel.cfg -o locale/atomy.pot .
    $ pybabel init -D atomy -i locale/atomy.pot -d locale -l zh_CN
    $ pybabel init -D atomy -i locale/atomy.pot -d locale -l en_US
    $ pybabel compile -D atomy -d locale

#### How to update?

    $ pybabel extract -F babel.cfg -o locale/atomy.pot . && pybabel update -D atomy -i locale/atomy.pot -d locale
    $ pybabel compile -D atomy -d locale

#### Service startup

Before you startup your service, I suggest you set system environment to make translation work. Both in development and production environment, we need to set ATOMY_LOCALEDIR besides you put all your translation files into system directory /usr/share/locale.

    export ATOMY_LOCALEDIR=$(pwd)/atomy/locale


#### Run obstor unit tests and coverage
```shell
tox -e obstor_unit         # 运行单元测试
tox -e obstor_functional   # 运行函数测试
tox -e obstor_cover        # 运行覆盖率输出html文件
```
