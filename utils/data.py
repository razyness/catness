import toml

class DictToAttr(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"Attribute '{name}' not found")

config = toml.load('config.toml')

icons: DictToAttr = DictToAttr({
	"edit": "<:edit:1062784953399648437>",
	"regen": "<:regen:1062784969749045318>",
	"download": "<:download:1062784992243105813>",
	"spotify_white": "<:spotify_white:1062784981203689472>",
	"bookmark": "<:bookmark:1062790109491114004>",
	"remove": "<:remove:1062791085404999781>",
	"active_developer": "<:Active_Developer:1078093417680224356>",
	"bot_http_interactions": "<:Supports_Commands:1078022481144729620>",
	"bug_hunter": "<:Bug_Hunter:1078015408684142743>",
	"bug_hunter_level_2": "<:Bug_Hunter_Level_2:1078015437285097542>",
	"discord_certified_moderator": "<:Discord_Mod_Alumni:1078091018886451281>",
	"early_supporter": "<:Early_Supporter:1078015810909524149>",
	"early_verified_bot_developer": "<:Verified_Bot_Developer:1078094815398461450>",
	"hypesquad": "<:HypeSquad_Event:1078014370912686180>",
	"hypesquad_balance": "<:HypeSquad_Balance:1078014406396485642>",
	"hypesquad_bravery": "<:HypeSquad_Bravery:1078014366953242794>",
	"hypesquad_brilliance": "<:HypeSquad_Brilliance:1078014368454820010>",
	"partner": "<:Discord_Partner:1078021591859986463>",
	"staff": "<:Discord_Staff:1078015590683390093>",
	"verified_bot": "<:Verified_Bot:1078090782118002719>",
	"lastfm": "<:lastfm:1080282189100482693>",
	"steam": "<:steam:1080281878847832186>",
	"contributor": "<:Contributor:1078661797185335398>",
	"back": "<:back:1101510067880202301>",
	"page_left": "<:page_left:1112880577390055544>",
	"page_right": "<:page_right:1112880675067015188>",
	"close": "<:close:1114209439122210918>",
	"special": "<:Special:1078664371661713449>",
	"bot": "<:bot:1078091845051088979>",
	"nitro": "<:nitro:1078094211351584928>",
	"github": "<:github:1114661850118897806>",
    "osu_supporter": "<:osu_supporter:1167584560624717876>"
})
