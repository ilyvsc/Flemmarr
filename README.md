# Flemmarr

<img width="30%" src="docs/logo.svg" alt="Flemmarr"></img>

> **flemmard (*noun or adj.*):** lazy, slacker, idler in French 🇫🇷
(cf. [Wiktionary](https://en.wiktionary.org/wiki/flemmard))

**Flemmarr** is an automation tool designed to simplify configuring all your **-arr applications (Sonarr, Radarr, Lidarr, Readarr, and Prowlarr)** using YAML configuration files. It leverages each application's API to seamlessly apply configurations as code, ensuring repeatability, simplicity, and consistency across your setups.

## Prerequisites

Before using Flemmarr, ensure that you have:

- **Docker** installed on your system.
- Your preferred **-arr applications** running and reachable (e.g., Sonarr, Radarr, Lidarr, Readarr, Prowlarr).
- **API keys** for each -arr application, retrievable from their web UI (`Settings > General`).
- Basic familiarity with YAML (recommended but not essential).

## Installation

The simplest way is to run Flemmarr using Docker alongside your other -arr applications:

```bash
docker run pierremesure/flemmarr:latest -v ./config/flemmarr:config
```

You can also just add it to your **docker-compose.yml**

```yaml
services:
  flemmarr:
    container_name: flemmarr
    image: pierremesure/flemmarr
    volumes:
      - "./config/flemmarr:/config"
```

Check out the example [docker-compose.yml](docker-compose.yml) with flemmarr alongside all other -arr apps.

## Configuration

To configure your apps, simply put a file called **config.yml** in the **config** folder.

For each app, you need to provide the address and the port under the **server** key.

Regarding the actual configuration, both keys and values need to be the ones used by the apps to communicate with their user interface through the API.

For instance, in order to change the app's language to French, a call would be made to `/config/ui` with a payload containing `uiLanguage: 2`. To add a new root folder, the call would go to `/rootfolder` and send the folder's name, path and some more metadata.

These two examples are displayed below:

```yaml
lidarr:
  server:
    address: localhost
    port: 8686
  config:
    ui:
      uiLanguage: 2 # 1 = English, 2 = French, 3 = Spanish...
  rootfolder:
    - name: Music
      path: /data/music
      defaultTags: []
      defaultQualityProfileId: 1
      defaultMetadataProfileId: 1
```

Check out the example [config.yml](config/flemmarr/config.yml) with more settings for various apps.

**Note:** The APIs for all -arr tools can be inconsistent. Sometimes, fields are required without clear reasons, and default values may differ from those applied by the GUI.

If you cannot find how to change a specific part of the configuration in this file, you will have to find out by yourself how it should look. You can:

- Browse the API docs of the app ([Sonarr](https://sonarr.tv/docs/api/), [Radarr](https://radarr.video/docs/api/), [Lidarr](https://lidarr.audio/docs/api/), [Readarr](https://readarr.com/docs/api/), [Prowlarr](http://prowlarr.com/docs/api/))
- Use your browser inspector to identify which call is sent by the GUI
- Use a REST client such as [Insomnia](https://insomnia.rest) to tinker with your payload and see exactly which values work and don't
- Ask for help by creating an issue.

Once you've found the solution, please add it to the example config file so others can benefit from your knowledge.

## Contributing

I created Flemmarr because I was surprised that there wasn't a way to write configuration as code for any of the -arr applications. I hope it is useful to more people.

I do not actually use any of the -arr apps in my daily life; I was just helping a friend to install them. So I don't plan on spending too much time on maintaining or improving the project. Feel free to submit your issues and suggestions! And feel free to look at the (very simple) code and documentation and try to make them better.

## Credits

Cute cartoon vector created by [catalyststuff](https://www.freepik.com/free-vector/cute-sloth-yoga-cartoon-icon-illustration_11167789.htm) - [freepik.com](https://www.freepik.com)
