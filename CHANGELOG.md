# Changelog

## v1.0.1
- Railway: Xray outbound works with IPv4 and IPv6 in every region; no dependency on geo files; nginx and the core use only the CPUs the service really has (Metal regions no longer start dozens of workers)
- HTTPUpgrade configs without early data, so half of the configs never depend on it
- GitHub page redesigned: cinematic deploy intro, live world map of the 4 Railway regions, animated panel, subscription page and sales bot
- Railway: no start step can stop the deploy any more (certificate, config paths and nginx settings all have a safe fallback)
- Config paths are written automatically if they are missing
- Back button of the phone or browser closes the open CHOST menu, dialog, page or QR sheet first (never leaves the panel by surprise); every dialog closes with X, Cancel, the background or Escape; menus close with a tap outside, Escape or scrolling
- Spelling: «سازنده‌ی پنل»، «باقی‌مانده»
- Build uses the same proven layout as the original Railway package; at start the panel folder and its Python (also a .venv) are found automatically
- CHOST doctor: checks configs, domain, subscription, core, panel, nginx and the bot all the time, repairs only the broken part and tells the bot admins in Telegram
- No more service restarts: every part runs under its own supervisor and is started again in place in a few seconds; database updates are never interrupted
- Railway: answers on 8080 and on the port Railway gives the service, so the domain and the health check pass in every region; nginx never stops the deploy because of IPv6
- Panel API calls survive PasarGuard route spelling changes (trailing slash)
- Configs always reach the subscription: the domain is picked up live (also when it is generated after the deploy), users saved without a group get all 6 configs, the subscription page loads the links from the panel if the page itself has none
- Works the same on all 4 Railway regions
- Phone menu (three lines): CHOST pages in every copy of the menu, the menu no longer changes between opens, the header stays visible, every CHOST page has a Back button
- Language: no more jumping between Persian and English when the menu is closed
- The creator card never covers the panel's own dialogs (creating users is never blocked) and shows once per login
- Faster configs: larger proxy buffers, TCP Fast Open on the way out
- New GitHub page: animated hero, one-brand showcase

## v1.0.0
- CHOST Panel: PasarGuard + Xray core + nginx in one Railway service (port 8080)
- Zero-touch setup: owner, core, 6 configs, hosts on the Railway domain, 2 groups, 10 templates, reseller role
- Two groups: 𝗖𝗛𝗢𝗦𝗧 VIP (Turbo, Stream, Ultra) and 𝗖𝗛𝗢𝗦𝗧 GAME (Gaming, Call, Stable)
- Config names use clean symbols only (✦ for VIP, ◆ for GAME); older lightning-bolt names are still detected by the subscription page
- 6 really different configs: VLESS-WS, VMess-WS, VLESS-HTTPUpgrade, Trojan-WS, all TLS 443 with early data
- New CHOST subscription page: liquid gold usage orb, live countdown, real ping test, auto device detection (phone / desktop), one-tap import, built-in QR, Persian and English
- Works in every Railway region: listens on IPv4 and IPv6 (auto IPv4-only fallback), longer start-up grace for slow regions, region shown in the logs
- Sidebar "پنل نمایندگی" (owner only): a native page inside the panel with stats, search, table / mobile cards and row actions; create reseller panels with a data quota, top up or set quota, change password, enable/disable, delete; login info ready to copy
- Login page "دسترسی مالک": new owner key dialog (CH-XXXX-XXXX-XXXX, 5 minutes, one use, paste button, password strength, any password from 4 characters, brute-force lock)
- Bot wallet: card-to-card top up, instant buy/renew from balance, automatic refund on failure
- Referral system: personal invite link, commission % to the inviter wallet
- Admin user management in the bot: search by ID/username, add/subtract balance, direct message, ban/unban
- Faster bot start (settings apply within seconds); fixed admin menu and back buttons
- Telegram sales bot: sidebar page "ربات تلگرام" (token + admin IDs, live status, sales numbers, test message). In the bot: plans, prices, card number, texts, channel + force join, pending receipts, broadcast, open/close sales. Users: buy, card-to-card receipt, auto-created subscription, renew, my subscriptions, help, support
- PasarGuard donation popup and "Support us" menu item removed; a CHOST creator card with the official channel (@CHOST543) shows once per login
- Bot: discount codes (percent, usage cap, once per user), one-time free test account, renewal reminders (low data / 3 days left), full daily backup to the admins (panel DB + bot DB + install keys) and on-demand backup
- Bilingual: every CHOST page, dialog, toast and server message follows the panel language (Persian / English) live, with the right text direction
- Dashboard: clean menu, password change in the "امنیت حساب" page, 5-minute owner key, self-healing core and watchdog
