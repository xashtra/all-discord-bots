# Exortic Selfbot Commands List

## Command Prefix
The bot's prefix is dynamically configured using the `PREFIX` environment variable in Railway. By default, it is `!`.

In the documentation below, `<prefix>` represents whatever prefix you set (e.g. `.` or `?` or `!`).

## Public Commands
These commands can be used by anyone unless the bot is locked.

- `<prefix>startcount`: Starts the counting loop in the current text channel. If a voice channel ID is configured in the environment, the bot connects to it; otherwise, it joins the voice channel you are currently in.
- `<prefix>stopcount`: Stops the counting loop and disconnects the bot from the voice channel.
- `<prefix>join` (or `<prefix>j`): Makes the bot join your current voice channel (or the configured voice channel if `VOICE_CHANNEL_ID` is set).
- `<prefix>leave` (or `<prefix>l`): Makes the bot leave the voice channel.
- `<prefix>clear`: Deletes the bot's status messages and replies from the last 100 messages, leaving only the numbers.
- `<prefix>countclear <number>` (or `<prefix>clearcount <number>`): Deletes the latest N counting messages and rolls back the count. Supported in text channels, voice chat, and special control channels.
- `<prefix>help`: Displays a list of all available commands.

## Owner-Only Commands
These commands can only be used by the bot owner.

- `<prefix>addadmin <@mention or ID>`: Adds a user to the admin list.
- `<prefix>removeadmin <@mention or ID>`: Removes a user from the admin list.
- `<prefix>admin`: Lists all current admins (mentions them).
- `<prefix>locked`: Restricts the bot so that only the owner can use it. Admins will be ignored.
- `<prefix>unlock`: Unlocks the bot so that admins can use commands again.

---

### Hosting Configuration
The bot uses the following environment variables (which should be set in the Railway dashboard):
- `TOKEN`: (Required) Your Discord user/selfbot token.
- `OWNER_ID`: (Required) Your Discord user ID (only the owner can execute owner-only commands).
- `PREFIX`: (Optional) The character(s) used as the command prefix. Defaults to `!`.
- `VOICE_CHANNEL_ID`: (Optional) The ID of the Discord voice channel the bot should bind to. When set, the bot will immediately connect to this voice channel on startup, only allow connection to this channel, automatically return to it if disconnected or moved, and ignore the voice state of command senders.
