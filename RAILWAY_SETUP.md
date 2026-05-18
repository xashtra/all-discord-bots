# Discord Counting Bot 2 — Railway Setup Guide

We have updated the counting bot codebase to dynamically read configuration from environment variables. Below is the guide to configure these environment variables in your **Railway** server.

---

## 🛠️ Step-by-Step Railway Configuration

1. **Open your project on Railway**:
   - Go to your [Railway Dashboard](https://railway.app/).
   - Click on the project containing **discord count bot 2**.

2. **Access the Variables Tab**:
   - Click on the bot's service card.
   - Select the **Variables** tab from the top menu.

3. **Add the New Variables**:
   Click on **+ Add Variable** and enter the following settings:

| Variable Name | Required | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `TOKEN` | **Yes** | *None* | Your Discord account user token (never share this!). |
| `OWNER_ID` | **Yes** | *None* | Your personal Discord user numeric ID (e.g. `123456789012345678`). |
| `PREFIX` | *No* | `!` | The command prefix of your choice (e.g. `!`, `.`, `?`, or any word). |
| `VOICE_CHANNEL_ID` | *No* | *None* | The exact ID of the voice channel the bot should bind to. |

---

## 🔒 Voice Channel ID Binding Behavior

When you configure the `VOICE_CHANNEL_ID` environment variable:
- **Startup Connection**: The bot will immediately connect to this voice channel as soon as it goes online on Railway.
- **Bound Restrictions**:
  - The bot will only stay in this voice channel.
  - If a user triggers the `join`, `j`, or `startcount` commands, the bot will join the configured VC ID, completely ignoring the user's current VC context.
  - If the bot is disconnected or dragged/moved to a different VC by someone, it will automatically reconnect to the configured voice channel after 5 seconds.
  - The keepalive background worker will check every 5 minutes and enforce that the bot remains connected to the configured voice channel.

---

## 📢 Special Control Channel Feature (ID: `1505813873033478164`)

We have added a custom remote-control feature bound exclusively to the Discord text channel ID **`1505813873033478164`**:
- **Reconnect Command** (`start` / `Start` / `START` / `st`):
  - Sends a direct command to the bot to reconnect (or connect) to the voice channel specified in `VOICE_CHANNEL_ID`.
  - Works both with and without the configured prefix.
- **Start Counting in VC text channel** (`startcount` / `Startcount` / `START COUNT`):
  - Ensures the bot is connected to the voice channel `VOICE_CHANNEL_ID`.
  - Commences the counting loop **inside the voice channel's text chat** (its VC text channel), rather than sending numbers in the command channel.
  - Works both with and without the configured prefix.

---

## 💬 Command Usage Example

Assuming you configured `PREFIX` to `.` and `VOICE_CHANNEL_ID` to `987654321098765432`:

* **Start counting**:
  ```text
  .startcount
  ```
  *(The bot will connect to VC `987654321098765432` and start the counting loop)*

* **Stop counting & disconnect**:
  ```text
  .stopcount
  ```

* **Manually join VC**:
  ```text
  .join
  ```
  *(Connects straight to VC `987654321098765432`)*

* **Check help menu**:
  ```text
  .help
  ```
