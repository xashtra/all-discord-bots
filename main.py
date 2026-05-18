import os
import sys
import asyncio
import discord
from dotenv import load_dotenv

# Load environment variables automatically (from .env file locally, or system variables on Railway)
load_dotenv()

# Configuration (Set these in Railway Variables or a local .env file)
TOKEN = os.getenv("TOKEN")
OWNER_ID_STR = os.getenv("OWNER_ID")
OWNER_ID = int(OWNER_ID_STR) if OWNER_ID_STR else None
PREFIX = os.getenv("PREFIX", "!")
VOICE_CHANNEL_ID_STR = os.getenv("VOICE_CHANNEL_ID")
VOICE_CHANNEL_ID = int(VOICE_CHANNEL_ID_STR) if VOICE_CHANNEL_ID_STR else None

class SilenceSource(discord.AudioSource):
    """Sends silent audio frames to keep the voice connection alive."""
    # Opus silence frame
    SILENCE = b'\xf8\xff\xfe'

    def read(self):
        return self.SILENCE

    def is_opus(self):
        return True

class SelfBot(discord.Client):
    def __init__(self):
        # Comprehensive spoofing to match a real Windows browser
        super().__init__(
            super_properties={
                'os': 'Windows',
                'browser': 'Chrome',
                'device': '',
                'system_locale': 'en-US',
                'browser_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'browser_version': '120.0.0.0',
                'os_version': '10',
                'referrer': '',
                'referring_domain': '',
                'referrer_current': '',
                'referring_domain_current': '',
                'release_channel': 'stable',
                'client_build_number': 302830,
                'client_event_source': None,
            }
        )
        self.counting_task = None
        self.count = 1
        self.admins = set()
        self.locked = False
        self.target_vc_channel = None  # Track VC for auto-reconnect
        self.target_text_channel = None  # Track text channel for counting
        self.keepalive_task = None

    def play_silence(self, voice_client):
        """Play silent audio to prevent idle disconnect."""
        if voice_client and voice_client.is_connected() and not voice_client.is_playing():
            voice_client.play(SilenceSource())

    async def connect_to_configured_vc(self):
        """Connect to the bound voice channel configured in environment variables."""
        await self.wait_until_ready()
        if not VOICE_CHANNEL_ID:
            return
        
        try:
            channel = self.get_channel(VOICE_CHANNEL_ID)
            if not channel:
                channel = await self.fetch_channel(VOICE_CHANNEL_ID)
            
            if not isinstance(channel, discord.VoiceChannel):
                print(f"Error: Channel with ID {VOICE_CHANNEL_ID} is not a Voice Channel.")
                sys.stdout.flush()
                return

            self.target_vc_channel = channel
            guild = channel.guild
            vc = guild.voice_client

            if vc is None or not vc.is_connected():
                print(f"Connecting to configured VC: {channel.name} ({channel.id})...")
                sys.stdout.flush()
                # Disconnect from any other voice client
                for existing_vc in self.voice_clients:
                    await existing_vc.disconnect()
                
                voice_client = await channel.connect(timeout=20.0, reconnect=True)
                self.play_silence(voice_client)
                print(f"Successfully connected to configured VC: {channel.name}")
                sys.stdout.flush()
            else:
                self.play_silence(vc)
        except Exception as e:
            print(f"Failed to connect to configured VC: {e}")
            sys.stdout.flush()

    async def on_ready(self):
        print(f"Logged in as {self.user.name} ({self.user.id})")
        print(f"Prefix configured: '{PREFIX}'")
        if VOICE_CHANNEL_ID:
            print(f"Bound to Voice Channel ID: {VOICE_CHANNEL_ID}")
        else:
            print("No Voice Channel ID configured. Running in dynamic VC mode.")
        print(f"Ready! Join/ensure bot is in voice and type {PREFIX}startcount in the text channel you want to count in.")
        sys.stdout.flush()

        # If VOICE_CHANNEL_ID is set, connect on startup
        if VOICE_CHANNEL_ID:
            self.loop.create_task(self.connect_to_configured_vc())

        # Start the keepalive loop
        if not self.keepalive_task:
            self.keepalive_task = self.loop.create_task(self.keepalive_loop())

    async def on_voice_state_update(self, member, before, after):
        """Auto-reconnect if the bot gets disconnected from voice or moved to wrong channel."""
        if member.id != self.user.id:
            return

        # Scenario 1: Bot was disconnected entirely (after.channel is None)
        if before.channel is not None and after.channel is None:
            if VOICE_CHANNEL_ID:
                print(f"Voice disconnected! Auto-reconnecting to bound VC ID {VOICE_CHANNEL_ID} in 5s...")
                sys.stdout.flush()
                await asyncio.sleep(5)
                await self.connect_to_configured_vc()
            elif self.target_vc_channel and self.counting_task:
                print(f"Voice disconnected! Auto-reconnecting to {self.target_vc_channel.name} in 5s...")
                sys.stdout.flush()
                await asyncio.sleep(5)
                try:
                    vc = await self.target_vc_channel.connect(timeout=20.0, reconnect=True)
                    self.play_silence(vc)
                    print(f"Auto-reconnected to {self.target_vc_channel.name}")
                    sys.stdout.flush()
                except Exception as e:
                    print(f"Auto-reconnect failed: {e}")
                    sys.stdout.flush()

        # Scenario 2: Bot was moved to a different voice channel
        elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            if VOICE_CHANNEL_ID and after.channel.id != VOICE_CHANNEL_ID:
                print(f"Bot was moved to a different voice channel, but it is bound to VC ID {VOICE_CHANNEL_ID}. Reconnecting to bound VC in 5s...")
                sys.stdout.flush()
                await asyncio.sleep(5)
                await self.connect_to_configured_vc()

    async def keepalive_loop(self):
        """Periodically check voice connection health and reconnect if needed."""
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                await asyncio.sleep(5 * 60)  # Check every 5 minutes

                if VOICE_CHANNEL_ID:
                    # Enforce the bound VC
                    channel = self.get_channel(VOICE_CHANNEL_ID)
                    if not channel:
                        channel = await self.fetch_channel(VOICE_CHANNEL_ID)
                    
                    if isinstance(channel, discord.VoiceChannel):
                        self.target_vc_channel = channel
                        guild = channel.guild
                        vc = guild.voice_client

                        if vc is None or not vc.is_connected():
                            print(f"Keepalive: Enforcing connection to bound VC: {channel.name}...")
                            sys.stdout.flush()
                            await self.connect_to_configured_vc()
                        else:
                            self.play_silence(vc)
                else:
                    if not self.target_vc_channel:
                        continue

                    # Check if we're supposed to be in a VC but aren't
                    guild = self.target_vc_channel.guild
                    vc = guild.voice_client

                    if vc is None or not vc.is_connected():
                        print(f"Keepalive: Not connected, reconnecting to {self.target_vc_channel.name}...")
                        sys.stdout.flush()
                        try:
                            vc = await self.target_vc_channel.connect(timeout=20.0, reconnect=True)
                            self.play_silence(vc)
                            print(f"Keepalive: Reconnected to {self.target_vc_channel.name}")
                            sys.stdout.flush()
                        except Exception as e:
                            print(f"Keepalive: Reconnect failed: {e}")
                            sys.stdout.flush()
                    else:
                        # Already connected — make sure silence is playing
                        self.play_silence(vc)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Keepalive error: {e}")
                sys.stdout.flush()

    async def on_message(self, message):
        content = message.content.strip()

        # Determine roles
        is_owner = (message.author.id == OWNER_ID or message.author.id == self.user.id)
        is_admin = (message.author.id in self.admins)

        # Permission check
        if not is_owner:
            if self.locked or not is_admin:
                return

        # Check for special text channel feature
        if message.channel.id == 1505813873033478164:
            # Strip the prefix if it exists, to support both prefix and prefix-less commands
            clean_content = content
            if content.startswith(PREFIX):
                clean_content = content[len(PREFIX):].strip()
            
            # Normalize spaces (e.g. "START COUNT" -> "start count")
            normalized_content = " ".join(clean_content.split()).lower()

            if normalized_content in ["start", "st"]:
                if VOICE_CHANNEL_ID:
                    await message.reply("Reconnecting to the configured voice channel...")
                    await self.connect_to_configured_vc()
                else:
                    await message.reply("No VOICE_CHANNEL_ID is configured in environment variables!")
                return

            elif normalized_content in ["startcount", "start count"]:
                # Make sure the bot is connected to its voice channel
                if VOICE_CHANNEL_ID:
                    channel = self.get_channel(VOICE_CHANNEL_ID)
                    if not channel:
                        try:
                            channel = await self.fetch_channel(VOICE_CHANNEL_ID)
                        except Exception:
                            channel = None
                    
                    if channel:
                        self.target_vc_channel = channel
                        guild = channel.guild
                        vc = guild.voice_client
                        if vc is None or not vc.is_connected():
                            await message.reply("Connecting to the configured voice channel first...")
                            await self.connect_to_configured_vc()
                
                # Check if we have a target voice channel now
                if not self.target_vc_channel:
                    await message.reply("Cannot start counting in VC: Bot is not connected to a voice channel.")
                    return
                
                if self.counting_task:
                    await message.reply("Already counting in VC text channel!")
                    return
                
                # Start counting in the voice channel's text channel
                self.counting_task = self.loop.create_task(self.count_loop(self.target_vc_channel))
                await message.reply(f"Started counting in the VC text channel: {self.target_vc_channel.name}")
                return

            elif normalized_content.startswith("clearcount") or normalized_content.startswith("countclear"):
                try:
                    num = int(normalized_content.split()[1])
                except (IndexError, ValueError):
                    await message.reply("Usage: clearcount <number>")
                    return

                if not self.target_vc_channel:
                    await message.reply("Cannot clear counts: Bot is not connected to a voice channel.")
                    return

                deleted = 0
                await message.reply(f"Clearing the latest {num} counting messages in VC text channel ({self.target_vc_channel.name})...")
                try:
                    async for msg in self.target_vc_channel.history(limit=500):
                        if deleted >= num:
                            break
                        # Only delete the bot's counting messages (digits only)
                        if msg.author.id == self.user.id and msg.content.isdigit():
                            await msg.delete()
                            deleted += 1
                            await asyncio.sleep(1)  # Avoid rate limits

                    # Roll back the count
                    self.count = max(1, self.count - deleted)
                    await message.reply(f"Deleted {deleted} counting messages in VC text channel. Count reset to {self.count}.")
                except Exception as e:
                    print(f"Error during clearcount in VC text channel: {e}")
                    sys.stdout.flush()
                    await message.reply(f"Error: {e}")
                return

        # Check if message starts with the configured prefix (for other channels/commands)
        if not content.startswith(PREFIX):
            return

        # Extract command and arguments
        cmd_content = content[len(PREFIX):].strip()
        cmd_lower = " ".join(cmd_content.split()).lower()

        if cmd_lower.startswith("startcount") or cmd_lower.startswith("start count"):
            if self.counting_task:
                await message.reply("Already counting!")
                return

            target_vc = None
            if VOICE_CHANNEL_ID:
                try:
                    target_vc = self.get_channel(VOICE_CHANNEL_ID)
                    if not target_vc:
                        target_vc = await self.fetch_channel(VOICE_CHANNEL_ID)
                except Exception as e:
                    await message.reply(f"Failed to find the configured voice channel (ID: {VOICE_CHANNEL_ID}): {e}")
                    return
                if not isinstance(target_vc, discord.VoiceChannel):
                    await message.reply(f"Configured channel ID {VOICE_CHANNEL_ID} is not a voice channel!")
                    return
            else:
                if message.author.voice and message.author.voice.channel:
                    target_vc = message.author.voice.channel
                else:
                    await message.reply(f"You are not in a voice channel. Please join one first, or configure a VOICE_CHANNEL_ID environment variable.")
                    return

            try:
                # Disconnect from any existing voice clients first
                for existing_vc in self.voice_clients:
                    await existing_vc.disconnect()
                
                voice_client = await target_vc.connect(timeout=20.0, reconnect=True)
                self.target_vc_channel = target_vc
                self.play_silence(voice_client)
                await message.reply(f"Joined voice channel: {target_vc.name}")
                sys.stdout.flush()
            except Exception as e:
                await message.reply(f"Failed to join voice channel: {e}")
                sys.stdout.flush()
                return

            # Determine counting destination: if VOICE_CHANNEL_ID is set, count in target_vc (VC text channel)
            # otherwise count in message.channel (the text channel)
            count_channel = target_vc if VOICE_CHANNEL_ID else message.channel
            self.target_text_channel = count_channel
            self.counting_task = self.loop.create_task(self.count_loop(count_channel))
            await message.reply(f"Counting started in {count_channel.name}")

        elif cmd_content.startswith("stopcount"):
            if self.counting_task:
                self.counting_task.cancel()
                self.counting_task = None
                self.target_vc_channel = None
                self.target_text_channel = None
                await message.reply("Stopped counting.")
                for vc in self.voice_clients:
                    await vc.disconnect()
            else:
                await message.reply("Not currently counting.")

        elif cmd_content.startswith("join") or cmd_content.startswith("j"):
            target_vc = None
            if VOICE_CHANNEL_ID:
                try:
                    target_vc = self.get_channel(VOICE_CHANNEL_ID)
                    if not target_vc:
                        target_vc = await self.fetch_channel(VOICE_CHANNEL_ID)
                except Exception as e:
                    await message.reply(f"Failed to find the configured voice channel (ID: {VOICE_CHANNEL_ID}): {e}")
                    return
                if not isinstance(target_vc, discord.VoiceChannel):
                    await message.reply(f"Configured channel ID {VOICE_CHANNEL_ID} is not a voice channel!")
                    return
            else:
                if message.author.voice and message.author.voice.channel:
                    target_vc = message.author.voice.channel
                else:
                    await message.reply("You are not in a voice channel. Please join one first, or configure a VOICE_CHANNEL_ID environment variable.")
                    return

            try:
                # Disconnect existing first
                for vc in self.voice_clients:
                    if vc.guild.id == message.guild.id:
                        await vc.disconnect()
                
                print(f"Attempting to join {target_vc.name}...")
                voice_client = await target_vc.connect(timeout=20.0, reconnect=True)
                self.target_vc_channel = target_vc
                self.play_silence(voice_client)
                await message.reply(f"Joined voice channel: {target_vc.name}")
                sys.stdout.flush()
            except Exception as e:
                error_msg = f"Failed to join voice channel: {e}"
                print(error_msg)
                await message.reply(error_msg)
                sys.stdout.flush()

        elif cmd_content.startswith("leave") or cmd_content.startswith("l"):
            self.target_vc_channel = None
            disconnected = False
            for vc in self.voice_clients:
                await vc.disconnect()
                disconnected = True
            
            if disconnected:
                await message.reply("Left the voice channel.")
            else:
                await message.reply("I am not in a voice channel.")

        elif cmd_content.startswith("countclear") or cmd_content.startswith("clearcount"):
            try:
                num = int(cmd_content.split()[1])
            except (IndexError, ValueError):
                await message.reply(f"Usage: {PREFIX}clearcount <number>")
                return

            deleted = 0
            try:
                async for msg in message.channel.history(limit=500):
                    if deleted >= num:
                        break
                    # Only delete the bot's counting messages (digits only)
                    if msg.author.id == self.user.id and msg.content.isdigit():
                        await msg.delete()
                        deleted += 1
                        await asyncio.sleep(1)  # Avoid rate limits

                # Roll back the count
                self.count = max(1, self.count - deleted)
                await message.reply(f"Deleted {deleted} counting messages. Count reset to {self.count}.")
            except Exception as e:
                print(f"Error during clearcount: {e}")
                sys.stdout.flush()
                await message.reply(f"Error: {e}")

        elif cmd_content.startswith("clear"):
            await message.reply("Clearing messages...")
            # Delete messages sent by the selfbot that are NOT numbers (like replies/status msgs)
            try:
                count = 0
                async for msg in message.channel.history(limit=100):
                    # If it's a message from the selfbot
                    if msg.author.id == self.user.id:
                        # Don't delete numbers (the counting messages)
                        if not msg.content.isdigit():
                            await msg.delete()
                            count += 1
                            await asyncio.sleep(1) # sleep to avoid rate limits on deletion
                
                # We will also delete the command if the owner sent it
                if message.author.id == OWNER_ID:
                    try:
                        await message.delete()
                    except discord.Forbidden:
                        pass
                        
            except Exception as e:
                print(f"Error during clearing: {e}")
                sys.stdout.flush()

        elif cmd_content == "help":
            help_text = (
                f"**Exortic Selfbot Commands:**\n"
                f"- `{PREFIX}startcount`: Start counting in the current channel.\n"
                f"- `{PREFIX}stopcount`: Stop counting and leave VC.\n"
                f"- `{PREFIX}join` / `{PREFIX}j`: Join the configured/current voice channel.\n"
                f"- `{PREFIX}leave` / `{PREFIX}l`: Leave the voice channel.\n"
                f"- `{PREFIX}clear`: Delete the bot's non-number messages.\n"
                f"- `{PREFIX}countclear <number>`: Delete the latest N counting messages.\n"
                f"- `{PREFIX}help`: Show this list.\n\n"
                f"**Owner Only:**\n"
                f"- `{PREFIX}addadmin <@mention/ID>`: Add an admin.\n"
                f"- `{PREFIX}removeadmin <@mention/ID>`: Remove an admin.\n"
                f"- `{PREFIX}admin`: Show current admins.\n"
                f"- `{PREFIX}locked`: Restrict to owner only.\n"
                f"- `{PREFIX}unlock`: Allow admins again."
            )
            await message.reply(help_text)

        # Owner-only Admin/Lock commands
        elif is_owner:
            if cmd_content.startswith("addadmin"):
                try:
                    raw_id = cmd_content.split()[1].strip('<@!>')
                    admin_id = int(raw_id)
                    self.admins.add(admin_id)
                    await message.reply(f"Added {admin_id} to admin list.")
                except (IndexError, ValueError):
                    await message.reply(f"Usage: {PREFIX}addadmin <ID or @mention>")

            elif cmd_content.startswith("removeadmin"):
                try:
                    raw_id = cmd_content.split()[1].strip('<@!>')
                    admin_id = int(raw_id)
                    if admin_id in self.admins:
                        self.admins.remove(admin_id)
                        await message.reply(f"Removed {admin_id} from admin list.")
                    else:
                        await message.reply(f"{admin_id} is not an admin.")
                except (IndexError, ValueError):
                    await message.reply(f"Usage: {PREFIX}removeadmin <ID or @mention>")

            elif cmd_content.startswith("locked"):
                self.locked = True
                await message.reply("Bot is now LOCKED to owner only.")

            elif cmd_content.startswith("unlock"):
                self.locked = False
                await message.reply("Bot is now UNLOCKED for admins.")

            elif cmd_content == "admin":
                if not self.admins:
                    await message.reply("No admins added.")
                else:
                    mentions = [f"<@{admin_id}>" for admin_id in self.admins]
                    await message.reply(f"**Current Admins:** {' '.join(mentions)}")

    async def count_loop(self, channel):
        while True:
            try:
                await channel.send(str(self.count))
                self.count += 1
                # Sleep for 4 minutes
                await asyncio.sleep(4 * 60)  
            except Exception as e:
                print(f"Error while counting: {e}")
                sys.stdout.flush()
                await asyncio.sleep(4 * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("      EXORTIC SELFBOT INITIALIZATION STATE")
    print("=" * 60)
    
    missing_vars = []
    if not TOKEN:
        missing_vars.append("TOKEN")
        print("[CRITICAL ERROR] 'TOKEN' Environment Variable is MISSING!")
    if not OWNER_ID:
        missing_vars.append("OWNER_ID")
        print("[CRITICAL ERROR] 'OWNER_ID' Environment Variable is MISSING!")
        
    if missing_vars:
        print("\nHOW TO FIX THIS IN RAILWAY:")
        print("1. Open your project dashboard on Railway (https://railway.app/).")
        print("2. Click on this bot service card.")
        print("3. Navigate to the 'Variables' tab at the top.")
        print("4. Click '+ Add Variable' to add the missing variables:")
        for var in missing_vars:
            print(f"   - Name: {var}")
        print("5. Once added, Railway will automatically redeploy the bot and it will start!")
        print("=" * 60)
        sys.stdout.flush()
        sys.exit(1)
        
    print("[INFO] 'TOKEN' and 'OWNER_ID' successfully detected.")
    print("=" * 60)
    sys.stdout.flush()

    bot = SelfBot()
    bot.run(TOKEN)
