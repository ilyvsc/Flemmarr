# Understanding the Configuration

Let's break down the YAML configuration file section by section.

- YAML aliases/anchors for reuse of config values.
- Naming conventions for files and folders (how Sonarr/Radarr will rename your TV episodes or movie files).
- Media management settings (options for how files are imported, whether to rename, etc.).
- Root folder structure (where your media is stored on disk).
- Download client configuration (how Sonarr/Radarr connect to qBittorrent or another client).

For clarity, we'll use examples and snippets. Even if your YAML file looks slightly different, the concepts will be the same.

## YAML Anchors and Aliases

The YAML configuration might use anchors and aliases to avoid repeating the same values in multiple places. This is a feature of YAML syntax that helps keep the file DRY (Don't Repeat Yourself). An anchor is defined with an ampersand (`&`) and gives a name to a block of content. Later in the file, an alias can reference that content with an asterisk (`*`). The result is that the aliased content is treated as if it were written in full in that place.

### How they work

You define a chunk of configuration once with `&name`, and then reuse it elsewhere with `*name`. This prevents errors and makes maintenance easier – change the anchor definition once, and all references update automatically.

#### Example Configuration

```yaml
# Define an anchor for the episode naming scheme
episodeFormat: &episodeFormat "{Series Title} - S{season:00}E{episode:00} - {Episode Title} [{Quality Full}]"

# Use the same format in multiple places via alias
sonarr:
  naming:
    standardEpisodeFormat: *episodeFormat
    dailyEpisodeFormat: *episodeFormat
    animeEpisodeFormat: *episodeFormat

otherAppConfig:
  someEpisodeFormat: *episodeFormat
```

Remember that anchors and aliases are purely a YAML convenience – **when the file is processed, those aliases are replaced with the actual values they point to**. So in the end, **Sonarr/Radarr get the full expanded settings** as if you typed them in each place.

## Naming Conventions for Media Files

One of the key parts of the configuration is setting up how Sonarr and Radarr should name your folders and files. Consistent naming is important for media servers (like Plex, Emby, Jellyfin) to correctly identify and display your content, and it helps avoid confusion or duplicate downloads.

### Why do we care about naming?

- **Prevent duplicate downloads**: If Sonarr/Radarr knows a file's quality from its name, it won't grab another of the same quality thinking you don't have it.
- **Upgrade clarity**: If you choose to upgrade a file (say from `HDTV` to `BluRay`), you can easily see which file is which by the name.
- **Media Server compatibility**: Plex/Emby don't require such detailed names (they often just need `Title (Year)` or `S01E01` patterns), but including extra info doesn't hurt because these servers ignore the tags in brackets. They typically only display the nice title (they parse the file name to match it to metadata). So having a longer filename doesn't clutter your Plex library's look.
- **Ease of troubleshooting**: If something's wrong with a file (bad release from a particular group, or a cam quality mislabeled as `HDTV`, etc.), the filename can provide clues about its source.

> [!IMPORTANT]
> After applying the config, you should see those patterns reflected in each app's `Settings > Media Management` (naming) section. Usually, you also need to ensure the `"Rename Files"` option is enabled for the naming to actually apply when new downloads are imported.

## Media Management Settings

- **Rename files after import**: This is the option `"Rename Episodes"` in Sonarr or `"Rename Movies"` in Radarr. We almost always want this enabled (set to true in the config) so that when a download is completed, Sonarr/Radarr will rename the video file according to the naming convention we just discussed.

- **Create empty series folders**: Sonarr can create a folder for a series as soon as you add it (even if no episodes are downloaded yet). This is optional – some prefer it for organization, others don't mind waiting until the first episode is grabbed. Check if the YAML has a setting for this; if not mentioned, Sonarr's default is to create the folder on first download.

- **Season folder usage**: A toggle for whether to put episodes in season subfolders. If the naming conventions are set (as above), usually the config will also ensure `"Use Season Folders"` is true. This goes hand-in-hand with the season folder naming format.

- **Replace Illegal Characters**: Filenames can sometimes contain characters not allowed by your OS (like `:` on Windows). Sonarr/Radarr by default replace these with harmless alternatives (e.g., replace `:` with `-`).

- **Delete Empty Folders**: After a series or season is completely deleted, Sonarr can remove the now-empty folders. If the YAML has this on, it helps keep your filesystem tidy (no leftover empty dirs). Likewise, Radarr can delete movie folders if a movie is removed. Beginners might not worry about this, but it's a nice housekeeping setting to enable.

## Root Folder Structure

A root folder in Sonarr/Radarr is the top-level directory where your media library resides. Typically, you have one root for TV shows and a different root for movies. Under these, the apps will create subfolders for each series or movie.

### Why root folders matter

When you add a new series in Sonarr, you must choose a root folder (e.g., you might have "`/media/TV Shows`" as the root, and Sonarr will then create `/media/TV Shows/Show Name`). The YAML configuration can preset your root folder paths so that when adding content, the correct location is already known to the app.

In the YAML, you might see something like:

```yaml
sonarr:
  rootFolder: /mnt/media/TV Shows

radarr:
  rootFolder: /mnt/media/Movies
```

> [!NOTE]
> If you use Docker, these correspond to **mounted volumes inside the container**. For instance, if in Docker you mapped your host's `/drive/Media/TV` to the container's `/tv` path, then Sonarr's root folder in settings should be `/tv`. Always ensure that the path Sonarr/Radarr sees is the correct one where it has access and where your media actually lives.

### Structure

> [!TIP]
> Your download client should NOT be set to download directly into these root folders. Instead, downloads should go to a separate "inbox" or intermediate folder, and then Sonarr/Radarr import to the root (library) folder.

Under the TV root, Sonarr will create a folder per show (named per the series folder format, e.g., "`Show (2020)`"). Under that, season subfolders if enabled, then files. Under the Movies root, Radarr will create a folder per movie (if movie folders are enabled), else it will drop the movie files directly under the root. We highly recommend using individual movie folders to avoid clutter and allow multiple versions of a movie if needed.

This separation means your library only has sorted, renamed files, and your downloader can handle seeding or cleanup in its own area. Never set your Sonarr/Radarr root folder to be the same as the downloader's folder – doing so can cause Sonarr/Radarr to try importing files that are still downloading, or your media server scanning incomplete files.

## Download Client Configuration

Sonarr and Radarr need to connect to a download client (like a BitTorrent or Usenet downloader) to fetch the media files. The YAML configuration includes settings to set up this connection so that you don't have to manually input them in the UI. We'll explain what these settings mean.

Common download clients:

- qBittorrent (torrent)
- uTorrent/Transmission/Deluge (torrent)
- SABnzbd or NZBGet (usenet)
- Others like Prowlarr (indexer aggregator, not exactly download client, but out of scope here)

For illustration, let's assume qBittorrent, since it's popular and was mentioned in prerequisites. A YAML snippet for adding qBittorrent to Sonarr might look like:

```yaml
sonarr:
  downloadClient:
    type: qBittorrent
    host: 192.168.1.100
    port: 8080
    username: admin
    password: yourpassword
    category: sonarr
```
